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
*Fin du log de veille du 30/08/2026. Ce fichier sera mis à jour à chaque cycle mensuel de révision.*
