from __future__ import annotations

from pathlib import Path

from maintidoc.config import PROJECT_ROOT, Settings


def test_artefacts_hors_du_depot() -> None:
    """Le venv, les modeles et l'index ne doivent pas etre synchronises par OneDrive."""
    settings = Settings()
    assert not settings.home.is_relative_to(PROJECT_ROOT)
    assert not settings.data_dir.is_relative_to(PROJECT_ROOT)


def test_home_surchargeable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MAINTIDOC_HOME", str(tmp_path))
    settings = Settings()
    assert settings.home == tmp_path
    assert settings.models_dir == tmp_path / "models"


def test_ensure_dirs_idempotent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MAINTIDOC_HOME", str(tmp_path))
    settings = Settings()

    settings.ensure_dirs()
    settings.ensure_dirs()

    for path in (settings.data_dir, settings.models_dir, settings.cache_dir, settings.runs_dir):
        assert path.is_dir()
