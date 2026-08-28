# `data/` — cache de prix locaux

Un fichier CSV par sous-jacent, nommé d'après son symbole :

| Symbole | Fichier |
|---|---|
| `BZ=F` | `BZ=F.csv` |
| `^GSPC` | `_GSPC.csv` |
| `EURUSD=X` | `EURUSD_X.csv` |

(`^` → `_`, `=` → `_`, `/` → `_`.)

Colonnes attendues, avec en-têtes, séparateur `,` ou `;` :

```
date,open,high,low,close
2026-07-15,84.10,85.40,83.90,84.95
2026-07-16,85.00,86.60,84.80,86.18
```

* `date` et `close` sont obligatoires ; `open`, `high`, `low` sont repris sur
  `close` s'ils manquent.
* Il faut un fichier pour **tous** les sous-jacents de l'univers demandé, sinon
  ShockDesk repasse sur le générateur synthétique.
* Dates ISO, une ligne par séance, ordre libre (le tri est fait au chargement).

Le badge en haut de l'interface indique la source réellement utilisée :
`csv` quand ce cache sert, `yfinance` pour des données téléchargées en direct,
`synthetic` pour le générateur.

Ce répertoire est ignoré par git (`data/*.csv`) : les prix ne sont pas du code.
