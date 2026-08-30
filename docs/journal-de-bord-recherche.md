# 📓 Journal de Bord de Recherche & Consignation Quant — ShockDesk

> **Document de veille et d'audit interne (Règle 2)**  
> Ce registre consigne silencieusement et méthodiquement l'ensemble des observations quantitatives, des écarts de calibration, des faiblesses identifiées dans les stratégies testées et des données de marché fraîches. Il sert de mémoire permanente pour les sessions Arena futures et pour le déploiement de la phase 2.

---

## 📅 Log du 30 Août 2026 — Audit Initial & Données de Référence

### 1. 🔍 Audit des Paramètres & Sous-estimations du Modèle
* **Sous-estimation d'amplitude sur le choc d'offre pétrolier (Brent `BZ=F`)** :
  * *Prévu (r1)* : +5,0 % d'amplitude au pic à J+7.
  * *Réalisé* : **+18,4 % à +18,5 %** au pic à J+8 (23 juillet).
  * *Facteur d'erreur* : **×3,68**.
  * *Insight de desk* : Les modèles scalaires d'amplitude sous-estiment systématiquement la non-linéarité des chocs géopolitiques/offre. **Action retenue** : Remplacer systématiquement toute amplitude scalaire par une grille de stress à 3 nœuds : $[0.5 \times \text{base},\ 1.0 \times \text{base},\ 3.7 \times \text{base}]$.
* **Vitesse de reversion post-pic** :
  * Le modèle r1 anticipait une décroissance lente vers −3,0 % en 21 jours.
  * La réalité a montré une chute brutale à **−6,5 % en seulement 9 séances ouvrées** après le pic.
  * *Règle quantifiée* : La reversion post-pic sur l'énergie est **deux fois plus abrupte** que la phase d'ascension (asymétrie de volatilité).

---

### 2. ⚡ Matrice Comparative des Stratégies sur la Fenêtre Juil-Août 2026

| Stratégie | Univers | Capital | P&L Net | Sharpe | Max Drawdown | Verdict de Robustesse |
|---|---|---|---|---|---|---|
| **Book Multi-actifs (`shock-lab-oil.py`)** | `global-macro` | 25,5 M$ | **+337 887 $ (+1,32 %)** | **1,67** | **−0,08 %** | **Excellente**. La prise de bénéfice à J+7 et le short S&P 500 (+82 k$) neutralisent les misses. |
| **Long Strangle (`long-strangle-shock.py`)** | `global-macro` | 1,0 M$ | **+12 084 $ (+1,21 %)** | **0,85** | **−0,39 %** | **Robuste sur gros choc**. Le Call OTM a surperformé le coût du Put et l'érosion Theta. |
| **Butterfly au Pic (`butterfly-peak.py`)** | `global-macro` | 1,0 M$ | **−22 365 $ (−2,24 %)** | **−5,92** | **−2,24 %** | **Plafond de risque validé**. L'amplitude réelle a traversé l'aile haute (+18,5 % vs +5 %), mais la perte est bornée à 100 % de la prime. |
| **Référence Momentum (`us-equities-momentum.py`)** | `us-equities` | 100 k$ | Passif | Base | Variable | Sert d'étalon de comparaison à battre en régime de tendance. |

---

### 3. 🧩 Identification des "Anticipations Naïves" vs Réalités de Marché

#### A. Le comportement de l'Or (`GC=F`) en Choc Pétrolier :
* *Hypothèse naïve macro* : "Le pétrole monte $\rightarrow$ tensions géopolitiques $\rightarrow$ achat refuge d'or $\rightarrow$ GC=F monte."
* *Réalité observée* : Le choc pétrolier a fait bondir les anticipations d'inflation et les taux réels américains, provoquant un raffermissement violent du dollar (`DX-Y.NYB`). L'or a été pénalisé par le coût d'opportunité des taux et a corrigé (**−71 k$ de contribution négative au stop**).
* *Recommandation Phase 2* : Ne plus inclure l'or comme simple valeur refuge mécanique lors d'un choc d'offre pétrolier lorsque le Dollar Index est en tendance haussière.

#### B. La duration obligataire (`TLT`) :
* *Hypothèse naïve* : "Fuite vers la qualité sur la dette souveraine."
* *Réalité observée* : Les craintes d'inflation tenace ont écrasé les obligations longues (**P&L TLT à −24,6 k$**).

---

### 4. 🚀 Pistes d'Amélioration Futures & Données à Consigner

1. **Enrichissement de l'univers Actions Énergie** :
   * Le book macro actuel n'a pas d'actions sectorielles pures.
   * *Ajout recommandé* : Intégrer les trackers `XLE` (Energy Select Sector SPDR) et `XOP` (Oil & Gas Exploration) qui réagissent avec un béta supérieur au brut tout en offrant des options très liquides.
2. **Surface d'IV Dynamique & Détection de Vega Crush** :
   * L'effondrement de l'IV post-pic (J+8) offre une opportunité de vente de volatilité (Short Strangle ou Calendar inversé) pour monétiser la seconde phase du scénario.
3. **Journal de bord des révisions futures** :
   * Noter systématiquement chaque mois le taux d'accord de signe et l'erreur médiane de timing.

---

## 📅 Log du 29 Août 2026 — Vérification expérimentale de l'Atelier 1 (session interactive)

> Entrée consignée automatiquement pendant l'atelier guidé. Objet : vérifier que les
> chiffres de référence sont reproductibles, et mesurer ce que vaut réellement le
> signal de timing de l'Atelier 1.

### 0. ⚠️ Conditions de reproductibilité — à lire avant tout chiffre

* Source effectivement utilisée par le moteur pendant cette session : **synthétique**
  (générateur factoriel déterministe). `yfinance` 1.7.0 est installé mais
  **injoignable** depuis l'environnement d'exécution
  (`SSL_connect: connection closed abruptly`, `query2.finance.yahoo.com:443`).
  Le bandeau *Provenance* de l'interface l'affiche ; aucun chiffre ne peut être
  pris pour une donnée réelle.
* Conséquence directe : les valeurs du log du 30/08 (**+337 887 $, Sharpe 1,67,
  BZ=F +187 k$**) ont été produites sur données **réelles** (Yahoo) et **ne sont pas
  reproductibles** dans cet environnement. Les écarts ci-dessous sont donc un
* **écart de source**, pas une erreur de stratégie.
* Règle ajoutée au protocole : **toute comparaison entre deux sessions doit
  d'abord vérifier la source de données** avant de commenter un P&L.

### 1. 📐 Mesures Atelier 1 — `TAKE_PROFIT_AT_PEAK` (capital 25,5 M$, `global-macro`)

| Fenêtre | `TAKE_PROFIT_AT_PEAK` | P&L | Sharpe | Max DD | Vol ann. | Trades | `BZ=F` | `^GSPC` | `GC=F` |
|---|---|---|---|---|---|---|---|---|---|
| 07-01 → 08-28 *(défaut interface)* | `True` | **+385 544 $ (+1,56 %)** | 2,256 | −0,04 % | 2,19 % | 21 | +283 621 | +55 143 | −71 012 |
| 07-01 → 08-28 *(défaut interface)* | `False` | **−14 268 $ (−0,06 %)** | −1,513 | −1,85 % | 2,90 % | 21 | −117 935 | +105 046 | −65 188 |
| 07-15 → 08-27 *(propre, avant r2)* | `True` | **+395 919 $ (+1,60 %)** | 3,463 | 0,00 % | 2,55 % | 14 | +284 541 | +59 787 | −69 978 |
| 07-15 → 08-27 *(propre, avant r2)* | `False` | **−4 054 $ (+0,03 %)** | −1,117 | −1,81 % | 3,42 % | 14 | −117 030 | +109 618 | −64 171 |

**Mécanisme confirmé par le journal moteur** (pas déduit, lu) :

* `True` → sortie le **2026-07-22, J+7** : `Sortie J+7 (pic modèle) — P&L +407 216 (+1,60 %)`.
* `False` → sortie le **2026-08-05, J+21** : `Sortie J+21 (stop calendar) — P&L +6 994 (+0,03 %)`.
* Toute la divergence se joue **après** le pic : la ligne `BZ=F` passe de
  **+284 541 $ à −117 030 $**, soit un swing de **401 571 $** entre J+7 et J+21.
* **Valeur du signal de timing (mesurée) : +399 973 $ ≈ 1,57 % du capital sur la
  fenêtre propre** — c'est la quasi-totalité du P&L de la stratégie. La vue
  directionnelle seule, sans règle de sortie, vaut ~0.
* Note de cadrage : la « −4 k$ » annoncée par le carnet d'entraînement correspond
  exactement à la fenêtre propre `False` (−4 054 $). Les autres repères du carnet
  (+337 887 $, BZ=F +187 k$) restent propres aux données réelles.

### 2. 🧪 Faiblesses identifiées — à traiter en phase 2

1. **Artefact de ré-entrée `r2` sur la dernière barre.** La révision `r2` est datée
   du **2026-08-28**, soit la dernière barre de la fenêtre par défaut. La garde
   `ONE_PASS` keyant sur `(id, rev)` considère `r2` comme un nouveau scénario : la
   stratégie **ré-ouvre le book sur la dernière barre et ne le ferme jamais**.
   Impact mesuré : **−10 375 $** sur le run `True` (395 919 → 385 544) et
   **−10 214 $** sur le run `False`, et le compteur de trades passe de 14 à 21
   (+50 %). Le P&L affiché mélange donc un trade terminé et une position ouverte.
   *Correctif suggéré : ignorer une entrée dont le stop/pic tombe après la fin de
   backtest, ou neutraliser le P&L de la position non débouclée.*
2. **Métriques de risque statistiquement vides sur cet exercice.** Sur la fenêtre
   propre `True`, **26 des 32 barres sont plates** (stratégie sortie au pic) et il
   n'y a **0 jour négatif**. D'où : Max Drawdown **0,00 %**, volatilité annualisée
   calculée sur ~5 jours actifs, Sharpe **3,463** annualisé depuis 32 observations.
   Ces chiffres sont arithmétiquement justes et **non significatifs** — ils ne
   doivent pas servir à classer la stratégie.
3. **`Sortino = 0.0` affiché comme une valeur.** La garde de `metrics.py`
   (`len(downside) > 1`) renvoie `0.0` quand le ratio est indéfini. Avec 0 jour
   négatif, l'interface affiche un Sortino nul qui se lit comme « mauvais » alors
   qu'il est *non défini*. *Correctif : renvoyer `None` et afficher « n.d. ».*
4. **Sensibilité extrême à la date de fin.** En prolongeant la fenêtre au
   2026-09-01 (35 barres), le run `True` tombe de **+385 544 $ à +159 717 $** et la
   ligne `^GSPC` **change de signe** (+55 143 → −48 783) — une deuxième passe
   perdante s'ajoute. Un résultat qui dépend à ce point du dernier jour de la
   fenêtre ne peut pas être publié tel quel.
5. **Documentation non reproductible.** Le carnet d'entraînement et ce journal
   citent des montants obtenus sous Yahoo sans mentionner la source. Toute valeur
   de référence devrait porter sa provenance + sa fenêtre + son nombre de barres.

### 3. 🧾 Données à consigner

* **Score prévisions** (07-15 → 08-28, synthétique) : signe **5/6** · erreur de pic
  **3,17 j** · ratio d'amplitude médian **1,47**. À comparer au **4/6, 1 j** du log
  du 30/08 : l'écart confirme que le score dépend lui aussi de la source de données.
* **Coût de friction** : l'équité de la première barre est de **25 488 842 $** pour
  25,5 M$ initiaux, soit **−11 158 $** de slippage + commissions à l'entrée
  (5 bps sur ~21 M$ d'exposition brute). L'aller-retour coûte donc **≈ 21 k$**,
  soit **~5 % de l'edge de timing** mesuré (400 k$). À retenir pour le
  dimensionnement : à 25,5 M$, la friction n'est pas négligeable.
* **Le miss or (`GC=F`) est confirmé indépendamment** : −69 978 $ (fenêtre propre)
  contre −71 k$ annoncés le 30/08. C'est la seule ligne négative reproductible
  d'une session à l'autre malgré le changement de source — le vrai signal faible
  du book, et le candidat n°1 de l'Atelier 3.

---

## 📅 Log du 30 Août 2026 — Captures reçues : validation sur données réelles (yfinance)

### 0. 🔬 Conditions du run utilisateur

* `shock-lab-oil` · `global-macro` · 25,5 M$ · **2026-07-01 → 2026-08-29** · **42 barres**
* Source : **yfinance — données réelles Yahoo Finance** (badge vert). Runtime : **36,7 s**.
* Paramètres : `TAKE_PROFIT_AT_PEAK = True`, `BASE_EXPOSURE = 0.85`, book inchangé.
* Le registre de prévisions du dépôt est **inchangé** : `GC=F r2` (publiée 2026-08-28) et
  `shocklab-2026-09-oil-roll` (publiée 2026-09-01) font partie de `config/forecasts.json`
  d'origine. Les chiffres diffèrent des sessions précédentes **parce que la source est
  réelle**, pas parce qu'un fichier a bougé.

### 1. ✅ Référence de l'Atelier 1 confirmée au dollar près

| Métrique | Carnet / log du 30/08 | Run réel utilisateur |
|---|---|---|
| P&L | +337 887 $ (+1,32 %) | **+337 887 $ (+1,32 %)** ✔ |
| Sharpe | 1,67 | **1,67** ✔ |
| Max drawdown | −0,08 % | **−0,08 %** ✔ |
| `BZ=F` | +187 k$ | **+187,1 k$** ✔ |

Les repères du carnet sont donc bien établis sur **données réelles** — et ne sont
reproductibles que sous Yahoo (sous générateur synthétique : +385 544 $, Sharpe 2,26).

### 2. ❌ Correction majeure : l'or n'est PAS le miss sur données réelles

* Run réel : `GC=F` = **+53,0 k$** (P&L réalisé **+54 084 $** dans la table des positions).
* Carnet (Atelier 3) et log du 30/08 : `GC=F` = **−71 k$**, qualifié de « miss de l'exercice ».
* Contrôle fait le 29/08 sous générateur synthétique : `GC=F` = **−69 978 $ / −71 012 $**.
  → Le chiffre de −71 k$ est un **artefact du générateur synthétique**, indûment recopié
  comme un fait de marché.
* Confirmation indépendante par le scorecard de l'utilisateur : « accord de signe **4/6** ·
  **misses : HYG, TLT** ». L'or y est marqué **✔** (amplitude réelle 4,9 % vs 3,0 %,
  **x1,63** ; net du drift **+4,89 %** ; pic réel J+21).
* Sur données réelles, les deux seules lignes négatives sont **HYG −11,7 k$** et
  **TLT −24,6 k$**. La narration « or = refuge défaillant » est donc **fausse sur Yahoo**.
* **Conséquence directe pour l'Atelier 3** : passer `BOOK['GC=F'] = 0.00` **retirera ~+53 k$**
  au lieu d'en ajouter ~+71 k$. Le P&L passerait de +337,9 k$ à **≈ +285 k$**, et non à
  « plus de +400 k$ ».

### 3. ⚠️ Le book sous-performe son benchmark

* Benchmark `^GSPC` **+3,05 %** sur la fenêtre contre **+1,32 %** pour le book
  → **alpha −1,73 %**, β −0,05.
* Mécanisme : le book encaisse le choc entre le 15 et le 22 juillet (sortie J+7), puis
  **reste en cash** pendant que les actions remontent. `^GSPC` rapporte +82,0 k$ sur la
  première semaine, mais le rallye suivant n'est pas capté.
* Le verdict « **Excellente** » du log du 30/08 est **benchmark-blind** : à reformuler en
  « excellente sur le choc, en retrait sur la fenêtre complète ».

### 4. 🧟 Artefact `r2` confirmé sur données réelles

* Journal moteur : sortie J+7 loguée à **+359 323 $** ; P&L final **+337 887 $**.
* Écart : **−21 436 $**. Décomposition (table des positions, book ré-ouvert le 2026-08-28
  sur 7 lignes et jamais débouclé) : ~**−11,8 k$** de frais d'entrée sur ~21 M$ d'exposition
  brute (slippage 5 bps + commissions) + ~**−9,7 k$** de latents.
* Le P&L affiché mélange donc un trade terminé et une position ouverte.

### 5. 📉 Métriques non significatives (aggravées ici)

* **Sortino 15,91** et **Calmar 102,37** : purs produits d'un drawdown max de 0,08 % sur
  42 barres (CAGR 8,43 / DD 0,08 ≈ 105). Non publiable.
* **Win rate 7,3 %** sur 21 trades (3 passes × 7 lignes) : la métrique compte des lignes,
  pas des décisions de trading.

### 6. 🎯 Score des prévisions : dépendant de la source

| | Données réelles (utilisateur) | Synthétique (29/08) |
|---|---|---|
| Accord de signe net du drift | **4/6** | 5/6 |
| Erreur de pic médiane | **7,0 j** | 3,17 j |
| Ratio d'amplitude médian | **1,07x** | 1,47x |

### 7. 🐛 Bug d'interface identifié (à corriger en phase 2)

* `shockdesk/web/static/app.js:791` : `(q.net_premium < 0 ? "débit" : "crédit")`
  — **convention inversée** par rapport à la ligne 687 du même fichier
  (`s.cost >= 0 ? "débit" : "crédit"`, elle correcte).
* Symptôme visible sur la capture « Options » : *Long strangle SPY 30 j — prime nette
  10,69 **(crédit)***, alors que la structure est achetée (perte max = prime payée = 10,69).
  Le CLI n'affiche pas le label et reste correct.

### 8. 🛢️ Le scénario pétrole, validé sur données réelles

* `BZ=F` r1 : amplitude réelle au pic **18,4 % vs 5,0 % → x3,68** (confirme le facteur
  consigné le 30/08) ; pic réel **J+8**, écart +1 j ; MFE/MAE 18,42 % / −6,47 %.
* Mais en fin de fenêtre de validation (→ 2026-08-05) : **brut −6,47 %, net du drift
  −6,38 %**. C'est la quantification exacte de la leçon de l'Atelier 1 : **au stop calendar,
  le Brent était sous le prix d'entrée.** Toute la performance du book vient de la sortie
  au pic — la vue directionnelle seule, tenue jusqu'au stop, perd.

---

## 📅 Log du 30 Août 2026 (2) — Atelier 1 exécuté : valeur du timing sur données réelles

### 1. 📐 Résultat brut (`TAKE_PROFIT_AT_PEAK`, 25,5 M$, 2026-07-01 → 2026-08-29, 42 barres, yfinance)

| | `True` | `False` | Écart |
|---|---|---|---|
| **P&L** | **+337 887 $ (+1,32 %)** | **−279 633 $ (−1,10 %)** | **−617 520 $** |
| Sharpe | 1,67 | −1,66 | — |
| Sortino | 15,91 | −1,73 | — |
| Vol annualisée | 2,40 % | 6,45 % | ×2,7 |
| Drawdown max | −0,08 % | −3,60 % | ×45 |
| Calmar | 102,37 | −1,82 | — |
| Win rate | 7,3 % | 14,6 % | — |
| Alpha (`^GSPC` +3,05 %) | −1,73 % | **−4,15 %** | — |
| β | −0,05 | −0,41 | — |
| Trades | 21 | 21 | — |

**Journal moteur, sorties loguées :**
* `True` → `2026-07-22 — Sortie J+7 (pic modèle) — P&L +359 323 (+1,41 %)`
* `False` → `2026-08-05 — Sortie J+21 (stop calendar) — P&L −258 457 (−1,01 %)`

### 2. 🔍 Décomposition de la casse (−617 520 $)

| Ligne | `True` | `False` | Écart | Part de la casse |
|---|---|---|---|---|
| `BZ=F` | +187,1 k | −117,5 k | **−304,6 k** | **49 %** |
| `^GSPC` | +82,0 k | −213,4 k | **−295,4 k** | **48 %** |
| `DBC` | +46,7 k | −16,9 k | −63,6 k | 10 % |
| `DX-Y.NYB` | +5,3 k | −10,7 k | −16,0 k | 3 % |
| `TLT` | −24,6 k | −27,4 k | −2,8 k | 0,5 % |
| `HYG` | −11,7 k | −1,0 k | +10,7 k | −2 % |
| `GC=F` | +53,0 k | +107,2 k | **+54,2 k** | **−9 % (compense)** |

**Deux lignes se partagent 97 % du dégât, à parts égales.** Ce n'est pas ce que disait
le carnet (100 % imputé au pétrole).

### 3. 💡 Enseignements à retenir

1. **Le signal de timing vaut 617 520 $ (2,42 % du capital) sur ce seul exercice** —
   davantage que le P&L total de la stratégie en l'absence de sortie au pic.
2. **La couverture actions est le vrai deuxième risque.** Le short `^GSPC` gagne +82,0 k$
   pendant le choc, puis le marché repasse au-dessus du prix d'entrée
   (7 568,614 → 7 727,412, soit +2,10 %) et la ligne devient la deuxième perte du book.
   Un take-profit au pic protège autant la couverture que la vue directionnelle.
3. **L'or est le contre-exemple : il gagne à tenir** (+54,2 k$ de plus en J+21). Une sortie
   au pic n'est pas optimale *ligne par ligne* — elle l'est au niveau du *portefeuille*.
   À ne pas confondre avec l'Atelier 3 : sur données réelles, l'or est une ligne gagnante
   dans les deux configurations.
4. **Le take-profit divise la volatilité par 2,7 et le drawdown par 45** (6,45 % → 2,40 %,
   −3,60 % → −0,08 %). C'est un effet de gestion du risque, pas seulement de performance.
5. **L'artefact `r2` est stable et mesurable** : P&L logué − P&L final = **−21 436 $** (`True`)
   et **−21 176 $** (`False`), soit ~0,08 % du capital dans les deux cas. Il s'agit
   d'une position ouverte sur la dernière barre, jamais débouclée. Correction suggérée
   (phase 2) : neutraliser le P&L des positions non débouclées en fin de backtest.
6. **Le scorecard est indépendant du paramètre** (4/6 · 7,0 j · 1,07x dans les deux runs) :
   le score mesure la qualité des prévisions, pas celle de l'exécution. Bon point de
   conception à conserver.
7. ⚠️ **Les fourchettes du carnet d'entraînement pour `False` (« −4 k$ à +99 k$ ») sont
   fausses sur données réelles** (−279 633 $ observé) : elles provenaient du générateur
   synthétique. Atelier 1 corrigé le 30/08/2026 avec les valeurs réelles.

### 9. 🐛 Piège d'interface confirmé : une modification non enregistrée est **silencieusement ignorée**

Constat : trois runs consécutifs annoncés avec `BASE_EXPOSURE` différent (0,85 → 1,00 → 0,40)
ont produit des résultats **identiques au dollar près** (P&L −279 633 $, `Exposition cible
82 %`, 60 639 145 $ échangés). Aucune erreur affichée.

Explication dans le code (`shockdesk/web/static/app.js`) :

* `runBacktest()` (l. 506) n'envoie au serveur que `{strategy_id, params}` — **pas le contenu
  de l'éditeur**. Le serveur relit donc le **fichier enregistré** sur le disque.
* La sauvegarde passe par `saveCode()` (l. 168), qui PUT sur `/api/strategies/<sid>/code`
  et affiche un toast `code enregistré dans strategies/…`.
* Le raccourci `Ctrl+S` (l. 150) est attaché **au seul `textarea` de l'éditeur**. Hors du
  champ de code, `Ctrl+S` ouvre la boîte « Enregistrer la page » du navigateur et ne
  sauvegarde rien.
* `state.dirty` (l. 136) n'est consulté **que** par le garde-fou de fermeture de page
  (l. 1025). `runBacktest` ne le teste jamais : aucune alerte n'est émise si l'on lance un
  backtest avec des modifications non enregistrées.

**Correctifs suggérés (phase 2)** : (1) `runBacktest()` doit avertir si `state.dirty` est
vrai, ou sauver automatiquement avant de lancer ; (2) afficher un indicateur « non
enregistré » permanent à côté du bouton, pas seulement à la fermeture ; (3) attacher
`Ctrl+S` au document, pas au seul éditeur.

**Règle d'atelier à retenir** : dans ShockDesk, *sauvegarder puis lancer* — et ne faire
confiance qu'au toast `code enregistré dans strategies/…`. Le témoin de bonne exécution est
dans le journal d'exécution : `Exposition cible = BASE_EXPOSURE × confiance × 1,6`, soit
**38 %** pour `0.40`, **82 %** pour `0.85`, **96 %** pour `1.00`.

### 10. 📐 Atelier 2 — mesure A : `BASE_EXPOSURE = 0.40` (données réelles)

Run validé par le témoin `Exposition cible 38 %` (r1) / `35 %` (r2), `TAKE_PROFIT_AT_PEAK = True`,
42 barres, yfinance, 25,5 M$.

| | `0.85` (référence) | `0.40` (mesure A) | Ratio |
|---|---|---|---|
| **P&L** | +337 887 $ (+1,32 %) | **+159 040 $ (+0,62 %)** | ×0,471 |
| CAGR | 8,43 % | 3,90 % | ×0,463 |
| Vol annualisée | 2,40 % | 1,13 % | ×0,471 |
| Drawdown max | −0,08 % | −0,04 % | ×0,500 |
| Montant échangé | 60 639 145 $ | 28 701 156 $ | ×0,473 |
| **Sharpe** | **1,67** | **−0,24** | ✗ non proportionnel |
| **Sortino** | **15,91** | **−2,29** | ✗ non proportionnel |
| Calmar | 102,37 | 100,56 | ✗ non significatif |
| Attribution `BZ=F` | +187,1 k | +88,1 k | ×0,471 |
| Attribution `^GSPC` | +82,0 k | +38,6 k | ×0,471 |
| Attribution `GC=F` | +53,0 k | +25,0 k | ×0,472 |
| Sortie loguée | J+7 · +359 323 $ | J+7 · +169 093 $ | ×0,471 |

**Conclusion 1 — `BASE_EXPOSURE` est bien un bouton de volume pur.** P&L, volatilité,
drawdown, montants échangés et chaque ligne d'attribution sont multipliés par le même
facteur (0,471 ≈ 0,40/0,85). Il ne change en rien la qualité de la thèse.

**Conclusion 2 — le Sharpe, lui, s'effondre et passe négatif : c'est le vrai résultat.**
* `metrics.py` l. 36-38 soustrait `rf_daily = risk_free / 252` avec **`risk_free = 0.041`
  (4,1 %)** codé en dur — et ce **chaque barre**, y compris les ~37 barres où le book est
  sorti et dort en cash.
* À `0.40`, le CAGR tombe à **3,90 %**, sous les 4,1 % du sans-risque → l'excédent devient
  négatif → Sharpe **−0,24** et Sortino **−2,29**. Arithmétiquement juste.
* ⚠️ **Mais c'est une incohérence de moteur** : `engine.py` ne crédite **aucun intérêt sur
  le cash** (le cash n'est mouvementé que par les ordres et le MTM). Une stratégie qui
  prend son profit et se met en liquidités est donc **pénalisée deux fois** : elle ne
  touche pas les 4,1 % qu'elle « aurait dû » gagner, et le Sharpe les lui retire quand même.
* **Correctifs suggérés (phase 2)** : (1) créditer le cash au taux sans risque, ou
  (2) rendre `risk_free` paramétrable et l'afficher, ou (3) neutraliser le Sharpe quand la
  stratégie est plate plus de x % des barres — et dans tous les cas **avertir** que le
  ratio n'est pas significatif sur une fenêtre majoritairement plate.
* **Règle de lecture pour le desk** : sur ce type d'exercice (book sorti au pic, ~37 barres
  sur 42 à plat), **le Sharpe et le Sortino ne doivent pas servir à classer la stratégie.**

**Prédiction chiffrée pour la mesure B (`BASE_EXPOSURE = 1.00`)** — à confronter au run :
P&L **≈ +397 000 $ (+1,56 %)** · vol **≈ 2,82 %** · CAGR ≈ 9,9 % · **Sharpe ≈ 1,9** ·
`Exposition cible 96 %` (r1) / `88 %` (r2) · échangé ≈ 71,3 M$.

### 11. 📐 Atelier 2 — mesure B : `BASE_EXPOSURE = 1.00` et démonstration du biais du Sharpe

Run validé par `Exposition cible 96 %` (r1) / `88 %` (r2). **Prédictions confirmées** :
P&L annoncé ≈ +397 000 $ → **mesuré +397 485 $** ; Sharpe annoncé ≈ 1,9 → **mesuré 1,93** ;
vol annoncée 2,82 % → **mesurée 2,83 %** ; échangé annoncé ≈ 71,3 M$ → **mesuré 71 969 163 $**.

| | `0.40` | `0.85` | `1.00` |
|---|---|---|---|
| Exposition cible (r1) | 38 % | 82 % | 96 % |
| **P&L** | +159 040 $ (+0,62 %) | +337 887 $ (+1,32 %) | **+397 485 $ (+1,56 %)** |
| CAGR | 3,90 % | 8,43 % | 9,97 % |
| Vol annualisée | 1,13 % | 2,40 % | 2,83 % |
| Drawdown max | −0,04 % | −0,08 % | −0,10 % |
| Échangé | 28,70 M$ | 60,64 M$ | 71,97 M$ |
| Alpha (`^GSPC` +3,05 %) | −2,43 % | −1,73 % | −1,50 % |
| **Sharpe affiché** | **−0,24** | **1,67** | **1,93** |
| **Sortino affiché** | **−2,29** | **15,91** | **18,32** |
| Sortie loguée | J+7 · +169 093 $ | J+7 · +359 323 $ | J+7 · +422 733 $ |

**A. La proportionnalité est vérifiée au dollar près.** Rapport à la référence `0.85` :
×0,4706 théorique pour `0.40` → P&L 159 010 $ attendu / **159 040 $** mesuré ;
×1,1765 pour `1.00` → 397 550 $ attendu / **397 485 $** mesuré. Volatilité et drawdown
suivent le même facteur (2,40 % → 1,13 % / 2,83 % ; −0,08 % → −0,04 % / −0,10 %).
`BASE_EXPOSURE` est **exactement** un bouton de volume : il ne crée aucune edge.

**B. Démonstration du biais du taux sans risque.** En recalculant le Sharpe **sans** le
terme `rf_daily` (mean(rets)/std(rets) × √252) sur les trois runs :

| `BASE_EXPOSURE` | Sharpe affiché (rf = 4,1 %) | Sharpe hors sans-risque |
|---|---|---|
| 0.40 | −0,24 | **3,36** |
| 0.85 | 1,67 | **3,36** |
| 1.00 | 1,93 | **3,36** |

**La qualité risque-ajustée du trade est identique à 3,36 dans les trois cas.** Toute la
variation du Sharpe affiché (−0,24 → 1,67 → 1,93) est produite par la soustraction d'une
constante (4,1 %/an) à un rendement qu'on fait varier. C'est la signature d'une métrique
contaminée par un terme fixe — et la confirmation directe du point 10 ci-dessus.
Correctif de priorité 1 en phase 2 : cesser de retirer le sans-risque à un book qui dort
en cash non rémunéré, ou au minimum afficher les deux valeurs.

**C. Alpha : le levier ne rattrape pas le benchmark.** L'alpha passe de −2,43 % à −1,50 %
quand on monte l'exposition de 0,40 à 1,00 : il reste **négatatif** dans tous les cas.
Le levier amplifie l'edge, il n'en crée pas — et il ne corrige pas un sous-benchmark.

**D. Prédiction pour l'Atelier 3 (`BOOK['GC=F'] = 0.00`, `BASE_EXPOSURE = 0.85`).**
Le poids des lignes est normalisé par l'exposition brute (`total = Σ|w|`). Retirer l'or
fait passer `total` de **0,94 à 0,84**, donc **chaque ligne restante est multipliée par
1,119** : le book ne perd pas le poids de l'or, il le **redistribue**.
D'où P&L prédit ≈ (337,9 − 53,0) × 1,119 + 0 ≈ **+319 k$**, soit une **baisse d'environ
19 k$** — et non la hausse à « plus de +400 k$ » annoncée par le carnet. À vérifier.

### 12. ⚖️ Atelier 3 — `BOOK['GC=F'] = 0.00` : redistribution confirmée au dollar, diagnostic du carnet invalidé

Conditions : `BASE_EXPOSURE = 0.85` (témoin `Exposition cible 82 %` / `75 %`),
`TAKE_PROFIT_AT_PEAK = True`, 42 barres, yfinance, 25,5 M$.

| | Avec l'or | Sans l'or | Écart |
|---|---|---|---|
| **P&L** | +337 887 $ (+1,32 %) | **+318 756 $ (+1,25 %)** | **−19 131 $** |
| Sharpe | 1,67 | 1,47 | dégradé |
| Sortino | 15,91 | **4,44** | ÷3,6 |
| Drawdown max | −0,08 % | **−0,15 %** | ×1,9 |
| Calmar | 102,37 | 53,24 | ÷1,9 |
| Alpha | −1,73 % | −1,80 % | dégradé |
| Trades | 21 | 18 | −3 |
| Échangé | 60,64 M$ | **61,07 M$** | en hausse |
| Sortie loguée | J+7 · +359 323 $ | J+7 · +340 310 $ | −19 013 |

**A. La prédiction de redistribution est confirmée à 0,08 %.** Modèle :
`P&L_après = (P&L_avant − contribution_retirée) × (Σ|w|_avant / Σ|w|_après)`
= (337,9 − 53,0) × (0,94/0,84) = **318,7 k$** → mesuré **318 756 $**.

Vérification ligne par ligne, toutes exactes au dixième de k$ :

| Ligne | Avant | ×1,119 | Mesuré |
|---|---|---|---|
| `BZ=F` | +187,1 k | 209,4 | **+209,4 k** |
| `^GSPC` | +82,0 k | 91,8 | **+91,8 k** |
| `DBC` | +46,7 k | 52,3 | **+52,3 k** |
| `DX-Y.NYB` | +5,3 k | 5,9 | **+5,9 k** |
| `HYG` | −11,7 k | −13,1 | **−13,1 k** |
| `TLT` | −24,6 k | −27,5 | **−27,6 k** |

**B. Le carnet d'entraînement était faux sur toute la ligne** (Atelier 3 : « −71 k$ sur l'or »,
« le P&L grimpe à plus de +400 k$ », « supprimer cette ligne assainit le portefeuille ») :
* L'or **rapportait +53,0 k$**, il ne coûtait rien. Le chiffre de −71 k$ provenait du
  générateur synthétique (mesuré −69 978 $ le 29/08).
* Le P&L **baisse** de 19 131 $, il ne monte pas à +400 k$ (erreur de ~82 k$, et de sens).
* Le retrait **dégrade** le risque : drawdown ×1,9, Sortino ÷3,6, Calmar ÷1,9. L'or était un
  **diversifiant**, pas un boulet.

**C. Mécanisme de premier ordre à ne jamais oublier.** Le book est normalisé par
l'exposition brute (`total = Σ|w|`, `shock-lab-oil.py` l. 92). Retirer une ligne ne libère
pas son poids : **il est redistribué au prorata sur les lignes restantes**, qui voient
toutes leur taille multipliée par `Σ|w|_avant / Σ|w|_après`. Conséquence contre-intuitive :
supprimer une ligne **gagnante** peut faire baisser le P&L global, et supprimer une ligne
perdante peut le faire monter moins qu'espéré — dans les deux cas, **l'effet net dépend du
rendement relatif de la ligne retirée par rapport au reste du book**, pas de son signe.

**D. Correction appliquée.** L'Atelier 3 du carnet d'entraînement a été entièrement réécrit
le 30/08/2026 avec les valeurs mesurées, la formule de redistribution et la conclusion
inversée. Les Ateliers 1 et 2 ont été corrigés de la même façon (sections ci-dessus).

### 13. 🛑 Atelier 4 — le long strangle **refuse de trader** : la discipline fonctionne, la prévision est en cause

Run : `long-strangle-shock.py`, `global-macro`, **1 000 000 $**, 2026-07-01 → 2026-08-29,
42 barres, yfinance. Résultat : **0 trade, P&L 0 $**, aucune position.

Journal moteur (deux lignes, aucune entrée) :

```
2026-07-15  Pas d'entrée : amplitude attendue 5.0% vs prime payée 9.6% du spot
            (edge 0.52 < 1.00). Mouvement implicite ATM 18.4% pour mémoire.
2026-08-28  Pas d'entrée : amplitude attendue 10.0% vs prime payée 10.8% du spot
            (edge 0.92 < 1.00). Mouvement implicite ATM 18.1% pour mémoire.
```

**A. Ce n'est pas un bug : c'est la règle de discipline** `MIN_EDGE = 1.00`
(`long-strangle-shock.py` l. 22) — on n'achète du gamma que si l'amplitude attendue par la
prévision dépasse la prime payée en % du spot. Le régime de vol, lui, passait
(`MAX_VOL_REGIME = 2.2` non déclenché).

**B. Le carnet annonçait +12 084 $ (+1,21 %) et 6 trades : non reproductible sur données
réelles.** Les 6 trades correspondent aux deux entrées (4 ordres) + la sortie J+7 (2 ordres)
— donc à un run où **les deux entrées passaient le filtre**, c'est-à-dire où la prime était
assez bon marché. Sur données réelles, l'IV 30 j de `BZ=F` est de **59,4 %** (onglet
Anticipation), d'où une prime de 9,6 % du spot : le filtre bloque.

**C. Le marché avait raison, le modèle avait tort.** Mouvement implicite ATM annoncé par le
moteur : **18,4 %**. Prévision r1 : **5,0 %**. Mouvement réalisé au pic : **18,4 %**.
Le marché prix correctement le choc que le modèle sous-estime — c'est le facteur **×3,68**
déjà consigné. **L'erreur est dans la prévision, pas dans l'exécution.**

**D. Le filtre a même évité une perte — démonstration chiffrée.**
* Strikes à ±5 % (`WIDTH = 0.05`), prime payée 9,6 % du spot.
* Point mort haut = +5 % (strike) + 9,6 % (prime) = **+14,6 %**.
* Sortie à J+7, le 22/07 : Brent **94,023** contre **84,992** à l'entrée = **+10,6 %**.
* **10,6 % < 14,6 % → sous le point mort.** Le pic (+18,4 %) n'arrive qu'à **J+8**, un jour
  après la sortie. Le trade, tel qu'il est paramétré, aurait donc **perdu** malgré une vue
  directionnelle correcte.

**E. Conséquence méthodologique (prioritaire pour la revue mensuelle).** Le nœud `r2` porte
une amplitude en grille `[0.05, 0.10, 0.185]`, mais le filtre n'utilise que
`f.amp_base` = **0.10** (nœud médian). Avec le nœud haut (0,185), l'edge serait
0,185/0,108 = **1,71** → entrée déclenchée. **La grille d'amplitudes n'est pas exploitée par
le filtre d'entrée** : c'est une incohérence interne à corriger en phase 2 (le filtre devrait
raisonner sur la grille, ou au moins sur son nœud haut, dès lors que la prévision assume une
incertitude d'un facteur ~3,7).

**F. À noter** : `MAX_VOL_REGIME = 2.2` n'a pas été déclenché alors que le régime mesuré de
`BZ=F` est de 1,37x (Anticipation) — le second garde-fou n'a donc pas eu à jouer.

---
*Fin du log de veille du 30/08/2026. Ce fichier sera mis à jour à chaque cycle mensuel de révision.*
