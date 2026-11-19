# Perimetre du projet

Version 1 — 2026-11-19. Ce document tranche ce qui est dans le projet et ce qui
n'y est pas. Toute demande hors de ce cadre est refusee ou reportee, pas absorbee
au fil de l'eau.

## Ce que le systeme fait

| Element | Perimetre retenu |
|---|---|
| Utilisateurs | Techniciens et responsables de maintenance, comptes fictifs |
| Corpus | 30 a 50 documents, deux familles d'equipements, textes et images |
| Entrees | Questions en francais, photographies, documents PDF |
| Sorties | Reponses sourcees, demandes de clarification, brouillons de tickets |
| Outil externe | Serveur MCP de demonstration : historique et tickets |
| Action sensible | Creation d'un ticket, apres approbation explicite et tracee |

## Ce que le systeme ne fait pas

- Il ne pilote aucun equipement et n'envoie aucune commande.
- Il ne produit pas de diagnostic garanti. Une ressemblance visuelle n'est pas
  une confirmation.
- Il ne remplace ni les procedures de securite, ni un technicien habilite.
- Il ne traite pas de donnees personnelles reelles : les documents sont
  synthetiques, les utilisateurs et les tickets sont fictifs.
- Il ne conserve pas le contenu des echanges par defaut : les journaux
  contiennent des metadonnees techniques, pas les textes.

## Hypotheses de travail

1. Le corpus est genere par script, de facon deterministe, avec un jeu de
   documents pieges (injection, contradiction, image illisible) present des la
   phase 1. Ajouter ces cas a la fin obligerait a refaire les phases 3 a 7.
2. Une seule requete est traitee a la fois. Les mesures de latence sont faites
   en serie, sur la machine de developpement.
3. Le modele vision-langage est un 4B quantifie (ADR 0001). Le 7B du sujet n'est
   pas tenable sur 8 Go de VRAM.
4. L'approbation humaine est un composant du systeme, pas une case a cocher
   dans l'interface : le serveur MCP refuse toute creation sans jeton valide.

## Definition de « termine »

Le projet est considere livre lorsque :

- les sept points de demonstration de la section 14 du sujet passent sur un jeu
  de donnees fige ;
- le harnais d'evaluation produit les indicateurs de la section 10, y compris
  les resultats negatifs ;
- aucune creation de ticket n'est possible sans approbation, et le test
  d'injection de la section 9 ne provoque ni exfiltration ni elevation ;
- une personne qui clone le depot peut installer et lancer la demonstration en
  suivant le README, sans intervention non documentee.

## Hors perimetre assume

- Interface mobile, authentification federée, multitenancy.
- Entrainement ou adaptation du modele vision-langage.
- Deploiement en production, haute disponibilite, montée en charge.
- Traitement de documents dans d'autres langues que le francais.
