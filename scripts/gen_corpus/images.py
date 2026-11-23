"""Rendu des images du corpus : panneaux, armoires, plaques, schémas.

Les images sont volontairement sobres. Du matériel de maintenance réel
ressemble à ça : fond gris, voyants, étiquettes courtes, pas d'illustration.

Deux images sont dégradées à dessein et servent de cas ambigus : la plaque
illisible (flou) et les deux voyants orange identiques sur des équipements
différents. Le sens du voyant dépend du constructeur, pas de sa couleur.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

LARGEUR, HAUTEUR = 1600, 1200
GRIS_FOND = (58, 61, 64)
GRIS_CLAIR = (86, 90, 94)
BLANC = (238, 238, 234)
NOIR = (28, 29, 30)

ROUGE = (226, 64, 52)
ORANGE = (240, 148, 24)
VERT = (60, 190, 96)
BLEU_VOYANT = (90, 150, 230)
ETEINT = (92, 95, 98)


def _police(taille: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for nom in ("arial.ttf", "segoeui.ttf", "calibri.ttf"):
        try:
            return ImageFont.truetype(nom, taille)
        except OSError:
            continue
    return ImageFont.load_default()


def _voyant(draw: ImageDraw.ImageDraw, centre: tuple[int, int], rayon: int,
            couleur: tuple[int, int, int], allume: bool = True) -> None:
    """Voyant circulaire. Un voyant éteint reste visible mais sans halo."""
    x, y = centre
    draw.ellipse((x - rayon, y + 3, x + rayon, y + rayon // 2 + 3), fill=(20, 20, 20))
    if allume:
        draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=couleur)
        draw.ellipse((x - rayon + 4, y - rayon + 4, x - rayon // 3, y - rayon // 3),
                     fill=(255, 255, 255, 90))
    else:
        draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=ETEINT,
                     outline=(70, 72, 74), width=2)


def panneau_cabine(destination: Path, equipement: str = "ASC-A-01") -> None:
    """Boîte à boutons d'ascenseur : boutons d'étage, afficheur, voyants.

    Seuls le défaut et le service sont allumés : c'est la situation décrite par
    la légende de la photo. Un panneau où tous les voyants brillent n'existe
    pas, et un correcteur le verrait.
    """
    image = Image.new("RGB", (LARGEUR, HAUTEUR), GRIS_FOND)
    draw = ImageDraw.Draw(image)
    fonte_titre = _police(34)
    fonte = _police(26)
    fonte_petite = _police(20)

    draw.rounded_rectangle((180, 90, 1420, 1110), radius=28, outline=GRIS_CLAIR, width=4,
                           fill=(66, 69, 72))
    draw.text((230, 130), "VERTICALIS", font=fonte_titre, fill=BLANC)
    draw.text((230, 176), equipement, font=fonte_petite, fill=(170, 175, 180))

    # Afficheur sept segments simplifié
    draw.rounded_rectangle((560, 150, 1040, 290), radius=12, fill=NOIR)
    draw.text((800, 220), "3", font=_police(84), fill=(230, 70, 60), anchor="mm")
    draw.text((800, 316), "CABINE AU NIVEAU 3", font=_police(16), fill=(150, 155, 160),
              anchor="mm")

    # Boutons d'étage : deux colonnes, du plus haut au plus bas
    positions = [(360, 380), (360, 500), (360, 620), (360, 740),
                 (560, 380), (560, 500), (560, 620), (560, 740)]
    for index, (x, y) in enumerate(positions):
        draw.ellipse((x, y, x + 110, y + 110), outline=(180, 184, 188), width=4,
                     fill=(46, 48, 50))
        draw.text((x + 55, y + 55), str(8 - index), font=fonte, fill=BLANC, anchor="mm")

    # Colonne de voyants à droite
    voyants = [
        ("ALARME", ROUGE, False),
        ("DÉFAUT", ORANGE, True),  # le voyant de la question
        ("SERVICE", VERT, True),
        ("HORS SERVICE", (90, 92, 96), False),
    ]
    y = 400
    for libelle, couleur, allume in voyants:
        _voyant(draw, (980, y), 34, couleur, allume)
        draw.text((1040, y - 16), libelle, font=fonte_petite, fill=BLANC)
        y += 120

    draw.text((360, 930), "Appel : maintenir 3 s", font=fonte_petite, fill=(160, 165, 170))
    draw.text((360, 970), "Alarme : sonnerie continue", font=fonte_petite, fill=(160, 165, 170))
    draw.rectangle((0, 1150, LARGEUR, HAUTEUR), fill=(40, 42, 44))
    draw.text((40, 1160), f"Photo 2025-10 - {equipement} - hall bâtiment A",
              font=fonte_petite, fill=(150, 155, 160))

    image.save(destination)


def panneau_porte(destination: Path, equipement: str = "PA-01", reference: str = "SL-400",
                  code: str = "") -> None:
    """Boîte de commande de porte automatique : afficheur, voyant, boutons.

    Le voyant orange est dessiné avec le même gabarit que celui de la boîte à
    boutons d'ascenseur : c'est la source de l'ambiguïté entre les deux photos.
    """
    image = Image.new("RGB", (LARGEUR, HAUTEUR), (72, 74, 76))
    draw = ImageDraw.Draw(image)
    fonte_titre = _police(34)
    fonte = _police(26)
    fonte_petite = _police(20)

    draw.rounded_rectangle((220, 140, 1380, 1060), radius=22, fill=(92, 95, 98),
                           outline=(140, 143, 146), width=4)
    draw.text((270, 180), "PORTALIS", font=fonte_titre, fill=BLANC)
    draw.text((270, 226), f"{reference} - {equipement}", font=fonte_petite,
              fill=(200, 203, 206))

    draw.rounded_rectangle((600, 190, 1120, 300), radius=10, fill=NOIR)
    affichage = f"d {code}" if code else "--"
    draw.text((860, 245), affichage, font=_police(64), anchor="mm",
              fill=(235, 150, 40) if code else (120, 180, 120))

    _voyant(draw, (1230, 240), 34, ORANGE, allume=bool(code))
    draw.text((1180, 300), "DÉFAUT", font=_police(16), fill=(210, 213, 216))

    boutons = [("OUV", VERT), ("FER", ROUGE), ("AUTO", BLEU_VOYANT), ("RÉG", (200, 200, 60))]
    x = 290
    for libelle, couleur in boutons:
        draw.rectangle((x, 400, x + 200, 520), outline=(60, 62, 64), width=3, fill=(70, 72, 74))
        draw.rectangle((x + 40, 430, x + 160, 490), fill=couleur)
        draw.text((x + 100, 540), libelle, font=fonte_petite, fill=BLANC, anchor="ma")
        x += 260

    draw.text((290, 660), "Temporisation fermeture : 2,5 s", font=fonte, fill=BLANC)
    draw.text((290, 710), "Vitesse ouverture : 0,4 m/s", font=fonte, fill=(200, 203, 206))
    draw.text((290, 760), "Mode : automatique", font=fonte, fill=(200, 203, 206))
    draw.text((290, 860), f"Porte {equipement} - hall principal", font=fonte_petite,
              fill=(180, 184, 188))

    image.save(destination)


def armoire_commande(destination: Path) -> None:
    """Armoire électrique : rangée de LED étiquetées."""
    image = Image.new("RGB", (LARGEUR, HAUTEUR), (52, 54, 56))
    draw = ImageDraw.Draw(image)
    fonte = _police(24)
    fonte_petite = _police(18)

    draw.rounded_rectangle((120, 80, 1480, 1120), radius=10, fill=(74, 78, 82),
                           outline=(120, 124, 128), width=5)
    draw.text((180, 120), "ARMOIRE DE COMMANDE", font=fonte, fill=BLANC)
    draw.text((180, 160), "ASC-A-01 - indice C", font=fonte_petite, fill=(190, 194, 198))

    etiquettes = [
        ("RÉSEAU", VERT, True), ("MOTEUR", VERT, True), ("FREIN", ORANGE, False),
        ("PORTE", ROUGE, True), ("SÉCURITÉ", VERT, True), ("VARIATEUR", ORANGE, False),
        ("BATTERIE", BLEU_VOYANT, True), ("DÉFAUT", ROUGE, True),
    ]
    for index, (libelle, couleur, allume) in enumerate(etiquettes):
        colonne, ligne = index % 4, index // 4
        x = 220 + colonne * 320
        y = 300 + ligne * 260
        draw.rounded_rectangle((x, y, x + 250, y + 150), radius=8, fill=(58, 61, 64),
                               outline=(100, 104, 108))
        _voyant(draw, (x + 125, y + 55), 26, couleur, allume)
        draw.text((x + 125, y + 105), libelle, font=fonte_petite, fill=BLANC, anchor="ma")

    draw.text((180, 900), "Alimentation coupée avant ouverture", font=fonte_petite,
              fill=(220, 180, 120))
    image.save(destination)


def plaque_signaletique(destination: Path, constructeur: str, reference: str, serie: str,
                        charge: str, annee: str, lisible: bool = True) -> None:
    """Plaque constructeur. Si elle est illisible, la photo est dégradée après coup.

    La dégradation combine une réduction de résolution et un flou, pas un simple
    flou gaussien. Un flou gaussien laisse les formes des lettres intactes : le
    numéro de série reste lisible à l'écran, alors que le document affirme le
    contraire. Une photo prise avec un téléphone et transmise compressée perd
    d'abord les détails fins ; c'est ce que reproduit la réduction à 260 px.

    Le numéro de série devient illisible, le constructeur reste reconnaissable :
    c'est précisément l'ambiguïté à traiter (savoir de quel matériel on parle
    sans pouvoir l'identifier formellement).
    """
    image = Image.new("RGB", (LARGEUR, 800), (120, 122, 124))
    draw = ImageDraw.Draw(image)
    fonte = _police(40)
    fonte_petite = _police(30)

    draw.rounded_rectangle((120, 80, 1480, 720), radius=16, fill=(158, 160, 162),
                           outline=(96, 98, 100), width=6)
    draw.text((180, 140), constructeur.upper(), font=_police(52), fill=(48, 50, 52))
    draw.text((180, 240), f"Type : {reference}", font=fonte, fill=(48, 50, 52))
    draw.text((180, 310), f"N° de série : {serie}", font=fonte, fill=(48, 50, 52))
    draw.text((180, 380), f"Charge nominale : {charge}", font=fonte_petite, fill=(48, 50, 52))
    draw.text((180, 440), "Vitesse : 1,6 m/s", font=fonte_petite, fill=(48, 50, 52))
    draw.text((180, 500), f"Année : {annee}", font=fonte_petite, fill=(48, 50, 52))
    draw.text((180, 600), "Ne pas démonter - identification obligatoire", font=_police(22),
              fill=(70, 72, 74))

    if not lisible:
        petite = image.resize((260, round(image.height * 260 / image.width)), Image.LANCZOS)
        floue = petite.filter(ImageFilter.GaussianBlur(radius=1.2))
        image = floue.resize(image.size, Image.BICUBIC)

    image.save(destination)


def _fleche(draw: ImageDraw.ImageDraw, depart: tuple[int, int], arrivee: tuple[int, int],
            largeur: int = 3) -> None:
    """Trait avec pointe de flèche, pour un schéma lisible."""
    x1, y1 = depart
    x2, y2 = arrivee
    draw.line((x1, y1, x2, y2), fill=NOIR, width=largeur)
    if y1 == y2:
        sens = -1 if x2 > x1 else 1
        draw.polygon([(x2, y2), (x2 + sens * 16, y2 - 9), (x2 + sens * 16, y2 + 9)], fill=NOIR)
    else:
        draw.polygon([(x2, y2), (x2 - 9, y2 - 16), (x2 + 9, y2 - 16)], fill=NOIR)


def schema_boucle(destination: Path, famille: str) -> None:
    """Schéma de principe : les organes de sécurité, en série.

    Le tracé suit l'ordre réel de la chaîne et serpente sur deux rangées. Les
    liaisons sont orthogonales : un schéma avec des diagonales qui traversent
    les blocs n'est pas exploitable par un technicien.
    """
    image = Image.new("RGB", (1700, 1200), (250, 250, 248))
    draw = ImageDraw.Draw(image)
    fonte = _police(24)
    fonte_petite = _police(20)

    if famille == "ascenseurs":
        titre = "SCHÉMA DE PRINCIPE - BOUCLE DE SÉCURITÉ"
        titres = ["Boîte à boutons\ncabine", "Contact de\nverrouillage", "Barre palpeuse",
                  "Arrêt\nd'urgence", "Relais de\nsécurité", "Variateur", "Moteur de\ntraction"]
        indice = "Indice B - 2024-09"
    else:
        titre = "SCHÉMA DE PRINCIPE - BOUCLE DE DÉTECTION"
        titres = ["Cellule\nphoto-électrique", "Détecteur de\nprésence", "Boucle au sol",
                  "Arrêt\nd'urgence", "Automate\nde porte", "Variateur", "Moteur de\nporte"]
        indice = "Indice A - 2024-05"

    draw.text((60, 40), titre, font=_police(32), fill=NOIR)

    largeur_boite, hauteur_boite = 300, 150
    positions: list[tuple[int, int]] = []
    for index in range(len(titres)):
        rangee, rang = divmod(index, 4)
        x = 80 + rang * 380 if rangee == 0 else 1220 - rang * 380
        y = 240 + rangee * 320
        positions.append((x, y))

    for (x, y), libelle in zip(positions, titres, strict=True):
        draw.rounded_rectangle((x, y, x + largeur_boite, y + hauteur_boite), radius=10,
                               outline=NOIR, width=3, fill=(255, 255, 255))
        draw.multiline_text((x + 18, y + 48), libelle, font=fonte, fill=NOIR, spacing=6)

    # Liaisons horizontales : la première rangée va vers la droite, la seconde
    # revient vers la gauche. Aucune liaison n'est omise : la chaîne doit se
    # lire d'un seul trait, sinon le schéma contredit sa propre légende
    # (« tous les contacts sont en série »).
    for index in range(6):
        x1, y1 = positions[index]
        x2, y2 = positions[index + 1]
        milieu = y1 + hauteur_boite // 2
        if y1 == y2:
            if x2 > x1:
                _fleche(draw, (x1 + largeur_boite + 6, milieu), (x2 - 8, milieu))
            else:
                _fleche(draw, (x1 - 6, milieu), (x2 + largeur_boite + 8, milieu))
    x_haut, y_haut = positions[3]
    _fleche(draw, (x_haut + largeur_boite // 2, y_haut + hauteur_boite + 6),
            (x_haut + largeur_boite // 2, positions[4][1] - 8))

    draw.text((80, 900), "Tous les contacts sont en série. L'ouverture d'un seul contact",
              font=fonte_petite, fill=NOIR)
    draw.text((80, 935), "entraîne l'arrêt immédiat et le blocage de la mise en mouvement.",
              font=fonte_petite, fill=NOIR)
    draw.text((80, 1020), f"{indice} - ne pas modifier sans mise à jour de l'indice",
              font=_police(18), fill=(90, 90, 90))
    draw.rectangle((40, 30, 1660, 1160), outline=NOIR, width=2)
    image.save(destination)


def schema_armoire(destination: Path) -> None:
    """Schéma d'armoire : alimentation, variateur, relais, moteur."""
    image = Image.new("RGB", (1700, 1200), (250, 250, 248))
    draw = ImageDraw.Draw(image)
    fonte = _police(24)

    draw.text((60, 50), "ARMOIRE DE COMMANDE ASC-A-01 - INDICE C", font=_police(32), fill=NOIR)
    draw.rectangle((60, 110, 1640, 1120), outline=NOIR, width=3)

    composants = [
        ("QF1\nDisjoncteur\ngénéral", (110, 170, 260, 120)),
        ("KM1\nContacteur\nprincipal", (420, 170, 240, 120)),
        ("V1\nVariateur", (710, 170, 260, 150)),
        ("M1\nMoteur de\ntraction", (1030, 170, 250, 150)),
        ("T1\nTransformateur\n48 V", (110, 430, 240, 130)),
        ("KA1\nRelais de\nsécurité", (420, 430, 240, 130)),
        ("U1\nAutomate\nde cabine", (710, 430, 260, 140)),
        ("B1\nBatterie\nde secours", (1030, 430, 250, 130)),
    ]
    for libelle, (x, y, w, h) in composants:
        draw.rectangle((x, y, x + w, y + h), outline=NOIR, width=2, fill=(255, 255, 255))
        draw.multiline_text((x + 12, y + 14), libelle, font=fonte, fill=NOIR, spacing=4)

    # Liaisons principales
    draw.line((370, 230, 420, 230), fill=NOIR, width=3)
    draw.line((660, 230, 710, 230), fill=NOIR, width=3)
    draw.line((970, 230, 1030, 230), fill=NOIR, width=3)
    # Alimentation du transformateur 48 V : départ sous le disjoncteur général,
    # arrivée en haut du transformateur, sans traverser un autre bloc.
    draw.line((240, 290, 240, 430), fill=NOIR, width=3)
    # Le 48 V alimente le relais de sécurité, l'automate et le chargeur de
    # batterie : sans ce trait, le transformateur n'a aucune sortie.
    draw.line((350, 495, 420, 495), fill=NOIR, width=3)
    draw.line((660, 495, 710, 495), fill=NOIR, width=3)
    draw.line((970, 495, 1030, 495), fill=NOIR, width=3)

    draw.text((110, 700), "Bornier X1 : 1-2 alimentation 400 V, 3-4 terre, 5-6 boucle de sécurité",
              font=fonte, fill=NOIR)
    draw.text((110, 760), "Bornier X2 : 1-2 moteur, 3-4 frein, 5-6 codeur", font=fonte, fill=NOIR)
    draw.text((110, 880), "Toute intervention : consignation selon la procédure ASC-PR-002",
              font=_police(20), fill=(120, 60, 40))
    image.save(destination)


def schema_moteur(destination: Path) -> None:
    image = Image.new("RGB", (1700, 1200), (250, 250, 248))
    draw = ImageDraw.Draw(image)
    fonte = _police(26)
    draw.text((60, 50), "MOTEUR ET RÉDUCTEUR DU PORTAIL PG-01", font=_police(32), fill=NOIR)
    draw.rectangle((400, 260, 900, 620), outline=NOIR, width=3, fill=(255, 255, 255))
    draw.text((650, 440), "M1 - 0,75 kW", font=fonte, fill=NOIR, anchor="mm")
    draw.rectangle((980, 300, 1400, 580), outline=NOIR, width=3, fill=(255, 255, 255))
    draw.text((1190, 440), "RÉDUCTEUR i=1/40", font=fonte, fill=NOIR, anchor="mm")
    draw.line((900, 440, 980, 440), fill=NOIR, width=4)
    draw.text((940, 400), "accouplement", font=_police(20), fill=NOIR, anchor="mm")
    draw.text((400, 760), "Frein : 24 V, desserrage à l'ouverture du contact F1", font=fonte,
              fill=NOIR)
    draw.text((400, 820), "Fin de course : came réglable, 2 contacts NO/NF", font=fonte, fill=NOIR)
    image.save(destination)
