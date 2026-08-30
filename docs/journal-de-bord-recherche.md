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

## 🛡️ Charte de provenance — la règle anti-« on me dit que tout est faux »

Adoptée le 30/08/2026. Elle protège contre le scénario où un chiffre de référence,
pris pour un fait de marché, s'effondre des mois plus tard.

1. **Tout chiffre consigné porte sa provenance** : source (`yfinance` / `synthétique` /
   `csv`), fenêtre, nombre de barres, capital, paramètres modifiés. Un chiffre sans
   provenance est **non vérifié**, pas « vrai ».
2. **Fait de marché et artefact de plateforme sont toujours séparés**, dans des sections
   distinctes, jamais mélangés dans un même tableau. C'est le mélange des deux qui a laissé
   trois repères synthétiques passer pour des résultats de marché dans le carnet
   (Ateliers 1, 3 et 4 — tous corrigés le 30/08/2026).
3. **Une leçon démontrée par un mécanisme ne se périme pas.** Le timing qui vaut 617 520 $,
   la proportionnalité du levier, la redistribution des poids : ce sont des mécanismes
   vérifiés, pas des montants. Les montants bougent avec les données ; les mécanismes non.
4. **Ce qui peut changer** : les grandeurs si la source change. **Ce qui ne changera pas** :
   les mécanismes ci-dessus.

---

## 🪜 Échelle junior → expert — backlog d'améliorations

> Ce que vous avez demandé de consigner : **les améliorations à faire, classées par palier**,
> y compris « les trucs fins » — subtils, très valorisants, mais hors de portée immédiate.
> Rien ici n'est à faire maintenant. L'objet de cette section est de **savoir qu'ils
> existent** et de pouvoir les ressortir le jour où le palier est atteint.

### 🟢 Palier 1 — Junior (fondations · un paramètre ou une ligne à la fois)

> ✅ **Les six correctifs ont été appliqués le 30/08/2026** (commit `bad72a2`).
> **Aucune régression** : les 37 tests passent et le P&L du book delta reste identique au
> dollar près (**385 544,16 $** avant comme après). Seules les stratégies d'options changent,
> ce qui était le but.

| # | Amélioration | Pourquoi c'est valorisant | Déclencheur |
|---|---|---|---|
| 1 | ✅ **Taille réelle des contrats** — `contract_size` : `BZ=F` et `CL=F` = 1000, `GC=F` = 100, `SI=F` = 5000, ETF/indices = 1. Les frais par contrat sont désormais appliqués au **nombre de contrats**, plus au nombre d'unités | Les frais options passent de **14,9 %** à ~0,015 % du volume. Le long strangle passe de **+12 084 $** à **+23 409 $**, commissions de **7 649 $** à **11,36 $** | **FAIT** |
| 2 | ✅ **`risk_free` dans `EngineSettings`** (0.041), transmis à `metrics.compute()` et renvoyé dans le payload ; une bulle d'aide l'indique sur la carte Sharpe | Le Sharpe redevient lisible : on sait qu'un terme fixe de 4,1 % est retiré chaque barre | **FAIT** |
| 3 | ✅ **« n.d. » au lieu de `0.0`** pour Sharpe / Sortino / Calmar / drawdown indéfinis (`metrics.py`, `cli.py`, `app.js`) | Un `0.00` se lisait comme une mesure ; `n.d.` dit vrai | **FAIT** |
| 4 | ✅ **Label débit/crédit** : `app.js` l. 807 aligné sur la convention de la l. 703 (positif = débit) | Un strangle acheté s'affiche enfin comme un débit | **FAIT** |
| 5 | ✅ **Alerte « code non enregistré »** au lancement d'un backtest (`state.dirty`) | Fini le backtest qui part silencieusement sur l'ancienne version | **FAIT** |
| 6 | ✅ **Signalement des positions ouvertes** en fin de backtest : `Fin de backtest : 7 position(s) encore ouverte(s), P&L latent −9 685 $ compris dans le résultat` | L'artefact `r2` n'est plus invisible. Choix assumé : on **signale** plutôt que de neutraliser — corriger le P&L d'une position réellement ouverte serait un mensonge comptable | **FAIT** (signalé, non neutralisé) |
| 7 | ✅ **Choc d'IV en points** : le champ du lab et le formulaire de révision acceptent des points (10 = +10 pts), convertis en fraction à la saisie | Un « 10 » produit enfin +10 pts (prime 23,91) au lieu de +1000 pts écrêtés en silence | **FAIT** |
| 8 | ✅ **Alerte de domaine sur le lab** : IV au plafond de 400 %, prime > 50 % du spot, points morts hors plage → bandeau `⚠` (UI) et `⚠` (CLI) | Fini le pricer silencieux : une cotation hors marché se voit, elle ne se devine plus | **FAIT** |
| 9 | ✅ **Points morts étendus par la prime nette** + dédoublonnage des plateaux à zéro | Cas extrême : les vrais BE (86,26 / 1198,74) s'affichent au lieu d'un champ vide | **FAIT** |
| 10 | ✅ **Bornes de payoff déclarées par structure** (`max_loss_bounded` / `max_gain_bounded` dans le catalogue) | « illimité / non bornée » remplace les artefacts de grille (gain max −274,74 → illimité) | **FAIT** |

### 🟡 Palier 2 — Intermédiaire (il faut comprendre le moteur)

| # | Amélioration | Pourquoi c'est valorisant |
|---|---|---|
| 7 | **Grille d'amplitudes dans le filtre d'entrée** : le filtre n'utilise aujourd'hui que le nœud médian (`0.10`). Avec le nœud haut (`0.185`), l'edge passe de 0,92 à **1,71** | Une prévision qui assume une incertitude ×3,7 doit se filtrer sur sa borne haute, pas sur sa médiane |
| 8 | **Sortie échelonnée (scale-out)** plutôt que tout-ou-rien au pic | Vendre la moitié à J+7 et laisser courir le reste capte à la fois le pic et le rebond — le défaut exact constaté à l'Atelier 1 |
| 9 | **Dimensionnement par volatilité** (vol targeting) au lieu d'un `%` fixe | Stabilise le profil de risque quand le régime de vol change (observé : 1,51x puis 1,37x sur BZ=F) |
| 10 | **Étendre l'univers énergie** : `XLE`, `XOP` | Bêta supérieur au brut, options très liquides — recommandé dès le 30/08 |
| 11 | **Walk-forward et fenêtres glissantes** | Un résultat qui tient sur une seule fenêtre de 42 barres n'est pas un résultat |
| 12 | **Comparaison côte à côte de deux variantes** | Aujourd'hui on relance et on retient les chiffres à la main |
| 13 | **Créditer le cash au taux sans risque** | Cohérence : le Sharpe retire 4,1 % que le moteur ne paie jamais |
| 14 | **Export CSV/PDF + identifiant de run** | Un backtest = un résultat conservé, pour la revue mensuelle |

### 🔴 Palier 3 — Expert (niveau industrie)

| # | Amélioration | Pourquoi c'est valorisant |
|---|---|---|
| 15 | Chaîne d'options réelle (CBOE / broker) au lieu de la surface paramétrique | Le pricing cesse d'être une approximation |
| 16 | Smile et structure de terme calés par sous-jacent | Les ailes sont précisément là où se jouent les chocs |
| 17 | VaR / ES conditionnelle par nœud de la grille de stress | La vraie mesure du risque de queue |
| 18 | Brier score et calibration des probabilités publiées | Savoir si une confiance de 60 % vaut 60 % |
| 19 | Marge, appels de marge, coût de financement | Indispensable dès qu'on vend de la volatilité |
| 20 | Exécution intraday, VWAP, impact de marché, liquidité par ligne | Le backtest journalier est optimiste |
| 21 | Attribution par facteur plutôt que par ligne | Distinguer « j'ai gagné sur l'énergie » de « j'ai gagné sur le bêta » |
| 22 | Multi-utilisateur, persistance des runs | Le desk devient partageable |

### 💎 Les « trucs fins » — petits en code, immenses en valeur

Ceux-là ne demandent presque pas de développement. Ce sont des **changements de raisonnement**.

1. **Séparer le *timing alpha* du *directionnel alpha*.** Vous l'avez mesuré : le timing vaut
   **617 520 $**, la vue directionnelle brute vaut **~0**. Un desk qui sait ça **ne paie plus
   jamais pour une vue directionnelle seule** — il paie pour le calendrier. C'est la
   différence la plus rentable entre un débutant et un pro.
2. **Généraliser le ratio amplitude / prime.** Le filtre `MIN_EDGE` compare ce que le marché
   vous fait payer à ce que votre modèle attend. Rien n'oblige à le réserver aux options :
   c'est un filtre d'entrée universel, valable pour n'importe quelle ligne.
3. **Sortir au pic du *book*, pas au pic d'une ligne.** Leçon de l'Atelier 1 : la couverture
   actions qui vous sauve dans le krach devient un passif dans le rebond (−295,4 k$).
4. **Ne jamais juger une ligne isolément** dans un book normalisé : la retirer redistribue
   son poids à toutes les autres (×1,119). Une « bonne » ligne peut faire baisser le P&L.
5. **Vérifier la provenance avant le chiffre.** C'est le réflexe qui évite, dans six mois,
   d'entendre que tout était faux. Trois repères du carnet sont tombés faute de l'avoir eu.

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

### 14. 💥 Atelier 4 (suite) — preuve définitive : le repère du carnet est un chiffre synthétique, et les options sont ruinées par les frais

**A. Contrôle décisif.** En exécutant `long-strangle-shock.py` sur le **générateur
synthétique** (1 M$, mêmes dates, `MIN_EDGE` à 1.00 ou 0.50 — indifférent) :

| | Synthétique | Données réelles (MIN_EDGE 0.50) |
|---|---|---|
| **P&L** | **+12 084 $ (+1,21 %)** | **−6 211 $ (−0,62 %)** |
| Trades | 6 | 6 |
| Sharpe | **0,846** | −9,20 |
| Drawdown max | −0,39 % | −0,62 % |
| Paires achetées (07-15) | 2 942 | 1 846 |
| Prime par paire | **2,63** | **8,129** |
| P&L latent logué à la sortie J+7 | **+23 443 $** | **+610 $** |

→ **Le repère de l'Atelier 4 du carnet (+12 084 $, 6 trades, Sharpe 0,85) est reproduit au
dollar près en synthétique.** Ce n'est donc pas un résultat de marché : c'est un artefact du
générateur, indûment présenté comme une performance. Même conclusion qu'à l'Atelier 1
(« −4 k$ à +99 k$ ») et à l'Atelier 3 (« or −71 k$ ») : **les trois repères chiffrés du
niveau 1 venaient du synthétique.**

**B. Sur données réelles, la perte est presque entièrement constituée de frais.**

Décomposition exacte (reconstituée depuis le journal des transactions) :

| | Montant |
|---|---|
| P&L brut r1 (acheté 15 005, revendu 15 607) | **+602 $** |
| P&L brut r2 (acheté 14 943, marqué 14 935) | **−8 $** |
| **P&L brut total** | **+594 $** |
| Commissions (1 199,90 × 4 + 1 002,95 × 2) | **−6 805,50 $** |
| **P&L net** | **−6 211,50 $** ✔ conforme à l'écran |

**Les frais représentent 6 805 $ sur 45 557 $ échangés, soit 14,9 % du volume — pour un P&L
brut de 594 $.**

**C. Cause racine : le multiplicateur de contrat vaut 1,0 partout.**

* `config.get_asset("BZ=F").multiplier = 1.0` — et **1.0 pour les sept sous-jacents** de
  l'univers. Un contrat Brent réel porte **1 000 barils** (notionnel ~85 000 $).
* `engine.py` l. 489 : `commission = abs(o.amount) * s.commission_per_contract`, avec
  `commission_per_contract = 0.65` (l. 248) — **appliqué sans multiplicateur**.
* Conséquence : l'option vaut ~4,25 $ et la commission 0,65 $, soit **15,3 % de la prime** à
  l'achat, et **~30 % aller-retour**. Aucune stratégie d'options ne peut survivre à ça.
* Le commentaire de `options.py` l. 14-15 annonçait l'intention inverse : *« les prix, grecs
  et P&L sont exprimés par contrat avant multiplicateur (AssetSpec.multiplier s'applique au
  moment du passage d'ordre) »* — le P&L applique bien le multiplicateur (l. 67, 71), mais
  **la commission ne l'applique jamais**. Incohérence interne.

**Correctif phase 2 (priorité haute)** : renseigner les multiplicateurs réels par
sous-jacent (BZ=F et GC=F = 1000, ETF = 1, indices = 1) **et** appliquer le multiplicateur à
la commission, ou passer à une commission en points de base du notionnel. Tant que ce n'est
pas fait, **tous les backtests d'options de ShockDesk sont structurellement faussés** et les
repères chiffrés des Ateliers 4 à 8 ne veulent rien dire.

**D. Correction d'une erreur d'analyse de ma part.** J'avais prédit une perte en raisonnant
sur le **point mort** (strikes ±5 %, prime 9,6 % → point mort haut à +14,6 %, or le Brent
n'avait fait que +10,6 % à J+7). La perte est réelle, mais **le raisonnement était faux** :
les options conservaient 23 jours de valeur temps, si bien que le P&L brut à la sortie était
**positif** (+610 $). Le point mort « intrinsèque » ne s'applique qu'à l'échéance, pas à une
sortie anticipée. La perte vient des frais, pas du point mort.

**E. À retenir pour le desk.** La discipline (`MIN_EDGE`) avait raison de bloquer. Une fois
forcée, l'opération perd — mais **à cause du moteur, pas du marché**. Deux erreurs
différentes, qu'il ne faut pas confondre : une erreur de **prévision** (amplitude ×3,68)
et une erreur de **modélisation** (frais). La première se corrige par une révision, la
seconde par du code.

### 15. 🔧 Correctifs appliqués (commit `bad72a2`) — mesure d'impact

Six correctifs du palier junior, appliqués le 30/08/2026. **Critère de non-régression
retenu : le P&L du book delta doit rester identique au dollar près.** C'est le cas.

| Run (synthétique, 42-43 barres) | Avant | Après | Écart |
|---|---|---|---|
| Book delta `shock-lab-oil`, 25,5 M$ | **385 544,16 $** | **385 544,16 $** | **0,00** ✔ |
| Long strangle, 1 M$ | +12 084 $ | **+23 409 $** | frais divisés |
| Commissions du strangle | ~7 649 $ | **11,36 $** | ÷673 |

* **Ce qui a changé** : uniquement les stratégies qui traitent des options. Le book delta ne
  négocie que des sous-jacents, dont la commission par part est restée inchangée.
* **Ce qui n'a pas changé** : aucun prix, aucune taille, aucun P&L de sous-jacent. Le champ
  `contract_size` est **nouveau** et n'est consulté qu'au calcul de la commission d'une option
  — `multiplier` (qui sert au pricing) reste à 1.0 et n'a pas été touché. C'est ce choix qui
  garantit l'absence de régression.
* **Effet de bord assumé** : les repères chiffrés des Ateliers 5 à 8, établis avant
  correction, sont désormais **périmés**. Ils devront être re-mesurés — c'est l'objet de la
  reprise des ateliers.
* **Leçons de méthode** : (1) corriger le *modèle* avant de corriger la *stratégie* — on a
  failli conclure « les options ne marchent pas » alors que c'était le moteur ; (2) un
  correctif ne se valide pas sur une impression mais sur un **chiffre témoin invariant**
  (ici : 385 544,16 $).

---
---

## 📅 Log du 30 Août 2026 (3) — Reprise de session : l'atelier Options (Atelier 7)

> La session précédente s'est coupée alors que l'utilisateur était sur l'**onglet Options**
> (SPY, long strangle, 30 j). Reprise en ce point. Ateliers 1 à 4 déjà consignés ✅.

### 0. État du dépôt à la reprise

* HEAD `20230e0` (merge de la PR #3 — contient les six correctifs du palier 1,
  commit `bad72a2`), arbre de travail propre, `strategies/shock-lab-oil.py` revenu à
  l'état de référence (`TAKE_PROFIT_AT_PEAK = True`, `BASE_EXPOSURE = 0.85`).
* **37 tests passent.** Serveur relancé sur 0.0.0.0:8050.
* **Yahoo Finance toujours injoignable depuis l'environnement d'exécution**
  (`TLS/SSL connection has been closed (EOF)` sur `query2.finance.yahoo.com`) — même
  constat que le 29/08. Tout backtest lancé ici retombera sur la source synthétique
  (badge orange) et **ne reproduira pas** les repères réels (+337 887 $, etc.).

### 1. ✅ Vérification du correctif débit/crédit sur la structure de la capture coupée

* La convention a bien été corrigée dans `app.js` (convention : **prime nette ≥ 0 = débit**).
* Contrôle par l'API (`/api/options/quote`, SPY, strangle, 30 j, largeur 3 %) :
  **prime nette 10,69 (débit)** — la même valeur que la capture précédente, désormais
  correctement étiquetée. La structure est achetée : perte max **−10,69 $** = prime payée. ✔

### 2. 📐 Références mesurées pour l'Atelier 7 (lab déterministe, hors réseau)

* Le lab Options price depuis la surface paramétrique et un spot **statique de config**
  (`spec.s0`) : aucune dépendance au réseau. Les valeurs ci-dessous sont donc
  reproductibles au centime dans cet environnement, contrairement aux backtests.

| | Choc d'IV 0 pt | Choc d'IV +10 pts |
|---|---|---|
| Prime nette | **10,69** | **23,91** (+13,22) |
| Vega | **1,242 / pt** | 1,374 / pt |
| Theta | **−0,344 / j** | −0,608 / j |
| Points morts | 614,3 / 670,7 | ≈ 601,1 / 683,9 |
| Jambes | call 660 à 5,88 (IV 16,4 %) · put 625 à 4,80 (IV 16,6 %) | mêmes strikes, primes gonflées |

* Écart prime : 10 pts × 1,242 = 12,42 attendus pour 13,22 réalisés → l'excédent
  (~0,8) est la convexité (volga) : le vega lui-même augmente avec le choc.
* Le payoff **à l'échéance** (intrinsèque) ne dépend pas de l'IV : seul le niveau de la
  courbe baisse (prime payée plus chère → points morts élargis).
* SPY : `iv_base` 16,5 %, spot 642,0 (config). `BZ=F` : `iv_base` 36 % — comparaison
  possible pour montrer que le marché prix le choc pétrole ~2,2× plus cher.

### 3. ⚠️ Faiblesses identifiées (à traiter en phase 2)

* Le lab Options est **déconnecté du marché** : spot figé à `spec.s0`, IV de base
  statique (`effective_iv_base`), régime de vol et choc d'IV réglés à la main.
  Correctif souhaitable : brancher spot + IV ATM sur le panel de données (Yahoo/CSV),
  avec badge de provenance — sinon l'atelier enseigne la mécanique, pas le marché.
  À ajouter au backlog (palier 2).

---

## 📅 Log du 30 Août 2026 (4) — Atelier 7 : le piège des unités du champ « choc d'IV »

### 0. Cause racine du run à « 1000 pts » — ce n'était pas une erreur de saisie

* L'utilisateur a saisi **10** dans le champ « choc d'IV (pts) », croyant demander +10 pts.
* Le champ (`#op-ivshift`, `index.html`) attend en réalité une **fraction** : la convention
  interne est `0.10 = +10 pts` (`options.py` l. 126, et tous les scénarios de `scenarios.py`).
  `quote()` (`app.js` l. 795) envoie `parseFloat(value)` **brut** ; l'affichage, lui,
  multiplie par 100 (`q.iv_shift * 100` + « pts »). Saisir 10 envoie donc **+1000 pts**.
* **Preuve par reproduction API** : `option_lab("SPY", "strangle", 30, 0.03, iv_shift=10.0)`
  reproduit l'écran utilisateur au centime — prime 538,74, IV 400 %/400 %, vega 1,244,
  theta −8,263, delta 0,435, gamma 0,00092, call 273,97, put 264,77, points morts vides,
  gain max −274,74.
* **Faiblesse d'interface consignée** : un champ libellé « (pts) » qui attend une fraction,
  sans exemple ni conversion, et aucune alerte quand le résultat sort du domaine réaliste.
  À ajouter au backlog (palier 1) : accepter les points réels (10 = +10 pts) ou afficher
  l'unité attendue, et avertir quand l'IV atteint le plafond de la surface.

### 1. Ce que le stress-test accidentel a révélé (tout est mécanisme, rien n'est un prix de marché)

1. **Plafond d'IV silencieux** : `iv_surface` borne l'IV entre 2 % et **400 %**
   (`options.py` l. 135). +1016 pts demandés → écrêtés à 400 % **sans aucun message**.
2. **Points morts vides = artefact de fenêtre** : la recherche se borne à ±1,5 span autour
   des strikes (572 → 712). Les vrais points morts du strangle à 538,74 de prime sont à
   **86 / 1199** — hors fenêtre, donc rien ne s'affiche au lieu d'un signal « hors plage ».
3. **Gain max −274,74 = artefact de grille** : c'est le meilleur point de la plage
   d'évaluation [375, 924], pas un plafond de la stratégie. Un strangle **acheté** a un
   gain max illimité ; l'affichage « gain max » devrait dire « hors plage ».
4. **Le vega n'est pas une constante** — mesuré sur 3 niveaux d'IV du même strangle SPY :
   IV 16,5 % → vega **1,242** · IV 26,5 % → vega **1,374** (en hausse) · IV 400 % → vega
   **1,244** (retombé). Le vega est une pente locale qui culmine vers 25–30 % de vol puis
   décroît. Le vega **moyen** du saut de 990 pts ≈ (538,74 − 23,91) ÷ 9,90 ≈ **0,52/pt** :
   un grand choc ne se price jamais au vega marginal.
5. **La structure change de nature à 400 % de vol** : delta 0,435 (le call se comporte
   presque comme l'action), gamma ÷24 (0,022 → 0,0009). Ce n'est plus un pari sur le choc :
   tout est déjà dans le prix. La prime = 84 % du spot ; un filtre `MIN_EDGE` (Atelier 4)
   calculerait un edge ≈ 0,06 ≪ 1 → la discipline refuse d'entrer. Le filtre existe
   précisément pour ce régime.
6. **Méta-leçon** : *garbage in, garbage out* — un desk pose des bornes sur ses paramètres
   et vérifie qu'une cotation sortie du pricer est un prix de marché, pas un artefact.

### 2. ⏳ À traiter (rappel ouvert)

* Le run hérité de la session précédente « **Backtest exécuté : 0,06 % sur 42 barres** »
  (capital 1 M$ dans l'URL, stratégie non identifiée avec certitude) reste **sans
  provenance établie**. À élucider à la prochaine occasion — un chiffre consigné sans
  provenance est non vérifié (charte).

---

## 📅 Log du 30 Août 2026 (5) — Atelier 7 : le choc +10 pts exécuté, prédictions validées, volga quantifiée

### 1. ✅ Run utilisateur conforme aux prédictions (choc `0.10` = +10 pts)

| | Choc 0 | Prédit | Écran utilisateur |
|---|---|---|---|
| Prime nette | 10,69 | ≈ 23,91 | **23,91** ✔ |
| Vega | 1,242 | ≈ 1,374 | **1,374** ✔ |
| Theta | −0,344 | ≈ −0,608 | **−0,608** ✔ |
| Points morts | 614/671 | ≈ 601/684 | **601,09 / 683,91** ✔ |
| IV surface | 16,4/16,6 % | ≈ 26,5/26,6 % | **26,4 / 26,6 %** ✔ |

* Courbe : même forme, translatée vers le bas (axe Y débutant à −20) — le payoff à
  l'échéance est intrinsèque, l'IV ne change que le niveau d'entrée.
* Jambes : call 660 : 5,88 → **12,72** (+6,84) · put 625 : 4,80 → **11,18** (+6,38).
  Somme +13,22 ✔. Deltas de jambes 0,389 / −0,332 (structure quasi delta-neutre, 0,056).

### 2. 🔬 Volga quantifiée

* Écart de prime 13,22 vs vega initial × choc = 12,42 → surplus **+0,80**.
* Vega moyen sur le trajet ≈ (1,242 + 1,374)/2 = **1,308** → 10 × 1,308 = 13,08 ≈ 13,22.
* Le vega est une **pente locale** : il monte avec l'IV (volga positive), culmine vers
  25–30 % de vol, puis décroît — les trois points mesurés (1,242 à 16,5 % · 1,374 à
  26,5 % · 1,244 à 400 %) décrivent cette bosse.
* Grecques croisées du choc : **delta inchangé** (0,056), **gamma ÷1,45** (0,02222 →
  0,01530), **theta ×1,77** (−0,344 → −0,608). Signatures du long vega : le choc d'IV
  renchérit la position (+124 % de prime) et le loyer du temps, sans changer l'exposition
  au spot.
* Mécanisme de lien avec l'Atelier 4 : la prime en % du spot passe de 1,7 % (10,69/642)
  à 3,7 % (23,91/642). Le filtre `MIN_EDGE` = amplitude attendue ÷ prime subit donc
  directement les chocs d'IV — c'est ainsi que les révisions `iv_shift` du registre
  (`BZ=F r1` : +0,10 pts, etc.) pèsent sur l'entrée.
* Choix de conception consigné : le choc est **additif en points** (16,4 % + 10 = 26,4 %),
  appliqué après le régime — un calibrage manuel d'`iv_shift` doit le savoir.

### 3. 📚 Carnet d'entraînement mis à jour

* Atelier 7 réécrit avec les valeurs mesurées, le piège d'unités et le diagnostic volga.
* Tableau de bord : Atelier 7 → **✅ Fait · 30/08**.

---

## 📅 Log du 30 Août 2026 (6) — Atelier 7 (contre-épreuve) : à 1 jour, le vega est mort

### 1. ✅ Run utilisateur conforme (maturité 30 → 1, choc 0)

| | 30 j | 1 j (prédit) | Écran utilisateur |
|---|---|---|---|
| Prime nette | 10,69 | 0,00 | **0,00** ✔ |
| Vega | 1,242 | ≈ 0 | **0,000** ✔ |
| Theta | −0,344 | ≈ 0 | **−0,000** ✔ |
| Gamma | 0,02222 | ≈ 0 | **0,00000** ✔ |
| Points morts | 614/671 | = strikes | **625,00 / 660,00** ✔ |

* À 1 jour, l'option est 3 % OTM : probabilité d'ITM quasi nulle (≈ 2,9 σ au vol
  journalier), la valeur temps s'est entièrement évaporée → la position n'est plus que
  son payoff intrinsèque. Un choc d'IV ne reprice que la valeur temps : sans valeur
  temps, **vega = 0** — et theta = 0 aussi. **Le vega et le theta naissent et meurent
  ensemble** : ce sont les deux faces de la valeur temps.
* Lien avec l'Atelier 4 : le filtre `MIN_EDGE` paie une prime 30 j (≈ 9,6–10,8 % du spot)
  *parce qu'on achète du temps* — c'est le temps qui porte le gamma et le vega. Une
  prime à 1 j serait gratuite… et ne porterait rien.
* **Preuve arithmétique de l'artefact « gain max »** : 253,31 (30 j) + 10,69 (prime) =
  **264,00** = gain max affiché à 1 j. Le « gain max » est donc le **point extrême de la
  grille d'évaluation** (924 − 660), pas un plafond de la stratégie (un strangle acheté a
  un gain max illimité). Cohérent avec le stress-test du log (4).
* Structure par terme observée : l'IV de surface passe de 16,5 % (30 j) à **10,8–11,0 %**
  (1 j) — `iv_term` compresse la vol courte. Un calibrage manuel d'`iv_shift` s'applique
  au-dessus de cette structure.

### 2. 🔭 Préparé pour l'Atelier 5 (lab, prédictions pré-calculées)

* Long straddle SPY, 30 j, largeur 0,03, choc 0 : prime **24,40** (call 640 à 14,27 +
  put 640 à 10,12) · gamma **0,02592** · vega **1,450** · theta **−0,405** · delta 0,128 ·
  points morts **615,6 / 664,4**.
* À comparer au strangle : prime ×2,3, gamma +17 %, vega +17 %, theta +18 %, points morts
  resserrés (49 pts vs 56). Le straddle paie l'ATM pour un gamma plus fort près du spot.

---

## 📅 Log du 30 Août 2026 (7) — Atelier 5 exécuté : straddle vs strangle, le verdict en deux lames

### 1. ✅ Run utilisateur conforme (SPY, 30 j, choc 0, largeur 0,03)

* Straddle : prime **24,40** · call 640 à 14,27 (IV 16,5 %, Δ 0,564) · put 640 à 10,12
  (IV 16,5 %, Δ −0,436) · gamma **0,02592** · vega **1,450** · theta **−0,405** ·
  delta 0,128 · points morts **615,60 / 664,40** (breakeven ±3,8 %).
* Gain max affiché 231,60 = 896 (bout de grille = 640 × 1,4) − 640 − 24,40 :
  **troisième confirmation de l'artefact de grille** (logs 4 et 6). Un straddle acheté a un
  gain max illimité.
* Delta 0,128 : spot 642 au-dessus du strike ATM 640 → léger biais long, insignifiant.

### 2. ⚖️ Payoffs à l'échéance (intrinsèque uniquement)

* Le straddle domine **pour tout mouvement au-delà de ±2,1 %** (|S−640| > 13,71) ; le
  strangle ne gagne que pour les mouvements **inférieurs à ±2,1 %** (il ne perd que sa
  prime, 13,71 moins chère).
* À +18,4 % (760,13) : straddle **+95,73** vs strangle **+89,44** → **+6,29** de mieux.
  À −18,4 % (523,87) : straddle **+91,73** vs strangle **+90,44** → +1,29. L'asymétrie
  (+6,29 en haut vs +1,29 en bas) vient des distances de strikes : 20 pts au-dessus
  (660−640) contre 15 pts en dessous (640−625), pour une prime supplémentaire de 13,71.
* **Par dollar déployé** : 24,40 achètent 1 straddle ou 2,28 strangles → sur +18,4 % :
  straddle **×3,92** de la prime, strangle **×8,37** (2,13× mieux). Le straddle ne gagne
  par structure que parce qu'il engage 2,3 fois plus de capital.
* Theta rapporté à la prime : straddle 1,7 %/j, strangle 3,2 %/j — le straddle est plus
  patient si le choc tarde ; il a simplement payé plus cher à l'entrée.

### 3. 📚 Leçons de desk consignées

* **La question du carnet était mal posée** — « le gamma ATM compense-t-il la prime ? »
  appelle deux réponses : oui par structure, non par dollar. La question du desk est
  « combien de structures puis-je acheter avec mon capital ? » → le strangle est un levier
  sur l'amplitude, le straddle une assurance chère proche du spot.
* **Cohérence avec l'Atelier 4** : le filtre `MIN_EDGE` (amplitude ÷ prime) est précisément
  la version automatisée du ratio « rendement par dollar de prime » — il favorise le
  strangle tant que l'amplitude attendue domine la prime.
* Carnet mis à jour : fiche Atelier 5 réécrite (valeurs mesurées + verdict), bandeau du
  Niveau 2 ajusté (Ateliers 5 et 7 re-mesurés), tableau de bord ✅.

---

## 📅 Log du 30 Août 2026 (8) — Correctifs « anti-artefacts » de l'atelier Options (appliqués et verrouillés)

> Priorité utilisateur : corriger ce qui freine l'apprentissage (le plafond d'IV
> silencieux, le piège d'unités, les artefacts d'affichage), sans rien casser.

### 1. ✅ Ce qui a été corrigé (4 blocages pédagogiques + 2 finitions)

1. **Piège d'unités du champ « choc d'IV (pts) »** — le lab accepte désormais des
   **points** (10 = +10 pts), comme son libellé et son affichage le promettent.
   Conversion UI → fraction moteur dans `quote()` (`app.js`). Même correction au
   formulaire de révision de l'Anticipation (pré-remplissage ×100, envoi ÷100).
   Un « 10 » produit maintenant un choc de +10 pts (prime 23,91), plus +1000 pts.
2. **Fini le pricer silencieux** — `api.option_lab` renvoie un tableau `warnings` :
   IV au plafond de 400 % (surface bornée), prime nette > 50 % du spot, points morts
   hors plage. Affiché en bandeau ambre dans le lab, en `⚠` dans le CLI.
3. **Points morts retrouvés loin des strikes** — la fenêtre de recherche de
   `breakevens()` est étendue par la prime nette (`pad = 2×span + |prime|`) et les
   plateaux exactement à zéro sont dédoublonnés. Cas extrême (+1000 pts) : les vrais
   BE **86,26 / 1198,74** s'affichent au lieu d'un champ vide.
4. **Bornes de payoff déclarées par structure** — le catalogue porte désormais
   `max_loss_bounded` / `max_gain_bounded` par structure. L'interface et le CLI
   affichent « illimité (structure acheteuse) » ou « non bornée (structure vendeuse) »
   au lieu d'artefacts de grille (le « gain max −274,74 » est devenu « illimité »).
5. **Infobulles d'unités** sur largeur (en % du spot) et régime de vol (×surface).

### 2. 🔒 Verrouillage — preuves de non-régression

* **41 tests passent** (37 existants + 4 nouveaux verrous) : références du lab gelées
  (strangle 10,69 · vega 1,242 · theta −0,344 · straddle 24,40 · choc +10 pts 23,91),
  plafond d'IV signalé, BE extrêmes retrouvés, bornes déclarées par structure.
* **Tous les repères pédagogiques mesurés pendant les ateliers 5 et 7 restent valides**
  au centime : la correction ne touche que les cas hors domaine (chocs absurdes) et
  l'affichage. Aucun prix, aucune grecque, aucun P&L de backtest n'est modifié
  (`build_structure`, `iv_surface`, `black_scholes` inchangés ; le moteur ne consomme
  que des champs ajoutés).
* Choix de conception assumé : le lab **signale** au lieu de **corriger** — on ne
  borne pas la saisie de l'utilisateur, on lui apprend à lire les alertes.

### 3. 🪜 Backlog mis à jour

* Les 4 blocages pédagogiques passent au palier 1 **✅ fait** (voir tableau).
* Reste ouvert (inchangé) : lab déconnecté du marché (spot/IV statiques de config) —
  palier 2.

---

## 📅 Log du 30 Août 2026 (9) — Atelier 8 : les frais d'options sur ETF surcomptés ×100

> **Document de veille et d'audit interne (Règle 2)** — tout chiffre est publié
> avec sa source, sa fenêtre et sa commande de reproduction.

### 1. 🔍 Le symptôme — atelier « Iron condor de range », univers `us-equities`

Run utilisateur : `iron-condor-range.py`, `us-equities`, 1 000 000 $,
2026-01-01 → 2026-08-28, **source yfinance** (165 barres).

* P&L **−10 158 $ (−0,83 %)** pour **85 725 $** de volume échangé, 60 trades.
* Journal des transactions : **410,80 $ de commission sur une jambe de 1 233 $**
  — **33 % du brut**, et **477,75 $** sur la jambe de 1 981 $ du 02/01.
* Total des commissions du run : **25 391,60 $**, soit **29,6 % du volume**.
  Le P&L est *presque entièrement* constitué de frais : le P&L brut du condor
  est positif, seules les commissions le rendent négatif.

### 2. 🧭 La cause — la taille du contrat d'option n'est pas celle de la part

Le moteur raisonne en **unités du sous-jacent** (des parts). Les frais sont
facturés **par contrat**. Le diviseur utilisé était `AssetSpec.contract_size` —
la taille du contrat **au comptant / à terme** :

| Sous-jacent | `contract_size` | Contrat d'option réel | Frais facturés |
|---|---|---|---|
| `SPY` (etf) | 1 part | **100 parts** | 100 × trop de contrats |
| `AAPL` (equity) | 1 action | **100 actions** | 100 × trop |
| `^GSPC` (index) | 1 point | **×100** | 100 × trop |
| `BZ=F` (future) | 1 000 barils | 1 000 barils | ✅ correct |

Le correctif du matin (`bad72a2`) avait branché le diviseur sur la taille du
contrat à terme : exact pour le Brent, l'or et l'argent, **faux pour les ETF,
les actions et les indices**, dont le contrat d'option porte 100 parts alors
que la part se négocie à l'unité. 738 parts d'option SPY (= 7,38 contrats)
étaient facturées **738 contrats**, soit 479,70 $ au lieu de 4,80 $.

Ce n'est pas un détail de calibration : **c'est un biais de signe**. Tant qu'il
est là, toute stratégie d'options sur ETF est perdante par construction, et la
perte se lit comme un résultat de marché.

### 3. ✅ Le correctif

* `AssetSpec.option_contract_size` (0 = dérivé) et la propriété
  `effective_option_contract_size` : **100 parts** pour `equity` / `etf` /
  `index`, taille du contrat à terme pour un `future`.
* `BacktestEngine._option_contract_size()` remplace `_contract_size()` pour les
  options ; le sous-jacent garde `contract_size` (inchangé au comptant).
* Plancher par ordre conservé : `max(contrats × 0,65 $, commission_min)` — un
  broker facture un ticket minimum, même pour un demi-contrat.
* La taille du contrat d'option est exposée dans la fiche sous-jacent
  (`config.asset_dict`) pour que l'interface puisse afficher « 100 parts ».

### 4. 📐 Impact mesuré — lab déterministe, reproductible hors réseau

```bash
python -m shockdesk.cli backtest --strategy iron-condor-range \
  --name us-equities --start-capital 1000000 \
  --start-date 2026-01-01 --end-date 2026-08-28 --source synthetic
```

| | Avant | Après |
|---|---|---|
| Trades | 68 | 68 |
| Volume échangé | 137 134,94 $ | 138 772,69 $ |
| **Commissions** | **30 869,80 $** | **313,04 $** |
| Frais / volume | **22,5 %** | **0,23 %** |
| Commission d'une jambe de 738 parts | 479,70 $ | **4,80 $** |
| **P&L** | **−29 156,91 $** | **+1 434,32 $** |

**Sur le run utilisateur (données réelles yfinance)**, le même correctif
divise les 25 391,60 $ de frais par ~100 : le P&L attendu passe de
**−10 158 $ à ≈ +15 000 $**. À re-mesurer au prochain run — ce n'est pas une
promesse de performance, c'est la suppression d'un coût fictif.

### 5. 🔒 Verrouillage — preuve de non-régression

* **43 tests passent** (41 → 43) : `test_les_frais_option_sont_comptes_par_contrat`
  (1 000 parts = 10 contrats sur SPY, 1 contrat sur `BZ=F`) et
  `test_taille_des_contrats_d_option_par_type_d_actif` (100/100/100/100/1000/100/5000).
* Le pricing, les grecs et le règlement à l'échéance ne sont pas touchés : seuls
  les frais changent. Aucun repère du lab d'options (ateliers 5 et 7) n'est
  affecté.
* **Les repères chiffrés de l'atelier 8 établis avant ce correctif sont
  périmés** — ils mesuraient des frais, pas un marché.

### 6. 🪜 Reste ouvert (consigné, non traité ici)

1. **Quantités fractionnaires** : 632 parts = 6,32 contrats. Un desk trade 6
   contrats entiers. Le moteur raisonne en parts et n'impose pas l'arrondi au
   lot — cohérent avec le reste du moteur, mais à décider (palier 2).
2. **Scorecard bruité** : en `us-equities`, 9 lignes sur 10 sont
   « non évaluable — sous-jacent absent du panneau » (DBC, HYG, ^GSPC, GC=F,
   BZ=F, DX-Y.NYB). Ce n'est pas un bug de calcul — ces prévisions portent sur
   des lignes hors univers — mais l'affichage gagnerait à filtrer sur le panneau
   chargé (palier 1, interface).

---

## 📅 Log du 30 Août 2026 (10) — Scorecard : distinguer « hors univers » de « non évaluable »

Repris dans la foulée du (9), sur la même sortie d'atelier.

### 1. 🔍 Le symptôme

En `us-equities`, le scorecard affichait **9 lignes « non évaluable » sur 10**
(DBC, HYG, ^GSPC, GC=F, BZ=F ×2, DX-Y.NYB), toutes pour la même raison :
« sous-jacent absent du panneau ». Lu vite, cela ressemble à une série de
misses — alors que ce sont des prévisions publiées sur des lignes que cet
univers ne charge pas.

### 2. ✅ Le correctif

* `scorecard()` marque chaque ligne `out_of_universe` (en erreur **et** le
  sous-jacent n'est pas dans le panneau chargé) et ajoute
  `out_of_universe`, `out_of_universe_total`, `evaluable_total`.
* L'interface trie ces lignes **en bas de table**, les étiquette
  « hors univers » avec le libellé « sous-jacent absent de cet univers », et le
  pied de table indique « 10 lignes publiées, 0 non-test, **1 évaluable dans cet
  univers** · hors univers : BZ=F, DBC, DX-Y.NYB, GC=F, HYG, ^GSPC ».
* La revue mensuelle CLI affiche la même ligne « hors univers ».

**Aucune ligne n'est supprimée et aucun score n'est modifié** : `sign_hits`,
`sign_total`, `non_test` et `misses` restent calculés exactement comme avant.
On ne fait que distinguer deux choses que la table confondait.

### 3. 📐 Mesuré

`us-equities` : 10 lignes publiées → **1 évaluable, 9 hors univers** (6
sous-jacents distincts). `global-macro`, qui charge les 7 lignes publiées :
**0 hors univers** — le score y est intégralement testable.

### 4. 🔒 Verrouillage

**44 tests passent** (43 → 44) : `test_scorecard_distingue_le_hors_univers`
vérifie les deux univers et que TLT, chargé dans `us-equities`, reste évalué.

---

## 📅 Log du 30 Août 2026 (11) — Session Arena : fin des ateliers + correctifs de bugs (PASSATION)

> Section écrite pour la **prochaine session Arena**. Un agent qui reprend ce dépôt
> DOIT d'abord lire cette section pour savoir où on en est, sans refaire l'audit.

### 0. 🔎 Résumé — où on en est (à lire en premier)

* **Parcours d'apprentissage : tous les ateliers du carnet sont faits.**
  | Atelier | Statut |
  |---|---|
  | 1 (timing) · 2 (exposition) · 3 (miss or) · 4 (strangle) · 5 (straddle) · 7 (vega) | ✅ fait (sessions précédentes) |
  | **6 (butterfly)** · **8 (iron condor)** · **9 (révision r2)** · **10 (revue CLI)** | ✅ **faits dans CETTE session** |

* **Les 44 tests passent** (`pytest tests/ -q`). Le README/ROADMAP annonçaient
  « 36 tests » : **corrigé à 44** (il y avait 39 fonctions de test + 4 verrous lab).

### 1. 🐛 Bugs corrects dans cette session — CHAQUE correctif est décrit

**a. BUG CRITIQUE — modifications non enregistrées silencieusement ignorées.**
* **Symptôme vécu** : l'utilisateur a changé `iron-condor-range.py` (`SHORT_WIDTH`
  0.03→0.04, `RISK_BUDGET` 0.01→0.005), puis lancé le backtest → **résultat
  IDENTIQUE au run précédent** (15 132 $, 60 trades). Aucune erreur affichée.
* **Cause** : `runBacktest()` (app.js) n'envoie que `{strategy_id, params}` ; le serveur
  relit le **fichier enregistré** sur disque. `saveCode()` (app.js) sauvegarde via PUT
  `/api/strategies/<sid>/code`, mais `runBacktest` ne **vérifiait pas** `state.dirty`.
  Sans `Ctrl+S`, le code de l'éditeur n'était jamais écrit sur disque.
* **Correctif** (`shockdesk/web/static/app.js`) : `runBacktest()` appelle désormais
  `saveCode()` **automatiquement** si `state.dirty` est vrai, et **annule** le lancement
  si la sauvegarde échoue. `saveCode()` renvoie `true`/`false`.
* **Règle d'atelier** (toujours valable) : dans ShockDesk, *sauvegarder puis lancer*.
  Le témoin de bonne exécution reste le toast `code enregistré dans strategies/…`.

**b. BUG FONCTIONNEL — `EXIT_IF_FORECAST` était un no-op (garde-fou mort).**
* **Symptôme** : dans `iron-condor-range.py`, toutes les sorties étaient
  « sortie avant gamma » ; **aucune** « prévision de choc active » sur 8 mois.
* **Cause** : le garde-fou surveillait `get_forecast("SPY")`, mais SPY **n'a aucune
  prévision** dans `config/forecasts.json` (le registre porte `^GSPC`, `BZ=F`,
  `TLT`, `GC=F`, etc.). `get_forecast` renvoie donc `None` toute l'année.
* **Correctif** (`strategies/iron-condor-range.py`) : nouvelle liste
  `FORECAST_SYMBOLS = ["SPY", "^GSPC"]` et helper `_shock_active()`. Le garde-fou
  surveille maintenant `^GSPC` (l'indice que SPY suit, qui a bien une prévision r1).
* **Effet validé** : le journal montre désormais `Sortie iron condor J+16
  (prévision de choc active)` dès le 2026-07-15. Le moteur lit `ledger.active()`
  indépendamment de l'univers chargé, donc `^GSPC` est identifiable partout.
* **Incohérence connexe corrigée** : l'entrée testait `f is None` (seulement SPY),
  donc après le 15/07 la stratégie ENTR-AIT puis sortait dès le lendemain (churn).
  → L'entrée teste désormais `not _shock_active()` : **plus de vente de prime quand
  une prévision de choc est active**. Le run passe de 184 à **56** trades, plus de churn.

### 2. 🧹 Nettoyage code mort (sans effet fonctionnel)

* `shockdesk/api.py` : retiré `pos_hist` (variable morte).
* `shockdesk/options.py` : retiré `intrinsic` non utilisé dans `greeks()`.
* `shockdesk/engine.py` : retiré `field` (import dataclasses inutilisé).
* `shockdesk/scenarios.py` : retiré `Sequence` (import typing inutilisé).
* `shockdesk/cli.py` : 6 `f"..."` sans placeholder → `"..."` (cosmétique).
* `tests/test_shockdesk.py` : retiré import `json` inutilisé au top.

### 3. 📚 Doc mise à jour

* `README.md` : « 36 tests » → « **44 tests** ».
* `ROADMAP.md` : « 36 tests » → « **44 tests** ».
* `docs/entrainement-progressif.md` : tableau de bord → Ateliers **6, 8, 9, 10** ✅,
  avec les résultats mesurés :
  * Atelier 6 (butterfly) : P&L ≈ −0,06 %, drawdown **−0,18 %** (plafond validé).
  * Atelier 8 (iron condor) : **+15 132 $ (+1,52 %)**, 60 trades, α −11,70 % vs SPY
    +13,21 % → le condor vend le temps, pas la direction. + correctif `EXIT_IF_FORECAST`.
  * Atelier 9 (révision r2) : POST `/api/ledger/<id>/revision` OK, historique préservé.
  * Atelier 10 (revue CLI) : `cli revue` sort les 4 sections.

### 4. 📊 Résultats de référence (ici, à re-mesurer si besoin)

* Iron condor `us-equities`, 1 M$, 2026-01-01 → 2026-08-28, **synthétique** (repère
  post-correctif) : **+1 434 $ (+0,15 %)**, 68 trades, commissions **313 $ (0,23 %)**.
* Iron condor `us-equities`, 1 M$, mêmes dates, **yfinance** (run utilisateur) :
  **+15 132 $ (+1,52 %)**, 60 trades. Benchmark SPY **+13,21 %**, alpha **−11,70 %**.
* ⚠️ La sandbox n'accède pas à Yahoo (`SSL/EOF` sur `query2.finance.yahoo.com`) : ici,
  tout backtest tombe sur **synthétique** (badge orange). Les chiffres yfinance de
  l'utilisateur ne sont **pas reproductibles** ici.

### 5. ✅ Files modifiés (tous committés et poussés)

`README.md` · `ROADMAP.md` · `docs/entrainement-progressif.md` · `docs/journal-de-bord-recherche.md` ·
`shockdesk/api.py` · `shockdesk/cli.py` · `shockdesk/engine.py` · `shockdesk/options.py` ·
`shockdesk/scenarios.py` · `shockdesk/web/static/app.js` · `strategies/iron-condor-range.py` ·
`tests/test_shockdesk.py`

---

*Fin du log de veille du 30/08/2026. Reprise prévue : phase 2 (chaîne d'options réelle,
collatéral de marge, grille d'amplitudes dans le filtre d'entrée — voir « Palier 2 »).*
