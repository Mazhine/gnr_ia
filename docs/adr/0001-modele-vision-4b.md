# ADR 0001 — Modele vision-langage 4B quantifie

- Statut : accepte
- Date : 2026-11-19

## Contexte

Le sujet propose Qwen2.5-VL-7B-Instruct. La machine de developpement dispose
d'une RTX 5060 Laptop de 8 Go de VRAM (8151 Mio rapportes par `nvidia-smi`),
sous Windows, avec un affichage qui consomme une partie de cette memoire.

Un modele 7B en 4 bits pese environ 5,5 Go. Il faut y ajouter l'encodeur visuel,
le cache KV et la reserve memoire du pilote. Sur une photographie de panneau de
commande, le nombre de tokens visuels monte vite : la marge disparait. Le
symptome n'est pas une erreur propre mais un debordement en memoire partagee,
qui divise la vitesse par dix sans message clair.

## Decision

Retenir **Qwen3-VL-4B-Instruct** en quantification 4 bits, avec un plafond de
tokens visuels (`max_pixels`) d'environ 1024 tokens par image.

Repli documente si la quantification se revele instable sur Blackwell :
Qwen2.5-VL-3B-Instruct, egalement en 4 bits.

## Alternatives ecartees

| Alternative | Raison de l'ecart |
|---|---|
| Qwen2.5-VL-7B en 4 bits | Depassement memoire des que l'image depasse quelques centaines de tokens |
| Qwen2.5-VL-7B en 8 bits | Impossible : 8 Go de poids seuls |
| Inference sur CPU | Latence incompatible avec l'objectif p95 < 30 s |
| API hebergement externe | Le corpus est cense rester maitrise ; sortir les images vers un tiers contredit la section 9 du sujet |

## Consequences

- L'ecart au sujet est assume et documente dans la fiche de limites. Ce n'est
  pas un oubli : c'est la consequence directe d'une contrainte materielle.
- La qualite d'analyse des images sera inferieure a celle d'un 7B. Les
  indicateurs de la phase 7 devront etre interpretes avec cette limite.
- Le benchmark memoire reel (phases 0 et 4) peut conduire a ajuster `max_pixels`.
  La valeur sera figee dans la configuration, pas dans le code.
- Le modele reste interchangeable : l'interface d'inference est isolee dans un
  module dedie pour permettre une comparaison ulterieure.
