# Environnement de developpement

Etat constate le 19/11/2026, puis procedure de verification. A relire si la
machine change ou si un composant se comporte bizarrement.

## Constats

| Element | Valeur constatee | Commentaire |
|---|---|---|
| GPU | NVIDIA GeForce RTX 5060 Laptop, 8151 Mio | Blackwell, sm_120 |
| Pilote | 573.13 | Compatible CUDA 12.8 et superieur |
| Python systeme | 3.12.10 et 3.14.1 via `py -0p` | Le projet utilise 3.12 |
| PyTorch systeme | `2.11.0+cpu`, CUDA `None` | **Build CPU installe** : l'inference serait tombee sur le processeur |
| Docker | 29.5.3, compose v5.1.4 | Demon arrete au moment du constat |
| Make / just | absents | D'ou `tasks.ps1` |
| Espace disque | environ 171 Gio libres | Suffisant pour les modeles |

## Consequence du build CPU

C'est le piege principal de cette configuration. Un PyTorch CPU ne leve aucune
erreur : il tourne, seulement quarante fois plus lentement. Sur un modele de
vision, cela se traduit par une generation de plusieurs minutes et une tentation
d'accuser le modele.

Le correctif est un environnement virtuel dedie avec un build CUDA 12.8 ou
superieur, installe depuis `https://download.pytorch.org/whl/cu128`. La
verification se fait en deux lignes :

```python
import torch
torch.cuda.is_available()          # doit valoir True
torch.cuda.get_device_capability() # doit valoir (12, 0)
```

## Emplacements

| Objet | Emplacement | Versionne |
|---|---|---|
| Code, documents, manifestes | depot Git | oui |
| Environnement virtuel | `%LOCALAPPDATA%\maintidoc\venv` | non |
| Modeles telecharges | `%LOCALAPPDATA%\maintidoc\models` | non |
| Donnees produites (bronze, silver, or) | `%LOCALAPPDATA%\maintidoc\data` | non |
| Cache de travail | `%LOCALAPPDATA%\maintidoc\cache` | non |
| Volumes Qdrant, PostgreSQL, MLflow | volumes Docker nommes | non |

Tout est surchargeable par `MAINTIDOC_HOME`. Aucun chemin absolu n'est ecrit dans
le code.

## Procedure de verification

```powershell
.\tasks.ps1 setup     # cree le venv hors depot, installe torch CUDA
.\tasks.ps1 check     # rapport Python / CUDA / VRAM / Docker / disque
.\tasks.ps1 test      # tests unitaires
```

`check` sort en code non nul si une verification obligatoire echoue. Le
demon Docker n'est obligatoire qu'avec `--strict` : on peut developper et
evaluer la recherche textuelle sans infrastructure.
