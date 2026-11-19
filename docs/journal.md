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
