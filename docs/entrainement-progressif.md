# 🏋️ Carnet d'Entraînement Progressif — ShockDesk

> **Protocole d'apprentissage interactif par capture d'écran**  
> Ce document est conçu pour vous entraîner pas à pas, sans changer le code de base, en modifiant un seul paramètre à la fois pour observer et comprendre chaque réaction de la plateforme.

---

## 🎯 Comment utiliser ce carnet ?

1. Vous choisissez un **Atelier** ci-dessous.
2. Vous appliquez la modification de paramètre indiquée dans l'éditeur (onglet **Code**).
3. Vous appuyez sur **`Ctrl + Entrée`** (ou cliquez sur *Run backtest*).
4. Vous observez le changement sur l'onglet **Backtest** (Courbe, Cartes métriques, Attribution).
5. Vous comparez votre résultat aux diagnostics expliqués ci-dessous.
6. Vous partagez la capture d'écran si vous souhaitez qu'une session Arena analyse votre progression !

---

# 🔰 NIVEAU 1 — LES RÉFLEXES DE BASE (Stratégie `shock-lab-oil.py`)

### 📌 Atelier 1 : La Leçon du Timing (Sortir au pic vs Rester jusqu'au stop)
* **Objectif** : Comprendre pourquoi le signal de timing vaut de l'argent alors que la vue directionnelle brute s'effondre.
* **Paramètre de départ** : Ligne 11 dans `shock-lab-oil.py` :
  ```python
  TAKE_PROFIT_AT_PEAK = False   # Passez de True à False
  ```
* **Ce qu'il faut observer** — valeurs **vérifiées le 30/08/2026** sur données réelles Yahoo
  (25,5 M$, `global-macro`, 2026-07-01 → 2026-08-29, 42 barres) :

  | | `True` (référence) | `False` (votre test) | Écart |
  |---|---|---|---|
  | **P&L** | **+337 887 $ (+1,32 %)** | **−279 633 $ (−1,10 %)** | **−617 520 $** |
  | Sharpe | 1,67 | −1,66 | |
  | Vol annualisée | 2,40 % | 6,45 % | ×2,7 |
  | Drawdown max | −0,08 % | −3,60 % | ×45 |
  | `BZ=F` | +187,1 k$ | **−117,5 k$** | −304,6 k$ |
  | `^GSPC` | +82,0 k$ | **−213,4 k$** | −295,4 k$ |
  | `GC=F` | +53,0 k$ | **+107,2 k$** | **+54,2 k$** |
  | `DBC` | +46,7 k$ | −16,9 k$ | −63,6 k$ |
  | `DX-Y.NYB` | +5,3 k$ | −10,7 k$ | −16,0 k$ |
  | `TLT` | −24,6 k$ | −27,4 k$ | −2,8 k$ |
  | `HYG` | −11,7 k$ | −1,0 k$ | +10,7 k$ |

  1. **La courbe d'équité** : au lieu de rester plate après le 22 juillet, elle dévisse
     jusqu'au 5 août — le drawdown passe de −0,08 % à **−3,60 %**.
  2. **La carte P&L** : +337 887 $ → **−279 633 $**. (Le carnet annonçait « −4 k$ à +99 k$ » :
     cette fourchette venait du générateur synthétique, elle est **fausse sur données réelles**.)
  3. **La ligne `BZ=F`** : +187,1 k$ → **−117,5 k$**. Le Brent est passé de **+18,4 % au pic
     (J+8)** à **−6,6 % au stop** (acheté 84,99, revendu 79,41).

* **Diagnostic Desk (corrigé le 30/08/2026)** : le carnet imputait toute la casse au pétrole.
  Sur données réelles, c'est **deux lignes à parts égales** :
  1. **Le pétrole : 304,6 k$ (49 % de la casse).** Vous avez laissé le marché vous reprendre
     le gain sur le brut.
  2. **Votre couverture actions : 295,4 k$ (48 %).** C'est la leçon que le carnet oubliait.
     Le short S&P a très bien payé pendant le choc (+82 k$), puis le marché est remonté
     **au-dessus de votre prix d'entrée** (7 568,61 → 7 727,41) : la couverture est devenue
     une perte.
  3. **Contre-exemple, l'or : +54,2 k$ en tenant plus longtemps** (+53,0 k$ → +107,2 k$).
     Sortir au pic n'est pas optimal pour *chaque* ligne — ça l'est pour le *book*.

  → **La vraie leçon** : le take-profit à J+7 ne protège pas seulement la vue pétrole, il
  protège **le book entier**, parce que la couverture qui paie dans le krach devient un
  passif dans le rebond. Un signal de timing se juge au niveau du portefeuille, jamais
  ligne par ligne.
* **Action** : Remettez `TAKE_PROFIT_AT_PEAK = True` pour reverrouiller le gain au sommet.

---

### 📌 Atelier 2 : Levier et Dimensionnement du Risque (`BASE_EXPOSURE`)
* **Objectif** : Comprendre l'impact de l'exposition globale sur la volatilité et le drawdown.
* **Paramètre à tester** : Ligne 14 dans `shock-lab-oil.py` :
  ```python
  BASE_EXPOSURE = 0.40   # Test A : Exposition prudente à 40 %
  # puis
  BASE_EXPOSURE = 1.00   # Test B : Exposition agressive à 100 % (zéro cash de réserve)
  ```
* **Ce qu'il faut observer** :
  * Avec `0.40` : P&L réduit de moitié (~+160 k$), mais Drawdown quasi nul et volatilité inférieure à 1,2 %.
  * Avec `1.00` : P&L maximisé (~+400 k$), mais les variations quotidiennes sont plus amples.
* **Diagnostic Desk** : `BASE_EXPOSURE` est votre bouton de volume. Il ne change pas la pertinence de votre thèse, il règle simplement l'intensité financière du trade.

---

### 📌 Atelier 3 : Neutraliser le "Miss" (L'Or `GC=F`)
* **Objectif** : Mesurer ce que rapporte le book lorsqu'on corrige un actif dont le comportement divergeait de la thèse.
* **Paramètre à tester** : Ligne 21 dans le dictionnaire `BOOK` :
  ```python
  "GC=F": 0.00,   # Mettez le poids de l'or à 0.00 (au lieu de 0.10)
  ```
* **Ce qu'il faut observer** :
  * La perte de −71 k$ sur l'or disparaît du tableau d'attribution.
  * Le P&L global grimpe immédiatement à plus de **+400 k$**.
* **Diagnostic Desk** : Dans un choc pétrolier avec hausse conjointe des taux réels et du dollar, l'or ne joue pas son rôle de refuge. Supprimer cette ligne assainit le portefeuille.

> ⚠️ **Note de vérification ajoutée le 30/08/2026** — à relire avant de faire l'atelier.
> Sur **données réelles Yahoo** (run du 29/08, `TAKE_PROFIT_AT_PEAK = True`), l'or ressort à
> **+53,0 k$**, pas à −71 k$ : le scorecard marque `GC=F` **✔** (amplitude 4,9 % vs 3,0 %
> prévus, x1,63) et ne liste comme misses que **HYG** et **TLT**. Le chiffre de −71 k$
> vient du **générateur synthétique** (mesuré à −69 978 $ le 29/08) et ne se vérifie pas
> sur le marché réel.
> **Attendez-vous donc à l'inverse du résultat annoncé** : mettre `GC=F` à 0.00 devrait
> faire *baisser* le P&L d'environ 53 k$ (de ~+338 k$ à ~+285 k$), pas le faire grimper à
> +400 k$. C'est un excellent exercice : mesurez-le, et dites-moi ce que vous trouves.

---

# ⚔️ NIVEAU 2 — EXPLORATION DES STRATÉGIES ALTERNATIVES

### 📌 Atelier 4 : Le Long Strangle (`long-strangle-shock.py`)
* **Objectif** : Découvrir comment gagner sur une explosion de volatilité sans parier sur la direction.
* **Procédure** :
  1. Sélectionnez la stratégie `long-strangle-shock.py`.
  2. Univers : `global-macro`, Capital : `1000000` (1 M$).
  3. Lancer le backtest (`Ctrl + Entrée`).
* **Ce qu'il faut observer** :
  * P&L : **+12 084 $ (+1,21 %)** avec seulement **6 trades**.
  * Le Call OTM a explosé en valeur grâce aux +18,4 % du Brent, couvrant largement la perte totale du Put et le coût du temps.

---

### 📌 Atelier 5 : Straddle vs Strangle (ATM vs OTM)
* **Objectif** : Comparer l'achat à la monnaie (Straddle, plus de gamma mais plus cher) et hors de la monnaie (Strangle, moins cher).
* **Paramètre à tester** : Ligne 17 dans `long-strangle-shock.py` :
  ```python
  MODE = "straddle"   # Remplacez "strangle" par "straddle"
  ```
* **Ce qu'il faut observer** :
  * Comparez le P&L final et la volatilité. Le straddle réagit plus vite au moindre mouvement du spot, mais coûte plus cher en prime quotidienne (Theta).

---

### 📌 Atelier 6 : Le Butterfly de Timing (`butterfly-peak.py`)
* **Objectif** : Comprendre pourquoi le risque est strictement borné quand l'amplitude dépasse les prévisions.
* **Procédure** :
  1. Sélectionnez `butterfly-peak.py`.
  2. Univers : `global-macro`, Capital : `1000000`.
  3. Lancer le backtest.
* **Ce qu'il faut observer** :
  * P&L : **−22 365 $ (−2,24 %)**.
  * Drawdown : Exactement **−2,24 %** (ligne plate après la perte initiale).
* **Diagnostic Desk** : Le Brent a dépassé l'aile haute du papillon (+18,5 % vs +5 % prévu). Malgré cette erreur d'amplitude majeure, vous n'avez perdu que la prime payée (2,24 %). Vos ailes achetées vous ont protégé d'une perte illimitée.

---

# 🔬 NIVEAU 3 — L'ATELIER D'OPTIONS ET LES GRECQUES

### 📌 Atelier 7 : L'impact d'un Choc de Volatilité (`iv_shift`)
* **Objectif** : Visualiser l'effet Vega sur une structure d'options.
* **Procédure** :
  1. Allez dans l'onglet **Options**.
  2. Choisissez `SPY`, structure `Long Strangle`, maturité `30 jours`.
  3. Observez la courbe de payoff et la prime nette.
  4. Notez le **Vega** (gain par point de hausse d'IV) et le **Theta** (coût journalier du temps).

---

### 📌 Atelier 8 : L'Iron Condor en Régime de Range (`iron-condor-range.py`)
* **Objectif** : Récolter la prime du temps qui passe (Theta carry) quand aucune crise n'est annoncée.
* **Procédure** :
  1. Sélectionnez la stratégie `iron-condor-range.py`.
  2. Univers : `us-equities`, Capital : `100000`.
  3. Fenêtre : `2026-01-01` au `2026-08-28`.
* **Ce qu'il faut observer** :
  * La courbe d'équité progresse régulièrement à la hausse grâce à l'érosion continue de la prime des options vendues.

---

# 🔄 NIVEAU 4 — L'ANTICIPATION & LA REVUE MENSUELLE

### 📌 Atelier 9 : Publier une Révision $r_2$ depuis l'interface
* **Objectif** : Apprendre à enregistrer une correction sans effacer l'historique de départ.
* **Procédure** :
  1. Allez dans l'onglet **Anticipation**.
  2. Sur la carte **Brent (BZ=F)**, faites défiler vers le bas jusqu'au formulaire de révision.
  3. Renseignez la nouvelle grille d'amplitudes : `[0.05, 0.10, 0.185]` et les jours de pic `[7, 9]`.
  4. Validez pour enregistrer la révision $r_2$.

---

### 📌 Atelier 10 : Audit Automatisé par Ligne de Commande
* **Objectif** : Exécuter la revue mensuelle complète du desk.
* **Commande** :
  ```bash
  python -m shockdesk.cli revue --name global-macro --asof 2026-08-28 --window 45
  ```
* **Ce qu'elle affiche** :
  1. Scorecard officiel (4/6 de signe, timing médian à 1 jour).
  2. Payload JSON prêt à coller pour les prochaines révisions.
  3. Tableau des volatilités réalisées vs calibrées avec alertes de dépassement > 15 %.

---

## 📋 Tableau de Bord de Progression Personnelle

| Atelier | Thème | Paramètre testé | Statut | Mon diagnostic / Remarque |
|---|---|---|---|---|
| **Atelier 1** | Timing de sortie | `TAKE_PROFIT_AT_PEAK = False` | ✅ Fait · 30/08 | +337 887 $ → **−279 633 $** (−617 520 $). Casse : `BZ=F` −304,6 k + `^GSPC` −295,4 k, compensées par `GC=F` +54,2 k. Le timing protège le book, pas la ligne. |
| **Atelier 2** | Exposition globale | `BASE_EXPOSURE = 0.40 / 1.00` | 🔲 À faire | |
| **Atelier 3** | Nettoyage du Miss | `BOOK['GC=F'] = 0.00` | 🔲 À faire | |
| **Atelier 4** | Long Strangle | Stratégie gamma | 🔲 À faire | |
| **Atelier 5** | Straddle vs Strangle | `MODE = "straddle"` | 🔲 À faire | |
| **Atelier 6** | Butterfly | Plafond de risque | 🔲 À faire | |
| **Atelier 7** | Vega & IV | Onglet Options | 🔲 À faire | |
| **Atelier 8** | Iron Condor | Carry de prime | 🔲 À faire | |
| **Atelier 9** | Révision $r_2$ | Onglet Anticipation | 🔲 À faire | |
| **Atelier 10** | CLI Revue | Revue mensuelle | 🔲 À faire | |
