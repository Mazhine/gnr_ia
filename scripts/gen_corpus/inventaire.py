"""Écriture de l'inventaire du corpus.

Règle de base : aucune valeur de l'inventaire n'est recopiée du catalogue. Le
nombre de pages et les éléments visuels sont mesurés sur le fichier produit
juste après son rendu. Si un document change de longueur, l'inventaire suit
sans intervention manuelle.

L'inventaire occupe les vingt colonnes imposées par le livrable 1. L'ordre et
les noms de colonnes ne doivent pas changer : ils sont vérifiés par
`verifier.py`, et le rapport les cite.
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path

from .catalogue import CONSTRUCTEURS, Document
from .render import reperer_elements

COLONNES: tuple[str, ...] = (
    "document_id",
    "fichier",
    "titre",
    "famille_equipement",
    "equipement_id",
    "type_document",
    "version",
    "nb_pages",
    "langue",
    "format",
    "elements_visuels",
    "provenance",
    "licence",
    "genere_par_ia",
    "outil_ia",
    "verifie_par",
    "corrections",
    "groupe_acces",
    "usage_test",
    "remarques",
)

# Corrections apportées à un document après relecture. Elles sont nominatives :
# un document corrigé doit pouvoir être distingué d'un document produit du
# premier coup. La justification détaillée est dans
# docs/livrable-1/journal-corrections.md.
CORRECTIONS: dict[str, str] = {
    "asc_manuel_en": "rédigé en anglais ; paragraphe orphelin supprimé (saut de page après le titre)",
    "pa_manuel_en": "rendu rédigé en anglais (la première version était en français)",
    "asc_manuel_mc": "caractéristiques du monte-charge corrigées (2 niveaux, 0,5 m/s)",
    "asc_manuel_a_v2": "la v2.0 indique désormais la valeur qu'elle remplace",
    "asc_histo_b_2025": "journal distinct de celui de ASC-A-01",
    "pa_histo_pg01": "journal adapté aux portes (pas de pêne de serrure)",
    "pa_fiche_secu_vent": "section vent fort ajoutée (seuils 60 et 90 km/h)",
    "asc_photo_boite_cabine": "voyants éteints corrigés (seuls défaut et service allumés)",
    "asc_photo_armoire": "légende des LED absente, document classé ambigu",
    "asc_photo_plaque": "flou renforcé : le numéro de série restait lisible",
    "pa_photo_plaque": "plaque réellement dégradée (elle était nette) et classée ambiguë",
    "asc_schema_armoire": "transformateur 48 V relié à la rangée du bas (sortie absente)",
    "pa_note_internet": "typée procedure (gabarit note) ; titre répété supprimé",
    "asc_proc_scannee": "usage_test ramené à normal : le scan est un format, pas un rôle",
    "pa_manuel_scanne": "usage_test ramené à normal : le scan est un format, pas un rôle",
    "pa_proc_scannee": "usage_test ramené à normal : le scan est un format, pas un rôle",
}

# Un document généré n'est pas relu par un humain du seul fait qu'il est écrit.
# Cette colonne reste donc explicite sur ce qui a été fait et ce qui ne l'a pas
# été. Elle est renseignée document par document après la relecture humaine.
VERIFICATION_AUTOMATIQUE = "contrôle automatique (verifier.py) ; relecture humaine à compléter"

LIBELLES_FORMAT: dict[str, str] = {
    "pdf_texte": "pdf texte",
    "pdf_scanne": "pdf scanné, image seule",
    "image": "image png",
}


def compter_pages(chemin: Path) -> int:
    """Nombre de pages réel. Une image compte pour une page."""
    if chemin.suffix.lower() != ".pdf":
        return 1
    import pymupdf

    with pymupdf.open(chemin) as pdf:
        return int(pdf.page_count)


def construire_ligne(doc: Document, racine: Path) -> dict[str, str]:
    chemin = racine / doc.fichier
    if not chemin.exists():
        raise FileNotFoundError(f"{doc.id} : fichier absent ({chemin})")

    elements = reperer_elements(chemin) if chemin.suffix.lower() == ".pdf" else "aucun"
    if elements == "aucun" and doc.format == "pdf_scanne":
        elements = "aucun (page numérisée, contenu non extractible)"

    marque = CONSTRUCTEURS[doc.famille] if doc.famille else "service maintenance"
    # `provenance` et `licence` commencent par le jeton imposé par la consigne
    # (« synthetique »), suivi d'une phrase lisible. Le jeton reste en ASCII :
    # c'est une valeur de vocabulaire contrôlé, pas de la prose.
    return {
        "document_id": doc.id,
        "fichier": doc.fichier,
        "titre": doc.titre,
        "famille_equipement": doc.famille.value if doc.famille else "transverse",
        "equipement_id": ";".join(doc.equipements),
        "type_document": doc.type_document,
        "version": doc.version,
        "nb_pages": str(compter_pages(chemin)),
        "langue": doc.langue,
        "format": doc.format,
        "elements_visuels": elements,
        "provenance": (
            f"synthetique ; corpus MaintiDoc généré par script, aucune source réelle "
            f"({marque} est un constructeur fictif)"
        ),
        "licence": "synthetique ; contenu fictif produit pour un projet pédagogique",
        "genere_par_ia": "oui",
        "outil_ia": "générateur Python dédié (P04) ; reportlab et Pillow, aucun modèle de langage",
        "verifie_par": VERIFICATION_AUTOMATIQUE,
        "corrections": CORRECTIONS.get(doc.id, "aucune"),
        "groupe_acces": doc.groupe_acces,
        "usage_test": doc.usage_test,
        "remarques": doc.remarques,
    }


def ecrire(racine: Path, documents: Sequence[Document]) -> list[dict[str, str]]:
    lignes = [construire_ligne(doc, racine) for doc in documents]
    chemin = racine / "inventaire.csv"
    # UTF-8 avec BOM : sans lui, Excel ouvre le fichier en cp1252 et affiche
    # « Ã© » à la place de « é ». Le BOM est la seule entorse au CSV strict, et
    # elle est sans effet pour pandas ou le module csv (lecture en utf-8-sig).
    with chemin.open("w", encoding="utf-8-sig", newline="") as flux:
        writer = csv.DictWriter(flux, fieldnames=COLONNES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(lignes)
    return lignes
