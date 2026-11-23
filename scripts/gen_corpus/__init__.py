"""Generateur du corpus documentaire de MaintiDoc.

Trois modules, trois responsabilites :

- `catalogue` : la source unique de verite (equipements, codes de defaut,
  liste des documents). Rien d'autre ne definit ces donnees.
- `images` : les visuels (photos de panneaux, plaques, schemas).
- `render` : la mise en page PDF, parametree par le catalogue.
- `inventaire` : l'ecriture de l'inventaire, a partir des fichiers produits.

Point d'entree : `python -m scripts.gen_corpus`. Verification : `python -m
scripts.gen_corpus.verifier`.
"""
