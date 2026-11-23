# MaintiDoc

Assistant documentaire multimodal et agentique pour la maintenance.

Le systeme repond a des questions techniques en s'appuyant sur un corpus de
manuels, de procedures, de schemas et de photographies. Chaque affirmation est
rattachee a une page et, si possible, a une figure. Il consulte l'historique des
interventions via MCP et peut preparer un ticket de maintenance : la creation
n'a lieu qu'apres approbation explicite de l'utilisateur.

Le systeme ne pilote aucun equipement, ne garantit aucun diagnostic et ne
remplace ni les procedures de securite ni un technicien habilite.

## Etat d'avancement

| Phase | Etat |
|---|---|
| 0 — Cadrage et environnement | termine |
| 1 — Corpus et manifeste | termine |
| 2 — Ingestion | a venir |
| 3 — Indexation et recherche | a venir |
| 4 — Generation et citations | a venir |
| 5 — Agent, MCP, validation humaine | a venir |
| 6 — Adaptation du reranker | a venir |
| 7 — Evaluation et securite | a venir |
| 8 — Deploiement et demonstration | a venir |

Le plan detaille, les criteres de sortie de chaque phase et les arbitrages
techniques sont dans [docs/plan-de-phases.md](docs/plan-de-phases.md).

## Prerequis

- Windows 11, Python 3.12
- GPU compatible CUDA (cible : 8 Go de VRAM), pilote recent
- [uv](https://docs.astral.sh/uv/) pour la gestion de l'environnement
- Docker Desktop, uniquement pour l'infrastructure (Qdrant, PostgreSQL, MLflow)

## Installation

```powershell
git clone https://github.com/Mazhine/gnr_ia.git maintidoc
cd maintidoc
Copy-Item .env.example .env
.\tasks.ps1 setup
.\tasks.ps1 check
```

`setup` cree l'environnement virtuel dans `%LOCALAPPDATA%\maintidoc\venv`, hors
du depot, puis installe PyTorch avec le support CUDA. `check` verifie que la
carte graphique est bien vue par PyTorch : sans cela, l'inference tournerait sur
le processeur sans signaler d'erreur.

## Commandes

```powershell
.\tasks.ps1 check        # etat de l'environnement
.\tasks.ps1 test         # tests unitaires
.\tasks.ps1 lint         # ruff et mypy
.\tasks.ps1 corpus       # regenere les 40 documents et l'inventaire
.\tasks.ps1 corpus-check # verifie le corpus produit (11 controles)
.\tasks.ps1 diagrammes   # figures du rapport
.\tasks.ps1 rapport      # rapport PDF, lu depuis l'inventaire
.\tasks.ps1 infra-up     # Qdrant, PostgreSQL, MLflow
.\tasks.ps1 infra-down
```

## Corpus

Quarante documents synthetiques, deux familles d'equipements fictives :
ascenseurs et monte-charges (constructeur Verticalis), portes et portails
automatiques (Portalis). Le corpus est produit par un generateur deterministe,
pas collecte sur le web : la licence est donc sans ambiguite et les identifiants
d'equipement sont les memes d'un document a l'autre.

Le registre est `corpus/inventaire.csv` : une ligne par fichier, vingt colonnes,
valeurs mesurees sur les fichiers produits. Les prompts qui ont pilote
l'ecriture du generateur sont traces dans `corpus/prompts_corpus.md`. Le corpus
contient volontairement deux paires contradictoires, un document piege
(injection de prompt), cinq cas ambigus et trois scans sans couche texte.

## Structure

```
corpus/          inventaire, prompts, documents PDF et images sources
docs/            plan, perimetre, ADR, journal, livrable 1, diagrammes
scripts/         generateur de corpus, figures, rapport
src/maintidoc/   code du projet
tests/           tests unitaires
```

Le livrable 1 (cadrage, corpus et architecture) est dans
`docs/livrable-1/` : rapport PDF, plan du corpus, journal des corrections,
protocole et grille de relecture. Les figures du rapport sont dans
`docs/diagrammes/` et se regenerent par `.\tasks.ps1 diagrammes`.

Les artefacts lourds (environnement virtuel, modeles, index, corpus extrait)
vivent dans `%LOCALAPPDATA%\maintidoc` et ne sont pas versionnes. Le depot est
volontairement restreint a ce qui se lit et se relit.

## Limites connues

- Le perimetre couvre deux familles d'equipements, avec des donnees fictives.
- Le modele vision-langage retenu est un modele 4B quantifie, et non le 7B
  propose par le sujet : 8 Go de VRAM ne permettent pas le 7B en pratique.
  L'ecart et ses consequences sont documentes dans
  [docs/adr/0001-modele-vision-4b.md](docs/adr/0001-modele-vision-4b.md).
- Aucun resultat de performance n'est garanti a ce stade.
