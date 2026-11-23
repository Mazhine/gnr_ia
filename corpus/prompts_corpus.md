# Prompts utilisés pour constituer le corpus

Ce fichier est exigé par le livrable 1. Il trace chaque prompt employé pour
chercher ou générer un document du corpus, avec l'outil et la date.

> **Nature de l'outil.** Le corpus n'a pas été écrit par un modèle de langage :
> il est produit par un générateur Python déterministe (`scripts/gen_corpus/`).
> Les prompts ci-dessous sont ceux qui ont piloté l'écriture de ce générateur et
> ses corrections, reproduits depuis l'historique de travail. L'outil employé est
> un assistant de code ; il a servi à écrire et relire du code, jamais à rédiger
> le texte des 40 documents. La colonne `outil_ia` de l'inventaire renvoie donc à
> `P04` (le générateur) pour toutes les lignes.

## Convention

- Les prompts sont numérotés `P01`, `P02`, … dans l'ordre chronologique.
- La colonne `outil_ia` de `inventaire.csv` renvoie à ce numéro.
- Un prompt peut produire plusieurs documents : la colonne `outil_ia` des
  documents concernés porte le même numéro.
- Le champ **Résultat** décrit ce qui a été produit, et le champ **Défauts
  relevés** liste ce qui a dû être corrigé après relecture. Un prompt sans
  défaut relevé est un prompt dont on n'a pas assez cherché les erreurs.

## Format d'une entrée

### P01 — <intitulé court>

- **Date** : AAAA-MM-JJ
- **Outil** : assistant de code
- **Objectif** : ce que le prompt devait produire
- **Prompt** :

```
<texte exact du prompt>
```

- **Documents produits** : `document_id` concernés
- **Résultat** : ce qui a effectivement été obtenu
- **Défauts relevés** : erreurs, incohérences, inventions, à corriger
- **Corrections appliquées** : ce qui a été modifié dans le document final

---

### P01 — Cadrer le corpus et choisir deux familles

- **Date** : 2026-10-28
- **Outil** : assistant de code
- **Objectif** : fixer l'univers documentaire avant d'écrire une ligne de code.
- **Prompt** :

```
Je prépare un corpus de 40 documents de maintenance pour un assistant
multimodal. Contraintes : deux familles d'équipements, 20 documents chacune,
des constructeurs fictifs pour avoir une licence claire, et des cas de test
(normal, contradictoire, ambigu, injection). Propose deux familles peu
utilisées dans les projets étudiants, un univers crédible (un seul site qui
exploite les deux), et les groupes d'accès associés.
```

- **Documents produits** : ensemble du corpus (cadrage)
- **Résultat** : deux familles retenues — ascenseurs/monte-charges
  (constructeur fictif Verticalis) et portes/portails automatiques (Portalis),
  exploitées par un même centre technique de bâtiment.
- **Défauts relevés** : une première proposition partait sur des pompes et des
  compresseurs, jugée trop attendue.
- **Corrections appliquées** : univers remplacé par ascenseurs et portes, avec un
  seul électromécanicien intervenant sur les deux.

### P02 — Construire le catalogue des équipements et des codes

- **Date** : 2026-10-28
- **Outil** : assistant de code
- **Objectif** : une source unique pour les identifiants, les équipements et les
  codes de défaut, afin que les 40 documents restent cohérents.
- **Prompt** :

```
Écris un catalogue Python qui décrit 8 équipements (4 ascenseurs/monte-charges,
4 portes/portails) et 13 codes de défaut par famille. Je veux une collision
volontaire : cinq numéros de code identiques entre les deux constructeurs mais
avec des libellés différents. Le catalogue doit être la seule source des
identifiants et des libellés, pour qu'aucun document ne les recopie à la main.
```

- **Documents produits** : `asc_codes_defaut`, `pa_codes_defaut`, et tous les
  documents qui citent un code.
- **Résultat** : catalogue unique avec collisions sur 12, 33, 42, 51 et 71.
- **Défauts relevés** : la première version ne prévoyait que trois collisions et
  deux codes avaient le même libellé dans les deux familles.
- **Corrections appliquées** : cinq collisions, libellés réellement distincts,
  vérifiés par `verifier.py`.

### P03 — Définir la mise en page des documents

- **Date** : 2026-10-29
- **Outil** : assistant de code
- **Objectif** : une charte commune (page de garde, en-tête, pied de page) et un
  gabarit par type de document.
- **Prompt** :

```
Écris le module de rendu PDF avec reportlab. Une page de garde par document
(marque, référence, version, équipements), un en-tête qui rappelle la marque et
la référence à partir de la page 2, un pied de page « Page X / Y ». Prévois un
gabarit distinct pour le manuel, la procédure, la fiche de sécurité, le tableau
de codes et l'historique. Aucune donnée ne doit être écrite en dur dans le rendu.
```

- **Documents produits** : tous les documents PDF.
- **Résultat** : charte commune et premiers gabarits.
- **Défauts relevés** : les procédures faisaient toutes exactement trois pages,
  avec la même suite d'étapes génériques.
- **Corrections appliquées** : contenu propre à chaque procédure (voir P08).

### P04 — Écrire le générateur Python déterministe

- **Date** : 2026-10-30
- **Outil** : assistant de code
- **Objectif** : générer les 40 documents et leurs images sans aucun aléa, pour
  que deux générations produisent des fichiers identiques.
- **Prompt** :

```
Écris le point d'entrée du générateur : `python -m scripts.gen_corpus` produit
les 40 documents et les images, `--only` en produit un, `--clean` repart de
zéro. Le rendu doit être déterministe (pas de graine aléatoire à conserver). Une
génération partielle ne doit pas réécrire l'inventaire, sinon il annoncerait des
fichiers absents. Chaque image passe par un registre explicite : une faute de
frappe doit échouer, pas produire une image générique.
```

- **Documents produits** : les 40 documents et les 10 images.
- **Résultat** : générateur déterministe, 40 documents, 100 pages.
- **Défauts relevés** : deux fichiers Python avaient reçu un BOM UTF-8 lors d'une
  édition précédente, ce qui cassait l'import ; les PDF scannés ressemblaient à
  des PDF vectoriels.
- **Corrections appliquées** : BOM retiré, scans retravaillés (voir P10).

### P05 — Générer les images : photos, plaques, schémas

- **Date** : 2026-10-30
- **Outil** : assistant de code
- **Objectif** : produire des images crédibles avec Pillow, dont une plaque
  volontairement illisible.
- **Prompt** :

```
Génère les images du corpus avec Pillow : panneaux de commande, armoire
électrique, plaques signalétiques et schémas. La plaque de ASC-A-01 doit être
illisible (numéro de série non déchiffrable) mais laisser reconnaître le
constructeur. Les schémas doivent être lisibles et cohérents : chaque composant
alimenté doit avoir une sortie.
```

- **Documents produits** : `asc_schema_armoire`, `asc_schema_boucle_secu`,
  `pa_schema_boucle`, `pa_schema_moteur`, `asc_photo_*`, `pa_photo_*`.
- **Résultat** : 10 images générées.
- **Défauts relevés** : un simple flou gaussien laissait le numéro de série
  lisible ; le transformateur 48 V du schéma d'armoire n'avait aucune sortie.
- **Corrections appliquées** : réduction à 260 px puis flou et remontée
  (le détail fin disparaît, les traits larges restent) ; liaison de sortie du
  transformateur ajoutée.

### P06 — Écrire l'inventaire par mesure, pas par recopie

- **Date** : 2026-10-31
- **Outil** : assistant de code
- **Objectif** : produire les 20 colonnes imposées en mesurant les fichiers.
- **Prompt** :

```
Écris l'écriture de `corpus/inventaire.csv` avec exactement les 20 colonnes du
livrable. Interdiction de recopier `nb_pages` et `elements_visuels` du catalogue :
mesure-les sur le PDF produit (pymupdf), juste après le rendu. Écris le CSV en
UTF-8 avec BOM pour qu'Excel n'affiche pas de caractères cassés, et lis-le en
utf-8-sig dans le vérificateur.
```

- **Documents produits** : `corpus/inventaire.csv`.
- **Résultat** : 40 lignes, 20 colonnes, valeurs mesurées.
- **Défauts relevés** : la première version publiait les cibles de planification
  du catalogue (24, 18, 8 pages) au lieu des pages réelles.
- **Corrections appliquées** : mesure systématique ; les cibles restent dans le
  catalogue comme objectifs de conception, documentées comme telles.

### P07 — Écrire le vérificateur automatique

- **Date** : 2026-10-31
- **Outil** : assistant de code
- **Objectif** : un contrôle qui échoue vraiment quand le corpus est faux.
- **Prompt** :

```
Écris `verifier.py` : il relit les fichiers produits, pas le catalogue. Contrôle
l'en-tête et le nombre de lignes de l'inventaire, l'absence d'orphelins, la
concordance des mesures, les quotas du sujet (30–50 documents, deux familles,
5 types, 10 documents avec éléments visuels, 2 scans, 2 contradictions, 1
injection), les collisions de codes, la marque par famille, la charge
d'injection, les langues et les extensions. Code de retour non nul si un
contrôle échoue.
```

- **Documents produits** : `scripts/gen_corpus/verifier.py`.
- **Résultat** : 11 contrôles, tous verts sur le corpus final.
- **Défauts relevés** : le contrôle des scans comptait un `usage_test` inventé
  (`scanne`) au lieu du format ; le contrôle des types acceptait `note`.
- **Corrections appliquées** : contrôle par `format == "pdf_scanne"` et
  appartenance des types et des usages aux listes imposées.

### P08 — Donner un contenu propre à chaque procédure

- **Date** : 2026-11-02
- **Outil** : assistant de code
- **Objectif** : casser l'uniformité des procédures génériques.
- **Prompt** :

```
Les procédures font toutes trois pages et racontent la même chose. Donne à
chacune son objet, ses étapes et ses points de contrôle, portés par le catalogue
et non par le rendu. Les prérequis doivent différer entre ascenseurs et portes.
Pas de saut de page forcé qui laisse une demi-page blanche.
```

- **Documents produits** : `asc_proc_consignation`, `asc_proc_deblocage`,
  `asc_proc_entretien_mensuel`, `pa_proc_reglage_capteurs`,
  `pa_proc_degagement`, `pa_proc_entretien`.
- **Résultat** : chaque procédure a ses étapes, ses contrôles et ses prérequis.
- **Défauts relevés** : le saut de page avant les points de contrôle produisait
  une page presque vide en fin de document.
- **Corrections appliquées** : saut de page retiré ; le tableau suit le texte et
  se coupe proprement, en-tête répété.

### P09 — Ajouter une fiche de contrôle et un contrat

- **Date** : 2026-11-02
- **Outil** : assistant de code
- **Objectif** : deux documents qui ne sont pas des modes opératoires.
- **Prompt** :

```
Ajoute une fiche de contrôle périodique à remplir sur site (cases C/NC,
observations, signature) et un contrat de maintenance (parties, prestations,
obligations, résiliation). Le type imposé reste `procedure` ; choisis la mise en
page par un paramètre `gabarit`, pas par une déduction sur le nom du fichier.
```

- **Documents produits** : `asc_controle_periodique`, `pa_contrat_maintenance`.
- **Résultat** : formulaire de contrôle et contrat paginés correctement.
- **Défauts relevés** : la case à cocher utilisait un caractère absent de la
  police Helvetica ; le formulaire annonçait une case S qui n'existait pas.
- **Corrections appliquées** : case dessinée par la grille du tableau, mention S
  retirée.

### P10 — Corriger les défauts trouvés à la relecture visuelle

- **Date** : 2026-11-03
- **Outil** : assistant de code
- **Objectif** : corriger ce que seule l'ouverture des fichiers révèle.
- **Prompt** :

```
Voici les défauts constatés en ouvrant les PDF : les scans ressemblent à des PDF
vectoriels, la plaque « illisible » est lisible, l'extrait anglais a un
paragraphe orphelin sur une page vide, la note d'exploitation répète son titre.
Corrige le générateur, régénère, et vérifie le résultat sur les pages concernées.
```

- **Documents produits** : `asc_proc_scannee`, `pa_manuel_scanne`,
  `pa_proc_scannee`, `asc_photo_plaque`, `pa_photo_plaque`, `asc_manuel_en`,
  `pa_manuel_en`, `pa_note_internet`.
- **Résultat** : défauts corrigés et revérifiés visuellement.
- **Défauts relevés** : Pillow de l'environnement n'a pas d'encodeur PNG, et
  reconstruire un `Pixmap` depuis des octets bruts échoue selon les versions.
- **Corrections appliquées** : écriture directe dans `pixmap.samples_mv[:]` ;
  gris de papier, flou léger et vignette déterministe pour les scans.

### P11 — Aligner les énumérations sur la consigne

- **Date** : 2026-11-04
- **Outil** : assistant de code
- **Objectif** : supprimer les valeurs inventées dans l'inventaire.
- **Prompt** :

```
Relis la consigne du livrable 1 : les valeurs autorisées de `type_document` et
`usage_test`. Supprime toute valeur inventée. Le scan est un format, pas un rôle
de test. Vérifie que le vérificateur refuse désormais une valeur hors liste.
```

- **Documents produits** : `asc_proc_scannee`, `pa_manuel_scanne`,
  `pa_proc_scannee`, `pa_note_internet`.
- **Résultat** : `usage_test` limité à normal/contradictoire/injection/ambigu,
  `type_document` limité aux sept valeurs imposées.
- **Défauts relevés** : trois documents portaient `scanne`, un portait `note`.
- **Corrections appliquées** : scans repassés en `normal`, note retypée
  `procedure` avec `gabarit = note`.

### P12 — Tenir le journal des corrections et préparer la relecture

- **Date** : 2026-11-05
- **Outil** : assistant de code
- **Objectif** : garder la trace honnête de ce qui a été corrigé et de ce qui
  reste à relire par un humain.
- **Prompt** :

```
Rédige le journal des corrections avec, pour chaque défaut, le symptôme, la
cause, la correction et la preuve. Prépare aussi une liste d'assertions
vérifiables pour la relecture humaine des documents critiques. N'écris jamais
« vérifié par » pour un document que je n'ai pas ouvert.
```

- **Documents produits** : `docs/livrable-1/journal-corrections.md`,
  `docs/livrable-1/protocole-relecture.md`.
- **Résultat** : journal et protocole de relecture.
- **Défauts relevés** : la première version du protocole citait des pages
  (p. 4, p. 11) qui n'existent pas dans un manuel de 7 pages.
- **Corrections appliquées** : assertions recalées sur les pages réellement
  produites.
