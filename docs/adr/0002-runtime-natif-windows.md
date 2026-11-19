# ADR 0002 — Inference native sous Windows et artefacts hors du depot

- Statut : accepte
- Date : 2026-11-19

## Contexte

Deux contraintes se combinent.

1. Le dossier du projet est dans OneDrive. Un environnement virtuel, des poids
   de modeles et un index vectoriel representent plusieurs gigaoctets et des
   milliers de petits fichiers. OneDrive les synchronise en continu, verrouille
   des fichiers pendant les ecritures et cree des conflits.
2. Docker Desktop sous Windows n'expose le GPU qu'a travers WSL2. Faire tourner
   un modele de vision dans un conteneur impose donc une seconde couche de
   virtualisation, avec son propre gaspillage memoire, sur une carte qui n'a
   que 8 Go.

## Decision

- **Inference en natif sous Windows.** PyTorch et les modeles tournent dans
  l'environnement virtuel du systeme, pas dans un conteneur.
- **Conteneurs limites a l'infrastructure** : Qdrant, PostgreSQL, MLflow. Ils
  n'ont pas besoin du GPU.
- **Artefacts lourds hors du depot**, dans `%LOCALAPPDATA%\maintidoc`, surchargeable
  par `MAINTIDOC_HOME`. Le depot ne contient que du texte : code, documents,
  manifestes, jeux d'evaluation.
- **Volumes Docker nommes** plutot que des dossiers montes depuis le depot, pour
  que les donnees Qdrant et PostgreSQL restent hors de la synchronisation.

L'environnement virtuel vit lui aussi hors du depot, en
`%LOCALAPPDATA%\maintidoc\venv`, et `tasks.ps1` le retrouve automatiquement.

## Alternatives ecartees

| Alternative | Raison de l'ecart |
|---|---|
| Tout dans Docker, GPU via WSL2 | Cout memoire et complexite de diagnostic sur 8 Go |
| Deplacer le depot hors de OneDrive | Possible et probablement preferable ; reporte tant que la phase 1 n'a pas montre de friction reelle |
| Ignorer le probleme | Corruption de fichiers et lenteurs differees, difficiles a attribuer |

## Consequences

- Le depot est deplacable : aucun chemin absolu n'est ecrit en dur, tout passe
  par `maintidoc.config`. Si la cohabitation avec OneDrive pose probleme en
  phase 1, un `git clone` suffit a repartir ailleurs.
- La sauvegarde des donnees Qdrant et PostgreSQL passe par `docker compose`,
  pas par une simple copie de dossier. C'est documente dans le runbook.
- L'API applicative et le serveur MCP tourneront en conteneurs et joindront le
  modele par HTTP : le modele n'est pas dans le meme processus que l'API.
