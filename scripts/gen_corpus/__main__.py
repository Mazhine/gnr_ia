"""Point d'entree du generateur de corpus.

    python -m scripts.gen_corpus                       # les 40 documents
    python -m scripts.gen_corpus --only asc_manuel_a   # un document
    python -m scripts.gen_corpus --clean               # repart de zero

Le rendu est deterministe : meme catalogue, memes fichiers. Il n'y a donc pas
de graine aleatoire a conserver, ce qui rend une regeneration verifiable.

Une generation partielle (`--only`) ne reecrit pas l'inventaire : il
annoncerait des fichiers absents.
"""

from __future__ import annotations

import argparse
import shutil
from collections.abc import Callable, Sequence
from pathlib import Path

from . import images as img
from . import inventaire
from .catalogue import DOCUMENTS, Document
from .render import construire, scanner

# Chaque photo et chaque schema a son rendu. Le registre est explicite plutot
# que deduit du nom de fichier : une faute de frappe doit echouer au rendu, pas
# produire silencieusement une image generique.
RENDUS_IMAGES: dict[str, Callable[[Path], None]] = {
    "asc_photo_boite_cabine": lambda p: img.panneau_cabine(p, "ASC-A-01"),
    "asc_photo_armoire": img.armoire_commande,
    "asc_photo_plaque": lambda p: img.plaque_signaletique(
        p, constructeur="Verticalis", reference="VRT-8-1000", serie="VRT-2019-04417",
        charge="1000 kg", annee="2019", lisible=False,
    ),
    "asc_schema_armoire": img.schema_armoire,
    "asc_schema_boucle_secu": lambda p: img.schema_boucle(p, "ascenseurs"),
    "pa_photo_boite_cmd": lambda p: img.panneau_porte(p, "PA-01", "SL-400"),
    "pa_photo_voyant": lambda p: img.panneau_porte(p, "PA-02", "SL-400", code="51"),
    "pa_photo_plaque": lambda p: img.plaque_signaletique(
        p, constructeur="Portalis", reference="CG-600", serie="PRT-2018-11203",
        charge="600 kg", annee="2018", lisible=False,
    ),
    "pa_schema_boucle": lambda p: img.schema_boucle(p, "portes"),
    "pa_schema_moteur": img.schema_moteur,
}


def preparer_dossiers(corpus: Path, propre: bool) -> Path:
    if propre:
        for dossier in ("documents", "images", ".cache"):
            cible = corpus / dossier
            if cible.exists():
                shutil.rmtree(cible)

    for dossier in ("documents/famille_1", "documents/famille_2", "images", ".cache"):
        (corpus / dossier).mkdir(parents=True, exist_ok=True)
    return corpus / ".cache"


def generer(corpus: Path, documents: Sequence[Document], propre: bool = False) -> None:
    cache = preparer_dossiers(corpus, propre)

    # Figures communes a plusieurs documents. Elles sont produites une fois,
    # puis inserees par `render._figure`.
    img.schema_boucle(cache / "schema_boucle_asc.png", "ascenseurs")
    img.schema_boucle(cache / "schema_boucle_porte.png", "portes")
    img.schema_moteur(cache / "schema_moteur.png")

    for doc in documents:
        destination = corpus / doc.fichier
        destination.parent.mkdir(parents=True, exist_ok=True)

        if doc.format == "image":
            rendu = RENDUS_IMAGES.get(doc.id)
            if rendu is None:
                raise KeyError(f"{doc.id} : aucun rendu d'image declare")
            rendu(destination)
        elif doc.format == "pdf_scanne":
            intermediaire = cache / f"{doc.id}.pdf"
            construire(doc, intermediaire, cache)
            scanner(intermediaire, destination)
        else:
            construire(doc, destination, cache)

        print(f"  {doc.fichier}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", type=Path, default=Path("corpus"),
                        help="dossier de sortie (defaut : corpus/)")
    parser.add_argument("--only", action="append", metavar="DOCUMENT_ID",
                        help="ne generer qu'un document (repetable)")
    parser.add_argument("--clean", action="store_true",
                        help="supprime documents/, images/ et .cache/ avant generation")
    args = parser.parse_args(argv)

    if args.only:
        connus = {doc.id for doc in DOCUMENTS}
        inconnus = sorted(set(args.only) - connus)
        if inconnus:
            parser.error(f"identifiant inconnu : {', '.join(inconnus)}")
        documents = tuple(doc for doc in DOCUMENTS if doc.id in set(args.only))
    else:
        documents = DOCUMENTS

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Generation de {len(documents)} document(s) dans {args.out}")
    generer(args.out, documents, propre=args.clean)

    if args.only:
        print("Generation partielle : inventaire.csv inchange.")
        return 0

    lignes = inventaire.ecrire(args.out, DOCUMENTS)
    total_pages = sum(int(ligne["nb_pages"]) for ligne in lignes)
    avec_elements = sum(1 for ligne in lignes if ligne["elements_visuels"] != "aucun")
    print()
    print(f"{len(lignes)} documents, {total_pages} pages, "
          f"{avec_elements} documents avec elements visuels reperes.")
    print(f"Inventaire ecrit : {args.out / 'inventaire.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
