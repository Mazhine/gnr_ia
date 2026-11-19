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
| 1 — Corpus et manifeste | a venir |
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
git clone <url> maintidoc
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
.\tasks.ps1 infra-up     # Qdrant, PostgreSQL, MLflow
.\tasks.ps1 infra-down
```

## Structure

```
docs/            plan, perimetre, decisions d'architecture (ADR), journal
scripts/         outils de developpement et de generation de donnees
src/maintidoc/   code du projet
tests/           tests unitaires
corpus/          sources documentaires versionnees (texte uniquement)
```

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
