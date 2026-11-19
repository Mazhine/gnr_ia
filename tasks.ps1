<#
.SYNOPSIS
    Lanceur de taches du projet MaintiDoc.

.DESCRIPTION
    Point d'entree unique pour les operations courantes. Volontairement en
    PowerShell : make et just ne sont pas installes sur la machine de
    developpement, et installer un outil de plus pour quatre commandes n'a
    aucun interet.

.EXAMPLE
    .\tasks.ps1 check
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Task = "help"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$env:PYTHONPATH = Join-Path $ProjectRoot "src"

if ($env:MAINTIDOC_PYTHON) {
    $Python = $env:MAINTIDOC_PYTHON
} else {
    $Python = Join-Path $env:LOCALAPPDATA "maintidoc\venv\Scripts\python.exe"
}

if (-not (Test-Path $Python)) {
    Write-Error "Environnement introuvable : $Python`nLancer : .\tasks.ps1 setup"
}

Set-Location $ProjectRoot

$tasks = @{
    help         = {
        @"
Taches disponibles :

  setup        Cree l'environnement virtuel hors du depot et installe les dependances
  check        Verifie Python, CUDA, Docker et l'espace disque
  test         Lance pytest
  lint         Lance ruff et mypy
  format       Formate le code avec ruff
  infra-up     Demarre Qdrant, PostgreSQL et MLflow (Docker Desktop requis)
  infra-down   Arrete l'infrastructure
"@
    }

    setup        = {
        # $Python vaut <home>\venv\Scripts\python.exe : deux remontees donnent <home>\venv
        $venv = Split-Path (Split-Path $Python)
        uv venv $venv --python 3.12
        uv pip install --python $Python -e ".[gpu]"
        uv pip install --python $Python ruff mypy pytest pytest-cov
        Write-Host "Environnement pret : $Python"
    }

    check        = { & $Python "scripts\check_env.py" }

    test         = { & $Python -m pytest }

    lint         = {
        & $Python -m ruff check .
        & $Python -m mypy
    }

    format       = { & $Python -m ruff format . ; & $Python -m ruff check --fix . }

    "infra-up"   = { docker compose up -d }

    "infra-down" = { docker compose down }
}

if (-not $tasks.ContainsKey($Task)) {
    Write-Host "Tache inconnue : $Task`n"
    & $tasks["help"]
    exit 1
}

& $tasks[$Task]
