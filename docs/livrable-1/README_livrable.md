# MaintiDoc — Livrable 1

## Équipe

**Mazine CHATER** — travail individuel, équipe `CHATER`.

Module « IA générative multimodale », EMSI 2026. Livrable 1 : cadrage, corpus et
architecture, version 1.0 du 5 novembre 2026.

## Objectif du projet

MaintiDoc est un assistant documentaire multimodal pour un service de
maintenance. Un technicien pose une question, en texte ou avec une photo de
panneau, et reçoit une réponse **sourcée** : document, page et élément cités.
L'assistant consulte aussi l'historique des interventions via MCP et peut
préparer un ticket, mais ne le crée qu'après approbation explicite.

Le système ne pilote aucun équipement et ne remplace ni une procédure de
sécurité ni un technicien habilité.

## Contenu de cette archive

```
L1_MaintiDoc_CHATER/
├── L1_MaintiDoc_CHATER_Rapport.pdf          rapport, parties 2.1 à 2.6 + annexes
├── L1_MaintiDoc_CHATER_LienGitHub.txt       URL du dépôt
├── README.md                                ce fichier
└── L1_MaintiDoc_CHATER_Corpus/
    ├── inventaire.csv                       une ligne par document, 20 colonnes
    ├── prompts_corpus.md                    prompts P01 à P12, dates et corrections
    ├── documents/famille_1/                 20 documents, ascenseurs (Verticalis)
    ├── documents/famille_2/                 20 documents, portes (Portalis)
    └── images/                              10 images sources (photos, schémas)
```

Les quatre pièces du dossier racine sont celles demandées par les consignes ;
le dossier corpus contient l'inventaire, les prompts et les fichiers nommés
`<document_id>.<ext>`, avec le même identifiant que dans l'inventaire.

## Le corpus en trois lignes

Quarante documents synthétiques, deux familles fictives, 100 pages mesurées,
28 documents avec un élément visuel repérable, 3 scans sans couche texte (OCR
requis), 2 paires contradictoires, 1 document piégé (injection de prompt), 5 cas
ambigus. Tout est produit par un générateur Python déterministe : aucun document
réel n'est redistribué et aucune donnée personnelle n'est utilisée.

## Structure du dépôt

```
corpus/          inventaire, prompts, documents PDF et images sources
docs/            plan, périmètre, ADR 0001 à 0006, journal, livrable 1, diagrammes
scripts/         générateur de corpus, figures, rapport
src/maintidoc/   code du projet
tests/           tests unitaires
tasks.ps1        lanceur de tâches (check, test, lint, corpus, rapport)
```

Le dépôt contient le code qui produit le corpus, pas seulement le corpus : les
quarante PDF se régénèrent à l'identique par `.\tasks.ps1 corpus`, et l'inventaire
est réécrit par mesure. Les artefacts lourds (environnement virtuel, modèles,
index) vivent hors dépôt, dans `%LOCALAPPDATA%\maintidoc`.
