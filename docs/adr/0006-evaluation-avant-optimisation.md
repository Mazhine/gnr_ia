# ADR 0006 — Evaluation avant optimisation

- Statut : accepte
- Date : 2026-11-19

## Contexte

La tentation classique sur un projet de RAG est de regler le decoupage, le `top_k`
et les prompts a l'intuition, puis de constater a la fin que « ca a l'air mieux ».
Sans reference chiffree, aucune decision d'amelioration ne peut etre justifiee,
et la section 10 du sujet devient impossible a remplir honnetement.

## Decision

Le harnais d'evaluation de la recherche est livre **a la fin de la phase 3**,
avant tout reglage et avant le modele de generation. Il mesure Recall@5, nDCG@5
et MRR@10 sur un jeu de requetes dont les elements attendus sont identifies.

Chaque phase suivante rejoue ce harnais. Une regression se traite immediatement.
Les jeux d'or sont versionnes en JSONL dans le depot, avec un schema valide.

Le jeu de 150 scenarios de la phase 7 est construit sur le meme principe : un
comportement attendu explicite par cas, verifie automatiquement, avec une liste
de cas difficiles revus a la main.

## Alternatives ecartees

| Alternative | Raison de l'ecart |
|---|---|
| Evaluer a la fin | Aucun moyen de savoir ce qui a ameliore ou degrade le systeme |
| Evaluation uniquement par le modele juge | Couteux, instable entre versions, difficile a reproduire |
| Evaluer sur les questions de demonstration | Biais de selection : on regle le systeme sur ce qu'on montrera |

## Consequences

- Le premier chiffre obtenu sera mediocre. C'est normal et utile : c'est le
  point de comparaison.
- Le jeu de requetes doit etre formule avec le vocabulaire d'un technicien, pas
  avec les titres des documents, sinon il mesure la facilite du jeu et non la
  qualite de la recherche.
- Le temps passe a annoter les elements attendus (phase 1 et 3) est du temps de
  developpement, pas de la surcharge.
