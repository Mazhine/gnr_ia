"""Verifie que la machine est capable de faire tourner le projet.

Ce script a une seule raison d'exister : detecter tot les problemes qui, sinon,
se manifestent trois semaines plus tard sous la forme d'une inference lente ou
d'un plantage inexplicable. Il verifie la version de Python, la pile PyTorch et
CUDA, la memoire de la carte graphique, le demon Docker et l'espace disque.

Sortie : un rapport lisible et un code de retour non nul si une verification
obligatoire echoue.

    python scripts/check_env.py
    python scripts/check_env.py --strict   # le demon Docker devient obligatoire
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from maintidoc.config import get_settings

MIN_PYTHON = (3, 12)

# La RTX 5060 Laptop est une puce Blackwell (sm_120). Un build PyTorch anterieur
# a CUDA 12.8 ne la reconnait pas et retombe silencieusement sur le CPU.
EXPECTED_CAPABILITY = (12, 0)
MIN_VRAM_GIB = 6.0
MIN_FREE_DISK_GIB = 40.0


@dataclass
class Check:
    name: str
    status: str  # "ok" | "warn" | "fail"
    detail: str


def check_python() -> Check:
    version = sys.version_info
    detail = f"{version.major}.{version.minor}.{version.micro} ({sys.executable})"
    if (version.major, version.minor) < MIN_PYTHON:
        return Check("Python", "fail", f"{detail} - 3.12 minimum requis")
    return Check("Python", "ok", detail)


def check_torch() -> list[Check]:
    try:
        import torch
    except ImportError:
        return [Check("PyTorch", "fail", "absent - uv sync --extra gpu")]

    checks = [Check("PyTorch", "ok", f"{torch.__version__} (CUDA {torch.version.cuda})")]

    if not torch.cuda.is_available():
        hint = "build CPU installe" if torch.version.cuda is None else "pilote ou carte non detectee"
        checks.append(Check("CUDA", "fail", f"indisponible - {hint}"))
        return checks

    capability = torch.cuda.get_device_capability(0)
    properties = torch.cuda.get_device_properties(0)
    vram_gib = properties.total_memory / 1024**3

    checks.append(
        Check(
            "GPU",
            "ok",
            f"{properties.name} - {vram_gib:.1f} Gio - sm_{capability[0]}{capability[1]}",
        )
    )
    if capability < EXPECTED_CAPABILITY:
        checks.append(
            Check(
                "Architecture",
                "warn",
                f"sm_{capability[0]}{capability[1]} detecte, sm_120 attendu",
            )
        )
    if vram_gib < MIN_VRAM_GIB:
        checks.append(Check("VRAM", "fail", f"{vram_gib:.1f} Gio - 6 Gio minimum"))

    bf16 = torch.cuda.is_bf16_supported()
    checks.append(
        Check("bfloat16", "ok" if bf16 else "warn", "supporte" if bf16 else "non supporte, float16 en repli")
    )
    return checks


def check_docker(strict: bool) -> Check:
    if shutil.which("docker") is None:
        return Check("Docker", "fail" if strict else "warn", "binaire introuvable")
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Check("Docker", "warn", f"verification impossible ({exc.__class__.__name__})")

    if result.returncode != 0:
        return Check("Docker", "fail" if strict else "warn", "demon arrete - lancer Docker Desktop")
    return Check("Docker", "ok", f"demon actif, version {result.stdout.strip()}")


def check_disk() -> Check:
    free_gib = shutil.disk_usage(Path.home()).free / 1024**3
    status = "ok" if free_gib >= MIN_FREE_DISK_GIB else "warn"
    return Check("Disque", status, f"{free_gib:.0f} Gio libres sur le profil")


def check_storage_writable() -> Check:
    settings = get_settings()
    try:
        settings.ensure_dirs()
        probe = settings.cache_dir / ".probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return Check("Depot artefacts", "fail", f"non inscriptible : {exc}")
    return Check("Depot artefacts", "ok", str(settings.home))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exige un demon Docker actif")
    args = parser.parse_args()

    checks = [check_python(), *check_torch(), check_disk(), check_storage_writable()]
    checks.append(check_docker(strict=args.strict))

    width = max(len(check.name) for check in checks)
    for check in checks:
        print(f"[{check.status.upper():4}] {check.name.ljust(width)}  {check.detail}")

    failures = [check for check in checks if check.status == "fail"]
    print()
    if failures:
        print(f"{len(failures)} verification(s) en echec.")
        return 1
    print("Environnement conforme.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
