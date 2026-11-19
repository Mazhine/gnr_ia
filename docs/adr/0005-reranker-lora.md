# ADR 0005 — Adaptation du reranker en LoRA

- Statut : accepte
- Date : 2026-11-19

## Contexte

Le sujet demande une adaptation ciblee d'un composant, avec une comparaison
mesurable avant et apres. Adapter le modele vision-langage serait plus
spectaculaire mais hors de portee : 4B parametres en 4 bits, 8 Go de VRAM, et
aucun jeu de donnees vision de qualite disponible. Le resultat serait un modele
degrade et un rapport incapable de prouver quoi que ce soit.

Un reranker cross-encoder de 568 M parametres, en revanche, s'entraine sur une
carte de 8 Go avec des sequences de 512 tokens.

## Decision

Adapter **BGE-reranker-v2-m3** par **LoRA**, avec `batch_size` 8, `max_length`
512, accumulation de gradient et checkpointing d'activation. Pas de fine-tuning
complet : le budget memoire ne le permet pas.

Le jeu d'entrainement est constitue de triplets `(requete, passage pertinent,
negatif difficile)`. Les negatifs sont **mines** dans les resultats de rangs 5 a
50 de la recherche de la phase 3 : meme famille d'equipements, alarmes
lexicalement proches, mauvais equipement. Des negatifs tires au hasard
apprendraient au modele a distinguer le sujet du hors-sujet, ce qu'il sait deja.

Decoupage par document et par famille d'equipements, jamais par triplet. Un
controle automatique verifie qu'aucun `doc_id` n'est present dans deux ensembles.

## Alternatives ecartees

| Alternative | Raison de l'ecart |
|---|---|
| Fine-tuning complet du reranker | Memoire insuffisante, et gain marginal attendu sur 800 a 1500 exemples |
| Adapter le modele vision | Hors budget memoire et hors budget de donnees |
| Ne pas faire de fine-tuning | Le sujet l'exige explicitement (section 5) |
| Negatifs aleatoires | Trop faciles, resultat gonfle et non transposable |

## Consequences

- Le resultat peut etre nul, voire negatif. C'est acceptable et documente : le
  sujet demande d'exposer les resultats observes, pas d'obtenir un gain.
- La metrique de decision est nDCG@5 et MRR@10 sur le meme jeu que la phase 3.
  Comparer avec un jeu different ne prouverait rien.
- Le LoRA represente quelques dizaines de Mo : versionnable hors Git, reference
  par hash dans `release.json`.
