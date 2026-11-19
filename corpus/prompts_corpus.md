# Prompts utilisés pour constituer le corpus

Ce fichier est exigé par le livrable 1. Il trace chaque prompt employé pour
chercher ou générer un document du corpus, avec l'outil et la date.

## Convention

- Les prompts sont numérotés `P01`, `P02`, … dans l'ordre chronologique.
- La colonne `outil_ia` de `inventaire.csv` renvoie à ce numéro, par exemple
  `ChatGPT (P03)`.
- Un prompt peut produire plusieurs documents : la colonne `outil_ia` des
  documents concernés porte le même numéro.
- Le champ **Résultat** décrit ce qui a été produit, et le champ **Défauts
  relevés** liste ce qui a dû être corrigé après relecture. Un prompt sans
  défaut relevé est un prompt dont on n'a pas assez cherché les erreurs.

## Format d'une entrée

### P01 — <intitulé court>

- **Date** : AAAA-MM-JJ
- **Outil** : ChatGPT / Claude / Gemini / Mistral Le Chat
- **Objectif** : ce que le prompt devait produire
- **Prompt** :

```
<texte exact du prompt>
```

- **Documents produits** : `document_id` concernés
- **Résultat** : ce qui a effectivement été obtenu
- **Défauts relevés** : erreurs, incohérences, inventions, à corriger
- **Corrections appliquées** : ce qui a été modifié dans le document final

---

<!-- Les entrées commencent ici, à la génération du corpus. -->
