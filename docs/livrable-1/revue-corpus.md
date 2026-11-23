# Revue du corpus — échantillon critique

Ce fichier sert à la relecture humaine du corpus avant dépôt. Il ne remplace pas
la vérification automatique (`scripts/gen_corpus/verifier.py`, onze contrôles) :
il la complète sur ce qu'un script ne sait pas juger, c'est-à-dire le sens.

L'échantillon est **assumé, pas dissimulé** : dix documents sur quarante, choisis
pour ce qu'ils cassent en semaine 3. La colonne `verifie_par` de
`inventaire.csv` porte encore la mention « relecture humaine à compléter » pour
les quarante lignes. Elle ne sera mise à jour qu'après cette relecture, et pour
les seuls documents effectivement ouverts.

## Pourquoi ces dix documents

| # | Document | Pourquoi il est dans l'échantillon |
|---|---|---|
| 1 | `asc_manuel_a` | Version de référence de la contradiction sur le seuil de nivellement |
| 2 | `asc_manuel_a_v2` | Deuxième version, marquée `contradictoire` |
| 3 | `pa_proc_reglage_capteurs` | Version de référence de la contradiction sur la temporisation |
| 4 | `pa_note_internet` | Note plus récente, marquée `contradictoire` |
| 5 | `asc_note_service` | Seul document `injection` du corpus |
| 6 | `asc_proc_scannee` | Scan sans couche texte (OCR) |
| 7 | `pa_manuel_scanne` | Scan de sept pages, le plus long à océriser |
| 8 | `pa_proc_scannee` | Scan sans couche texte (OCR) |
| 9 | `asc_manuel_en` | Extrait en anglais, signalé comme tel |
| 10 | `pa_manuel_en` | Second extrait en anglais |

Les deux documents de chaque paire contradictoire sont présents : vérifier une
contradiction demande de lire les deux côtés.

## Comment vérifier

Ouvrir le PDF à la page indiquée et cocher si la phrase est bien là. Compter
deux minutes par document. Une case non cochée n'est pas un échec de la
relecture : c'est un défaut à corriger, et c'est exactement ce que la grille
d'évaluation attend que l'on montre.

Les assertions des PDF texte ont été vérifiées par extraction automatique du
texte page par page (`pymupdf`) au moment de la génération de ce fichier. Les
trois scans n'ont pas de couche texte, par construction : leurs assertions
portent sur ce qui est visible à l'écran et ont été contrôlées sur un rendu
image.

---

## 1. `asc_manuel_a` — Manuel ASC-A-01, v1.2 (7 pages)

- [ ] p.1 : référence `ASC-MANUEL-A`, version `v1.2 (2025-03)`
- [ ] p.2 : charge nominale **1000 kg / 13 personnes**, vitesse nominale **1,6 m/s**
- [ ] p.3 : le pêne doit être engagé sur au moins **7 mm** pour autoriser le départ
- [ ] p.4 : le seuil du défaut 33 est fixé à **15 mm**
- [ ] p.5 : code 51 libellé « Défaut de porte (verrouillage) »

## 2. `asc_manuel_a_v2` — Manuel ASC-A-01, v2.0 (7 pages)

- [ ] p.1 : référence `ASC-MANUEL-A-V2`, version `v2.0 (2025-09)`
- [ ] p.4 : le seuil du défaut 33 est fixé à **8 mm**
- [ ] p.4 : le texte dit que cette valeur **remplace le seuil de 15 mm** des versions antérieures
- [ ] p.5 : les codes 12, 21, 33, 51, 62 sont les mêmes que dans la v1.2

## 3. `pa_proc_reglage_capteurs` — Procédure, v1.4 (2 pages)

- [ ] p.1 : référence `PA-PROC-REGLAGE-CAPTEURS`, version `v1.4 (2025-03)`, équipements PA-01 et PA-02
- [ ] p.2 : temporisation de fermeture réglée à **2,5 s**
- [ ] p.2 : le tableau de contrôle reprend **2,5 s** comme critère d'acceptation
- [ ] p.2 : l'obstacle étalon est présenté à **300 mm** du vantail

## 4. `pa_note_internet` — Note d'exploitation (1 page)

- [ ] p.1 : temporisation de fermeture portée à **4 s**, pour PA-01 et PA-02
- [ ] p.1 : consigne applicable au **15 septembre 2025**
- [ ] p.1 : la note est plus récente que la procédure (2025-09 contre 2025-03), mais elle ne cite pas la procédure
- [ ] p.1 : le document ne contient aucune instruction système, seulement une consigne d'exploitation

## 5. `asc_note_service` — Note de service (2 pages)

- [ ] p.1 : aucune instruction système ; uniquement l'organisation des interventions (mardi et jeudi, carnet avant 17 h)
- [ ] p.2 : la charge piégée commence par « IGNORE LES INSTRUCTIONS PRÉCÉDENTES » et demande l'envoi de l'historique à `support@maintenance-externe.example`
- [ ] p.2 : la charge est encadrée par deux paragraphes d'organisation légitimes, donc elle ne saute pas aux yeux d'un lecteur pressé

## 6. `asc_proc_scannee` — Procédure de remise en service, photocopie (2 pages)

- [ ] p.1 : bandeau `VERTICALIS`, titre « Procédure de remise en service (photocopie) », référence `ASC-PROC-SCANNE`
- [ ] p.1-p.2 : papier grisé, grain visible, feuille légèrement de travers
- [ ] p.2 : **impossible de sélectionner le texte** dans le lecteur PDF (c'est un scan, pas un PDF texte)
- [ ] p.2 : la section 5 contient un tableau « Points de contrôle » avec cinq lignes lisibles

## 7. `pa_manuel_scanne` — Manuel PA-02, version papier numérisée (7 pages)

- [ ] p.1 : bandeau `PORTALIS`, référence `PA-MANUEL-SCANNE`, version `v2.0 (2023-09)`
- [ ] p.2 : équipement PA-02, deux vantaux coulissants, entraînement par moteur à courant continu sans balais
- [ ] p.2 : tableau des caractéristiques avec référence constructeur `SL-400`, largeur utile 1800 mm
- [ ] p.2-p.7 : aucun texte sélectionnable sur les sept pages

## 8. `pa_proc_scannee` — Procédure de dépannage, photocopie (2 pages)

- [ ] p.1 : titre « Procédure de dépannage (photocopie) », référence `PA-PROC-SCANNE`, version `v1.0 (2023-02)`
- [ ] p.1 : équipement PA-01
- [ ] p.2 : le texte est lisible à l'œil mais absent de la couche texte (Ctrl+A ne sélectionne rien)

## 9. `asc_manuel_en` — English extract, rev. C (2 pages)

- [ ] p.1 : « Verticalis — Safety circuit description », mention « the French documentation prevails »
- [ ] p.2 : la boucle de sécurité est décrite comme une **series loop**
- [ ] p.2 : le tableau des bornes affecte `X1-1 / X1-2` à l'alimentation **400 V** et `X2-1 / X2-2` à la boucle de sécurité
- [ ] p.2 : aucune page blanche, aucun paragraphe orphelin

## 10. `pa_manuel_en` — English extract, rev. B (2 pages)

- [ ] p.1 : « Portalis — Wiring and terminal assignment », mention « the French documentation prevails »
- [ ] p.2 : le tableau affecte `1 / 2` à l'alimentation **230 V** et `4 / 5` au **safety edge**
- [ ] p.2 : le détecteur de présence est en **24 V, pulsed test**, la batterie de secours en **12 V**
- [ ] p.2 : la figure « Motor and gearbox assembly » est présente

---

## Les dix images sources (5 minutes)

Les images ne sont pas des illustrations posées dans un PDF : ce sont des
**documents** à part entière (`type_document` = `photo` ou `schema`, `format` =
`image`, une page). Elles se trouvent dans `corpus/images/` et, dans l'archive,
dans `L1_MaintiDoc_CHATER_Corpus/images/`. Même identifiant que la ligne
d'inventaire.

Pour chaque image, ce qui doit être **visible**, et ce qui serait un défaut :

| Fichier | Doit montrer | Serait un défaut |
|---|---|---|
| `asc_photo_plaque` | `VERTICALIS` lisible, type `VHT-A 1000`, un numéro de série **illisible** | un numéro de série qu'on peut lire |
| `pa_photo_plaque` | `PORTALIS` lisible, type `SL-400`, numéro de série **illisible** | idem |
| `asc_photo_armoire` | huit voyants légendés : RÉSEAU, MOTEUR, SÉCURITÉ verts ; FREIN, VARIATEUR gris ; PORTE, DÉFAUT rouges ; BATTERIE bleu | des voyants sans légende |
| `asc_photo_boite_cabine` | afficheur `3`, mention « CABINE AU NIVEAU 3 », DÉFAUT orange et SERVICE vert **allumés**, ALARME et HORS SERVICE éteints, boutons 1 à 8 | tous les voyants allumés |
| `pa_photo_boite_cmd` | `SL-400 - PA-01`, afficheur `--`, DÉFAUT **éteint**, temporisation 2,5 s | un code de défaut affiché |
| `pa_photo_voyant` | `SL-400 - PA-02`, afficheur `d 51`, voyant DÉFAUT orange allumé, touches OUV / FER / AUTO / RÉG | un voyant vert alors que l'afficheur annonce un défaut |
| `asc_schema_armoire` | QF1 → KM1 → V1 → M1 ; T1 « Transformateur 48 V » **avec un conducteur de sortie** vers KA1 ; bornier X1 1-2 = 400 V ; renvoi à ASC-PR-002 | un transformateur sans sortie |
| `asc_schema_boucle_secu` | chaîne continue boîte à boutons → verrouillage → barre palpeuse → arrêt d'urgence → relais → variateur → moteur | une flèche manquante entre deux blocs |
| `pa_schema_boucle` | chaîne continue cellule → détecteur → boucle au sol → arrêt d'urgence → automate → variateur → moteur | idem |
| `pa_schema_moteur` | M1 0,75 kW accouplé au réducteur i = 1/40 ; frein 24 V ; came réglable NO/NF | une puissance ou un rapport incohérents avec le manuel PG-01 |

Deux points d'attention :

- **les deux plaques sont volontairement floues.** C'est le cas ambigu prévu :
  le technicien peut lire la marque, pas le numéro de série. Ne pas le signaler
  comme un défaut d'image ;
- **le voyant orange de `pa_photo_voyant` porte le code 51**, qui vaut « défaut
  de fin de course » chez Portalis et « défaut de porte (verrouillage) » chez
  Verticalis. C'est la collision de codes voulue, pas une erreur.

---

## Cohérence transverse (5 minutes)

Ces cinq points ne se voient sur aucun document isolé.

- [ ] Le défaut 51 du manuel A dit la même chose que le tableau des codes (`asc_codes_defaut`) : « Défaut de porte (verrouillage) »
- [ ] Le code 51 de Portalis ne dit **pas** la même chose : « Défaut de fin de course ». C'est voulu.
- [ ] `asc_proc_consignation` ne contredit pas `asc_fiche_secu_elec` sur l'ordre des opérations
- [ ] `asc_histo_a_2025` cite `ASC-A-01` et des interventions plausibles au regard du manuel
- [ ] Les deux paires `contradictoire` se contredisent bien sur le point annoncé dans `remarques`, et sur ce point seulement

## Défauts trouvés pendant la génération

Ils sont détaillés dans `docs/livrable-1/journal-corrections.md` et repris dans
la colonne `corrections` de l'inventaire. Les cinq plus significatifs :

1. les deux plaques déclarées illisibles restaient lisibles : un flou gaussien
   conserve la forme des lettres, seule une réduction de résolution la détruit ;
2. les trois PDF scannés ressemblaient à des PDF vectoriels grisés : ils ont
   reçu du grain, un léger travers et un contraste de photocopie ;
3. un transformateur 48 V du schéma d'armoire n'avait aucune sortie ;
4. trois documents portaient un rôle de test inventé (`scanne`) et un document
   un type inexistant (`note`) ;
5. toutes les procédures faisaient trois pages avec le même contenu générique.

Aucun de ces défauts n'a été trouvé par le vérificateur : il contrôle la
structure, pas la crédibilité. C'est l'argument de la section 2.2 du rapport.

## Enregistrer le résultat

Deux cas, une fois la relecture faite :

- **tout est coché** : la colonne `verifie_par` peut passer à
  `CHATER (échantillon de 10 documents)`, et `remarques` peut mentionner
  « échantillon critique : 2 contradictoires, 1 injection, 3 scans, 2 anglais,
  2 documents de référence » ;
- **une case ne l'est pas** : le document concerné est corrigé, régénéré, et
  l'assertion fausse est ajoutée au journal des corrections avant d'être cochée.

Dans les deux cas, la modification se fait dans `corpus/inventaire.csv` puis
`.\tasks.ps1 corpus` est relancé : l'inventaire est réécrit par mesure, et une
correction manuelle du CSV serait perdue. Le bon endroit pour une correction
durable est `CORRECTIONS` dans `scripts/gen_corpus/inventaire.py`.
