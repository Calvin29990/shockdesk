# ShockDesk

Le pendant **desk** de ShockLab : une plateforme de recherche et de backtest à la
forme Blueshift, pour passer du scénario publié au trade testé.

Une stratégie est un fichier Python. Un backtest est une URL. Une prévision est
une révision datée qu'on corrige mois après mois sans réécrire l'historique.

```
/research/strategies/3395e5bb-…-d052adcf9023/code
    ?name=global-macro&startCapital=25500000
    &startDate=2026-07-01&endDate=2026-08-28&action=backtest
```

---

## Démarrage

```bash
./run.sh                      # crée le venv, installe, lance sur http://0.0.0.0:8050
```

ou à la main :

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m shockdesk.cli serve --host 0.0.0.0 --port 8050
```

Puis ouvrir `/` : l'application redirige vers la première stratégie avec ses
paramètres par défaut, et `action=backtest` déclenche l'exécution au chargement.

---

## Ce que fait la phase 1

| Onglet | Contenu |
|---|---|
| **Code** | Éditeur Python (coloration, numéros de ligne, `Ctrl+S`, `Ctrl+Entrée` pour lancer), univers et prévisions actives en regard |
| **Backtest** | Métriques, courbe d'équité vs benchmark, drawdown, attribution par ligne, grecs du book, signaux `record()`, positions, transactions, journal |
| **Anticipation** | Par sous-jacent : la prévision active, sa validation face au marché, et les structures d'options cohérentes avec elle (P&L par nœud de la grille d'amplitudes) |
| **Options** | Atelier de pricing : strangle, straddle, butterfly, iron condor, spreads, risk reversal, calendar — payoff, points morts, grecs, choc d'IV, régime de vol |
| **API & doc** | L'API disponible dans le code, les trois portes d'entrée (URL / HTTP / CLI), les règles de discipline |

### Écrire une stratégie

```python
"""Ma stratégie — une phrase qui la résume."""

WEIGHT = 0.30

def initialize(context):
    context.asset = symbol('BZ=F')
    schedule_function(trade, date_rules.every_day())

def trade(context, data):
    f = get_forecast('BZ=F')          # prévision active, sans fuite d'information
    if f is None:
        return
    if f.sign > 0:
        order_target_percent(context.asset, WEIGHT)
        call = option_contract('BZ=F', 'call', moneyness=1.05, days=30)
        put  = option_contract('BZ=F', 'put',  moneyness=0.95, days=30)
        order(call, 10); order(put, 10)
    record(signal=f.sign, iv=get_iv('BZ=F', 1.0, 30))
```

L'API reprend la forme Zipline/Blueshift (`initialize`, `handle_data`,
`schedule_function`, `order_target_percent`, `data.history`, `record`…) et y
ajoute la couche ShockDesk : `get_forecast`, `option_contract`, `get_iv`,
`vol_regime`.

---

## Stratégies livrées

| Fichier | Idée | Univers |
|---|---|---|
| `shock-lab-oil.py` | Le book multi-actifs du scénario publié, avec stop calendar **et** take-profit au jour de pic | `global-macro` |
| `long-strangle-shock.py` | Acheter du gamma des deux côtés quand l'amplitude attendue dépasse la prime payée | `global-macro` |
| `butterfly-peak.py` | Le trade du timing : corps du butterfly sur le niveau de pic prévu | `global-macro` |
| `short-strangle-carry.py` | Vendre la prime quand aucune prévision de choc n'est active | `us-equities` |
| `iron-condor-range.py` | Même idée, risque borné par des ailes achetées | `us-equities` |
| `us-equities-momentum.py` | Référence : momentum 6-1 mensuel avec filtre de tendance | `us-equities` |

### Ce que donne l'exercice de démonstration

Sur le jeu hors ligne (fenêtre du scénario publié, book de 25,5 M$) :

| Règle de sortie | P&L figé |
|---|---|
| Take-profit au jour de pic du modèle (J+7) | **+395 919 $ (+1,55 %)** au 22/07 |
| Stop calendar du 05/08 | **−4 054 $ (−0,02 %)** |

Attribution au stop : `^GSPC +105 k$ · TLT +23 k$ · DX-Y.NYB +23 k$ · DBC +13 k$ ·
HYG +5 k$ · GC=F −65 k$ · BZ=F −118 k$`.

C'est la leçon de l'exercice, rejouée : **le signal de timing vaut de l'argent, la
vue directionnelle sur le brut non**, et c'est l'architecture du book qui porte le
P&L. Basculez `TAKE_PROFIT_AT_PEAK` en tête de stratégie pour comparer les deux
règles.

Validation des prévisions sur la même fenêtre : **accord de signe 5/6** (net du
drift), **erreur de timing du pic : 1 jour** (médiane), **amplitude sous-estimée
×3,7 sur le Brent**, **miss : l'or**.

---

## Anticiper, puis corriger

Le registre `config/forecasts.json` porte les prévisions. Chaque prévision a une
liste de **révisions datées** :

```json
{
  "id": "shocklab-2026-07-oil",
  "name": "Choc pétrolier — Brent",
  "asset": "BZ=F",
  "benchmark": "^GSPC",
  "stop_date": "2026-08-05",
  "revisions": [
    {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.05,
     "peak_day": 7, "reversion": -0.03, "iv_shift": 0.10, "confidence": 0.6},
    {"rev": 2, "date": "2026-08-28", "sign": 1, "amplitude": [0.05, 0.10, 0.185],
     "peak_day": [7, 9], "reversion": -0.065, "iv_shift": 0.14,
     "note": "amplitude passée en grille, sous-estimée d'un facteur ~3,7"}
  ]
}
```

* `get_forecast(sym)` dans une stratégie ne renvoie que la dernière révision
  publiée **avant** la date du bar. Aucune fuite d'information : un backtest ne
  peut pas profiter d'une correction faite après coup.
* Le scorecard ne compte que la révision **originale** (r1) : une correction ne
  peut pas améliorer un score ex-post. Elle reste affichée.
* `amplitude` et `peak_day` acceptent une valeur ou une **grille** : la phase 1
  apprend à donner une fourchette plutôt qu'un chiffre.

Ajouter une révision : depuis l'onglet Anticipation (formulaire en bas de chaque
carte), ou en API :

```bash
curl -X POST localhost:8050/api/ledger/shocklab-2026-07-oil/revision \
  -H 'Content-Type: application/json' \
  -d '{"sign":1,"amplitude":[0.05,0.12],"peak_day":[7,9],"reversion":-0.06,
       "iv_shift":0.12,"confidence":0.55,"note":"revue de septembre"}'
```

---

## Données

Trois sources, essayées dans cet ordre :

1. **`yfinance`** — données réelles. Installez le paquet (`pip install yfinance`)
   et c'est lui qui répond.
2. **`data/*.csv`** — un fichier par sous-jacent, colonnes `date,open,high,low,close`
   (`,` ou `;`). Pour travailler hors ligne sur des données réelles exportées.
3. **Générateur synthétique** — modèle factoriel à 7 facteurs (SPX, OIL, RATES,
   GOLD, USD, CREDIT, VOL), betas explicites dans `shockdesk/config.py`,
   déterministe, avec la reconstruction de l'exercice publié de juillet 2026.

**La source utilisée est affichée en permanence** dans le bandeau supérieur :
badge vert = données réelles, badge orange = synthétique. Ne lisez jamais un
chiffre du mode synthétique comme une donnée de marché.

La calibration (niveaux de référence, volatilités, betas, IV de base) se corrige
dans `config/calibration.json` — voir `config/calibration.example.json`. C'est le
fichier à reprendre à chaque revue mensuelle.

---

## Univers

| `name` | Contenu |
|---|---|
| `global-macro` | Le book ShockLab : Brent, S&P 500, TLT, or, dollar, HYG, DBC |
| `us-equities` | SPY, QQQ, AAPL, MSFT, NVDA, XLE, XLF, TLT — options activées |
| `energy-shock` | BZ=F, CL=F, XLE, XOP, UNG, TLT |
| `rates-fx` | TLT, IEF, HYG, DX-Y.NYB, EURUSD |
| `options-lab` | SPY, QQQ, TLT, GC=F, BZ=F |

Ajouter un sous-jacent ou un univers : `shockdesk/config.py` (`_ASSETS`,
`UNIVERSES`). Ajouter un choc historique : `SHOCK_EVENTS` / `PRICE_OVERLAYS` dans
`shockdesk/marketdata.py`.

---

## Trois portes d'entrée, une grammaire

```bash
# 1. URL
/research/strategies/<uuid>/code?name=…&startCapital=…&startDate=…&endDate=…&action=backtest

# 2. API
curl -X POST localhost:8050/api/backtest -H 'Content-Type: application/json' \
  -d '{"strategy_id":"<uuid>","name":"global-macro","startCapital":25500000,
       "startDate":"2026-07-01","endDate":"2026-08-28","action":"backtest"}'

# 3. CLI
.venv/bin/python -m shockdesk.cli backtest --strategy shock-lab-oil \
  --name global-macro --start-capital 25500000 \
  --start-date 2026-07-01 --end-date 2026-08-28

.venv/bin/python -m shockdesk.cli strategies
.venv/bin/python -m shockdesk.cli scenarios --name global-macro
.venv/bin/python -m shockdesk.cli option-lab --underlying SPY --structure butterfly --days 30
```

Autres points d'API : `/api/universes`, `/api/strategies` (GET/POST),
`/api/strategies/<id>/code` (PUT), `/api/scenarios`, `/api/options/quote`,
`/api/ledger` (GET/POST), `/api/ledger/<id>/revision`, `/health`.

---

## Règles de la maison

1. **Pas de fuite d'information.** Les prévisions sont lues point-in-time.
2. **Le sens se mesure net du drift.** Le score déduit le benchmark, pondéré par
   le beta de la ligne. Le benchmark lui-même n'est pas un test.
3. **Le stop est fixé ex-ante.** Il est porté par la prévision, pas décidé en
   regardant la courbe.
4. **Les misses sont affichés.** Un backtest sans miss n'est pas un backtest.
5. **On corrige par révision.** Jamais en réécrivant l'historique.
6. **Un modèle de choc vend du timing, pas des niveaux.** Le scorecard sépare les
   deux : erreur de pic d'un côté, ratio d'amplitude de l'autre.

---

## Tests

```bash
.venv/bin/pytest tests/ -q
```

44 tests : ancrage et reconstruction des données, parité call/put et bornes des
structures, P&L du moteur et réconciliation de l'attribution, règlement des
options à l'échéance, plafond de levier, prévisions point-in-time, scoring net du
drift, exécution des six stratégies livrées, API et page de recherche.

---

## Structure

```
shockdesk/
  config.py        univers, fiches sous-jacents, calibration factorielle
  marketdata.py    yfinance / CSV / générateur factoriel + épisodes documentés
  options.py       Black-Scholes, surface d'IV, grecs, catalogue de structures
  engine.py        boucle de backtest, portefeuille, exécution, API utilisateur
  metrics.py       Sharpe, Sortino, drawdown, beta, alpha…
  scenarios.py     prévisions révisables, scoring ex-post, recommandation de structures
  registry.py      stratégies sur disque + index UUID
  api.py           orchestration (web + CLI)
  webapp.py        application Flask, routes à la forme Blueshift
  web/             interface (vanilla JS, zéro dépendance externe)
strategies/        vos stratégies (.py) + _index.json
config/            forecasts.json (registre), calibration.json (recalibration)
tests/             suite pytest
docs/              notes de travail
```

## Déploiement

Trois façons de faire tourner ShockDesk, de la plus locale à la plus publique.

**1. En local** — `./run.sh`, puis ouvrir `http://localhost:8050`. C'est le
serveur de développement Flask : il ne doit pas être exposé.

**2. En production** — l'application expose un objet WSGI (`shockdesk/wsgi.py`),
donc n'importe quel serveur Python la sert :

```bash
gunicorn shockdesk.wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 600
```

Le dépôt contient le nécessaire pour trois hébergeurs courants, tous capables de
**se redéployer à chaque push sur GitHub** — c'est ce qui rend un lien public
vivant plutôt qu'une capture d'écran :

| Fichier | Pour | Comment |
|---|---|---|
| `render.yaml` | [Render](https://render.com) | New → Blueprint → pointer sur ce dépôt. Le plan gratuit suffit ; le healthcheck est `/health`. |
| `Procfile` | Heroku, Railway, Fly (buildpack) | détecté automatiquement |
| `Dockerfile` | tout ce qui sait lire un Dockerfile | `docker build -t shockdesk . && docker run -p 8050:8050 shockdesk` |

**3. En intégration continue** — `deploy/github-actions-ci.yml` lance les 37
tests sur Python 3.11 et 3.12 à chaque push. Le fichier est fourni hors de
`.github/workflows/` parce que le token utilisé pour construire ce dépôt n'a pas
la permission `workflows` : il suffit de le copier pour l'activer.

```bash
mkdir -p .github/workflows && cp deploy/github-actions-ci.yml .github/workflows/ci.yml
```

Ensuite ce badge devient vert ou rouge tout seul — à coller en tête de README :

```markdown
[![tests](https://github.com/Calvin29990/shockdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/Calvin29990/shockdesk/actions/workflows/ci.yml)
```

> Un lien GitHub n'est pas un site : `github.com/…` montre le code. Pour
> envoyer à quelqu'un une URL qui s'ouvre dans un navigateur **et** qui suit les
> modifications du dépôt, il faut l'étape 2 — l'hébergeur tire le code de GitHub
> et le redéploie.

## Limites connues

* Un seul bar par jour, exécution au close. Pas d'intraday.
* Options européennes synthétiques sur surface paramétrique : pas de chaîne
  d'options réelle, pas de smile calé sur le marché, pas de dividendes discrets.
* Pas de collatéral de marge : les stratégies vendeuses de prime ne sont bornées
  que par le plafond de levier (`max_leverage`, 2× par défaut).
* Pas de coût de financement (repo, emprunt de titres), pas de dividende versé.
* Le générateur synthétique est un jeu de démonstration, pas un historique réel.

Voir `ROADMAP.md` pour la suite.
