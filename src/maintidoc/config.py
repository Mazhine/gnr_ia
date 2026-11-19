"""Configuration centralisée du projet.

Une seule source de vérité pour les chemins et les URL d'infrastructure. Tout
est surchargeable par variable d'environnement (préfixe ``MAINTIDOC_``) ou par
le fichier ``.env`` à la racine du dépôt.

Les artefacts lourds (environnement virtuel, modèles, index, corpus extrait)
sortent volontairement du dépôt : celui-ci vit dans un dossier synchronisé par
OneDrive, qui gère mal les fichiers verrouillés et les volumes de plusieurs
gigaoctets. Voir docs/adr/0002-runtime-natif-windows.md.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from platformdirs import user_data_dir
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Dossier versionné contenant les sources documentaires (texte, petit volume).
CORPUS_DIR = PROJECT_ROOT / "corpus"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MAINTIDOC_",
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    home: Path = Path(user_data_dir("maintidoc", appauthor=False))

    qdrant_url: str = "http://localhost:6333"
    postgres_dsn: str = "postgresql://maintidoc:maintidoc@localhost:5432/maintidoc"
    mlflow_url: str = "http://localhost:5000"

    @property
    def data_dir(self) -> Path:
        """Racine des données produites (zone bronze, silver, or)."""
        return self.home / "data"

    @property
    def models_dir(self) -> Path:
        """Cache des poids de modèles téléchargés."""
        return self.home / "models"

    @property
    def cache_dir(self) -> Path:
        """Cache de travail : OCR, embeddings, rendus de pages."""
        return self.home / "cache"

    @property
    def runs_dir(self) -> Path:
        """Journaux d'exécution des pipelines et des évaluations."""
        return self.home / "runs"

    def ensure_dirs(self) -> None:
        """Crée l'arborescence d'artefacts. Idempotent."""
        for path in (self.data_dir, self.models_dir, self.cache_dir, self.runs_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
