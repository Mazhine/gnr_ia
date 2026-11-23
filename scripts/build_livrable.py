"""Construit l'archive du livrable 1 au format impose par les consignes.

L'archive n'est pas assemblee a la main : elle est recopiee depuis le depot, et
le lien GitHub est lu dans le remonte distant de git. Un depot sans remonte
echoue avec un message explicite plutot que de produire une archive avec un
lien vide, qui serait consideree comme non rendue.

Structure produite (noms imposes, rien d'autre a la racine) :

    L1_MaintiDoc_CHATER.zip
    └── L1_MaintiDoc_CHATER/
        ├── L1_MaintiDoc_CHATER_Rapport.pdf
        ├── L1_MaintiDoc_CHATER_LienGitHub.txt
        ├── README.md
        └── L1_MaintiDoc_CHATER_Corpus/
            ├── inventaire.csv
            ├── prompts_corpus.md
            ├── documents/famille_1/
            ├── documents/famille_2/
            └── images/
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

EQUIPE = "CHATER"
RACINE = f"L1_MaintiDoc_{EQUIPE}"
RAPPORT = f"{RACINE}_Rapport.pdf"
LIEN = f"{RACINE}_LienGitHub.txt"
CORPUS = f"{RACINE}_Corpus"


def lien_github(explicite: str | None) -> str:
    """URL du depot, sans dependre de la forme du remonte local.

    Un remonte SSH (`git@github.com:utilisateur/depot.git`) n'est pas ouvrable
    par l'enseignante : il est converti en URL https.
    """
    if explicite:
        return explicite.strip()
    resultat = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True, check=False,
    )
    if resultat.returncode != 0 or not resultat.stdout.strip():
        raise SystemExit(
            "Aucun remonte git 'origin'. Creer le depot GitHub, puis :\n"
            "  git remote add origin https://github.com/<compte>/maintidoc.git\n"
            "ou relancer avec --url https://github.com/<compte>/maintidoc"
        )
    url = resultat.stdout.strip()
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.removeprefix("git@github.com:")
    return url.removesuffix(".git")


def copier_corpus(racine: Path, destination: Path) -> int:
    """Recopie le corpus sans les intermediaires de generation."""
    destination.mkdir(parents=True)
    shutil.copy2(racine / "corpus" / "inventaire.csv", destination / "inventaire.csv")
    shutil.copy2(racine / "corpus" / "prompts_corpus.md", destination / "prompts_corpus.md")
    for famille in ("famille_1", "famille_2"):
        shutil.copytree(racine / "corpus" / "documents" / famille,
                        destination / "documents" / famille)
    shutil.copytree(racine / "corpus" / "images", destination / "images")
    return sum(1 for _ in destination.rglob("*") if _.is_file())


def construire(racine: Path, sortie: Path, url: str) -> tuple[Path, int]:
    rapport = racine / "docs" / "livrable-1" / RAPPORT
    if not rapport.is_file():
        raise SystemExit(f"Rapport absent : {rapport}\nLancer : python -m scripts.gen_rapport")

    with tempfile.TemporaryDirectory(prefix="maintidoc_zip_") as temporaire:
        dossier = Path(temporaire) / RACINE
        dossier.mkdir()
        shutil.copy2(rapport, dossier / RAPPORT)
        shutil.copy2(racine / "docs" / "livrable-1" / "README_livrable.md",
                     dossier / "README.md")
        (dossier / LIEN).write_text(url + "\n", encoding="utf-8")
        fichiers = copier_corpus(racine, dossier / CORPUS)

        sortie.parent.mkdir(parents=True, exist_ok=True)
        sortie.unlink(missing_ok=True)
        with zipfile.ZipFile(sortie, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            # rglob ne rend pas le dossier racine : il est ecrit explicitement,
            # sans quoi l'archive n'a pas l'entree L1_MaintiDoc_CHATER/ attendue.
            archive.write(dossier, RACINE + "/")
            for chemin in sorted(dossier.rglob("*")):
                archive.write(chemin, chemin.relative_to(Path(temporaire)).as_posix())

    return sortie, fichiers


def verifier(archive: Path, racine: Path) -> list[str]:
    """Controle l'archive apres coup, sur le fichier produit et non sur l'intention."""
    with zipfile.ZipFile(archive) as flux:
        noms = flux.namelist()
        if any("__MACOSX" in nom or ".cache" in nom or nom.endswith(".env") for nom in noms):
            raise SystemExit("Archive polluee : cache, .env ou fichier systeme present")

        attendus = {
            f"{RACINE}/",
            f"{RACINE}/{RAPPORT}",
            f"{RACINE}/{LIEN}",
            f"{RACINE}/README.md",
            f"{RACINE}/{CORPUS}/inventaire.csv",
            f"{RACINE}/{CORPUS}/prompts_corpus.md",
            f"{RACINE}/{CORPUS}/documents/famille_1/",
            f"{RACINE}/{CORPUS}/documents/famille_2/",
            f"{RACINE}/{CORPUS}/images/",
        }
        manquants = attendus - set(noms)
        if manquants:
            raise SystemExit("Elements manquants : " + ", ".join(sorted(manquants)))

        # Les identifiants de l'inventaire et les noms de fichiers doivent
        # correspondre dans les deux sens, sinon une citation ne resout rien.
        inventaire = flux.read(f"{RACINE}/{CORPUS}/inventaire.csv").decode("utf-8-sig")
        lignes = [ligne for ligne in inventaire.splitlines()[1:] if ligne.strip()]
        identifiants = {ligne.split(",")[0] for ligne in lignes}
        fichiers_corpus = {
            Path(nom).stem for nom in noms
            if not nom.endswith("/")
            and (
                (nom.startswith(f"{RACINE}/{CORPUS}/") and "/documents/" in nom)
                or nom.startswith(f"{RACINE}/{CORPUS}/images/")
            )
        }
        ecarts = identifiants.symmetric_difference(fichiers_corpus)
        if ecarts:
            raise SystemExit("Inventaire et fichiers divergent : " + ", ".join(sorted(ecarts)))

    return [f"{len(noms)} entrees", f"{len(lignes)} documents inventaries",
            f"{archive.stat().st_size / 1024 / 1024:.1f} Mio"]


def main() -> int:
    parseur = argparse.ArgumentParser(description="Assemble le ZIP du livrable 1")
    parseur.add_argument("--url", default=None, help="URL du depot, si le remonte git ne suffit pas")
    parseur.add_argument("--sortie", default=None, help="chemin du ZIP produit")
    options = parseur.parse_args()

    racine = Path(__file__).resolve().parent.parent
    sortie = Path(options.sortie) if options.sortie else racine / "docs" / "livrable-1" / f"{RACINE}.zip"
    url = lien_github(options.url)
    archive, _ = construire(racine, sortie, url)
    for ligne in verifier(archive, racine):
        print(f"  {ligne}")
    print(f"\n{archive} — {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
