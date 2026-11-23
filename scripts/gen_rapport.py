"""Genere le rapport du livrable 1 au format PDF.

Le texte est ecrit ici, en francais, et non importe du corpus : le rapport
raconte des decisions, il ne recopie pas des documents. Les chiffres du corpus
sont en revanche lus dans `corpus/inventaire.csv` au moment du rendu, pour que
le rapport ne puisse pas annoncer 28 elements visuels si l'inventaire en compte
un autre.

    python -m scripts.gen_rapport
    python -m scripts.gen_rapport --out docs/livrable-1
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

BLEU = colors.HexColor("#1f3b57")
GRIS = colors.HexColor("#5a5f63")
GRIS_CLAIR = colors.HexColor("#e8eaec")
FILET = colors.HexColor("#b9bdc1")

MARGE = 22 * mm
NOM_EQUIPE = "CHATER"

_styles = getSampleStyleSheet()
TITRE_COUVERTURE = ParagraphStyle("couverture_titre", parent=_styles["Title"],
                                  fontName="Helvetica-Bold", fontSize=26, leading=32,
                                  textColor=BLEU, alignment=TA_CENTER)
SOUS_TITRE = ParagraphStyle("sous_titre", parent=_styles["Normal"], fontName="Helvetica",
                            fontSize=13, leading=18, textColor=GRIS, alignment=TA_CENTER)
H1 = ParagraphStyle("h1", parent=_styles["Heading1"], fontName="Helvetica-Bold",
                    fontSize=16, leading=20, textColor=BLEU, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=_styles["Heading2"], fontName="Helvetica-Bold",
                    fontSize=11.5, leading=15, textColor=BLEU, spaceBefore=10, spaceAfter=4)
CORPS = ParagraphStyle("corps", parent=_styles["BodyText"], fontName="Helvetica",
                       fontSize=10, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=7)
ITEM = ParagraphStyle("item", parent=CORPS, leftIndent=5 * mm, bulletIndent=1 * mm,
                      spaceAfter=3)
# Les paragraphes qui contiennent un chemin ou un identifiant long sont alignes a
# gauche : une justification distribuerait des blancs enormes autour du jeton
# insecable.
CORPS_GAUCHE = ParagraphStyle("corps_gauche", parent=CORPS, alignment=0)
PETIT = ParagraphStyle("petit", parent=CORPS, fontSize=8, leading=10.5, textColor=GRIS)
LEGENDE = ParagraphStyle("legende", parent=PETIT, alignment=TA_CENTER, spaceBefore=3,
                         spaceAfter=10)
CELLULE = ParagraphStyle("cellule", parent=CORPS, fontSize=8, leading=10.2,
                         alignment=TA_CENTER, spaceAfter=0)
CELLULE_GAUCHE = ParagraphStyle("cellule_gauche", parent=CELLULE, alignment=0)
CELLULE_ENTETE = ParagraphStyle("cellule_entete", parent=CELLULE, fontName="Helvetica-Bold",
                                textColor=colors.white)


class _Canevas:
    """Ajoute le numero de page en pied de page, sauf sur la couverture."""

    def __init__(self, titre: str) -> None:
        self.titre = titre

    def __call__(self, canvas, doc) -> None:  # type: ignore[no-untyped-def]
        if doc.page == 1:
            return
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(MARGE, 12 * mm, "MaintiDoc — Livrable 1")
        canvas.drawRightString(A4[0] - MARGE, 12 * mm, f"Page {doc.page}")
        canvas.setStrokeColor(GRIS_CLAIR)
        canvas.line(MARGE, 15 * mm, A4[0] - MARGE, 15 * mm)
        canvas.restoreState()


def tableau(donnees: list[list[str]], largeurs: list[float],
            gauche: set[int] | None = None) -> Table:
    gauche = gauche or {0}
    lignes = []
    for indice, ligne in enumerate(donnees):
        style = CELLULE_ENTETE if indice == 0 else CELLULE
        style_gauche = CELLULE_ENTETE if indice == 0 else CELLULE_GAUCHE
        lignes.append([Paragraph(str(cellule), style_gauche if colonne in gauche else style)
                       for colonne, cellule in enumerate(ligne)])
    table = Table(lignes, colWidths=largeurs, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLEU),
        ("GRID", (0, 0), (-1, -1), 0.4, FILET),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f5f6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def lire_inventaire(racine: Path) -> list[dict[str, str]]:
    with (racine / "inventaire.csv").open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux))


def image(chemin: Path, largeur_mm: float, legende: str) -> list[object]:
    with PILImage.open(chemin) as source:
        ratio = source.height / source.width
    largeur = largeur_mm * mm
    return [Image(str(chemin), width=largeur, height=largeur * ratio),
            Paragraph(legende, LEGENDE)]


# --------------------------------------------------------------------------
# Contenu
# --------------------------------------------------------------------------

def couverture() -> list[object]:
    return [
        Spacer(1, 45 * mm),
        Paragraph("MaintiDoc", TITRE_COUVERTURE),
        Spacer(1, 4 * mm),
        Paragraph("Assistant documentaire multimodal et agentique<br/>pour la maintenance",
                  SOUS_TITRE),
        Spacer(1, 22 * mm),
        Paragraph("Livrable 1 — Cadrage, corpus et architecture", ParagraphStyle(
            "couverture_partie", parent=SOUS_TITRE, fontName="Helvetica-Bold",
            fontSize=15, textColor=BLEU)),
        Spacer(1, 40 * mm),
        Table([
            [Paragraph("Auteur", PETIT), Paragraph("Mazine CHATER", CORPS)],
            [Paragraph("Équipe", PETIT), Paragraph("CHATER (travail individuel)", CORPS)],
            [Paragraph("Module", PETIT), Paragraph("IA générative multimodale — EMSI 2026", CORPS)],
            [Paragraph("Version", PETIT), Paragraph("1.0 — 5 novembre 2026", CORPS)],
        ], colWidths=[35 * mm, 100 * mm], hAlign="LEFT", style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, GRIS_CLAIR),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])),
        PageBreak(),
    ]


def sommaire() -> list[object]:
    entrees = [
        ("2.1", "Cadrage du projet"),
        ("2.2", "Corpus documentaire"),
        ("2.3", "Architecture cible"),
        ("2.4", "Flux et modèle d'accès"),
        ("2.5", "Analyse des risques"),
        ("2.6", "Planning et rôles"),
        ("A", "Annexe A — Composition mesurée du corpus"),
        ("B", "Annexe B — Index des prompts"),
        ("C", "Annexe C — Arborescence du dépôt"),
    ]
    lignes = [[numero, intitule] for numero, intitule in entrees]
    return [
        Paragraph("Sommaire", H1),
        Spacer(1, 4 * mm),
        tableau([["", "Partie"], *lignes],
                [18 * mm, 140 * mm], gauche={1}),
        Spacer(1, 10 * mm),
        Paragraph(
            "Le rapport suit les six parties imposées par les consignes. Les annexes "
            "sont hors décompte de pages : elles donnent les éléments vérifiables "
            "(composition du corpus, index des prompts, arborescence du dépôt).", CORPS),
        PageBreak(),
    ]


def cadrage() -> list[object]:
    return [
        Paragraph("2.1 Cadrage du projet", H1),
        Paragraph("Contexte", H2),
        Paragraph(
            "MaintiDoc est un assistant documentaire destiné au service maintenance d'un "
            "centre technique de bâtiment. Il répond à des questions posées en langage "
            "naturel, à partir d'une photo ou d'un texte, en s'appuyant exclusivement sur "
            "un corpus documentaire interne : manuels constructeur, procédures, fiches de "
            "sécurité, schémas, tableaux de codes d'alarme et historiques d'intervention. "
            "L'objectif n'est pas de remplacer le technicien, mais de lui éviter de feuilleter "
            "cent pages pour retrouver la page qui répond à sa question.", CORPS),
        Paragraph(
            "Le projet est conduit en travail individuel. Cette contrainte est assumée et "
            "déclarée : elle explique les choix de sobriété technique (modèle 4 bits, "
            "infrastructure conteneurisée minimale) et le périmètre volontairement resserré "
            "sur deux familles d'équipements.", CORPS),
        Paragraph("Utilisateurs", H2),
        Paragraph(
            "Deux profils sont décrits par ce qu'ils font, pas par des adjectifs. Le "
            "<b>technicien d'intervention</b> est sur le terrain, souvent devant l'équipement, "
            "avec un téléphone et une question courte ; il n'a pas le temps de lire un manuel "
            "de sept pages et encore moins de chercher la bonne version. Le <b>responsable de "
            "maintenance</b> arbitre, ouvre les tickets et a besoin de la trace documentaire "
            "qui justifie une décision. Ces deux profils n'ont pas les mêmes droits : le "
            "premier lit les documents de sa famille, le second accède aux documents "
            "transverses et aux contrats.", CORPS),
        Paragraph("Cas d'usage", H2),
        tableau([
            ["#", "Cas d'usage", "Ce qui le rend vérifiable"],
            ["U1", "Identifier un voyant orange à partir d'une photo du panneau",
             "La réponse cite la page et la figure du manuel de la bonne famille"],
            ["U2", "Retrouver la procédure de remise en service après un défaut thermique",
             "La procédure citée correspond à l'équipement, pas à l'équipement voisin"],
            ["U3", "Consulter l'historique d'un équipement avant d'intervenir",
             "L'appel MCP renvoie l'historique du bon equipement_id"],
            ["U4", "Préparer un ticket puis le créer après approbation",
             "Aucune création sans jeton d'approbation valide"],
            ["U5", "Photo illisible ou équipement non identifiable",
             "Le système demande une précision au lieu d'inventer une référence"],
        ], [10 * mm, 72 * mm, 76 * mm], gauche={1, 2}),
        Paragraph("Objectifs vérifiables", H2),
        Paragraph(
            "Les objectifs sont formulés de manière testable, sans pourcentage prématuré : "
            "ils seront mesurés en semaine 5, pas annoncés en semaine 1.", CORPS),
    ] + [
        Paragraph(f"• {texte}", ITEM) for texte in [
            "citer la page et l'élément exacts pour toute affirmation documentaire ;",
            "refuser l'accès à un document d'un autre groupe, y compris par URL directe ;",
            "ne créer aucun ticket sans approbation explicite liée au contenu approuvé ;",
            "demander une clarification plutôt que répondre quand la source manque ;",
            "distinguer deux codes d'alarme de même numéro appartenant à deux constructeurs.",
        ]
    ] + [
        Paragraph("Périmètre et hors-périmètre", H2),
        tableau([
            ["Dans le périmètre", "Hors périmètre"],
            ["Recherche documentaire texte et image sur le corpus interne",
             "Récupération de documents sur Internet"],
            ["Réponse sourcée avec page et élément cités", "Pilotage direct d'un équipement"],
            ["Consultation d'historiques et préparation de tickets via MCP",
             "Création de ticket sans approbation humaine"],
            ["Deux familles : ascenseurs, portes et portails", "Autres familles d'équipements"],
        ], [85 * mm, 73 * mm], gauche={0, 1}),
        Paragraph("Hypothèses et contraintes", H2),
        Paragraph(
            "La machine de développement est un portable équipé d'une RTX 5060 Laptop de "
            "8 Go de mémoire vidéo. Un modèle 7B en 4 bits n'y tient pas avec le contexte "
            "nécessaire ; le choix d'un modèle vision-langage 4B quantifié est donc un fait "
            "mesuré, pas une préférence. L'infrastructure lourde (Qdrant, PostgreSQL, MLflow) "
            "est conteneurisée ; l'inférence reste native sous Windows pour accéder directement "
            "au GPU. Ces choix sont consignés dans les ADR du dépôt (0001 à 0006).", CORPS),
        PageBreak(),
    ]


def corpus(documents: list[dict[str, str]]) -> list[object]:
    familles = Counter(doc["famille_equipement"] for doc in documents)
    usages = Counter(doc["usage_test"] for doc in documents)
    types = Counter(doc["type_document"] for doc in documents)
    pages = sum(int(doc["nb_pages"]) for doc in documents)
    visuels = sum(1 for doc in documents if doc["elements_visuels"] != "aucun")
    scans = sum(1 for doc in documents if doc["format"] == "pdf_scanne")

    return [
        Paragraph("2.2 Corpus documentaire", H1),
        Paragraph("Méthode", H2),
        Paragraph(
            "Le corpus est <b>généré par un script déterministe</b> et non collecté sur le "
            "web. Ce choix a trois conséquences, toutes voulues. La licence est claire : "
            "aucun document réel n'est redistribué, les deux constructeurs (Verticalis pour "
            "les ascenseurs, Portalis pour les portes) sont fictifs. La cohérence est "
            "garantie : un identifiant d'équipement, un code d'alarme ou un seuil vient d'une "
            "source unique, le catalogue Python, et ne peut pas diverger d'un document à "
            "l'autre. Enfin, le corpus est reproductible : deux générations produisent des "
            "fichiers identiques, sans graine aléatoire à conserver.", CORPS),
        Paragraph(
            "Les prompts qui ont piloté l'écriture du générateur sont tracés dans "
            "<font face='Courier'>corpus/prompts_corpus.md</font> (P01 à P12). Il faut être "
            "précis sur ce point : aucun modèle de langage n'a rédigé le texte des documents. "
            "Un assistant de code a servi à écrire et corriger le générateur ; la colonne "
            "<font face='Courier'>outil_ia</font> de l'inventaire renvoie donc au générateur "
            "(P04) pour toutes les lignes. C'est moins spectaculaire qu'un corpus « généré par "
            "ChatGPT », mais c'est vérifiable, et cela évite les incohérences qu'un modèle "
            "introduit dès qu'il produit quarante documents séparés.", CORPS),
        Paragraph("Composition mesurée", H2),
        Paragraph(
            f"L'inventaire compte <b>{len(documents)} documents</b> pour <b>{pages} pages</b>. "
            f"Les deux familles sont équilibrées ({familles['ascenseurs']} ascenseurs, "
            f"{familles['portes']} portes). {visuels} documents portent un élément visuel "
            f"repéré automatiquement, {scans} sont des PDF scannés sans texte extractible, "
            "et les sept types de documents autorisés sont représentés. Ces chiffres sont "
            "lus dans <font face='Courier'>corpus/inventaire.csv</font> au moment du rendu du "
            "rapport : ils ne peuvent pas être plus flatteurs que le corpus réel.", CORPS),
        tableau([
            ["Exigence", "Cible", "Réalisé"],
            ["Documents", "30 à 50", str(len(documents))],
            ["Familles", "2", f"2 ({familles['ascenseurs']} + {familles['portes']})"],
            ["Types distincts", "variés", f"{len(types)} sur 7"],
            ["Éléments visuels", "au moins 10", str(visuels)],
            ["Scannés (OCR)", "au moins 2", str(scans)],
            ["Contradictoires", "au moins 2", str(usages["contradictoire"])],
            ["Piégé (injection)", "au moins 1", str(usages["injection"])],
            ["Ambigus", "non exigé", str(usages["ambigu"])],
            ["Anglais signalés", "tolérés", "2"],
        ], [55 * mm, 45 * mm, 58 * mm], gauche={0}),
        KeepTogether([
            Paragraph("Le dispositif d'ambiguïté", H2),
            Paragraph(
                "Le corpus ne se contente pas d'être volumineux : il est construit pour mettre "
                "l'assistant en difficulté de façon contrôlée. Cinq numéros de code d'alarme sont "
                "volontairement partagés entre les deux constructeurs avec des sens différents. "
                "Un technicien qui lit « défaut 51 » sans regarder la marque se trompe "
                "d'équipement ; l'assistant doit, lui, distinguer les deux tables.", CORPS),
            tableau([
                ["Code", "Verticalis (ascenseur)", "Portalis (porte)"],
                ["12", "Défaut de communication cabine", "Défaut capteur de sécurité"],
                ["33", "Défaut de nivellement", "Fin de course ouverture"],
                ["42", "Thermique moteur de traction", "Thermique moteur de porte"],
                ["51", "Défaut de porte (verrouillage)", "Défaut de fin de course"],
                ["71", "Survitesse", "Défaut de boucle de détection"],
            ], [16 * mm, 74 * mm, 68 * mm], gauche={1, 2}),
        ]),
        Paragraph("Les deux contradictions", H2),
        Paragraph(
            "Deux contradictions sont franches et vérifiables, pas des nuances de "
            "formulation. La première oppose deux versions du manuel ASC-A-01 : la v1.2 fixe "
            "le seuil du défaut de nivellement à 15 mm, la v2.0 à 8 mm, et le dit "
            "explicitement. La seconde oppose la procédure de réglage des capteurs (2,5 s de "
            "temporisation de fermeture) à une note d'exploitation plus récente (4 s). Dans "
            "les deux cas, le document le plus récent n'est pas le plus sûr : l'assistant doit "
            "signaler le désaccord, pas trancher à la place de l'humain.", CORPS),
        Paragraph("Le document piégé", H2),
        Paragraph(
            "Un document de service (<font face='Courier'>asc_note_service</font>) contient, "
            "en page 2, une instruction demandant d'ignorer les consignes précédentes et de "
            "transmettre l'historique complet des équipements à une adresse externe. Il est "
            "marqué <font face='Courier'>injection</font> dans l'inventaire. Le système devra "
            "le traiter comme une donnée à citer, jamais comme une consigne à exécuter. Le "
            "test correspondant est prévu en semaine 5.", CORPS),
        Paragraph("Analyse critique : ce qui a été corrigé", H2),
        Paragraph(
            "Un corpus généré n'est pas fiable du seul fait qu'il est écrit. La relecture des "
            "fichiers produits a révélé des défauts que le code ne montrait pas ; plusieurs "
            "rendaient un document faux au regard de ce que l'inventaire annonçait. Ils sont "
            "consignés dans <font face='Courier'>docs/livrable-1/journal-corrections.md</font> "
            "et repris dans la colonne <font face='Courier'>corrections</font> de l'inventaire. "
            "Les plus significatifs :", CORPS_GAUCHE),
    ] + [
        Paragraph(f"• {texte}", ITEM) for texte in [
            "les deux plaques signalétiques déclarées illisibles restaient lisibles ; un flou "
            "gaussien conserve la forme des lettres, une réduction de résolution non ;",
            "les trois PDF scannés n'avaient plus de texte extractible mais ressemblaient "
            "visuellement à des PDF vectoriels ; ils ont reçu grain, travers de feuille et gris "
            "de papier ;",
            "un transformateur 48 V du schéma d'armoire n'avait aucune sortie, donc ne servait "
            "à rien sur le dessin ;",
            "les deux schémas de boucle affirmaient que tous les contacts sont en série tout en "
            "laissant une liaison non tracée : le dessin contredisait sa légende ;",
            "trois documents portaient un rôle de test inventé (<font face='Courier'>scanne</font>) "
            "et un document un type inexistant (<font face='Courier'>note</font>) ;",
            "un extrait anglais laissait un paragraphe orphelin sur une page presque vide ;",
            "la note d'exploitation répétait son titre, et les procédures faisaient toutes "
            "exactement trois pages avec le même contenu générique.",
        ]
    ] + [
        PageBreak(),
    ]


def architecture() -> list[object]:
    return [
        Paragraph("2.3 Architecture cible", H1),
        Paragraph(
            "L'architecture est organisée autour d'un orchestrateur qui ne fait jamais "
            "confiance à un seul bloc : la recherche fournit des extraits, le modèle "
            "vision-langage les met en forme, et une étape séparée vérifie que chaque "
            "affirmation est bien reliée à une source. Les quatre points de contrôle imposés "
            "sont placés sur le schéma, pas seulement décrits dans le texte.", CORPS),
    ] + image(Path("docs/diagrammes/architecture.png"), 160,
              "Figure 1 — Architecture cible : sept blocs, quatre points de contrôle.") + [
        Paragraph("Les quatre points de contrôle", H2),
    ] + [
        Paragraph(f"<b>({numero})</b> {texte}", ITEM) for numero, texte in [
            ("1", "contrôle d'accès avant la recherche, jamais après : un extrait interdit ne "
                  "doit même pas être récupéré ;"),
            ("2", "vérification que chaque citation existe et soutient l'affirmation ; une "
                  "citation qui ne dit pas ce qu'on lui fait dire est rejetée ;"),
            ("3", "interruption pour approbation humaine avant tout appel MCP de création ;"),
            ("4", "contrôle des autorisations côté serveur MCP, à chaque appel, et non côté "
                  "client."),
        ]
    ] + [
        KeepTogether([
            Paragraph("Les sept blocs", H2),
            tableau([
                ["Bloc", "Rôle", "Entrées → sorties", "Outil envisagé"],
                ["Interface web", "Poser une question, joindre une photo",
                 "question, image → requête", "Application web légère"],
                ["API", "Authentifier et contrôler l'accès avant tout traitement",
                 "requête → requête autorisée", "Service HTTP, jetons"],
                ["Orchestration", "Planifier les étapes et assembler le contexte",
                 "requête → plan d'appels", "Code applicatif"],
                ["Recherche documentaire", "Retrouver les extraits texte et image pertinents",
                 "requête → extraits + scores", "Qdrant"],
                ["Modèle vision-langage", "Décrire une photo, rédiger la réponse",
                 "extraits, image → réponse", "Qwen3-VL-4B, 4 bits"],
                ["Serveur MCP", "Lire les historiques, préparer un ticket",
                 "appel outil → données", "Serveur MCP"],
                ["Vérification des citations", "Relier chaque affirmation à une source",
                 "réponse → réponse vérifiée", "Code + règles"],
            ], [30 * mm, 45 * mm, 48 * mm, 38 * mm], gauche={0, 1, 2, 3}),
        ]),
    ] + [
        Paragraph("Parcours d'une requête", H2),
    ] + [
        Paragraph(f"<b>{numero}.</b> {texte}", ITEM) for numero, texte in [
            ("1", "authentification : les groupes autorisés sont calculés avant toute recherche ;"),
            ("2", "planification : la question, et la photo si elle existe, sont transformées en "
                  "requête de recherche ;"),
            ("3", "récupération : seuls les extraits des documents autorisés remontent de Qdrant ;"),
            ("4", "analyse de la photo par le modèle vision-langage, s'il y a une photo ;"),
            ("5", "assemblage : chaque affirmation de la réponse est rattachée à une page et à un "
                  "élément ;"),
            ("6", "vérification des citations, puis affichage ; si un extrait manque ou si deux "
                  "sources se contredisent, la réponse devient une demande de clarification."),
        ]
    ] + [
        Paragraph(
            "La demande de clarification est un résultat acceptable, pas un échec : elle coûte "
            "une question au technicien, alors qu'une réponse inventée coûte une intervention "
            "sur le mauvais organe.", CORPS),
        Paragraph("Questions ouvertes", H2),
    ] + [
        Paragraph(f"• {texte}", ITEM) for texte in [
            "le modèle 4B suffira-t-il à lire une plaque signalétique photographiée, ou "
            "faudra-t-il un OCR spécialisé en amont ?",
            "faut-il appliquer l'OCR à tous les documents ou seulement aux PDF scannés, au "
            "risque de dégrader les PDF texte déjà propres ?",
            "quel seuil de score de récupération doit déclencher une demande de clarification "
            "plutôt qu'une réponse ?",
        ]
    ] + [PageBreak()]


def flux() -> list[object]:
    return [
        Paragraph("2.4 Flux et modèle d'accès", H1),
        Paragraph("Flux d'ingestion", H2),
        Paragraph(
            "L'ingestion transforme un document en blocs indexables. Le texte est extrait "
            "avec pymupdf ; les PDF scannés passent par un OCR, ce qui les distingue des "
            "autres. Chaque bloc conserve ses métadonnées, dont les groupes d'accès : le "
            "filtre de sécurité s'applique à l'indexation et à la requête, pas à "
            "l'affichage.", CORPS),
        *image(Path("docs/diagrammes/flux-ingestion.png"), 130,
               "Figure 2 — Ingestion d'un document, de l'extraction à l'index Qdrant."),
        Paragraph("Flux de requête et flux de ticket", H2),
        Paragraph(
            "Le flux de requête reprend les six étapes de la section 2.3. Le flux de ticket "
            "est volontairement séparé : l'assistant prépare un brouillon, le présente, attend "
            "une approbation explicite, puis appelle le serveur MCP avec un jeton lié au "
            "contenu approuvé. Un appel rejoué avec le même jeton ne crée pas de doublon "
            "(idempotence).", CORPS),
        Paragraph(
            "Chaque bloc indexé porte un identifiant de document et de version, un numéro de "
            "page, un identifiant de bloc, la famille et l'équipement, les groupes autorisés "
            "et le type de contenu. Ces métadonnées sont ce qui permet de citer une page "
            "précise et de filtrer avant la recherche.", CORPS),
        Paragraph("Modèle d'accès", H2),
        *image(Path("docs/diagrammes/modele-acces.png"), 130,
               "Figure 3 — Trois groupes, deux périmètres étanches. Le filtre est appliqué "
               "dans la requête, pas sur le résultat."),
        Paragraph(
            "Deux groupes techniques (<font face='Courier'>techniciens_ascenseurs</font> et "
            "<font face='Courier'>techniciens_portes</font>) et un groupe transverse "
            "(<font face='Courier'>responsables</font>) se partagent les quarante documents. "
            "Le point à démontrer est simple : un technicien ascenseurs ne doit obtenir aucun "
            "extrait d'un manuel de porte, même si la recherche le classe premier. Le filtre "
            "est donc une condition de la requête Qdrant, pas un tri après coup.", CORPS),
        PageBreak(),
    ]


def risques() -> list[object]:
    lignes = [
        ["Risque", "Catégorie", "P", "I", "Mesure prévue", "Resp."],
        ["Hallucination et citation non fondée", "Qualité", "2", "3",
         "Vérification des citations avant affichage ; refus de répondre sans source", "CHATER"],
        ["Fuite entre groupes", "Sécurité", "2", "3",
         "Filtre d'accès dans la requête ; test par URL directe", "CHATER"],
        ["Ticket créé sans approbation", "Sécurité", "1", "3",
         "Jeton d'approbation lié au contenu ; idempotence", "CHATER"],
        ["Erreurs introduites par l'IA dans le corpus", "Qualité", "3", "2",
         "Vérificateur automatique + journal des corrections", "CHATER"],
        ["Licence des documents", "Juridique", "1", "2",
         "Corpus synthétique, constructeurs fictifs, licence explicite", "CHATER"],
        ["Ressources matérielles insuffisantes", "Technique", "2", "3",
         "Modèle 4B quantifié ; repli sur un 3B si nécessaire", "CHATER"],
        ["Injection de prompt via un document", "Sécurité", "2", "2",
         "Traitement des documents comme données ; test dédié en semaine 5", "CHATER"],
        ["DNS instable pendant les téléchargements", "Technique", "3", "2",
         "Modèles mis en cache localement ; reprise manuelle", "CHATER"],
        ["Dérive de périmètre sur l'interface", "Gestion", "2", "2",
         "Périmètre figé dans le cahier des charges ; revue en fin de phase", "CHATER"],
        ["Perte de reproductibilité du corpus", "Gestion", "1", "3",
         "Générateur déterministe versionné ; inventaire mesuré", "CHATER"],
    ]
    return [
        Paragraph("2.5 Analyse des risques", H1),
        Paragraph(
            "Les risques sont notés sur une échelle de 1 à 3 en probabilité (P) et en impact "
            "(I). Les sept risques imposés par le sujet sont couverts, auxquels s'ajoutent "
            "trois risques propres à cette machine et à ce mode de travail. Les mesures sont "
            "techniques quand elles peuvent l'être ; les autres sont des règles de "
            "conduite.", CORPS),
        tableau(lignes, [42 * mm, 20 * mm, 7 * mm, 7 * mm, 64 * mm, 19 * mm],
                gauche={0, 1, 4, 5}),
        Paragraph(
            "Le risque le plus élevé n'est pas l'hallucination spectaculaire, mais l'erreur "
            "silencieuse dans le corpus : un code d'alarme mal libellé se propage à tous les "
            "documents qui le citent. C'est pourquoi le corpus est généré depuis un catalogue "
            "unique et vérifié fichier par fichier, plutôt qu'assemblé à la main.", CORPS),
        PageBreak(),
    ]


def planning() -> list[object]:
    return [
        Paragraph("2.6 Planning et rôles", H1),
        Paragraph(
            "Le projet est mené en travail individuel : la colonne « responsable » porte un "
            "seul nom, et c'est assumé plutôt que simulé. Le planning couvre les semaines 2 "
            "à 6, aligné sur les phases réelles du projet et non sur un découpage "
            "théorique.", CORPS),
        tableau([
            ["Semaine", "Phase", "Livrable attendu", "Ressources"],
            ["S2", "Ingestion du corpus", "Index Qdrant, OCR des scannés", "GPU local, Qdrant"],
            ["S3", "Recherche documentaire", "Recherche texte + image, filtres d'accès", "Qdrant, embeddings"],
            ["S4", "Génération sourcée", "Réponses avec citations vérifiées", "Qwen3-VL-4B"],
            ["S5", "Agent et MCP", "Historiques, tickets, approbation", "Serveur MCP, PostgreSQL"],
            ["S6", "Évaluation et dépôt", "Jeu de tests, mesures, démonstration", "MLflow, matériel local"],
        ], [18 * mm, 40 * mm, 65 * mm, 40 * mm], gauche={0, 1, 2, 3}),
        Spacer(1, 4 * mm),
        Paragraph(
            "Les ressources consommées sont annoncées à chaque phase : temps de calcul GPU "
            "pour l'inférence, espace disque pour l'index, et temps de relecture humaine pour "
            "le corpus. Ce dernier n'est pas nul : la vérification automatique contrôle la "
            "structure, pas la crédibilité d'une phrase.", CORPS),
        Paragraph("Composition de l'équipe", H2),
        Paragraph(
            "<b>Mazine CHATER</b> — conception, génération du corpus, développement, "
            "évaluation et rédaction. Le travail est individuel ; aucune autre personne "
            "n'est déclarée.", CORPS),
        Paragraph("Répartition des tâches", H2),
        Paragraph(
            "Le découpage suit les phases du projet, pas les six parties du rapport. La "
            "colonne « quand » indique la semaine où la tâche est réellement exécutée : "
            "le corpus n'est pas figé à la fin de la semaine 1, il est relu à chaque "
            "dépôt.", CORPS),
        tableau([
            ["Tâche", "Contenu", "Quand"],
            ["Cadrage et corpus", "Catalogue, générateur, inventaire, vérificateur", "S1, terminé"],
            ["Ingestion", "Extraction du texte, OCR des scannés, découpage, métadonnées", "S2"],
            ["Recherche", "Index Qdrant, embeddings texte et image, filtres d'accès", "S3"],
            ["Génération", "Prompts, réponses sourcées, vérification des citations", "S4"],
            ["Agent et MCP", "Historiques, brouillon de ticket, approbation humaine", "S5"],
            ["Évaluation", "Jeu de tests, mesures, démonstration, dépôt final", "S6"],
            ["Relecture humaine", "Documents critiques, seuils et libellés de codes", "S1, puis à chaque dépôt"],
        ], [30 * mm, 86 * mm, 32 * mm], gauche={0, 1, 2}),
        Paragraph("Relecture du corpus", H2),
        Paragraph(
            "Le corpus a été relu par échantillon assumé : les dix documents critiques — les "
            "deux paires contradictoires, la note piégée, les trois scans, les deux extraits "
            "anglais — et les dix images sources. Les assertions sont dans "
            "<font face='Courier'>docs/livrable-1/revue-corpus.md</font>, une case par phrase "
            "vérifiée. Les vingt documents restants ne sont pas déclarés relus : ils sont "
            "contrôlés par le vérificateur, ce qui n'est pas la même chose. La colonne "
            "<font face='Courier'>verifie_par</font> de l'inventaire distingue explicitement "
            "les deux cas.", CORPS),
        PageBreak(),
    ]


def annexes(documents: list[dict[str, str]]) -> list[object]:
    types = Counter(doc["type_document"] for doc in documents)
    familles = Counter(doc["famille_equipement"] for doc in documents)
    formats = Counter(doc["format"] for doc in documents)
    pages = sum(int(doc["nb_pages"]) for doc in documents)
    lignes = [["Dimension", "Valeur", "Nombre"]]
    lignes += [["Type de document", type_doc, str(nombre)]
               for type_doc, nombre in sorted(types.items())]
    lignes += [["Famille", famille, str(nombre)]
               for famille, nombre in sorted(familles.items())]
    lignes += [["Format", forme, str(nombre)]
               for forme, nombre in sorted(formats.items())]
    lignes += [["Total", "documents", str(len(documents))],
               ["Total", "pages", str(pages)]]
    blocs: list[object] = [
        Paragraph("Annexe A — Composition mesurée du corpus", H1),
        Paragraph(
            "Répartition lue dans <font face='Courier'>corpus/inventaire.csv</font>. "
            "L'inventaire complet, avec les vingt colonnes imposées et une ligne par fichier, "
            "est fourni dans le dossier <font face='Courier'>corpus/</font> de l'archive. "
            "Les valeurs de pages et d'éléments visuels y sont mesurées sur les fichiers, "
            "jamais recopiées du catalogue de conception.", CORPS),
        tableau(lignes, [45 * mm, 70 * mm, 35 * mm], gauche={1}),
        Spacer(1, 6 * mm),
        Paragraph(
            "Les documents sont nommés <font face='Courier'>&lt;document_id&gt;.&lt;ext&gt;</font> "
            "et rangés par famille : <font face='Courier'>famille_1</font> pour les ascenseurs, "
            "<font face='Courier'>famille_2</font> pour les portes. Les images sources sont dans "
            "<font face='Courier'>corpus/images/</font> et portent le même identifiant que le "
            "document qui les publie.", CORPS),
        PageBreak(),
        Paragraph("Annexe B — Index des prompts", H1),
        Paragraph(
            "Le fichier <font face='Courier'>corpus/prompts_corpus.md</font> contient le texte "
            "des douze prompts et, pour chacun, les documents concernés, les défauts relevés "
            "et les corrections appliquées. Rappel : ces prompts pilotent l'écriture du "
            "générateur ; ils ne rédigent pas les documents.", CORPS),
        tableau([
            ["Prompt", "Objet", "Effet sur le corpus"],
            ["P01", "Cadrer le corpus et choisir deux familles",
             "Deux constructeurs fictifs, vingt documents chacun"],
            ["P02", "Construire le catalogue des équipements et des codes",
             "Huit équipements, treize codes, cinq collisions assumées"],
            ["P03", "Définir la mise en page des documents",
             "Sept gabarits, pagination et pieds de page cohérents"],
            ["P04", "Écrire le générateur Python déterministe",
             "Quarante documents reproductibles, sans graine à conserver"],
            ["P05", "Générer les images : photos, plaques, schémas",
             "Dix images sources, dont deux plaques volontairement illisibles"],
            ["P06", "Écrire l'inventaire par mesure, pas par recopie",
             "Pages et éléments visuels comptés sur les fichiers produits"],
            ["P07", "Écrire le vérificateur automatique",
             "Onze contrôles, échec bloquant en cas d'écart"],
            ["P08", "Donner un contenu propre à chaque procédure",
             "Étapes et contrôles distincts, deux pages par procédure"],
            ["P09", "Ajouter une fiche de contrôle et un contrat",
             "Deux gabarits de plus, sans nouvelle famille"],
            ["P10", "Corriger les défauts trouvés à la relecture visuelle",
             "Plaques crédibles, scans reconnaissables, sortie 48 V rétablie"],
            ["P11", "Aligner les énumérations sur la consigne",
             "Rôles de test et types de document conformes au sujet"],
            ["P12", "Tenir le journal des corrections et préparer la relecture",
             "Défauts tracés, huit documents critiques désignés"],
        ], [16 * mm, 88 * mm, 54 * mm], gauche={1, 2}),
        PageBreak(),
        Paragraph("Annexe C — Arborescence du dépôt", H1),
        Paragraph(
            "Le dépôt est organisé pour que le corpus, le code qui le produit et la "
            "documentation de cadrage soient séparés. Les artefacts lourds (modèles, index) "
            "sont hors dépôt et référencés par variable d'environnement.", CORPS),
    ]
    arbre = [
        "MaintiDoc/",
        "  corpus/",
        "    inventaire.csv             inventaire mesuré, 20 colonnes",
        "    prompts_corpus.md          prompts P01 à P12",
        "    documents/famille_1/       20 documents ascenseurs",
        "    documents/famille_2/       20 documents portes",
        "    images/                    10 images sources",
        "  scripts/",
        "    gen_corpus/                catalogue, rendu, images, inventaire, vérificateur",
        "    gen_diagrammes.py          figures du rapport",
        "    gen_rapport.py             ce rapport",
        "  docs/",
        "    adr/                       décisions d'architecture 0001 à 0006",
        "    livrable-1/                plan, protocole, journal des corrections",
        "    diagrammes/                figures PDF et PNG",
        "    sujet/                     consignes fournies",
        "  tests/                       tests du générateur et du vérificateur",
        "  tasks.ps1                    lanceur de tâches",
        "  pyproject.toml",
        "  README.md",
    ]
    style_arbre = ParagraphStyle("arbre", parent=PETIT, fontName="Courier", fontSize=7.6,
                                 leading=9.6, textColor=colors.black, alignment=0)
    blocs.append(Paragraph("<br/>".join(arbre).replace(" ", "&nbsp;"), style_arbre))
    return blocs


def construire(destination: Path, racine: Path) -> None:
    documents = lire_inventaire(racine / "corpus")
    gabarit = BaseDocTemplate(
        str(destination), pagesize=A4,
        leftMargin=MARGE, rightMargin=MARGE, topMargin=20 * mm, bottomMargin=20 * mm,
        title="MaintiDoc — Livrable 1", author="Mazine CHATER",
        subject="Cadrage, corpus et architecture",
    )
    cadre = Frame(MARGE, 20 * mm, A4[0] - 2 * MARGE, A4[1] - 40 * mm, id="corps")
    gabarit.addPageTemplates([
        PageTemplate(id="standard", frames=[cadre], onPage=_Canevas("MaintiDoc")),
    ])
    blocs: list[object] = []
    blocs += couverture()
    blocs += sommaire()
    blocs += cadrage()
    blocs += corpus(documents)
    blocs += architecture()
    blocs += flux()
    blocs += risques()
    blocs += planning()
    blocs += annexes(documents)
    gabarit.build(blocs)


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--out", type=Path, default=Path("docs/livrable-1"))
    arguments = parseur.parse_args()
    arguments.out.mkdir(parents=True, exist_ok=True)
    destination = arguments.out / f"L1_MaintiDoc_{NOM_EQUIPE}_Rapport.pdf"
    construire(destination, Path("."))
    import pymupdf

    with pymupdf.open(destination) as document:
        print(f"{destination} — {document.page_count} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
