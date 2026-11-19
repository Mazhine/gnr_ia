# MaintiDoc — Plan de réalisation par phases

> Document de travail — version 0.2 — contrainte matérielle intégrée (voir §2.1).
> Projet intégrateur d'IA générative multimodale · Assistant documentaire et agentique pour la maintenance.

---

## 0. Lecture du sujet

Le sujet impose 14 sections, 6 livrables et 7 points de démonstration. Une fois qu'on enlève
l'habillage, il reste trois choses à produire, et une seule est du « prompt engineering » :

| Ce qui est réellement évalué | Poids réel |
|---|---|
| **Le corpus et sa qualité de preuve** (document → page → figure → affirmation) | ~40 % |
| **Le contrôle** (accès, approbation humaine, budgets, anti-injection) | ~30 % |
| **Le modèle** (VLM, reranker fine-tuné) | ~30 % |

Conséquence directe : **le VLM est un composant interchangeable**. Ce qui fera la note, c'est la
chaîne de données qui relie une réponse à une page réelle, et la capacité à démontrer qu'elle ne
fuit pas. Le plan ci-dessous est donc **data-first** : on construit le corpus, les contrats et
l'évaluation avant de brancher le modèle.

Trois pièges classiques sur ce type de sujet, et la parade retenue :

1. **Le corpus est sous-estimé.** 30 à 50 documents avec figures, schémas et photos, c'est le
   poste de coût le plus lourd. Parade : un **générateur de corpus par script** (déterministe,
   reproductible), pas de fabrication manuelle.
2. **L'évaluation arrive trop tard.** On se retrouve à « optimiser » sans référence. Parade : le
   harnais d'évaluation est livré **avant** le premier réglage (fin de phase 3).
3. **La démo est prête à J-2.** Parade : un **slice vertical** démontrable à la fin de chaque phase,
   jamais une phase qui ne produit que de l'infrastructure.

---

## 1. Principes directeurs (approche data engineering)

Ces huit règles structurent toutes les phases. Elles sont aussi ce qui rendra le dépôt lisible
pour un correcteur.

- **D1 — Le corpus est un produit.** Chaque document a un identifiant, une version, un hash, une
  licence, une famille d'équipement, des groupes d'accès. Rien n'entre dans le système sans fiche.
- **D2 — Architecture en zones.** `bronze` (fichiers bruts immuables) → `silver` (éléments
  extraits, Parquet) → `gold` (index vectoriels + jeux d'évaluation). On ne réécrit jamais le brut.
- **D3 — Contrats de données.** Quatre schémas versionnés en Git font office de frontière entre
  étages : `document_manifest`, `element`, `answer`, `scenario`. Aucun passage d'étage sans
  validation.
- **D4 — Idempotence et reprise.** Chaque job a un `run_id`, un hash d'entrée, ses paramètres.
  Le recalcul est évité par cache sur hash de contenu (embeddings, OCR, descriptions d'images).
- **D5 — L'évaluation est un test de régression.** Les jeux d'or sont versionnés, les scores sont
  comparés à chaque commit significatif. Une régression bloque.
- **D6 — Lignage complet.** `réponse → citation → element_id → page → version de document → hash
  source`. Sans ce chemin, une citation n'est pas une preuve.
- **D7 — Slice vertical d'abord.** Une seule famille d'équipement, 3 documents, une question, une
  citation : ça marche de bout en bout avant d'élargir.
- **D8 — Tout ce qui est généré est généré par du code.** Corpus synthétique, paires de
  fine-tuning, scénarios de test : des scripts et des seeds, pas des fichiers à la main.

---

## 2. Décisions à figer avant la phase 1

Ces choix conditionnent tout le reste. Valeurs par défaut proposées, avec le repli si contrainte.

| Sujet | Défaut proposé | Repli / variante |
|---|---|---|
| Matériel d'inférence | RTX 5060 Laptop, **8 Go** — Qwen3-VL-4B-Instruct en 4 bits | Qwen2.5-VL-3B quantifié ; endpoint hébergé en dernier recours (§2.1) |
| Serveur d'inférence | PyTorch build CUDA 12.8+ et `qwen-vl-utils`, `max_pixels` plafonné | llama.cpp / GGUF si la quantification 4 bits est instable sur Blackwell |
| Embeddings texte | BGE-M3 (dense + sparse) | `multilingual-e5-large` si BGE-M3 pose problème |
| Embeddings image | `jina-clip-v2` (multilingue) | SigLIP2 + traduction des requêtes |
| OCR | Tesseract `fra` (baseline), escalade PaddleOCR/surya si layout complexe | — |
| Vector DB | Qdrant (filtrage par payload avant recherche) | — |
| Métadonnées / tickets | PostgreSQL | SQLite pour le prototype si Docker pose problème |
| Fichiers | MinIO | système de fichiers local, même arborescence |
| Orchestration | LangGraph + LangChain | — |
| Suivi d'expériences | MLflow | journal JSON versionné si MLflow coûte du temps |
| Reranker | BGE-reranker-v2-m3 adapté en LoRA | `bge-reranker-base` si le coût mémoire du m3 est trop élevé |

### 2.1 Contrainte matérielle : 8 Go de VRAM

Le sujet propose Qwen2.5-VL-7B. Sur 8 Go, ce n'est pas tenable en pratique : environ 5,5 Go de
poids en 4 bits, plus l'encodeur visuel, le cache KV et la réserve mémoire de Windows (WDDM)
laissent trop peu de marge dès qu'une image dépasse quelques centaines de tokens visuels.
Quatre conséquences, à assumer et à documenter dans le rapport :

- **Modèle retenu : Qwen3-VL-4B-Instruct** (4 bits), `max_pixels` plafonné à ~1024 tokens
  visuels. Repli si instable : Qwen2.5-VL-3B. L'écart au sujet est un **choix d'ingénierie
  argumenté** : il ira dans la fiche de limites, pas dans une note de bas de page.
- **Pile CUDA** : la RTX 5060 Laptop est une puce Blackwell (sm_120), le pilote installé est
  573.13. Elle exige un build PyTorch **CUDA 12.8 minimum** ; les wheels plus anciens échouent ou
  retombent en CPU silencieusement. Vérification dès la phase 0 : `torch.cuda.is_available()` et
  `torch.cuda.get_device_capability()` doit renvoyer `(12, 0)`.
- **Séparation des runtime** : l'inférence tourne **en natif sous Windows**. Le GPU passthrough
  Docker sous Windows suppose WSL2 et coûte plus qu'il ne rapporte ici. Les conteneurs ne servent
  qu'à l'infrastructure (Qdrant, PostgreSQL, MinIO, MLflow).
- **Conséquence sur l'évaluation** : p95 < 30 s reste atteignable, mais **une requête à la fois**.
  Les mesures de latence se font en série ; toute mesure en concurrence serait trompeuse.

> ⚠️ **Prérequis d'environnement, à traiter en phase 0 :** le dossier actuel est dans OneDrive.
> Un dépôt Python avec `.venv`, volumes Qdrant, caches de modèles et jeux de données ne doit
> **pas** être synchronisé (lenteur, corruption de fichiers, conflits). Recommandation : dépôt
> local (ex. `C:\dev\maintidoc`), et OneDrive ne conserve que les documents de rendu.
> Le dossier n'est pas encore un dépôt Git : `git init` fait partie de la phase 0.

---

## 3. Carte des phases

| # | Phase | Durée (j-h) | Dépend de | Livrable du sujet couvert |
|---|---|---|---|---|
| 0 | Cadrage opérationnel & décisions | 1 | — | L1 (début) |
| 1 | Fondations data : corpus & manifeste | 3–4 | 0 | L1 |
| 2 | Ingestion bronze → silver | 4–5 | 1 | L2 (partiel) |
| 3 | Indexation & recherche + harnais d'éval | 4–5 | 2 | L2, L4 (socle) |
| 4 | Génération VLM, citations, sorties structurées | 4–5 | 3 | L3 (partiel) |
| 5 | Workflow agentique, MCP, validation humaine, UI | 5–6 | 4 | L3 |
| 6 | Fine-tuning du reranker | 4–5 | 3 (+ données dès la 3) | L4 |
| 7 | Évaluation 150 scénarios & sécurité | 3–4 | 4, 5, 6 | L4, L5 |
| 8 | MLOps, déploiement, documentation, démo | 3–4 | toutes | L2, L6 |

**Total : 31 à 39 j-h**, hors rédaction du rapport (~2–3 j).

### Ressources par phase

Annoncées au début de chaque phase, et récapitulées ici. « Temps machine » est le
temps de calcul à laisser tourner ; « ton temps » est le temps d'attention
réellement nécessaire (relecture, arbitrage), pas le temps de présence.

| Phase | Matériel mobilisé | Disque | Temps machine | Ton temps |
|---|---|---|---|---|
| 0 | GPU (vérification), PyTorch CUDA | ~6 Go | 10–20 min de téléchargement | 30 min |
| 1 | CPU seul | < 1 Go | < 10 min | 1–2 h de relecture du corpus |
| 2 | CPU seul | 5–10 Go (images de pages) | 30–60 min | 30 min sur un échantillon |
| 3 | GPU 8 Go (embeddings) | 10–20 Go (index, caches) | 1–3 h en tâche de fond | 30 min |
| 4 | GPU 8 Go (VLM) | 4–8 Go (poids du modèle) | 10–20 min par passe | 1 h de revue des réponses |
| 5 | GPU + Docker Desktop | 2–3 Go | < 30 min | 1–2 h (mise en route Docker) |
| 6 | GPU 8 Go (LoRA) | 3–5 Go | 2–6 h d'entraînement | 30 min |
| 7 | GPU + Docker | 1–2 Go | 1–2 h d'exécution | 2–3 h de revue des cas difficiles |
| 8 | Docker Desktop | quelques Go | 20–30 min | 1–2 h |

Le seul moment où la machine est réellement bloquée est la phase 4 : pendant une
inférence, 8 Go de VRAM sont occupés et l'affichage peut ralentir. Les autres
phases laissent la machine utilisable.

Honnêteté sur le calendrier : le sujet annonce 6 semaines. En solo à temps plein (5 j/sem), le
plan complet fait **7 semaines**. La différence se joue sur deux leviers, à décider maintenant :
le corpus généré par script (phase 1 tenue en 3 j au lieu de 6), et le démarrage du fine-tuning
en parallèle de la phase 5 (la préparation des données dépend seulement de la phase 3).

```
Sem. 1   [P0][------ P1 ------][-- P2 --]
Sem. 2   [---- P2 ----][------ P3 ------]
Sem. 3   [---- P4 ----]        [P6 données]
Sem. 4   [------ P5 ------]    [-- P6 --]
Sem. 5   [-- P6 --][---- P7 ----]
Sem. 6   [---- P8 ----][ rapport ]
```

---

## 4. Détail des phases

### Phase 0 — Cadrage opérationnel & décisions *(1 j)*

**Objectif** : ne plus jamais rediscuter « quel modèle », « quelle base », « quel périmètre ».

**Travaux**
- Trancher le tableau de la section 2 (matériel d'abord : il débloque tout le reste).
- **Remettre la pile GPU d'aplomb.** Constat du 19/11 sur la machine : `torch 2.11.0+cpu`,
  `torch.cuda.is_available()` = `False`. Un wheel CPU est installé, l'inférence tomberait en
  processeur sans erreur visible. Réinstaller un build CUDA 12.8+ et vérifier
  `get_device_capability() == (12, 0)` avant d'écrire la moindre ligne d'inférence.
- Choisir les **2 familles d'équipements** (ex. pompes centrifuges + armoires de commande).
- Décider le mode de corpus : 100 % synthétique généré, 100 % réel autorisé, ou mixte.
- Initialiser le dépôt : `git init`, arborescence, `uv`/`pyproject.toml`, `pre-commit`,
  `.env.example`, `docker-compose.yml` squelette, `tasks.ps1` (lanceur de tâches — ni `make` ni
  `just` ne sont installés sur la machine).
- Écrire 4 à 6 ADR courts (1 page chacun) : VLM, vector DB, stockage, reranker, stratégie d'OCR,
  stratégie d'évaluation.
- Écrire `docs/scope.md` : ce qui est dedans, ce qui est dehors (reprise du hors-périmètre du
  sujet), et le **MVP vs. stretch**.

**Artefacts** : `docs/adr/*.md`, `docs/scope.md`, dépôt initialisé, `README.md` squelette.

**Critère de sortie** : aucune décision technique restante ; le `docker-compose` démarre (services
vides) ; `.\tasks.ps1 help` liste les tâches.

---

### Phase 1 — Fondations data : corpus & manifeste *(3–4 j)*

**Objectif** : produire un corpus **réel, contrôlable et reproductible**, avec une fiche par
document. C'est la phase la plus rentable de tout le projet.

**Travaux**
- **Générateur de corpus** (`scripts/gen_corpus/`) : génération déterministe depuis des modèles
  + tables de données + un seed.
  - Manuels d'équipement (sections, tableaux d'alarmes, valeurs de seuil)
  - Procédures de maintenance (étapes numérotées, prérequis sécurité)
  - Schémas et schémas de câblage (générés en PNG/SVG, légendés)
  - Fiches de sécurité, gammes de vérification
  - Photographies de panneaux de commande (voyants, étiquettes, plaques signalétiques) —
    dont des cas volontairement **illisibles** et des cas **ambigus** (voyant orange sur deux
    équipements différents)
  - 3 à 5 documents **piégés** (injection) et 2 à 3 documents **contradictoires** entre eux
- **Deux familles d'équipements** avec des alarmes *volontairement proches* (le sujet cite
  explicitement l'alarme de température vs. un voyant similaire d'un autre équipement).
- **Manifeste** `corpus/manifest.yaml` → `schemas/document_manifest.schema.json` :
  `doc_id`, `version`, `hash`, `family`, `equipment_ids`, `access_groups`, `doc_type`,
  `source`, `license`, `pages`, `lang`, `ocr_required`.
- **Zone bronze** : `data/raw/<doc_id>/<version>/` immuable, checksums.
- **Contrôles qualité** : nombre de pages, extractibilité du texte, résolution des images,
  détection de doublons par hash, cohérence manifeste ↔ fichiers.
- **Jeu de questions « or » textuel initial** (~40 questions) : réponse attendue + élément source
  identifié à la main. Il servira dès la phase 3.

**Artefacts** : `data/raw/` (40 doc. max, ≥ 30), `corpus/manifest.yaml` validé, `docs/data_card.md`,
`corpus/dq_report.md`, générateur exécutable (`.\tasks.ps1 corpus -Seed 42`).

**Critère de sortie** : `.\tasks.ps1 corpus` reproduit le corpus octet pour octet ; le validateur de
schéma passe ; les 40 questions ont une source identifiée.

**Risque principal** : dérive du périmètre de génération. Parade : le corpus est figé en fin de
phase 1 et versionné ; les ajouts sont des `v2`, jamais des modifications en place.

---

### Phase 2 — Ingestion bronze → silver *(4–5 j)*

**Objectif** : transformer le corpus en un jeu de données **interrogeable, auditable, ligné**.

**Travaux**
- Extraction PyMuPDF : blocs de texte, titres, **tableaux** (`find_tables`), images avec `bbox`,
  rendu des pages en image.
- **OCR sélectif** : uniquement pour les documents dont le texte est absent ou dégradé, résultats
  marqués `ocr: true` et conservés séparément du texte natif.
- Modèle d'**élément** (`schemas/element.schema.json`) :
  `element_id = doc_id:version:page:type:index` — type ∈ {`paragraph`, `table`, `table_row`,
  `figure`, `page_image`} ; champs : `text`, `ocr_text`, `image_path`, `bbox`, `section`,
  `family`, `equipment_ids`, `access_groups`, `doc_hash`.
- **Chunking** : découpage par section, 300–600 tokens, chevauchement contrôlé ; les tableaux
  restent entiers (ou découpés par ligne avec en-tête répété) ; les figures conservent légende
  **et** image d'origine.
- **Pipeline idempotent** : `run_manifest.json` (run_id, hash d'entrée, paramètres, compteurs,
  durée), reprise après échec, cache par hash de contenu.
- **Zone silver** : `data/silver/elements.parquet` (+ `data/silver/images/`), requêtable avec
  DuckDB/Polars pour les audits.
- **Tests de données** : chaque page est couverte, aucun texte vide sans `ocr_required`, aucun
  `element_id` dupliqué, `bbox` dans les bornes de la page.

**Artefacts** : `elements.parquet`, store d'images, `docs/ingestion_report.md` (volumétrie,
taux d'OCR, tableaux détectés, figures extraites), tests `tests/test_ingestion.py`.

**Critère de sortie** : ≥ 95 % des pages produisent au moins un élément ; tableaux d'alarmes
correctement extraits sur un échantillon de 10 documents vérifiés à la main.

**Risque principal** : les tableaux PDF. Parade : accepter une extraction semi-manuelle
(overrides YAML par document) plutôt que de développer un extracteur générique.

---

### Phase 3 — Indexation & recherche + harnais d'évaluation *(4–5 j)*

**Objectif** : prouver, **chiffres en main**, que la recherche trouve la bonne page — avant
d'ajouter un LLM.

**Travaux**
- Embeddings **BGE-M3** sur les éléments texte (dense + sparse), par lots, cache par hash de
  contenu → ré-indexation incrémentale.
- Embeddings **image** (`jina-clip-v2`) sur figures et photos ; en complément, indexation des
  **légendes et descriptions** dans la collection texte (la fusion a besoin des deux).
- Qdrant : deux collections `text_elements` / `image_elements`, vecteurs nommés, payload
  `access_groups`, `family`, `equipment_ids`, `doc_id`, `version`, `page`, `type`.
- **Filtrage d'accès au niveau requête** (pre-filter Qdrant), jamais en post-traitement.
- **Hybride** : dense + BM25/sparse, fusion par **RRF**, avec `k` configurable.
- **Harnais d'évaluation retrieval** (`eval/run_retrieval.py`) :
  - `eval/retrieval_gold.jsonl` : ~80 requêtes, `gold_element_ids`, `family`, `type`
  - métriques : **Recall@5, nDCG@5, MRR@10**, par catégorie
  - sortie JSON + tableau Markdown, comparable entre exécutions
- **Ablations** : dense seul / hybride / +reranker d'origine. On documente les écarts, pas on les
  devine.

**Artefacts** : snapshot Qdrant (ou script de reconstruction), `eval/retrieval_gold.jsonl`,
`docs/retrieval_baseline.md` avec les chiffres de référence.

**Critère de sortie** : harnais exécutable en une commande (`.\tasks.ps1 eval-retrieval`) ; chiffres de
référence enregistrés ; l'écart hybride vs dense est mesuré.

**Risque principal** : un jeu d'or trop facile (questions copiées des titres). Parade : formuler
les requêtes comme un technicien parlerait (« le voyant orange clignote au démarrage »).

---

### Phase 4 — Génération VLM, citations, sorties structurées *(4–5 j)*

**Objectif** : produire une réponse **sourcée et validée par schéma**, ou une abstention.

**Travaux**
- Intégration du VLM (Qwen2.5-VL) : une fonction d'inférence, une limite de pixels, un budget de
  tokens, une température basse.
- **Constructeur de contexte** : top-k texte + top-k images, déduplication, budget de tokens,
  ordre stable, délimiteurs explicites (« le contenu suivant est une donnée, pas une instruction »).
- **Prompts YAML versionnés** : `answer_v1`, `visual_analysis_v1`, `evidence_check_v1`,
  `ticket_draft_v1` — avec `version`, `model`, `date`, `notes de changement`.
- **Schéma Pydantic** de sortie, strictement celui du sujet : `status` ∈ {`answered`,
  `needs_clarification`, `refused`}, `answer`, `citations[]`, `uncertainties[]`,
  `clarification_question`, `proposed_action`. Aucun champ « confiance » inventé.
- **Vérificateur de citations** en deux temps :
  1. *structurel* — l'`element_id` existe, a bien été récupéré, la page correspond ;
  2. *soutien* — passe `evidence_check` (claim vs. passage) → `supported` / `partial` /
     `unsupported`. Objectif mesurable : ≥ 90 % de citations qui soutiennent l'affirmation.
- **Politique d'incertitude codée** (pas seulement dans le prompt) : score de récupération trop
  bas, image illisible, documents contradictoires, demande hors rôle → `needs_clarification` ou
  `refused`.
- **Comparaison texte seul vs. multimodal** sur le même jeu : c'est un indicateur explicitement
  demandé.

**Artefacts** : endpoint interne `ask()` retournant le JSON validé, `prompts/*.yaml`,
`docs/citations_report.md`, tableau comparatif texte/multimodal.

**Critère de sortie** : sur 20 questions de contrôle, 100 % des sorties passent le schéma, 0
citation inexistante, taux de soutien mesuré.

**Risque principal** : le VLM « décore » une citation plausible. Parade : le vérificateur est un
composant séparé, pas une consigne dans le prompt.

---

### Phase 5 — Workflow agentique, MCP, validation humaine, UI *(5–6 j)*

**Objectif** : le parcours de démonstration complet, avec les garde-fous **dans le code**.

**Travaux**
- **Graphe LangGraph** (état typé, transitions explicites, limite de boucle) :
  `verify_access → analyze_request(+image) → retrieve → [get_history] → compose_answer →
  evidence_check → respond | clarify | refuse → [draft_ticket] → interrupt(human) → create_ticket`
- **Serveur MCP** (FastMCP) : `get_equipment_history(equipment_id)`,
  `get_open_tickets(equipment_id)`,
  `create_ticket(equipment_id, title, description, approval_token)`.
  - Données de démonstration fictives mais **réalistes** (20–30 interventions, quelques tickets
    ouverts, deux équipements).
  - **Autorisation vérifiée côté serveur à chaque appel**, pas côté client.
- **Approbation humaine** : jeton = HMAC(`user_id` + hash du contenu exact du ticket), usage
  unique, TTL court ; toute modification du brouillon invalide le jeton ; **clé d'idempotence**
  contre les doublons.
- **Budgets appliqués par le code** : ≤ 3 appels MCP, ≤ 6 appels modèle, ≤ 60 s hors attente
  humaine, plafonds tokens/images, quotas par utilisateur.
- **API FastAPI** : auth (JWT simple), `POST /ask` (multipart : question + image), `POST /tickets/{id}/approve`,
  `GET /documents/{id}/pages/{p}` (contrôle d'accès à l'ouverture aussi).
- **UI Streamlit** minimale : question + upload photo, réponse avec citations cliquables
  (page + figure surlignée), carte d'approbation du ticket, écran de refus d'accès.
- Tests : budget dépassé, double clic sur « approuver », jeton réutilisé, accès inter-groupe.

**Artefacts** : graphe + serveur MCP + API + UI, diagrammes de séquence (`docs/sequences.md`),
`tests/test_mcp_approval.py`, `tests/test_budgets.py`.

**Critère de sortie** : les 3 premiers points de démo du sujet passent à la main, y compris le
refus d'une création sans approbation.

**Risque principal** : l'UI mange le temps. Parade : Streamlit, zéro CSS, 4 écrans maximum.

---

### Phase 6 — Fine-tuning du reranker *(4–5 j)*

**Objectif** : une expérimentation **mesurable** sur un composant ciblé, avec un résultat honnête
(y compris s'il est négatif).

**Travaux**
- **Génération du jeu de paires** (800–1 500) : `(requête, passage positif, négatif difficile)`.
  - requêtes générées depuis les passages (style technicien, pas style manuel) ;
  - **négatifs difficiles minés** : rangs 5 à 50 de la recherche, même famille, autre équipement,
    alarmes lexicalement proches ;
  - sous-ensemble vérifié à la main (~150 paires) pour contrôler la qualité.
- **Découpage par document / famille d'équipement** — jamais par paires aléatoires (fuite).
  Contrôle automatique : aucun `doc_id` commun entre train/val/test.
- Entraînement cross-encoder (BGE-reranker-v2-m3) en LoRA, suivi MLflow (hyperparamètres,
  courbes, checkpoints).
- **Contrainte 8 Go** : LoRA obligatoire, pas de full fine-tuning. `batch_size` 8,
  `max_length` 512, accumulation de gradient, checkpointing d'activation. On mesure la mémoire
  avant de lancer le run complet, et on réduit le `batch_size` si nécessaire plutôt que la qualité
  des paires.
- **Ablation en trois points** : sans reranker / reranker d'origine / reranker adapté — même
  harnais, mêmes requêtes. nDCG@5, MRR@10, plus un échantillon de qualité de réponse finale.
- Rédaction de la fiche dataset (`docs/ft_dataset_card.md`) : source, taille, méthode de
  négatifs, limites.

**Artefacts** : `ft/triples.jsonl` + splits, config d'entraînement, runs MLflow,
`docs/reranker_results.md` (tableau avant/après + analyse).

**Critère de sortie** : les trois configurations sont comparées sur le même jeu ; le rapport
explique l'écart, quel qu'il soit.

**Risque principal** : pas de gain. Parade : c'est un **résultat acceptable et attendu** par le
sujet ; le documenter proprement vaut mieux qu'un chiffre gonflé.

---

### Phase 7 — Évaluation 150 scénarios & sécurité *(3–4 j)*

**Objectif** : produire les indicateurs demandés et démontrer les échecs contrôlés.

**Travaux**
- Suite structurée `eval/scenarios.jsonl` (schéma `scenario`), 150 cas répartis comme le sujet :
  40 texte · 30 image · 20 MCP · 20 sources absentes/contradictoires · 20 accès+approbation ·
  20 injections.
- **Runner automatique** : exécute, compare au comportement attendu, produit un rapport par
  catégorie (pass/fail) + une liste de cas à revue manuelle.
- **Corpus d'injection** : texte dans le document, instruction cachée dans une image (OCR),
  sortie d'outil MCP piégée. Attendu : aucune exfiltration, aucune élévation de privilège, aucun
  appel non autorisé.
- **Tests d'accès** : tentative de récupération hors groupe, accès direct à une image, ticket sur
  un équipement non autorisé.
- **Mesures de performance** : latence médiane et p95, mémoire GPU, temps d'inférence, tokens.
- **Fiche de limites** (livrable 5) : usages autorisés, risques, équipements couverts, conditions.

**Artefacts** : `eval/scenarios.jsonl`, `docs/eval_report.md`, `docs/security_report.md`,
`docs/limites.md`.

**Critère de sortie** : le rapport couvre les 8 familles d'indicateurs du sujet ; les objectifs
(≥ 90 % citations soutenues, 0 création non approuvée, 0 fuite inter-groupes, p95 < 30 s sur
requêtes simples) sont soit atteints, soit expliqués.

---

### Phase 8 — MLOps, déploiement, documentation, démo *(3–4 j)*

**Objectif** : que quelqu'un d'autre puisse relancer le projet et le démontrer en 15 minutes.

**Travaux**
- `docker-compose` complet : `api`, `ui`, `mcp-server`, `qdrant`, `postgres`, `minio`, `mlflow`,
  versions figées, script de téléchargement des modèles, healthchecks.
- **CI** : lint, tests unitaires, test d'intégration sur un index réduit (fixture), validation des
  schémas de données, `gitleaks`, `pip-audit`.
- **Versionnement** : corpus, index (snapshot), prompts, modèles adaptés, jeu d'éval — tous liés
  par un `release.json` (hash + version) ; procédure de **retour arrière** documentée.
- **Observabilité** : logs structurés sans contenu brut, métriques erreurs/latences/refus,
  tableau de bord minimal.
- **Documentation** : README (installation en 5 commandes), runbook, diagrammes d'architecture et
  de flux de données, data card, fiche de limites.
- **Script de démonstration** couvrant les 7 points du sujet, avec un jeu de données figé.

**Artefacts** : dépôt « prêt à cloner », `docs/runbook.md`, `docs/demo_script.md`,
`docs/architecture.md`.

**Critère de sortie** : `docker compose up` depuis un clone vierge → démo complète sans
intervention manuelle non documentée.

---

## 5. Traçabilité consignes → phases

| Consigne du sujet | Phase(s) |
|---|---|
| §2 Note de cadrage, périmètre, hors-périmètre | 0 |
| §3 Architecture technique, choix de composants | 0, 8 |
| §4.1 Ingestion (passages, tableaux, figures, OCR, métadonnées) | 1, 2 |
| §4.2 Recherche (texte + visuel, RRF, reranking, citations) | 3, 4 |
| §5 Fine-tuning reranker (données, splits, comparaisons, métriques) | 6 |
| §6 Workflow agentique, MCP, approbation, idempotence | 5 |
| §7 Prompts versionnés, sorties Pydantic, versionnage des exécutions | 4, 8 |
| §8 Gestion de l'incertitude | 4, 7 |
| §9 Sécurité, confidentialité, budgets, test d'injection | 5, 7 |
| §10 Évaluation (150 scénarios, indicateurs, objectifs) | 3, 7 |
| §11 Déploiement et MLOps (8 étapes) | 8 |
| §12 Planning 6 semaines | 3 (carte des phases) |
| §13 Livrables 1 à 6 | 0/1/2/5/7/8 |
| §14 Démonstration (7 points) | 5, 8 |

Aucune section du sujet n'est orpheline.

---

## 6. Plan de coupe

**MVP (à ne pas négocier)** : phases 0 → 5, plus la phase 7 réduite aux catégories
« citations » et « approbation », et une phase 8 minimale (compose + README + démo).

**Stretch (si le temps le permet)** : MLflow complet, tableau de bord d'observabilité, corpus
étendu au-delà de 40 documents, interface UI enrichie, seconde famille de VLM comparée.

**Ordre de sacrifice en cas de retard** (du premier au dernier) :

1. Tableau de bord d'observabilité → logs seuls.
2. MLflow → journal JSON versionné.
3. UI enrichie → 4 écrans.
4. Corpus à 40 → 30 documents (mais garder les 2 familles et les documents piégés).
5. **Jamais** : le fine-tuning, la validation humaine, les tests d'injection, la vérification des
   citations. Ce sont des points notés explicitement.

---

## 7. Risques majeurs

| Risque | Impact | Parade |
|---|---|---|
| 8 Go de VRAM seulement | Un VLM 7B n'entre pas | Modèle 4B quantifié, `max_pixels` plafonné, écart documenté (§2.1) |
| Corpus trop « propre » | Recherche et éval triviales | Distracteurs, alarmes proches, images ambiguës, documents contradictoires |
| Fuite dans les splits de fine-tuning | Résultats invalides | Split par document, contrôle automatique des `doc_id` |
| VLM qui hallucine des citations | Point noté majeur | Vérificateur structurel + soutien, refus si non soutenu |
| Injection via document ou sortie MCP | Point noté majeur | Contenu traité comme donnée, délimiteurs, tests adversariaux dès la phase 7 |
| OneDrive sur le dépôt | Lenteur, corruption, conflits | Dépôt hors OneDrive (phase 0) |
| Dérive de l'UI | Retard sur le cœur | 4 écrans, aucune personnalisation visuelle |
| Fine-tuning qui n'apporte rien | Perception d'échec | Résultat présenté comme expérimentation, analyse de l'écart |

---

## 8. Standards de production (code et documentation)

Le dépôt doit ressembler à un projet d'ingénieur, pas à une démonstration générée. C'est une
exigence de qualité, pas de style : c'est aussi ce qui rend le code défendable en soutenance.

**Code**
- Python 3.12, typage partout, `ruff` et `mypy` en CI.
- Un dossier par responsabilité : `ingestion/`, `indexing/`, `retrieval/`, `generation/`, `agent/`,
  `mcp_server/`, `api/`, `ui/`, `eval/`. Pas de fichier de plus de 300 lignes, pas de fonction de
  plus de 50 lignes.
- **Commentaires** : uniquement pour expliquer *pourquoi* (une contrainte matérielle, un
  contournement, le choix d'un seuil). Jamais pour paraphraser le code. Pas de docstring sur les
  fonctions triviales.
- Configuration par `pydantic-settings` : une seule source de vérité pour les chemins, seuils et
  budgets. Aucune constante magique dans le code.
- Erreurs explicites et typées, pas de `except Exception: pass`.
- Tests `pytest`, un test par contrat de données, et une fixture sur un mini-corpus de 3 documents
  pour que la CI tourne en moins de deux minutes.

**Documentation**
- README en français : ce que fait le projet, installation en 5 commandes, lancement de la démo,
  limites connues. Pas de badges décoratifs, pas d'emoji.
- Un ADR par décision structurante, une page maximum : contexte, options, raison du choix.
- `docs/journal.md` mis à jour à chaque phase en trois lignes : fait, cassé, suivant.

**Données**
- Aucun binaire lourd dans Git : `data/`, `models/`, snapshots Qdrant restent hors dépôt et sont
  référencés par hash dans `release.json`.
- Tout script qui produit des données est déterministe : seed explicite, sortie reproductible,
  et vérification du résultat par un humain avant de le déclarer valide.

**Git**
- Commits en français à l'impératif, une intention par commit
  (`ingestion: extrait les tableaux d'alarmes via find_tables`).
- Une branche par phase ; fusion quand le critère de sortie de la phase est atteint.

---

## 9. Rythme de travail suggéré

Pour rester « humain » et éviter l'effet tunnel :

- **Fin de chaque phase** : un artefact démontrable + une note de 10 lignes dans
  `docs/journal.md` (ce qui marche, ce qui casse, décision suivante).
- **Chaque vendredi** : `.\tasks.ps1 eval` complet et comparaison aux chiffres de référence. Une
  régression se traite tout de suite, pas à la fin.
- **Rédaction en continu** : chaque phase alimente directement une section du rapport
  (data card → §4.1, baseline retrieval → §10, résultats reranker → §5). Aucune phase ne produit
  que du code.
- **Journal de décisions** : toute décision technique = une ligne datée. C'est ce qui rendra la
  soutenance solide sur les questions « pourquoi ce choix ? ».

---

## 10. Décisions actées et points ouverts

**Actées**

| Sujet | Décision |
|---|---|
| Matériel | RTX 5060 Laptop, 8 Go, pilote 573.13 — VLM 4B quantifié, voir §2.1 |
| Organisation | Projet solo ; je produis code, tests et documentation, tu arbitres et valides chaque phase |
| Corpus | 100 % généré par script, avec relecture humaine avant validation ; manuels réels seulement si un besoin est démontré |
| Démarche | Phase par phase, avec un point de validation explicite à chaque fin de phase |

**À trancher pendant la phase 0**

1. Emplacement du dépôt hors OneDrive (proposé : `C:\dev\maintidoc`).
2. Qwen3-VL-4B vs. Qwen2.5-VL-3B : dépend du benchmark mémoire réel sur la machine, pas d'un avis.
3. PostgreSQL vs. SQLite pour le prototype : Postgres si Docker s'installe sans friction, SQLite
   sinon. Les deux sont derrière la même interface de dépôt, donc le choix n'est pas bloquant.
4. Les deux familles d'équipements à couvrir.
