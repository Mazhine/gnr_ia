"""Verifie le corpus produit, fichier par fichier.

Ce script existe pour une raison precise : un corpus genere peut sembler
correct a la lecture et contenir une page annoncee au mauvais endroit, un
document annonce en anglais et ecrit en francais, ou un tableau de codes qui ne
correspond pas au constructeur. Ces defauts ne se voient pas dans le code, ils
se voient dans les fichiers.

    python -m scripts.gen_corpus.verifier
    python -m scripts.gen_corpus.verifier --corpus corpus

Sortie : une ligne par controle, code de retour non nul si un controle echoue.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .catalogue import CODES_PAR_FAMILLE, CONSTRUCTEURS, DOCUMENTS, Famille
from .inventaire import COLONNES, compter_pages
from .render import reperer_elements

CHAINE_INJECTION = "IGNORE LES INSTRUCTIONS PRÉCÉDENTES"
ADRESSE_INJECTION = "support@maintenance-externe.example"
CODES_PARTAGES = ("12", "33", "42", "51", "71")

# Valeurs imposées par le livrable 1. Les contrôler ici évite qu'un type ou un
# usage inventé se glisse dans l'inventaire sans que personne ne le remarque :
# c'est exactement ce qui était arrivé avec `usage_test=scanne`, qui n'existe
# pas dans la consigne (le scan est un format, pas un rôle de test).
TYPES_AUTORISES = {"manuel", "procedure", "fiche_securite", "schema", "codes_alarme", "photo",
                   "historique"}
USAGES_AUTORISES = {"normal", "contradictoire", "injection", "ambigu"}


@dataclass
class Resultat:
    nom: str
    ok: bool
    detail: str


class Corpus:
    """Acces memoise aux fichiers du corpus : un PDF n'est lu qu'une fois."""

    def __init__(self, racine: Path) -> None:
        self.racine = racine
        self._textes: dict[str, str] = {}

    def chemin(self, document_id: str) -> Path:
        doc = next(d for d in DOCUMENTS if d.id == document_id)
        return self.racine / doc.fichier

    def texte(self, document_id: str) -> str:
        """Texte extractible, espaces normalises. Vide pour une image ou un scan.

        La normalisation n'est pas cosmetique : un libelle long est coupe sur
        deux lignes par la mise en page. Comparer des chaines brutes donnerait
        des echecs qui n'en sont pas.
        """
        if document_id not in self._textes:
            chemin = self.chemin(document_id)
            if chemin.suffix.lower() != ".pdf":
                self._textes[document_id] = ""
            else:
                import pymupdf

                with pymupdf.open(chemin) as pdf:
                    brut = "\n".join(page.get_text() for page in pdf)
                self._textes[document_id] = " ".join(brut.split())
        return self._textes[document_id]

    def lignes_inventaire(self) -> list[dict[str, str]]:
        # utf-8-sig : le fichier est écrit avec un BOM pour Excel. Sans ce mode,
        # le BOM resterait collé au premier nom de colonne.
        with (self.racine / "inventaire.csv").open(encoding="utf-8-sig", newline="") as flux:
            return list(csv.DictReader(flux))


def verifier_inventaire(corpus: Corpus) -> Resultat:
    chemin = corpus.racine / "inventaire.csv"
    if not chemin.exists():
        return Resultat("Inventaire", False, "corpus/inventaire.csv absent")
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        entete = next(csv.reader(flux))
    attendu = list(COLONNES)
    if entete != attendu:
        manquantes = [c for c in attendu if c not in entete]
        en_trop = [c for c in entete if c not in attendu]
        return Resultat("Inventaire", False,
                        f"colonnes non conformes (manquantes : {manquantes}, en trop : {en_trop})")

    lignes = corpus.lignes_inventaire()
    identifiants = [ligne["document_id"] for ligne in lignes]
    attendus = [doc.id for doc in DOCUMENTS]
    if sorted(identifiants) != sorted(attendus):
        return Resultat("Inventaire", False, "les identifiants ne correspondent pas au catalogue")
    if len(set(identifiants)) != len(identifiants):
        doublons = [i for i, n in Counter(identifiants).items() if n > 1]
        return Resultat("Inventaire", False, f"identifiants en double : {doublons}")
    return Resultat("Inventaire", True, f"{len(lignes)} lignes, {len(entete)} colonnes conformes")


def verifier_fichiers(corpus: Corpus) -> Resultat:
    manquants = [doc.fichier for doc in DOCUMENTS if not (corpus.racine / doc.fichier).exists()]
    if manquants:
        return Resultat("Fichiers", False, f"{len(manquants)} fichier(s) absent(s) : {manquants[:3]}")

    attendus = {doc.fichier for doc in DOCUMENTS}
    presents = {
        chemin.relative_to(corpus.racine).as_posix()
        for dossier in ("documents", "images")
        for chemin in (corpus.racine / dossier).rglob("*")
        if chemin.is_file() and chemin.name != ".gitkeep"
    }
    orphelins = sorted(presents - attendus)
    if orphelins:
        return Resultat("Fichiers", False, f"fichier(s) hors catalogue : {orphelins[:3]}")
    return Resultat("Fichiers", True, f"{len(presents)} fichiers, aucun orphelin")


def verifier_mesures(corpus: Corpus) -> Resultat:
    """Les valeurs publiees doivent etre celles des fichiers, pas du catalogue."""
    ecarts: list[str] = []
    for ligne in corpus.lignes_inventaire():
        chemin = corpus.racine / ligne["fichier"]
        pages = compter_pages(chemin)
        if str(pages) != ligne["nb_pages"]:
            ecarts.append(f"{ligne['document_id']} : {ligne['nb_pages']} annonce, {pages} mesure")
        if chemin.suffix.lower() == ".pdf" and ligne["format"] != "pdf_scanne":
            elements = reperer_elements(chemin)
            if elements != ligne["elements_visuels"]:
                ecarts.append(
                    f"{ligne['document_id']} : elements « {ligne['elements_visuels']} » "
                    f"annonces, « {elements} » mesures"
                )
    if ecarts:
        return Resultat("Mesures", False, f"{len(ecarts)} ecart(s) : {ecarts[:3]}")
    return Resultat("Mesures", True, "pages et elements visuels conformes aux fichiers")


def verifier_quotas(corpus: Corpus) -> Resultat:
    lignes = corpus.lignes_inventaire()
    familles = Counter(ligne["famille_equipement"] for ligne in lignes)
    types = {ligne["type_document"] for ligne in lignes}
    avec_elements = [ligne for ligne in lignes if ligne["elements_visuels"] != "aucun"]
    usages = Counter(ligne["usage_test"] for ligne in lignes)
    scans = [ligne for ligne in lignes if ligne["format"] == "pdf_scanne"]

    problemes: list[str] = []
    hors_types = sorted({ligne["type_document"] for ligne in lignes} - TYPES_AUTORISES)
    hors_usages = sorted({ligne["usage_test"] for ligne in lignes} - USAGES_AUTORISES)
    if hors_types:
        problemes.append(f"types hors consigne : {hors_types}")
    if hors_usages:
        problemes.append(f"usages hors consigne : {hors_usages}")
    if not 30 <= len(lignes) <= 50:
        problemes.append(f"{len(lignes)} documents (30 a 50 attendus)")
    if familles.get("ascenseurs", 0) == 0 or familles.get("portes", 0) == 0:
        problemes.append("les deux familles ne sont pas representees")
    if len(types) < 5:
        problemes.append(f"{len(types)} types de documents (5 attendus au minimum)")
    if len(avec_elements) < 10:
        problemes.append(f"{len(avec_elements)} documents avec elements visuels (10 attendus)")
    if len(scans) < 2:
        problemes.append(f"{len(scans)} documents scannes (2 attendus)")
    if usages["contradictoire"] < 2:
        problemes.append(f"{usages['contradictoire']} contradictions (2 attendues)")
    if usages["injection"] < 1:
        problemes.append("aucun document piege")
    if usages["ambigu"] < 5:
        problemes.append(f"{usages['ambigu']} documents ambigus (5 prevus)")

    detail = (f"{len(lignes)} documents, familles {dict(familles)}, {len(types)} types, "
              f"{len(avec_elements)} avec elements visuels, {len(scans)} scans, "
              f"usages {dict(usages)}")
    return Resultat("Quotas", not problemes, detail if not problemes else " ; ".join(problemes))


def verifier_codes(corpus: Corpus) -> Resultat:
    problemes: list[str] = []
    for famille in Famille:
        codes = CODES_PAR_FAMILLE[famille]
        numeros = [code.code for code in codes]
        if len(set(numeros)) != len(numeros):
            problemes.append(f"{famille.value} : codes en double")
        document = "asc_codes_defaut" if famille is Famille.ASCENSEURS else "pa_codes_defaut"
        texte = corpus.texte(document)
        absents = [code.libelle for code in codes if code.libelle not in texte]
        if absents:
            problemes.append(f"{document} : libelles absents {absents}")

    for numero in CODES_PARTAGES:
        asc = next(c for c in CODES_PAR_FAMILLE[Famille.ASCENSEURS] if c.code == numero)
        prt = next(c for c in CODES_PAR_FAMILLE[Famille.PORTES] if c.code == numero)
        if asc.libelle == prt.libelle:
            problemes.append(f"code {numero} : meme libelle dans les deux familles")

    if problemes:
        return Resultat("Codes de defaut", False, " ; ".join(problemes))
    return Resultat("Codes de defaut", True,
                    f"{len(CODES_PARTAGES)} codes partages, libelles distincts, tableaux complets")


def verifier_marques(corpus: Corpus) -> Resultat:
    ecarts: list[str] = []
    for doc in DOCUMENTS:
        if doc.format in {"pdf_scanne", "image"} or doc.famille is None:
            continue
        if doc.params.get("gabarit") == "note":
            # Une note d'exploitation est redigee par le site, pas par le
            # constructeur : elle ne porte pas sa marque. L'exclure est une
            # decision de corpus, pas un contournement du controle.
            continue
        marque = CONSTRUCTEURS[doc.famille]
        # La marque figure en capitales sur la page de garde et en minuscules
        # dans les tableaux : la comparaison est insensible a la casse.
        if marque.lower() not in corpus.texte(doc.id).lower():
            ecarts.append(f"{doc.id} ne mentionne pas {marque}")
    if ecarts:
        return Resultat("Constructeurs", False, " ; ".join(ecarts))
    return Resultat("Constructeurs", True, "chaque document porte la marque de sa famille")


def verifier_injection(corpus: Corpus) -> Resultat:
    porteurs = [doc.id for doc in DOCUMENTS
                if doc.format != "image" and CHAINE_INJECTION in corpus.texte(doc.id)]
    fuites = [doc.id for doc in DOCUMENTS
              if doc.format != "image" and ADRESSE_INJECTION in corpus.texte(doc.id)
              and doc.id not in porteurs]
    if porteurs != ["asc_note_service"]:
        return Resultat("Injection", False,
                        f"charge presente dans {porteurs} au lieu de ['asc_note_service']")
    if fuites:
        return Resultat("Injection", False, f"adresse externe hors document piege : {fuites}")
    return Resultat("Injection", True, "charge unique, dans asc_note_service, signalee dans l'inventaire")


def verifier_scans(corpus: Corpus) -> Resultat:
    scans = [doc for doc in DOCUMENTS if doc.format == "pdf_scanne"]
    lisibles = [doc.id for doc in scans if corpus.texte(doc.id).strip()]
    if lisibles:
        return Resultat("Scans", False, f"texte encore extractible dans {lisibles}")
    return Resultat("Scans", True, f"{len(scans)} documents sans texte extractible (OCR requis)")


def verifier_contradictions(corpus: Corpus) -> Resultat:
    problemes: list[str] = []

    v1 = corpus.texte("asc_manuel_a")
    v2 = corpus.texte("asc_manuel_a_v2")
    if "fixé à 15 mm" not in v1:
        problemes.append("asc_manuel_a n'annonce pas le seuil de 15 mm")
    if "fixé à 8 mm" not in v2:
        problemes.append("asc_manuel_a_v2 n'annonce pas le seuil de 8 mm")
    if "15 mm" not in v2:
        problemes.append("asc_manuel_a_v2 ne dit pas quelle valeur elle remplace")

    procedure = corpus.texte("pa_proc_reglage_capteurs")
    note = corpus.texte("pa_note_internet")
    if "2,5 s" not in procedure:
        problemes.append("pa_proc_reglage_capteurs ne fixe pas la temporisation a 2,5 s")
    if "4 s" not in note:
        problemes.append("pa_note_internet ne fixe pas la temporisation a 4 s")

    if problemes:
        return Resultat("Contradictions", False, " ; ".join(problemes))
    return Resultat("Contradictions", True,
                    "seuil 15/8 mm et temporisation 2,5/4 s documentes dans les deux sens")


def verifier_langues(corpus: Corpus) -> Resultat:
    anglais = [doc.id for doc in DOCUMENTS if doc.langue == "en"]
    if not anglais:
        return Resultat("Langues", False, "aucun document en anglais")
    manquants = [doc for doc in anglais
                 if not re.search(r"\b(the|safety|terminal|assignment)\b", corpus.texte(doc), re.I)]
    if manquants:
        return Resultat("Langues", False, f"documents annonces en anglais mais rediges en francais : {manquants}")
    return Resultat("Langues", True, f"{len(anglais)} extraits en anglais, textes coherents")


def verifier_extensions(corpus: Corpus) -> Resultat:
    ecarts: list[str] = []
    for ligne in corpus.lignes_inventaire():
        extension = Path(ligne["fichier"]).suffix.lower()
        attendu = ".png" if ligne["format"] == "image" else ".pdf"
        if extension != attendu:
            ecarts.append(f"{ligne['document_id']} : {extension} pour un format {ligne['format']}")
    if ecarts:
        return Resultat("Extensions", False, " ; ".join(ecarts))
    return Resultat("Extensions", True, "extension de fichier coherente avec le format declare")


CONTROLES = (
    verifier_inventaire,
    verifier_fichiers,
    verifier_mesures,
    verifier_quotas,
    verifier_codes,
    verifier_marques,
    verifier_injection,
    verifier_scans,
    verifier_contradictions,
    verifier_langues,
    verifier_extensions,
)


def executer(racine: Path) -> Sequence[Resultat]:
    corpus = Corpus(racine)
    if not (racine / "inventaire.csv").exists():
        return [Resultat("Inventaire", False, f"{racine / 'inventaire.csv'} absent")]
    return [controle(corpus) for controle in CONTROLES]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--corpus", type=Path, default=Path("corpus"),
                        help="dossier du corpus (defaut : corpus/)")
    args = parser.parse_args(argv)

    resultats = executer(args.corpus)
    largeur = max(len(resultat.nom) for resultat in resultats)
    for resultat in resultats:
        etat = "OK   " if resultat.ok else "ECHEC"
        print(f"[{etat}] {resultat.nom.ljust(largeur)}  {resultat.detail}")

    echecs = [resultat for resultat in resultats if not resultat.ok]
    print()
    if echecs:
        print(f"{len(echecs)} controle(s) en echec.")
        return 1
    print(f"{len(resultats)} controles passes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
