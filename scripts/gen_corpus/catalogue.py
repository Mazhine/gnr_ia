"""Catalogue du corpus MaintiDoc.

Source unique de vérité : équipements, codes de défaut et documents. Le
générateur ne rédige rien à partir de valeurs saisies ailleurs. Si un code de
défaut change ici, il change dans le manuel, dans le tableau d'alarmes et dans
l'historique d'intervention en même temps.

Toute modification du catalogue doit être suivie de :
    .\\tasks.ps1 corpus        puis        .\\tasks.ps1 corpus-check
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Famille(StrEnum):
    ASCENSEURS = "ascenseurs"
    PORTES = "portes"


# Raison sociale fictive par famille. Elle apparaît en en-tête des documents et
# dans les tableaux de codes : deux constructeurs, donc deux numérotations.
CONSTRUCTEURS: dict[Famille, str] = {
    Famille.ASCENSEURS: "Verticalis",
    Famille.PORTES: "Portalis",
}


@dataclass(frozen=True)
class Equipement:
    id: str
    designation: str
    famille: Famille
    constructeur: str
    reference: str
    localisation: str
    charge: str
    groupe: str


EQUIPEMENTS: tuple[Equipement, ...] = (
    Equipement("ASC-A-01", "Ascenseur principal", Famille.ASCENSEURS, "Verticalis",
               "VRT-8-1000", "Bâtiment A, hall", "1000 kg / 13 personnes", "techniciens_ascenseurs"),
    Equipement("ASC-A-02", "Ascenseur de service", Famille.ASCENSEURS, "Verticalis",
               "VRT-8-630", "Bâtiment A, zone logistique", "630 kg / 8 personnes", "techniciens_ascenseurs"),
    Equipement("ASC-B-01", "Ascenseur bâtiment B", Famille.ASCENSEURS, "Verticalis",
               "VRT-6-630", "Bâtiment B, hall", "630 kg / 8 personnes", "techniciens_ascenseurs"),
    Equipement("MC-01", "Monte-charge", Famille.ASCENSEURS, "Verticalis",
               "MCH-2000", "Zone réception", "2000 kg", "techniciens_ascenseurs"),
    Equipement("PA-01", "Porte automatique hall", Famille.PORTES, "Portalis",
               "SL-400", "Bâtiment A, entrée principale", "2 vantaux / 140 kg", "techniciens_portes"),
    Equipement("PA-02", "Porte automatique personnel", Famille.PORTES, "Portalis",
               "SL-400", "Bâtiment A, accès personnel", "2 vantaux / 140 kg", "techniciens_portes"),
    Equipement("PG-01", "Portail coulissant parking", Famille.PORTES, "Portalis",
               "CG-600", "Parking extérieur", "600 kg / 6 m", "techniciens_portes"),
    Equipement("PB-01", "Barrière levante", Famille.PORTES, "Portalis",
               "BR-300", "Parking, sortie", "300 kg", "techniciens_portes"),
)

EQUIPEMENTS_PAR_ID: dict[str, Equipement] = {e.id: e for e in EQUIPEMENTS}


@dataclass(frozen=True)
class CodeDefaut:
    code: str
    famille: Famille
    libelle: str
    cause: str
    action: str
    gravite: str


# Collision volontaire sur 12, 33, 42, 51, 71 : deux constructeurs, deux
# numérotations, des libellés proches mais des organes différents. C'est la
# source des négatifs difficiles du reranker.
CODES_DEFAUT: tuple[CodeDefaut, ...] = (
    CodeDefaut("12", Famille.ASCENSEURS, "Défaut de communication cabine",
               "Rupture du câble de voyage ou connecteur desserré au niveau du toit de cabine",
               "Contrôler la continuité du câble souple et resserrer les connecteurs", "majeur"),
    CodeDefaut("21", Famille.ASCENSEURS, "Défaut variateur",
               "Surchauffe du module de puissance ou défaut de ventilation de l'armoire",
               "Vérifier le ventilateur, dépoussiérer l'armoire, relever la température", "majeur"),
    CodeDefaut("33", Famille.ASCENSEURS, "Défaut de nivellement",
               "Écart supérieur au seuil entre le plancher de cabine et le palier",
               "Contrôler les capteurs de position et la propreté des guides", "mineur"),
    CodeDefaut("42", Famille.ASCENSEURS, "Thermique moteur de traction",
               "Surcharge répétée ou ventilation moteur insuffisante",
               "Laisser refroidir, contrôler la charge réelle et le sens de rotation du ventilateur",
               "majeur"),
    CodeDefaut("51", Famille.ASCENSEURS, "Défaut de porte (verrouillage)",
               "Pêne de porte mal engagé ou contact de verrouillage encrassé",
               "Nettoyer le contact, vérifier l'alignement du pêne de serrure", "critique"),
    CodeDefaut("62", Famille.ASCENSEURS, "Fin de course haut",
               "Capteur de fin de course supérieur désactivé ou mal positionné",
               "Repositionner le capteur, vérifier le câblage", "mineur"),
    CodeDefaut("71", Famille.ASCENSEURS, "Survitesse",
               "Limiteur de vitesse déclenché ou capteur de vitesse défaillant",
               "Immobiliser l'appareil, contrôler le limiteur avant toute remise en service",
               "critique"),
    CodeDefaut("12", Famille.PORTES, "Défaut capteur de sécurité",
               "Cellule photo-électrique sale, désalignée ou obstruée",
               "Nettoyer les lentilles, réaligner le faisceau, tester avec un obstacle étalon",
               "majeur"),
    CodeDefaut("33", Famille.PORTES, "Fin de course ouverture",
               "Came de fin de course décalée ou interrupteur usé",
               "Régler la came, remplacer l'interrupteur si la course reste incohérente",
               "mineur"),
    CodeDefaut("42", Famille.PORTES, "Thermique moteur de porte",
               "Frottement important, rail encrassé ou charge excessive sur un vantail",
               "Nettoyer le rail, vérifier le galet, contrôler l'intensité moteur", "majeur"),
    CodeDefaut("51", Famille.PORTES, "Défaut de fin de course",
               "Le vantail n'atteint pas sa position de fermeture complète",
               "Vérifier l'obstacle en fin de course et la temporisation de fermeture", "majeur"),
    CodeDefaut("71", Famille.PORTES, "Défaut de boucle de détection",
               "Boucle au sol coupée ou détecteur de présence en défaut",
               "Mesurer la résistance de la boucle, remplacer le détecteur si nécessaire",
               "majeur"),
    CodeDefaut("88", Famille.PORTES, "Batterie de secours faible",
               "Batterie en fin de vie, autonomie inférieure à 30 minutes",
               "Remplacer la batterie et vérifier la charge après remplacement", "mineur"),
)

CODES_PAR_FAMILLE: dict[Famille, tuple[CodeDefaut, ...]] = {
    famille: tuple(c for c in CODES_DEFAUT if c.famille is famille) for famille in Famille
}


@dataclass(frozen=True)
class Document:
    """Fiche descriptive d'un document du corpus.

    `pages` et `elements_visuels` sont des cibles de rédaction, utiles pour
    dimensionner le corpus. Ils ne sont pas publiés tels quels : l'inventaire
    contient les valeurs mesurées sur les fichiers produits (voir
    `inventaire.py`). Un écart entre les deux est un défaut de plan, pas une
    donnée à recopier.
    """

    id: str
    famille: Famille | None
    type_document: str
    titre: str
    pages: int
    usage_test: str = "normal"
    langue: str = "fr"
    format: str = "pdf_texte"
    equipements: tuple[str, ...] = ()
    groupe_acces: str = ""
    version: str = "v1.0 (2025-03)"
    elements_visuels: str = "aucun"
    remarques: str = ""
    params: dict[str, str] = field(default_factory=dict)

    @property
    def fichier(self) -> str:
        if self.format == "image":
            return f"images/{self.id}.png"
        dossier = "famille_1" if self.famille is Famille.ASCENSEURS else "famille_2"
        return f"documents/{dossier}/{self.id}.pdf"

    @property
    def extension(self) -> str:
        return "png" if self.format == "image" else "pdf"


ASC = Famille.ASCENSEURS
PRT = Famille.PORTES
G_ASC = "techniciens_ascenseurs"
G_PRT = "techniciens_portes"

DOCUMENTS: tuple[Document, ...] = (
    # --- Famille 1 : ascenseurs et monte-charges ---
    Document("asc_manuel_a", ASC, "manuel", "Manuel d'utilisation et de maintenance ASC-A-01",
             24, equipements=("ASC-A-01",), groupe_acces=G_ASC, version="v1.2 (2025-03)",
             elements_visuels="figure de la chaîne de sécurité ; tableau des codes",
             remarques="seuil de nivellement 15 mm, contredit la v2.0"),
    Document("asc_manuel_a_v2", ASC, "manuel", "Manuel d'utilisation et de maintenance ASC-A-01",
             24, usage_test="contradictoire", equipements=("ASC-A-01",), groupe_acces=G_ASC,
             version="v2.0 (2025-09)",
             elements_visuels="figure de la chaîne de sécurité ; tableau des codes",
             remarques="seuil de nivellement ramené à 8 mm ; version non diffusée aux techniciens",
             params={"seuil_nivellement": "8 mm"}),
    Document("asc_manuel_mc", ASC, "manuel", "Manuel du monte-charge MC-01",
             18, equipements=("MC-01",), groupe_acces=G_ASC, version="v1.0 (2024-11)",
             elements_visuels="figure de la chaîne de sécurité ; tableau des codes"),
    Document("asc_codes_defaut", ASC, "codes_alarme", "Tableau des codes défaut Verticalis",
             4, equipements=("ASC-A-01", "ASC-A-02", "ASC-B-01", "MC-01"), groupe_acces=G_ASC,
             version="v3.1 (2025-01)", elements_visuels="tableau complet des codes"),
    Document("asc_proc_consignation", ASC, "procedure", "Consignation électrique d'un ascenseur",
             6, equipements=("ASC-A-01", "ASC-B-01"), groupe_acces=G_ASC, version="v2.0 (2025-02)",
             elements_visuels="tableau des points de contrôle",
             params={
                 "objet": ("mettre hors tension et condamner l'installation avant toute "
                           "intervention en armoire ou en gaine"),
                 "etapes": (
                     "Prévenir l'exploitant et afficher la consigne d'indisponibilité sur chaque "
                     "porte palière.|Amener la cabine au niveau de dégagement et poser le calage "
                     "mécanique sous la cabine.|Ouvrir le sectionneur général de l'armoire de "
                     "commande et le verrouiller par un cadenas personnel.|Vérifier l'absence de "
                     "tension sur les bornes X1-1, X1-2 et X1-3 au VAT.|Attendre cinq minutes la "
                     "décharge des condensateurs du variateur, puis vérifier l'absence de tension "
                     "résiduelle.|Poser l'étiquette d'identification du circuit et remettre les clés "
                     "au responsable en fin d'intervention."
                 ),
                 "controles": (
                     "Absence de tension|Vérifiée au VAT sur les trois phases et entre phase et "
                     "terre;Condensateurs|Tension résiduelle inférieure à 60 V après cinq "
                     "minutes;Calage mécanique|En place et verrouillé avant l'accès en "
                     "gaine;Cadenas|Un cadenas par intervenant, clé nominative;Registre|Consignation "
                     "datée et signée par l'intervenant"
                 ),
             }),
    Document("asc_proc_deblocage", ASC, "procedure", "Déblocage de personnes en cabine",
             5, equipements=("ASC-A-01", "ASC-A-02", "ASC-B-01"), groupe_acces=G_ASC,
             version="v1.3 (2024-12)", elements_visuels="tableau des points de contrôle",
             params={
                 "objet": ("libérer sans délai les personnes bloquées en cabine, sans exposer "
                           "l'intervenant ni les occupants"),
                 "etapes": (
                     "Établir le contact avec les personnes bloquées, les rassurer et vérifier "
                     "l'absence de blessé.|Couper l'alimentation de l'appareil et condamner le "
                     "sectionneur.|Repérer la position de la cabine par rapport au palier le plus "
                     "proche et noter l'écart.|Si l'écart est inférieur à 300 mm, déverrouiller la "
                     "porte palière à la clé triangle et accompagner la sortie.|Sinon, utiliser le "
                     "volant de déblocage en machinerie en maintenant le frein desserré, sans "
                     "dépasser 0,3 m/s.|Refermer les portes, rétablir l'alimentation et consigner "
                     "l'événement dans le carnet."
                 ),
                 "controles": (
                     "Personnes|Aucune blessée, sortie accompagnée;Palier|Porte palière "
                     "verrouillée après évacuation;Frein|Resserré avant remise sous tension;Vitesse "
                     "de déblocage|Inférieure à 0,3 m/s;Traçabilité|Événement consigné le jour même"
                 ),
             }),
    Document("asc_proc_entretien_mensuel", ASC, "procedure", "Gamme d'entretien mensuel",
             8, equipements=("ASC-A-01", "ASC-B-01"), groupe_acces=G_ASC, version="v1.1 (2025-01)",
             elements_visuels="tableau des points de contrôle",
             params={
                 "objet": ("assurer le suivi mensuel des organes de sécurité et des points "
                           "d'usure des appareils du bâtiment A"),
                 "etapes": (
                     "Consulter le carnet de maintenance et relever les codes enregistrés depuis "
                     "la dernière visite.|Contrôler le niveau d'huile du réducteur et l'absence de "
                     "fuite sous la machine.|Essayer le dispositif de déblocage manuel et vérifier "
                     "que la cabine se déplace sans à-coup.|Mesurer le jeu des patins de guidage et "
                     "le comparer aux valeurs du manuel.|Nettoyer les contacts de verrouillage des "
                     "portes palières et vérifier l'engagement du pêne.|Essayer la barre palpeuse et "
                     "l'arrêt d'urgence en cabine.|Contrôler le serrage des raccordements au bornier "
                     "et l'état des fusibles.|Renseigner la fiche de visite et signaler toute "
                     "anomalie au responsable."
                 ),
                 "controles": (
                     "Niveau d'huile|Entre les repères de la jauge, pas de fuite;Déblocage|Cabine "
                     "mobile, frein resséré au relâchement;Patins|Jeu conforme au manuel;Verrouillage|"
                     "Pêne engagé sur 7 mm minimum;Barre palpeuse|Arrêt immédiat au contact;Traces|"
                     "Fiche de visite signée"
                 ),
             }),
    Document("asc_schema_armoire", ASC, "schema", "Schéma de l'armoire de commande ASC-A-01",
             1, equipements=("ASC-A-01",), groupe_acces=G_ASC, format="image",
             version="indice C (2024-09)", elements_visuels="schéma unifilaire de l'armoire"),
    Document("asc_schema_boucle_secu", ASC, "schema", "Schéma de la boucle de sécurité",
             1, equipements=("ASC-A-01", "ASC-B-01"), groupe_acces=G_ASC, format="image",
             version="indice B (2024-09)", elements_visuels="schéma de la boucle de sécurité"),
    Document("asc_fiche_secu_cuvette", ASC, "fiche_securite", "Espace libre en cuvette",
             2, equipements=("ASC-A-01", "ASC-B-01"), groupe_acces=G_ASC, version="v1.0 (2024-01)"),
    Document("asc_fiche_secu_elec", ASC, "fiche_securite", "Intervention électrique en armoire",
             2, equipements=("ASC-A-01", "ASC-B-01", "MC-01"), groupe_acces=G_ASC,
             version="v2.0 (2025-02)"),
    Document("asc_photo_boite_cabine", ASC, "photo", "Boîte à boutons ASC-A-01, voyant orange allumé",
             1, usage_test="ambigu", equipements=("ASC-A-01",), groupe_acces=G_ASC,
             format="image", version="2025-10", elements_visuels="voyant orange en façade",
             remarques="voyant identique à celui de PA-02, sens différent"),
    Document("asc_photo_armoire", ASC, "photo", "Armoire de commande, rangée de LED",
             1, usage_test="ambigu", equipements=("ASC-A-01",), groupe_acces=G_ASC, format="image",
             version="2025-10", elements_visuels="rangée de 8 LED",
             remarques="aucune légende ne relie les LED aux codes de défaut"),
    Document("asc_photo_plaque", ASC, "photo", "Plaque signalétique ASC-A-01 (illisible)",
             1, usage_test="ambigu", equipements=("ASC-A-01",), groupe_acces=G_ASC, format="image",
             version="2025-10", remarques="floue : le numéro de série n'est pas lisible"),
    Document("asc_histo_a_2025", ASC, "historique", "Historique des interventions ASC-A-01",
             3, equipements=("ASC-A-01",), groupe_acces=G_ASC, version="extraction 2025-10"),
    Document("asc_histo_b_2025", ASC, "historique", "Historique des interventions ASC-B-01",
             3, equipements=("ASC-B-01",), groupe_acces=G_ASC, version="extraction 2025-10"),
    Document("asc_note_service", ASC, "procedure", "Note de service - consignes internes",
             2, usage_test="injection", equipements=("ASC-A-01",), groupe_acces="responsables",
             version="v1.0 (2025-08)", remarques="instruction malveillante p.2"),
    Document("asc_manuel_en", ASC, "manuel", "Verticalis - Safety circuit description",
             2, langue="en", equipements=("ASC-A-01",), groupe_acces=G_ASC,
             version="rev. C (2024-06)", remarques="extrait en anglais, signalé comme tel"),
    Document("asc_proc_scannee", ASC, "procedure", "Procédure de remise en service (photocopie)",
             4, equipements=("ASC-A-01",), groupe_acces=G_ASC,
             format="pdf_scanne", version="v1.0 (2023-06)",
             remarques="scan 150 dpi, texte non extractible",
             params={"etapes": (
                 "Contrôler l'absence d'outillage en gaine et sur le toit de cabine."
                 "|Vérifier la fermeture et le verrouillage des portes palières."
                 "|Remettre sous tension et attendre la fin de l'auto-test."
                 "|Effectuer un cycle à vide, puis un cycle en charge nominale."
                 "|Renseigner la fiche de remise en service et l'afficher en local technique."
             )}),
    Document("asc_controle_periodique", ASC, "procedure", "Fiche de contrôle périodique",
             3, equipements=("ASC-A-01", "ASC-A-02", "ASC-B-01", "MC-01"),
             groupe_acces="responsables", version="v1.0 (2025-01)",
             params={
                 "gabarit": "controle",
                 "objet": ("contrôle annuel des quatre appareils du site, réalisé par un "
                           "organisme agréé en présence du responsable de maintenance"),
                 "lignes": (
                     "Mécanique|État des câbles, attaches et poulies;Mécanique|Usure des patins de "
                     "guidage et jeu dans les guides;Mécanique|Niveau d'huile et étanchéité du "
                     "réducteur;Mécanique|Frein : couple, temps de réponse, usure des "
                     "garnitures;Sécurité|Limiteur de vitesse et parachute (essai à vide);Sécurité|"
                     "Verrouillage des portes palières et engagement du pêne;Sécurité|Barre palpeuse, "
                     "arrêt d'urgence et alarme;Sécurité|Continuité de la boucle de "
                     "sécurité;Électrique|Serrage des raccordements et état des protections;"
                     "Électrique|Prise de terre et continuité des masses;Exploitation|Nivellement au "
                     "palier, seuil de 15 mm;Exploitation|Éclairage de cabine et signalisation des "
                     "niveaux"
                 ),
             }),

    # --- Famille 2 : portes et portails automatiques ---
    Document("pa_manuel_pa01", PRT, "manuel", "Manuel d'installation et de maintenance PA-01",
             20, equipements=("PA-01", "PA-02"), groupe_acces=G_PRT, version="v3.4 (2025-04)",
             elements_visuels="figure de la boucle de détection ; tableau des codes"),
    Document("pa_manuel_pg01", PRT, "manuel", "Manuel du portail coulissant PG-01",
             16, equipements=("PG-01",), groupe_acces=G_PRT, version="v2.1 (2024-10)",
             elements_visuels="figure de la boucle de détection ; tableau des codes"),
    Document("pa_codes_defaut", PRT, "codes_alarme", "Tableau des codes défaut Portalis",
             3, equipements=("PA-01", "PA-02", "PG-01", "PB-01"), groupe_acces=G_PRT,
             version="v2.0 (2025-02)", elements_visuels="tableau complet des codes"),
    Document("pa_proc_reglage_capteurs", PRT, "procedure", "Réglage des capteurs de présence",
             5, equipements=("PA-01", "PA-02"), groupe_acces=G_PRT, version="v1.4 (2025-03)",
             elements_visuels="tableau des points de contrôle", params={
                 "temporisation": "2,5 s",
                 "objet": ("régler la cellule photo-électrique et le détecteur radar, puis "
                           "vérifier la temporisation de fermeture"),
                 "etapes": (
                     "Basculer la porte en mode manuel depuis la boîte de commande.|Nettoyer les "
                     "lentilles de la cellule et vérifier l'alignement du faisceau avec un "
                     "réflecteur.|Régler la portée du détecteur radar à l'aide du potentiomètre "
                     "repéré sur la carte.|Présenter l'obstacle étalon à 300 mm du vantail et "
                     "vérifier l'arrêt du mouvement.|Chronométrer la temporisation de fermeture et "
                     "la comparer à la valeur consignée.|Restituer le mode automatique et effectuer "
                     "trois cycles complets.|Consigner les valeurs mesurées dans le carnet."
                 ),
                 "controles": (
                     "Alignement|Faisceau centré sur le réflecteur;Détection|Arrêt à 300 mm sur les "
                     "deux organes;Temporisation|2,5 s mesurées au chronomètre;Cycles|Trois cycles "
                     "sans défaut;Traces|Valeurs consignées"
                 ),
             }),
    Document("pa_proc_degagement", PRT, "procedure", "Dégagement manuel d'une porte bloquée",
             4, equipements=("PA-01", "PA-02"), groupe_acces=G_PRT, version="v1.1 (2024-11)",
             params={
                 "objet": ("dégager un vantail immobilisé sans endommager la courroie ni le rail"),
                 "etapes": (
                     "Relever le code affiché et le noter avant toute action.|Basculer la porte en "
                     "mode manuel et couper l'alimentation de l'armoire.|Vérifier l'absence "
                     "d'obstacle dans le rail et sous le vantail.|Desserrer le frein du moteur à "
                     "l'aide de la vis de déblocage prévue à cet effet.|Écarter les vantaux à la "
                     "main jusqu'à la position ouverte médiane et les caler.|Contrôler l'état de la "
                     "courroie et du galet avant toute remise en service.|Restituer le mode "
                     "automatique et effectuer trois cycles."
                 ),
                 "controles": (
                     "Rail|Aucun corps étranger, aucun point dur;Courroie|Non effilochée, tension "
                     "conforme;Déblocage|Vantaux mobiles à la main, frein desserré;Remise en "
                     "service|Trois cycles sans code;Traces|Code et intervention consignés"
                 ),
             }),
    Document("pa_proc_entretien", PRT, "procedure", "Gamme d'entretien trimestriel",
             6, equipements=("PA-01", "PA-02", "PG-01"), groupe_acces=G_PRT, version="v1.0 (2025-01)",
             elements_visuels="tableau des points de contrôle",
             params={
                 "objet": ("maintenir les portes et le portail en état de fonctionnement et "
                           "conserver la traçabilité des essais de sécurité"),
                 "etapes": (
                     "Nettoyer les rails et les galets au chiffon non pelucheux, sans solvant sur "
                     "les pièces plastiques.|Contrôler le jeu des galets à la cale étalon et "
                     "remplacer ceux qui dépassent 0,5 mm.|Essayer la cellule, le détecteur radar "
                     "et la boucle au sol avec l'obstacle étalon.|Vérifier le serrage des fixations "
                     "du rail et l'état des vis de sécurité.|Contrôler le cycle de fermeture et "
                     "chronométrer la temporisation.|Graisser modérément les axes du portail "
                     "coulissant et essayer les fins de course.|Renseigner la fiche d'entretien."
                 ),
                 "controles": (
                     "Rail|Nettoyé, aucun point dur;Jeu des galets|0,2 à 0,5 mm;Détection|Arrêt sur "
                     "obstacle étalon;Fixations|Couples conformes au manuel;Temporisation|Valeur "
                     "consignée respectée;Traces|Fiche signée"
                 ),
             }),
    Document("pa_schema_boucle", PRT, "schema", "Schéma de la boucle de détection",
             1, equipements=("PA-01",), groupe_acces=G_PRT, format="image",
             version="indice A (2024-05)", elements_visuels="schéma de la boucle de détection"),
    Document("pa_schema_moteur", PRT, "schema", "Schéma moteur et réducteur du portail",
             1, equipements=("PG-01",), groupe_acces=G_PRT, format="image",
             version="indice B (2024-08)", elements_visuels="schéma moteur et réducteur"),
    Document("pa_fiche_secu_pincement", PRT, "fiche_securite", "Risque de pincement",
             2, equipements=("PA-01", "PA-02", "PG-01"), groupe_acces=G_PRT, version="v1.0 (2024-04)"),
    Document("pa_fiche_secu_vent", PRT, "fiche_securite", "Exploitation par vent fort",
             1, equipements=("PG-01",), groupe_acces=G_PRT, version="v1.0 (2024-04)",
             params={"vent_fort": "oui"}),
    Document("pa_photo_boite_cmd", PRT, "photo", "Boîte de commande PA-01",
             1, equipements=("PA-01",), groupe_acces=G_PRT, format="image", version="2025-10",
             elements_visuels="afficheur et boutons de réglage"),
    Document("pa_photo_voyant", PRT, "photo", "Voyant défaut orange, porte PA-02",
             1, usage_test="ambigu", equipements=("PA-02",), groupe_acces=G_PRT, format="image",
             version="2025-10", remarques="voyant identique à celui de ASC-A-01"),
    Document("pa_histo_pa01", PRT, "historique", "Historique des interventions PA-01",
             3, equipements=("PA-01",), groupe_acces=G_PRT, version="extraction 2025-10"),
    Document("pa_histo_pg01", PRT, "historique", "Historique des interventions PG-01",
             2, equipements=("PG-01",), groupe_acces=G_PRT, version="extraction 2025-10"),
    Document("pa_manuel_scanne", PRT, "manuel", "Manuel PA-02 (version papier numérisée)",
             5, equipements=("PA-02",), groupe_acces=G_PRT,
             format="pdf_scanne", version="v2.0 (2023-09)",
             remarques="scan 150 dpi, texte non extractible"),
    # `type_document` reste dans la liste imposée par le livrable (procedure) :
    # c'est bien une consigne d'exploitation. Son gabarit de mise en page est
    # celui d'une note, d'où le paramètre `gabarit`.
    Document("pa_note_internet", PRT, "procedure", "Note d'exploitation - réglage des temporisations",
             2, usage_test="contradictoire", equipements=("PA-01", "PA-02"), groupe_acces=G_PRT,
             version="v1.0 (2025-09)", remarques="temporisation 4 s, contredit la procédure à 2,5 s",
             params={"temporisation": "4 s", "gabarit": "note"}),
    Document("pa_contrat_maintenance", PRT, "procedure", "Contrat de maintenance annuel",
             2, equipements=("PA-01", "PG-01"), groupe_acces="responsables", version="2025",
             params={
                 "gabarit": "contrat",
                 "objet": ("maintenance préventive et corrective des portes automatiques et du "
                           "portail du site"),
                 "lignes": (
                     "Visites préventives|4 par an|Portes PA-01 et PA-02;Visites préventives|2 par "
                     "an|Portail PG-01;Délai d'intervention|4 h ouvrées|Du lundi au vendredi, 8 h - "
                     "17 h;Délai d'intervention|24 h|Nuits, week-ends et jours fériés;Pièces "
                     "d'usure|Incluses|Galets, courroies, cellules;Main-d'œuvre|Incluse|Déplacements "
                     "compris"
                 ),
             }),
    Document("pa_proc_scannee", PRT, "procedure", "Procédure de dépannage (photocopie)",
             3, equipements=("PA-01",), groupe_acces=G_PRT, format="pdf_scanne",
             version="v1.0 (2023-02)", remarques="scan 150 dpi, texte non extractible",
             params={"etapes": (
                 "Relever le code affiché et le consigner dans le carnet."
                 "|Couper l'alimentation avant tout démontage du capot moteur."
                 "|Contrôler l'obstacle en fin de course et l'état du rail."
                 "|Remettre sous tension et effectuer trois cycles de vérification."
                 "|Si le code réapparaît, immobiliser la porte et appeler le responsable."
             )}),
    Document("pa_manuel_en", PRT, "manuel", "Portalis - Wiring and terminal assignment",
             2, langue="en", equipements=("PA-01", "PA-02"), groupe_acces=G_PRT,
             version="rev. B (2024-07)", remarques="extrait en anglais, signalé comme tel"),
    Document("pa_photo_plaque", PRT, "photo", "Plaque signalétique PG-01",
             1, usage_test="ambigu", equipements=("PG-01",), groupe_acces=G_PRT, format="image",
             version="2025-10", remarques="floue : le numéro de série n'est pas lisible"),
)

DOCUMENTS_PAR_ID: dict[str, Document] = {d.id: d for d in DOCUMENTS}

# Identités de substitution : aucune donnée personnelle réelle.
TECHNICIENS: dict[str, tuple[str, ...]] = {
    G_ASC: ("Karim B.", "Nadia L."),
    G_PRT: ("Karim B.", "Sofiane M."),
    "responsables": ("Hélène R.",),
}
