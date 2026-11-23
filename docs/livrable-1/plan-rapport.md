# Livrable 1 — plan du rapport et correspondance avec la grille

Le L1 n'est pas un rapport de projet classique : c'est un **dossier de cadrage
figé avant le code**. La grille donne 5 points sur 20 au corpus et 4 à
l'architecture ; ce sont les deux endroits où il faut mettre le temps.

## Contraintes à respecter à la lettre

| Contrainte | Valeur |
|---|---|
| Format | PDF, 10 à 15 pages hors annexes, en français |
| Parties | six, dans l'ordre imposé (2.1 à 2.6) |
| Archive | `L1_MaintiDoc_<NomEquipe>.zip` |
| Dossier racine | `L1_MaintiDoc_<NomEquipe>/` |
| Rapport | `L1_MaintiDoc_<NomEquipe>_Rapport.pdf` |
| Lien dépôt | `L1_MaintiDoc_<NomEquipe>_LienGitHub.txt` (une ligne) |
| README | `README.md` (une page) |
| Corpus | `L1_MaintiDoc_<NomEquipe>_Corpus/` |
| Équipe | 1 à 3 personnes, composition déclarée dans le rapport |

---

## Répartition des pages

| Partie | Pages | Points |
|---|---|---|
| Page de garde + sommaire | 1 | — |
| 2.1 Cadrage | 3 | 3 |
| 2.2 Corpus | 4 | 5 |
| 2.3 Architecture cible | 3 | 4 |
| 2.4 Flux et modèle d'accès | 2 | 2 |
| 2.5 Analyse des risques | 1,5 | 2 |
| 2.6 Planning et rôles | 1 | 1 |
| **Total** | **15,5 → à resserrer à 14** | **17** (+3 présentation) |

Annexes, hors décompte : inventaire complet, prompts, sources des diagrammes,
arborescence du dépôt.

---

## 2.1 — Cadrage (3 pages)

**Contexte et utilisateurs.** Deux profils seulement, décrits par ce qu'ils font
et non par des adjectifs : le technicien d'intervention (sur le terrain, une
photo, une question courte, pas le temps de lire 100 pages de documentation) et
le responsable de maintenance (arbitre, ouvre les tickets, a besoin de la trace
documentaire).

**Quatre cas d'usage** — chacun doit pouvoir être rejoué en démonstration :

| # | Cas d'usage | Ce qui le rend vérifiable |
|---|---|---|
| U1 | Identifier un voyant orange à partir d'une photo du panneau | La réponse doit citer la page et la figure du manuel de la bonne famille |
| U2 | Retrouver la procédure de remise en service après un défaut thermique | La procédure citée doit correspondre à l'équipement, pas à l'équipement voisin |
| U3 | Consulter l'historique d'une pompe avant d'intervenir | L'appel MCP doit renvoyer l'historique du bon `equipement_id` |
| U4 | Préparer un ticket puis le créer après approbation | Aucune création sans jeton d'approbation valide |

Un cinquième cas, celui qui fait la différence à l'oral : **U5 — photo
illisible ou équipement non identifiable**. Le système doit demander une
précision, pas inventer.

**Objectifs vérifiables.** Formulés au futur et testables, pas en pourcentage
avant la semaine 5 :

- citer la page et l'élément exacts pour toute affirmation documentaire ;
- refuser l'accès à un document d'un autre groupe, y compris par URL directe ;
- ne créer aucun ticket sans approbation explicite liée au contenu approuvé ;
- demander une clarification plutôt que répondre quand la source manque ;
- distinguer une alarme de température d'un voyant similaire d'un autre
  équipement.

**Périmètre / hors-périmètre.** Reprendre le tableau du cahier des charges, plus
la ligne qui compte : le système *ne pilote aucun équipement*.

**Hypothèses et contraintes.** Machine réelle : RTX 5060 Laptop, 8 Go. Un modèle
7B n'y tient pas, d'où un 4B quantifié — c'est un fait mesuré, pas une
préférence. Travail individuel dans la limite des 1 à 3 personnes autorisées.

---

## 2.2 — Corpus (4 pages) — **le poste le plus lourd, 5 points**

**Méthode.** Génération par script déterministe, avec prompts tracés dans
`prompts_corpus.md`. Aucun document récupéré sur le web : c'est le seul moyen
d'avoir une licence claire et un contenu cohérent entre manuels, schémas et
codes d'alarme. La cohérence des identifiants est explicitement attendue.

**Ce que le tableau de synthèse doit montrer d'un coup d'œil :**

| Exigence du sujet | Cible |
|---|---|
| Documents | 40 (fourchette 30–50) |
| Familles | 2, environ 20 chacune |
| Types | manuel, procédure, fiche de sécurité, schéma, codes d'alarme, photo, historique |
| Documents avec éléments visuels | ≥ 10, cible 28 |
| Documents scannés (OCR) | ≥ 2, cible 3 |
| Langue | français, 2 documents en anglais signalés |
| Contradictoires | 2 minimum |
| Piégé (injection) | 1 minimum |
| Ambigu | 5 (voyants proches, plaque illisible) |

**Traçabilité.** Chaque ligne de `inventaire.csv` porte provenance, licence,
outil, numéro de prompt, relecteur et corrections. Les prompts sont dans
`prompts_corpus.md`, numérotés P01…

**Analyse critique (½ page, notée).** C'est la partie que les étudiants bâclent.
Elle doit nommer des erreurs précises et leur correction :

- unités de pression incohérentes entre deux pages d'un même manuel ;
- un renvoi de page qui pointe vers une figure inexistante ;
- un code d'alarme réutilisé pour deux défauts différents ;
- une procédure qui contredit la fiche de sécurité sur l'ordre de consignation.

Chaque défaut cité doit être réellement présent dans les documents **avant**
correction, et réellement corrigé ensuite. C'est vérifiable en comparant le
prompt et le document final.

---

## 2.3 — Architecture cible (3 pages) — 4 points

**Schéma à sept blocs**, avec les flèches qui portent le nom de ce qui circule :

```
Interface web  ──question + photo──▶  API  ──requête authentifiée──▶  Orchestration
                                                                          │
        ┌─────────────────────────────────────────────────────────────────┤
        ▼                         ▼                                       ▼
  Recherche documentaire     Modèle vision-langage                 Client MCP
  (texte + images)           (description, analyse)                      │
        │                         │                                       ▼
        └──────────▶ contexte ◀───┘                          Serveur MCP (historique, tickets)
                          │                                              ▲
                          ▼                                              │
                  Vérification des citations ──▶ réponse / clarification / ticket
                                                                         │
                                                            approbation humaine ──┘
```

**Fiche par bloc** : rôle en une phrase, entrées, sorties, outil envisagé.
Sept lignes de tableau, pas sept paragraphes.

**Points de contrôle à placer explicitement sur le schéma** — c'est noté :

1. contrôle d'accès avant la recherche (jamais après) ;
2. vérification que chaque citation existe et soutient l'affirmation ;
3. interruption pour approbation humaine avant tout appel MCP de création ;
4. contrôle des autorisations côté serveur MCP, à chaque appel.

**Parcours d'une requête** : six étapes, avec les mots du projet, pas ceux du
cours.

**Questions ouvertes** — à écrire et à assumer. Trois suffisent : le 4B suffira-t-il
à lire une plaque signalétique photographiée ? Faut-il un OCR pour tous les
documents ou seulement les scannés ? Quel seuil de score de récupération
déclenche une demande de clarification plutôt qu'une réponse ?

---

## 2.4 — Flux et modèle d'accès (2 pages) — 2 points

Trois flux à décrire : **ingestion** (PDF/image → découpage → OCR si besoin →
embeddings → métadonnées), **requête** (question + photo → réponse sourcée avec
les contrôles), **ticket** (préparation → approbation → appel MCP → idempotence).

**Schéma des métadonnées d'un élément indexé** : identifiant et version du
document, page, identifiant d'élément, type d'équipement, groupes d'accès.

**Modèle d'accès** : deux groupes fictifs (`techniciens_ascenseurs`,
`techniciens_portes`) plus un groupe transverse (`responsables`), et la
répartition des documents entre eux. Le point à démontrer : un technicien
ascenseurs ne doit obtenir aucun extrait d'un manuel de porte, même si la
recherche le classerait premier.

---

## 2.5 — Analyse des risques (1,5 page) — 2 points

Dix risques, colonnes imposées : risque, catégorie, probabilité 1–3, impact 1–3,
mesure prévue, responsable. Le sujet impose d'en couvrir au minimum sept :

hallucination et citations non fondées · fuite entre groupes · ticket non
approuvé · erreurs introduites par l'IA dans le corpus · licences des documents ·
ressources matérielles insuffisantes · injection de prompt.

Trois de plus, propres à cette machine : DNS instable pendant les téléchargements
de modèles, dérive de périmètre sur l'interface, et perte de reproductibilité
si le corpus n'est pas versionné.

---

## 2.6 — Planning et rôles (1 page) — 1 point

Planning S2 à S6, aligné sur les phases réelles (ingestion, recherche,
génération, agent, évaluation, déploiement), avec les ressources consommées
annoncées. En travail individuel, la colonne « responsable » porte un seul nom :
mieux vaut l'assumer que simuler une équipe.

---

## 3. Ce que je produis, ce que tu dois faire

| Élément | Qui |
|---|---|
| Générateur de corpus et documents | moi |
| `inventaire.csv`, `prompts_corpus.md` | moi, à partir des prompts réellement utilisés |
| Diagrammes (sources Mermaid + images) | moi |
| Rédaction du rapport (parties 2.1 à 2.6) | moi, en français, 14 pages |
| Mise en page PDF | moi |
| **Relecture des documents générés** | **toi** — c'est la colonne `verifie_par` |
| **Corrections constatées et assumées** | **toi**, à partir de la liste que je fournis |
| Création du dépôt GitHub et accès à l'enseignante | toi |
| Dépôt du ZIP sur Classroom | toi |

La relecture n'est pas une formalité : la grille donne 3 points à « usage
critique de l'IA », et un document dont personne ne peut dire ce qui a été
corrigé n'obtient pas ces points.

## 4. Checklist avant dépôt

- [ ] ZIP nommé exactement `L1_MaintiDoc_<NomEquipe>.zip`, dossier unique dedans
- [ ] Rapport PDF, 10–15 pages hors annexes, s'ouvre sans erreur
- [ ] Lien GitHub accessible depuis un compte extérieur
- [ ] Chaque fichier de `corpus/documents/` et `corpus/images/` figure dans `inventaire.csv`, et inversement
- [ ] `document_id` identique entre le nom de fichier et l'inventaire
- [ ] ≥ 10 documents avec éléments visuels, ≥ 2 scannés
- [ ] ≥ 2 contradictoires, ≥ 1 piégé, tous signalés dans `usage_test`
- [ ] Aucun secret dans le ZIP ni dans le dépôt
- [ ] `prompts_corpus.md` couvre tous les documents générés par IA
