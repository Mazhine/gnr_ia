"""Genere les diagrammes de l'architecture cible.

Les schemas sont dessines en vectoriel (reportlab) puis rasterises en PNG pour
etre inseres dans le rapport. Le rendu est deterministe : memes coordonnees,
memes fichiers. Aucun outil externe (Graphviz, Mermaid CLI) n'est requis, ce qui
evite une dependance reseau fragile sur cette machine.

    python -m scripts.gen_diagrammes
    python -m scripts.gen_diagrammes --out docs/diagrammes
"""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas

BLEU = colors.HexColor("#1f3b57")
BLEU_CLAIR = colors.HexColor("#dbe4ee")
GRIS = colors.HexColor("#5a5f63")
GRIS_FOND = colors.HexColor("#eef1f4")
VERT = colors.HexColor("#2f6b4f")
VERT_CLAIR = colors.HexColor("#dcebe2")
ROUGE = colors.HexColor("#8a2f2f")
ROUGE_CLAIR = colors.HexColor("#f3dede")
BLANC = colors.white

TAILLE_LIBELLE = 8
TAILLE_TITRE = 9.5


def _boite(c: pdfcanvas.Canvas, x: float, y: float, largeur: float, hauteur: float,
           titre: str, detail: str = "", fond: colors.Color = GRIS_FOND,
           bord: colors.Color = BLEU) -> None:
    """Boite arrondie avec un titre en gras et un detail optionnel."""
    c.setFillColor(fond)
    c.setStrokeColor(bord)
    c.setLineWidth(0.9)
    c.roundRect(x, y, largeur, hauteur, 3 * mm, stroke=1, fill=1)
    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", TAILLE_TITRE)
    c.drawCentredString(x + largeur / 2, y + hauteur - 6 * mm, titre)
    if detail:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", TAILLE_LIBELLE)
        lignes = detail.split("\n")
        base = y + hauteur - 10.5 * mm
        for indice, ligne in enumerate(lignes):
            c.drawCentredString(x + largeur / 2, base - indice * 4 * mm, ligne)


def _fleche(c: pdfcanvas.Canvas, x1: float, y1: float, x2: float, y2: float,
            label: str = "", couleur: colors.Color = GRIS) -> None:
    """Fleche droite avec pointe, et libelle centre au-dessus du segment."""
    c.setStrokeColor(couleur)
    c.setFillColor(couleur)
    c.setLineWidth(0.9)
    c.line(x1, y1, x2, y2)
    import math

    angle = math.atan2(y2 - y1, x2 - x1)
    taille = 2.6 * mm
    for delta in (0.45, -0.45):
        c.line(x2, y2,
               x2 - taille * math.cos(angle + delta),
               y2 - taille * math.sin(angle + delta))
    if label:
        c.setFont("Helvetica", 7)
        c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 1.6 * mm, label)


def _titre(c: pdfcanvas.Canvas, largeur: float, hauteur: float, texte: str) -> None:
    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(18 * mm, hauteur - 16 * mm, texte)
    c.setStrokeColor(BLEU_CLAIR)
    c.setLineWidth(1.2)
    c.line(18 * mm, hauteur - 18 * mm, largeur - 18 * mm, hauteur - 18 * mm)


def architecture(destination: Path) -> None:
    largeur, hauteur = landscape(A4)
    c = pdfcanvas.Canvas(str(destination), pagesize=(largeur, hauteur))
    _titre(c, largeur, hauteur, "Architecture cible — sept blocs et quatre points de contrôle")

    # Colonne de gauche : acquisition. Colonne centrale : traitement. Droite : outils.
    _boite(c, 18 * mm, 120 * mm, 52 * mm, 30 * mm, "Interface web",
           "question + photo\ntechnicien / responsable", BLEU_CLAIR)
    _boite(c, 18 * mm, 78 * mm, 52 * mm, 26 * mm, "API",
           "authentification\ncontrôle d'accès (1)", BLANC)
    _boite(c, 95 * mm, 96 * mm, 62 * mm, 40 * mm, "Orchestration",
           "planification\nassemblage du contexte\ngarde-fous", BLEU_CLAIR)
    _boite(c, 185 * mm, 138 * mm, 58 * mm, 26 * mm, "Recherche documentaire",
           "texte + images\nQdrant", BLANC)
    _boite(c, 185 * mm, 96 * mm, 58 * mm, 26 * mm, "Modèle vision-langage",
           "Qwen3-VL-4B\n4 bits, 8 Go", BLANC)
    _boite(c, 185 * mm, 54 * mm, 58 * mm, 26 * mm, "Serveur MCP",
           "historique, tickets\n(4) autorisation", BLANC)
    _boite(c, 95 * mm, 34 * mm, 62 * mm, 30 * mm, "Vérification des citations",
           "chaque affirmation\nest reliée à une source (2)", VERT_CLAIR, VERT)
    _boite(c, 18 * mm, 34 * mm, 52 * mm, 30 * mm, "Approbation humaine",
           "avant tout appel MCP\nde création (3)", VERT_CLAIR, VERT)

    # Acquisition : l'interface passe par l'API, qui authentifie avant tout.
    _fleche(c, 44 * mm, 120 * mm, 44 * mm, 104 * mm, "question + photo")
    _fleche(c, 70 * mm, 91 * mm, 95 * mm, 108 * mm, "requête authentifiée")
    # Orchestration -> outils
    _fleche(c, 157 * mm, 124 * mm, 185 * mm, 148 * mm, "recherche")
    _fleche(c, 157 * mm, 116 * mm, 185 * mm, 109 * mm, "photo / texte")
    _fleche(c, 157 * mm, 104 * mm, 185 * mm, 67 * mm, "appel outil")
    # Outils -> orchestration (retour)
    _fleche(c, 185 * mm, 132 * mm, 157 * mm, 118 * mm, "extraits")
    _fleche(c, 185 * mm, 96 * mm, 157 * mm, 100 * mm, "réponse")
    # Orchestration -> verification -> reponse
    _fleche(c, 126 * mm, 96 * mm, 126 * mm, 64 * mm, "réponse candidate")
    _fleche(c, 95 * mm, 49 * mm, 70 * mm, 49 * mm, "ticket proposé")
    _fleche(c, 44 * mm, 64 * mm, 44 * mm, 78 * mm, "approbation")

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 7.5)
    c.drawString(18 * mm, 18 * mm,
                 "Les chiffres (1) à (4) renvoient aux points de contrôle imposés : "
                 "accès avant recherche, citations vérifiées, approbation humaine, "
                 "autorisation côté serveur MCP.")
    c.showPage()
    c.save()


def ingestion(destination: Path) -> None:
    largeur, hauteur = A4
    c = pdfcanvas.Canvas(str(destination), pagesize=(largeur, hauteur))
    _titre(c, largeur, hauteur, "Flux d'ingestion d'un document")

    largeur_boite = 55 * mm
    hauteur_boite = 22 * mm
    colonnes = (12 * mm, 79 * mm, 146 * mm)
    ligne_1 = hauteur - 66 * mm
    ligne_2 = hauteur - 108 * mm

    # Etapes 1 a 3 sur la premiere ligne, de gauche a droite.
    etapes_ligne_1 = [
        ("PDF ou image", "40 documents sources", BLEU_CLAIR, BLEU),
        ("Extraction du texte", "pymupdf ; OCR si pdf_scanne", GRIS_FOND, BLEU),
        ("Découpage", "par page et par bloc", GRIS_FOND, BLEU),
    ]
    for indice, (titre, detail, fond, bord) in enumerate(etapes_ligne_1):
        x = colonnes[indice]
        _boite(c, x, ligne_1, largeur_boite, hauteur_boite, titre, detail, fond, bord)
        if indice < len(etapes_ligne_1) - 1:
            _fleche(c, x + largeur_boite, ligne_1 + hauteur_boite / 2,
                    x + largeur_boite + 12 * mm, ligne_1 + hauteur_boite / 2)

    # Etapes 4 et 5 : on repart de la droite vers la gauche (serpentin).
    _boite(c, colonnes[2], ligne_2, largeur_boite, hauteur_boite, "Embeddings",
           "vecteurs texte + image", GRIS_FOND, BLEU)
    _boite(c, colonnes[1], ligne_2, largeur_boite, hauteur_boite, "Indexation",
           "Qdrant : vecteur\n+ métadonnées", VERT_CLAIR, VERT)
    _fleche(c, colonnes[2] + largeur_boite / 2, ligne_1,
            colonnes[2] + largeur_boite / 2, ligne_2 + hauteur_boite)
    _fleche(c, colonnes[2], ligne_2 + hauteur_boite / 2,
            colonnes[1] + largeur_boite, ligne_2 + hauteur_boite / 2)

    y_metadonnees = ligne_2 - 22 * mm
    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(12 * mm, y_metadonnees, "Métadonnées conservées pour chaque bloc indexé")
    metadonnees = [
        "document_id et version du document",
        "numéro de page et identifiant du bloc",
        "famille d'équipement et equipement_id",
        "groupes d'accès autorisés",
        "type de contenu : texte, tableau, figure",
    ]
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 9)
    for indice, ligne in enumerate(metadonnees):
        c.drawString(16 * mm, y_metadonnees - 8 * mm - indice * 6 * mm, f"•  {ligne}")

    c.setFillColor(ROUGE)
    c.setFont("Helvetica", 8)
    c.drawString(12 * mm, y_metadonnees - 40 * mm,
                 "Le contrôle d'accès est appliqué à l'ingestion (métadonnées) et à la requête, "
                 "jamais après la recherche.")
    c.showPage()
    c.save()


def acces(destination: Path) -> None:
    largeur, hauteur = A4
    c = pdfcanvas.Canvas(str(destination), pagesize=(largeur, hauteur))
    _titre(c, largeur, hauteur, "Modèle d'accès — trois groupes, deux périmètres étanches")

    _boite(c, 24 * mm, hauteur - 70 * mm, 62 * mm, 22 * mm, "Technicien ascenseurs",
           "groupe techniciens_ascenseurs", BLEU_CLAIR)
    _boite(c, 24 * mm, hauteur - 104 * mm, 62 * mm, 22 * mm, "Technicien portes",
           "groupe techniciens_portes", BLEU_CLAIR)
    _boite(c, 24 * mm, hauteur - 138 * mm, 62 * mm, 22 * mm, "Responsable",
           "groupe responsables", GRIS_FOND)

    _boite(c, 130 * mm, hauteur - 70 * mm, 62 * mm, 22 * mm, "Documents ascenseurs",
           "20 documents", VERT_CLAIR, VERT)
    _boite(c, 130 * mm, hauteur - 104 * mm, 62 * mm, 22 * mm, "Documents portes",
           "20 documents", VERT_CLAIR, VERT)
    _boite(c, 130 * mm, hauteur - 138 * mm, 62 * mm, 22 * mm, "Documents transverses",
           "contrôle périodique, contrat", VERT_CLAIR, VERT)

    _fleche(c, 86 * mm, hauteur - 59 * mm, 130 * mm, hauteur - 59 * mm, "lecture")
    _fleche(c, 86 * mm, hauteur - 93 * mm, 130 * mm, hauteur - 93 * mm, "lecture")
    _fleche(c, 86 * mm, hauteur - 127 * mm, 130 * mm, hauteur - 127 * mm, "lecture")

    # Refus explicite : le technicien ascenseurs ne voit pas les documents portes.
    c.setStrokeColor(ROUGE)
    c.setDash(2, 2)
    c.line(86 * mm, hauteur - 62 * mm, 130 * mm, hauteur - 90 * mm)
    c.setDash()
    c.setFillColor(ROUGE)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(108 * mm, hauteur - 80 * mm, "refusé")

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 8)
    c.drawString(24 * mm, 34 * mm,
                 "Un technicien du groupe ascenseurs n'obtient aucun extrait d'un document du "
                 "groupe portes,")
    c.drawString(24 * mm, 29 * mm,
                 "même si la recherche le classe premier. Le filtre est appliqué dans la requête "
                 "Qdrant, pas sur le résultat affiché.")
    c.showPage()
    c.save()


def rasteriser(pdf: Path, png: Path) -> None:
    """Rasterise la page en la rognant sur son contenu.

    Les diagrammes sont dessines sur une page A4 dont la moitie basse reste
    blanche. Inseree telle quelle dans le rapport, l'image reserve cette place
    vide et coupe le texte. On calcule donc la boite englobante des traits et
    des textes, puis on ne rasterise que cette zone.
    """
    import pymupdf

    with pymupdf.open(pdf) as document:
        page = document[0]
        rectangles = [dessin["rect"] for dessin in page.get_drawings()]
        rectangles += [pymupdf.Rect(bloc[:4]) for bloc in page.get_text("blocks")]
        if rectangles:
            contenu = rectangles[0]
            for rectangle in rectangles[1:]:
                contenu |= rectangle
            marge = 6
            zone = pymupdf.Rect(contenu.x0 - marge, contenu.y0 - marge,
                                contenu.x1 + marge, contenu.y1 + marge)
        else:
            zone = page.rect
        page.get_pixmap(dpi=170, clip=zone).save(png)


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--out", type=Path, default=Path("docs/diagrammes"))
    arguments = parseur.parse_args()

    arguments.out.mkdir(parents=True, exist_ok=True)
    diagrams = {
        "architecture": architecture,
        "flux-ingestion": ingestion,
        "modele-acces": acces,
    }
    for nom, fonction in diagrams.items():
        pdf = arguments.out / f"{nom}.pdf"
        png = arguments.out / f"{nom}.png"
        fonction(pdf)
        rasteriser(pdf, png)
        print(f"  {pdf}")
        print(f"  {png}")
    print(f"{len(diagrams)} diagramme(s) dans {arguments.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
