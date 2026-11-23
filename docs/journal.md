# Journal de projet

Trois lignes par phase : ce qui a ete fait, ce qui casse ou reste ouvert, ce qui
vient ensuite. Les decisions techniques detaillees vont dans `docs/adr/`.

---

## 2026-11-19 — Phase 0 : cadrage et environnement

**Fait.** Plan par phases ecrit et valide. Six ADR prises : modele vision 4B,
runtime natif Windows, Qdrant, embeddings BGE-M3 et CLIP multilingue, reranker
LoRA, evaluation precoce. Depot Git initialise avec `tasks.ps1`, configuration
centralisee, `docker-compose` d'infrastructure et script de verification de
l'environnement.

**Casse / ouvert.** Le PyTorch installe sur la machine est un build CPU : CUDA
n'est pas disponible, l'inference serait tombee sur le processeur sans erreur.
Environnement virtuel recree hors du depot avec un build CUDA 12.8. Le
telechargement du wheel (2,6 Gio) a echoue deux fois sur un DNS instable ; la
reprise par `curl -C -` a permis d'aboutir. Verification finale : sm_120, 8 Gio,
bfloat16, 13,5 TFLOPS mesures. Le demon Docker est arrete : l'infrastructure
n'a pas encore ete demarree. L'image `minio/minio` ne se resout plus sur Docker
Hub, le stockage d'objets est reporte en phase 2.

**Suivant.** Phase 1 : generateur de corpus deterministe, manifeste des
documents, deux familles d'equipements, documents pieges.

---

## 2026-11-20 - Phase 1 : corpus et manifeste

**Fait.** Generateur deterministe (`scripts/gen_corpus/`) : catalogue unique de
8 equipements et 13 codes, 40 documents sur 100 pages, 28 avec un element
visuel, 3 scans sans couche texte, 2 paires contradictoires, 1 document
d'injection, 5 cas ambigus. Inventaire de 20 colonnes ecrit en UTF-8 avec BOM,
valeurs mesurees sur les fichiers. Verificateur automatique : 11 controles, code
de sortie non nul en cas d'ecart. Rapport de 15 pages (12 hors annexes) et trois
figures generees par `reportlab`. Prompts P01 a P12 reconstruits depuis
l'historique reel du projet, avec les defauts et corrections de chacun.

**Casse / ouvert.** Les defauts trouves ne l'ont pas ete par le verificateur
mais par la relecture visuelle : plaques illisibles qui restaient nettes, scans
indistinguables de PDF vectoriels, transformateur sans sortie, enums inventees,
procedures identiques. Tous corriges, journalises dans
`docs/livrable-1/journal-corrections.md`. La relecture humaine du corpus reste a
faire : dix documents critiques sont prepares dans
`docs/livrable-1/revue-corpus.md`, la colonne `verifie_par` porte encore
« relecture humaine a completer » et ne sera remplie qu'apres ouverture des
fichiers. Le lien GitHub n'existe pas encore : le depot est local, le fichier
`LienGitHub.txt` ne peut pas etre rempli avant sa creation.

**Suivant.** Phase 2 : ingestion du corpus (extraction, OCR des trois scans,
decoupage, metadonnees), index Qdrant et premiers embeddings.
