# ADR 0003 — Qdrant pour les vecteurs, stockage d'objets differe

- Statut : accepte
- Date : 2026-11-19

## Contexte

Le sujet demande une recherche textuelle et une recherche visuelle sur un corpus
restreint par les droits de l'utilisateur. Le filtrage par groupe d'acces doit
s'appliquer **avant** la recherche, pas apres : filtrer apres revient a laisser
le modele voir des passages interdits, puis a les retirer de la reponse.

Le sujet suggere Qdrant pour les vecteurs, PostgreSQL pour les metadonnees et
MinIO pour les fichiers.

## Decision

**Qdrant**, avec index de payload sur `access_groups`, `equipment_family` et
`doc_id`. Le filtrage est passe a la requete, ce qui garantit qu'aucun element
hors perimetre n'entre dans le contexte du modele. Deux collections distinctes :
`text_elements` et `image_elements`, avec des vecteurs nommes.

**PostgreSQL** pour les metadonnees applicatives, les utilisateurs et les
tickets.

**Stockage d'objets differe a la phase 2.** L'image historique `minio/minio` ne
se resout plus sur Docker Hub (`404` constate le 19/11/2026), et MinIO publie
desormais sur `quay.io`. Plutot que d'epingler un chemin de registre non verifie
une semaine avant d'en avoir besoin, on definit des maintenant une interface de
stockage (`put`, `get`, `url`) avec une implementation systeme de fichiers.

## Alternatives ecartees

| Alternative | Raison de l'ecart |
|---|---|
| Chroma ou FAISS | Pas de filtrage par payload aussi direct ; FAISS n'est pas un service |
| pgvector | Serait coherent avec PostgreSQL, mais le filtrage hybride et les vecteurs nommes sont moins simples a mener |
| Filtrer apres la recherche | Contredit la section 9 du sujet sur le controle documentaire |
| MinIO des maintenant | Chemin de registre non verifie ; aucun besoin avant la phase 2 |

## Consequences

- La volumetrie du prototype (quelques centaines de Mo) ne justifie pas un
  serveur d'objets : le systeme de fichiers suffit et simplifie le debogage.
- L'interface de stockage est le point de bascule : passer a MinIO ne doit
  toucher qu'une classe d'implementation.
- Les index de payload Qdrant doivent etre crees explicitement a l'initialisation,
  sinon le filtrage degrade silencieusement les performances.
