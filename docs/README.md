# Documentation

| Fichier | Contenu |
|---|---|
| `cahier-des-charges.pdf` | Projet, périmètre (binôme), acteurs, architecture, feuille de route sécurité |
| `recueil-des-besoins.pdf` | Besoins fonctionnels, justification de l'approche SRE, SQUARE étapes 1 à 9, exigences de sécurité, traçabilité |
| `exigences.csv` | Référentiel des exigences de sécurité (priorité AHP, statut, version) — séparateur `;` |

## Gestion des exigences

Le référentiel unique est `src/data.py` : **toute évolution d'exigence se fait là**, puis on régénère.

```bash
pip install reportlab numpy      # + Graphviz (commande `dot`)
cd docs/src && ./build.sh
```

Le script régénère les diagrammes, les deux PDF et `exigences.csv`. Pensez à incrémenter `VERSION`
et à ajouter une ligne d'historique dans `cdc.py` / `rdb.py` (section 11 du recueil).
