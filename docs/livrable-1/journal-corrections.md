# Journal des corrections du corpus

Ce journal ne liste pas des finitions. Il liste les défauts qui rendaient un
document faux, illisible ou non conforme, et qui ont été trouvés **en relisant
le fichier produit**, pas en relisant le code. C'est la pièce qui justifie la
colonne `corrections` de l'inventaire et l'usage critique de l'IA demandé par la
grille d'évaluation.

Chaque entrée suit le même plan : symptôme observé, cause, correction, preuve
que la correction tient. Les identifiants renvoient aux lignes de
`corpus/inventaire.csv`.

## Défauts de rendu

### `asc_photo_plaque`, `pa_photo_plaque` — la plaque « illisible » restait lisible

**Symptôme.** Les deux photos étaient déclarées `ambigu` avec une plaque dont le
numéro de série devait être illisible. À l'écran, un flou gaussien seul laissait
les lettres et les chiffres parfaitement déchiffrables : le document affirmait
une chose que l'image démentait.

**Cause.** Un flou gaussien conserve la forme des caractères ; il baisse le
contraste local sans détruire l'information. Une vraie photo prise au téléphone
puis compressée perd d'abord les détails fins, pas la netteté globale.

**Correction.** La plaque est d'abord réduite à 260 px de large, floutée à
1,2 px, puis agrandie à sa taille finale (interpolation bicubique). Les traits
larges (le nom du constructeur) survivent, les caractères fins (le numéro de
série) disparaissent. `pa_photo_plaque` était en plus rendue nette : elle est
désormais dégradée comme `asc_photo_plaque`.

**Preuve.** Les deux images ont été réexaminées sur une planche de contrôle ; le
numéro de série n'y est plus lisible, le constructeur reste identifiable.
`verifier.py` ne peut pas juger de la lisibilité d'une image, c'est pourquoi ce
contrôle est visuel et consigné ici.

### `asc_schema_armoire` — un transformateur sans sortie

**Symptôme.** Sur le schéma de l'armoire, le transformateur 48 V était alimenté
mais aucun conducteur ne partait de sa sortie : le schéma montrait un composant
qui ne sert à rien.

**Cause.** Une ligne de liaison manquait entre la sortie du transformateur et la
rangée de relais.

**Correction.** Ajout du trait `(350, 495, 420, 495)`. Le 48 V alimente désormais
le relais de sécurité, l'automate et le chargeur de batterie.

**Preuve.** Vue zoomée du schéma régénérée ; la continuité est visible.

### `pa_note_internet` — le titre affiché deux fois

**Symptôme.** La page 1 affichait « NOTE D'EXPLOITATION » puis, juste en dessous,
le titre complet du document, qui répétait la même information.

**Cause.** Le gabarit « note » insérait le bandeau et le titre du catalogue sans
distinguer les deux niveaux.

**Correction.** Le titre de niveau 1 devient « Réglage des temporisations de
fermeture », le bandeau garde « NOTE D'EXPLOITATION ». Le titre du catalogue
reste, lui, la valeur publiée dans l'inventaire.

### `asc_manuel_en` — un paragraphe orphelin sur une page presque vide

**Symptôme.** L'extrait anglais faisait deux pages, mais la page 2 ne contenait
qu'un paragraphe « 3. Remarks » isolé, le reste étant blanc.

**Cause.** Aucune coupure n'était forcée après le bloc de couverture ; le dernier
paragraphe débordait seul.

**Correction.** `PageBreak()` après le bloc de titre. La page 1 porte la marque et
l'avertissement, la page 2 le contenu. Même traitement pour `pa_manuel_en`.

### Scans — un PDF « scanné » qui ressemblait à un PDF vectoriel

**Symptôme.** Les trois documents `pdf_scanne` n'avaient plus de texte
extractible (le contrôle passait), mais visuellement rien ne les distinguait d'un
PDF normal : ni grain, ni gris de papier, ni ombre de bord. À l'oral, cela se voit
immédiatement.

**Correction.** `scanner()` applique désormais un gris de papier
(`0.90 × niveau + 10`), un léger flou (0,5 px), une vignette radiale
déterministe, un grain de capteur tiré d'une graine fixe et un travers de
feuille de 0,4°. Le résultat est identique à chaque génération, sans tirage
aléatoire.

**Note technique.** Pillow de cet environnement n'a pas d'encodeur PNG et
`pymupdf.Pixmap(...)` échoue à partir d'octets bruts ; les échantillons sont donc
réécrits dans `pixmap.samples_mv[:]`. C'est laid mais stable, et documenté dans le
code.

### `asc_schema_boucle_secu`, `pa_schema_boucle` — une chaîne de sécurité coupée

**Symptôme.** Les deux schémas de boucle affirmaient, en légende, que « tous les
contacts sont en série », mais la liaison entre le troisième bloc (barre
palpeuse, ou boucle au sol) et l'arrêt d'urgence n'était pas tracée. La chaîne se
lisait donc en deux morceaux : le schéma contredisait sa propre légende.

**Cause.** La boucle de dessin sautait explicitement la liaison d'indice 2,
probablement pour éviter un tracé qui semblait encombré. La géométrie laissait
pourtant 80 px entre les deux blocs.

**Correction.** La liaison est rétablie ; le tracé se lit maintenant d'un seul
trait, puis redescend vers le relais de sécurité et revient vers le moteur.

**Preuve.** Les deux images ont été réexaminées après régénération ; la flèche
manquante est visible et la continuité est complète.

## Défauts de conformité aux consignes

### `usage_test = "scanne"` — une valeur inventée

**Symptôme.** Trois documents portaient `scanne` dans `usage_test`. Cette valeur
n'existe pas dans la consigne, qui fixe quatre rôles de test : `normal`,
`contradictoire`, `injection`, `ambigu`.

**Cause.** Confusion entre le **format** (PDF image, OCR requis) et le **rôle de
test**. Le scan est une propriété de fichier, pas un cas de test.

**Correction.** Les trois documents repassent en `normal` ; leur format reste
`pdf_scanne` et le contrôle « Scans » compte bien 3 fichiers sans texte
extractible. `verifier.py` refuse désormais toute valeur hors des quatre rôles
imposés.

### `pa_note_internet` — un type de document inexistant

**Symptôme.** Le document était typé `note`, valeur absente de la liste imposée
par le livrable (manuel, procedure, fiche_securite, schema, codes_alarme, photo,
historique).

**Correction.** `type_document = "procedure"` (c'est bien une consigne
d'exploitation) et `params["gabarit"] = "note"` pour conserver la mise en page
d'une note. Le type reste dans le vocabulaire imposé, la forme reste juste.
`verifier.py` contrôle l'appartenance des sept types.

## Défauts de contenu trouvés plus tôt

Ces corrections ont été faites lors d'une passe antérieure ; elles restent dans
la colonne `corrections` de l'inventaire.

| Document | Correction |
|---|---|
| `asc_manuel_en`, `pa_manuel_en` | première version rédigée en français, réécrite en anglais |
| `asc_manuel_mc` | caractéristiques du monte-charge erronées (2 niveaux, 0,5 m/s) |
| `asc_manuel_a_v2` | la v2.0 n'indiquait pas la valeur qu'elle remplace |
| `asc_histo_b_2025` | journal identique à celui de ASC-A-01, différencié |
| `pa_histo_pg01` | journal adapté aux portes (pas de pêne de serrure) |
| `pa_fiche_secu_vent` | section vent fort absente, seuils 60 et 90 km/h ajoutés |
| `asc_photo_boite_cabine` | tous les voyants allumés, seuls défaut et service le sont |
| `asc_photo_armoire` | légende des LED absente, document reclassé `ambigu` |

## Ce que la vérification automatique ne couvre pas

`verifier.py` contrôle la structure : nombre de lignes, enums, extensions,
présence de la charge d'injection, cohérence des codes. Il ne juge ni la
lisibilité d'une image, ni la crédibilité d'une phrase. Ces deux contrôles
restent manuels et sont la raison d'être de la relecture humaine décrite dans
`protocole-relecture.md`.
