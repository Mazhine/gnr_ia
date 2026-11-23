# Protocole de relecture du corpus

## Pourquoi cette colonne existe

`inventaire.csv` contient une colonne `verifie_par` : le nom de la personne qui
a relu et validé le document. Les consignes sont explicites — « l'IA vous aide à
trouver ou produire les documents, mais ne remplace pas votre vérification » —
et la grille donne 3 points sur 20 à l'usage critique de l'IA, c'est-à-dire à la
capacité à montrer **ce qui a été corrigé**.

Un corpus de 40 documents dont aucun n'a été ouvert ne peut pas revendiquer ces
points. Il ne s'agit pas de morale : c'est un critère noté.

## Ce que « vérifier » veut dire ici

Pas de relecture intégrale. On ne cherche pas des fautes de style, on cherche
les erreurs qui cassent le système en semaine 3 :

| Ce qu'on vérifie | Pourquoi ça compte |
|---|---|
| Les identifiants d'équipement (`ASC-A-01`) sont les mêmes partout | Sinon l'historique MCP ne correspond à aucun manuel |
| Les codes d'alarme ont un seul sens | Sinon deux documents se contredisent sans que ce soit voulu |
| Les unités sont cohérentes (bar, °C, mm) | Erreur classique d'un texte généré par morceaux |
| Les renvois de page pointent vers une page qui existe | Une citation fausse est pire qu'une absence de citation |
| Le document contient bien ce que l'inventaire annonce | `elements_visuels`, `nb_pages`, `format` |

## Le protocole, en trois passes

**Passe 1 — Inventaire (10 min).** Un script compare `inventaire.csv` au disque :
autant de lignes que de fichiers, aucun orphelin, `document_id` identique au nom
de fichier. Le résultat est mécanique, tu ne fais que constater.

**Passe 2 — Contrôles ponctuels (20 min).** Les dix documents critiques ont
chacun leurs assertions dans `revue-corpus.md` :

```
asc_manuel_a.pdf
  [ ] p.2 : la charge nominale est 1000 kg / 13 personnes, vitesse 1,6 m/s
  [ ] p.4 : le seuil du défaut 33 (nivellement) est fixé à 15 mm
  [ ] p.5 : le code 51 est libellé « Défaut de porte (verrouillage) »
```

```
asc_manuel_a_v2.pdf
  [ ] p.4 : le seuil du défaut 33 est fixé à 8 mm
  [ ] p.4 : le texte dit qu'il remplace le seuil de 15 mm
```

Tu ouvres, tu regardes, tu coches. Si une assertion est fausse, tu le notes :
c'est exactement la ligne `corrections` de l'inventaire.

**Passe 3 — Cohérence transverse (15 min).** Quatre ou cinq vérifications qui
traversent plusieurs documents, celles qui font mal en semaine 3 :

- le défaut 51 du manuel A dit la même chose que dans le tableau des alarmes ;
- la procédure de consignation ne contredit pas la fiche de sécurité ;
- l'historique MCP de `ASC-A-01` cite des interventions plausibles au regard du
  manuel ;
- les deux documents marqués `contradictoire` se contredisent **volontairement**,
  sur le point annoncé ;
- le document `injection` contient bien l'instruction piégée, et uniquement là.

## Ce que je te livre

Un fichier `docs/livrable-1/revue-corpus.md` avec, pour les dix documents
critiques, trois à cinq assertions et une case à cocher, plus cinq contrôles
transverses. Une section « défauts trouvés pendant la génération » y est
remplie honnêtement.

Tu n'as pas à me croire sur parole : les assertions sont vérifiables en ouvrant
le PDF à la page indiquée.

## Si tu n'as pas le temps

Deux options défendables, à choisir explicitement et à écrire dans le rapport :

1. **Échantillon critique** : les dix documents de `revue-corpus.md` — les deux
   paires contradictoires, le document piégé, les trois scannés, les deux
   extraits en anglais. Environ 30 minutes, contrôles transverses compris.
2. **Échantillon élargi** : les dix précédents plus dix documents tirés au sort,
   environ 45 minutes. Le rapport indique alors la méthode et la taille de
   l'échantillon.

Dans les deux cas, une limite annoncée vaut mieux qu'une couverture prétendue.
Ce qui n'est pas défendable : mettre ton nom partout sans avoir ouvert un seul
fichier, puis se faire poser la question à l'oral.

## Le temps réel

| Étape | Durée |
|---|---|
| Passe 1, mécanique | 10 min |
| Passe 2, assertions | 20 min |
| Passe 3, cohérence | 15 min |
| Arbitrage des corrections à garder | 10 min |
| **Total** | **environ 55 min** |
