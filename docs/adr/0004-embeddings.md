# ADR 0004 — Embeddings texte BGE-M3 et image multilingue

- Statut : accepte
- Date : 2026-11-19

## Contexte

Le corpus est en francais. Les questions aussi, mais elles emploient le
vocabulaire du terrain, pas celui du manuel : « le voyant orange clignote au
demarrage » ne partage presque aucun terme avec « defaut de sequence de
prechauffage ». Une recherche purement lexicale echoue sur ce decalage.

La recherche visuelle doit fonctionner sans traduction intermediaire : une
photographie de panneau doit pouvoir etre comparee a une legende francaise.

## Decision

- **Texte : BGE-M3**, en dense et sparse simultanement. Le modele produit les
  deux representations d'un meme passage, ce qui rend l'hybridation simple et
  coherente. Multilingue, contexte long, bien documente.
- **Image : CLIP multilingue** (`jina-clip-v2`), qui place texte et image dans un
  espace commun couvrant une centaine de langues.
- **Fusion par RRF** (Reciprocal Rank Fusion) : insensible a l'echelle des
  scores, donc pas de normalisation fragile a calibrer.
- Les figures sont indexees **deux fois** : par leur image, et par leur legende
  dans la collection texte. Une legende explicite est souvent plus discriminante
  qu'un vecteur visuel.

## Alternatives ecartees

| Alternative | Raison de l'ecart |
|---|---|
| BM25 seul | Rate le decalage lexical terrain / manuel |
| Embeddings uniquement denses | Perd les references exactes (codes d'alarme, references de piece) que le sparse capture bien |
| CLIP original (anglais) | Le corpus et les questions sont en francais |
| Traduire les requetes avant recherche visuelle | Ajoute une etape faillible et un appel de modele supplementaire dans le budget |

## Consequences

- BGE-M3 et l'encodeur image sont deux modeles a charger : environ 1,5 Go de
  memoire au total, compatible avec le GPU disponible.
- L'indexation coute cher en calcul mais une seule fois ; le cache par hash de
  contenu evite de la refaire a chaque modification du corpus.
- Le choix du `k` de RRF et des poids dense/sparse se tranche par mesure en
  phase 3, pas par intuition. Les valeurs par defaut restent dans la config.
