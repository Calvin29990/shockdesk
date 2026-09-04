# Guide de Prise en Main & Manuel d'Utilisation — ShockDesk

> **Le pendant desk de ShockLab** : Une plateforme professionnelle de recherche macroéconomique et de backtest quantitatif pour passer du scénario théorique au trade testé.

---

## Sommaire

1. [L'analogie du simulateur de vol : Pourquoi ShockDesk ?](#1-lanalogie-du-simulateur-de-vol--pourquoi-shockdesk-)
2. [Les 12 mots clés indispensables expliqués simplement](#2-les-12-mots-clés-indispensables-expliqués-simplement)
3. [Votre premier backtest pas à pas](#3-votre-premier-backtest-pas-à-pas)
4. [Comment lire les résultats : Cartes métriques, Courbe & Attribution](#4-comment-lire-les-résultats--cartes-métriques-courbe--attribution)
5. [L'Anticipation et le Registre de Prévisions](#5-lanticipation-et-le-registre-de-prévisions)
6. [L'Exemple réel du choc pétrolier (Brent +18,5 % vs +5 %) & La révision de modèle](#6-lexemple-réel-du-choc-pétrolier-brent-185--vs-5--la-révision-de-modèle)
7. [L'Atelier d'Options & Payoffs calculés](#7-latelier-doptions--payoffs-calculés)
8. [Les 3 portes d'entrée & La boucle de revue mensuelle](#8-les-3-portes-dentrée--la-boucle-de-revue-mensuelle)
9. [Glossaire complet & Les 7 règles d'or](#9-glossaire-complet--les-7-règles-dor)

---

## 1. L'analogie du simulateur de vol : Pourquoi ShockDesk ?

En aviation de ligne, aucun commandant de bord ne prend les commandes d'un avion transportant des passagers sans avoir accumulé des centaines d'heures d'entraînement dans un simulateur de vol haute fidélité. Le simulateur est conçu pour recréer fidèlement les tempêtes de haute altitude, les turbulences imprévues, les pannes de réacteur et les procédures d'urgence. Il n'a pas pour rôle de rassurer artificiellement, mais d'éprouver la discipline et d'inculquer des réflexes de survie.

**ShockDesk est exactement ce simulateur de vol pour le trader macro et l'analyste quantitatif.**

Sur les marchés financiers, les opinions sont gratuites, mais les erreurs d'exécution et les biais psychologiques coûtent des fortunes. ShockDesk vous installe dans le cockpit d'un desk institutionnel :
* Vous pilotez un book multi-actifs (actions S&P 500, obligations d'État TLT, pétrole brut Brent BZ=F, or GC=F, dollar DX-Y.NYB, crédit HYG, matières premières DBC) ou un portefeuille d'options européennes.
* Vous êtes connecté aux données réelles de **Yahoo Finance** (ou au modèle factoriel synthétique hors ligne).
* Vous testez vos thèses macroéconomiques sous forme de scénarios de choc chiffrés.
* Vous mesurez en continu l'impact des grecques (Delta, Gamma, Vega, Theta), le coût de la prime, l'attribution détaillée du P&L, sans jamais engager de capital réel imprudemment.

---

## 2. Les 12 mots clés indispensables expliqués simplement

| # | Terme | Définition simple & Rôle sur le desk |
|---|---|---|
| 1 | **Alpha ($\alpha$)** | La surperformance pure générée par la stratégie, indépendamment des mouvements de l'ensemble du marché. Un alpha positif prouve que vos décisions apportent une vraie valeur ajoutée propre. |
| 2 | **Beta ($\beta$)** | La sensibilité du portefeuille aux variations de son indice de référence (benchmark). Un beta de 1,20 signifie que si le marché monte de 1 %, votre book a tendance à monter de 1,20 %. |
| 3 | **Ratio de Sharpe** | Le rendement excédentaire par unité de risque global (volatilité). Formule : $\frac{\text{Rendement} - \text{Taux sans risque}}{\text{Volatilité}}$. Au-dessus de 1,0, c'est bon ; au-dessus de 2,0, c'est remarquable. |
| 4 | **Ratio de Sortino** | Variante du Sharpe qui ne pénalise que la volatilité baissière (les pertes réelles). Il évite de pénaliser une stratégie qui enregistre de fortes hausses subites. |
| 5 | **Max Drawdown** | La perte maximale (en %) enregistrée par le portefeuille entre son sommet historique le plus haut et son creux le plus bas. C'est le baromètre de la résistance financière et émotionnelle. |
| 6 | **Point-in-Time** | Règle absolue de discipline interdisant toute fuite d'information future (*lookahead bias*). À la date $T$, le modèle n'a accès qu'aux cours et prévisions publiés strictement avant ou à $T$. |
| 7 | **Volatilité Implicite (IV)** | L'estimation par le marché de l'agitation future du sous-jacent, déduite du prix des options via la formule de Black-Scholes. Plus l'IV est forte, plus les options sont chères. |
| 8 | **Prime (Premium)** | Le prix payé par l'acheteur d'une option au vendeur. Acheter une option génère un débit (coût) ; vendre une option génère un crédit (encaissement de prime). |
| 9 | **Strike (Prix d'exercice)** | Le cours fixé à l'avance auquel le détenteur de l'option a le droit d'acheter (Call) ou de vendre (Put) l'actif à la date d'échéance convenue. |
| 10 | **Les Grecques** | Les sensibilités mathématiques de l'option : **Delta** (direction), **Gamma** (accélération du delta), **Vega** (sensibilité à la vol), **Theta** (perte de valeur journalière liée au temps). |
| 11 | **Drift & Benchmark** | Le drift est la dérive tendancielle naturelle du marché. Le benchmark est l'indice de référence (ex: S&P 500 `^GSPC`). Toute performance doit être mesurée nette de l'effet de marée du benchmark. |
| 12 | **Débit / Crédit / Carry** | Une structure à débit coûte de la prime à l'entrée (long gamma, risque borné). Une structure à crédit encaisse la prime à l'entrée (vendeur de temps/theta, gain borné, carry positif). |

---

## 3. Votre premier backtest pas à pas

### 3.1 L'interface et la barre de commande
Sur l'interface web (déployée sur [https://shockdesk.onrender.com](https://shockdesk.onrender.com)), le bandeau supérieur contrôle l'environnement :
* **Sélecteur de Stratégie** : Charge le fichier Python dans l'éditeur.
* **Univers (Bundle)** : Choisit le panier d'actifs (`global-macro`, `us-equities`, `energy-shock`...).
* **Capital initial** : Montant de départ (ex : 25 500 000 $ pour le book macro, 100 000 $ pour les options).
* **Dates (Début / Fin)** : Fenêtre historique testée (ex : `2026-07-01` au `2026-08-28`).
* **Badge Source** : Vert (*données réelles Yahoo Finance*) ou Orange (*modèle factoriel synthétique*).

### 3.2 Structure standard d'une stratégie
Une stratégie ShockDesk reprend la grammaire Blueshift / Zipline :

```python
"""Stratégie d'introduction — Tradage d'un choc macroéconomique."""

def initialize(context):
    # Enregistrement des actifs et planification
    context.asset = symbol('BZ=F')
    schedule_function(trade, date_rules.every_day())

def trade(context, data):
    # Lecture de la prévision active point-in-time (sans triche)
    f = get_forecast('BZ=F')
    if f and f.sign > 0 and not context.portfolio.positions:
        # Prise de position proportionnelle au capital
        order_target_percent(context.asset, 0.30)
        record(spot=data.current(context.asset, 'close'), sign=f.sign)
```

### 3.3 Procédure d'exécution pas à pas
1. Cliquez sur l'onglet **Code**.
2. Dans le menu déroulant, sélectionnez `shock-lab-oil.py`.
3. Vérifiez les paramètres : Univers `global-macro`, Capital `25500000`, Période du `2026-07-01` au `2026-08-28`.
4. Appuyez sur **`Ctrl + Entrée`** (ou cliquez sur le bouton bleu *Lancer le backtest*).
5. L'application bascule automatiquement sur l'onglet **Backtest** avec les métriques calculées.

---

## 4. Comment lire les résultats : Cartes métriques, Courbe & Attribution

### 4.1 Les Cartes Métriques de Performance
* **Capital final & P&L** : Le montant net d'équité en fin de période et le pourcentage de profit réalisé.
* **CAGR** : Le taux de croissance annualisé composé.
* **Volatilité Annualisée & Sharpe** : La régularité de la trajectoire. Un Sharpe > 2,0 reflète un profil très maîtrisé.
* **Max Drawdown** : La pire chute relative enregistrée depuis un sommet.
* **Sortino & Calmar** : Ratios spécifiques mesurant la protection contre les queues de distribution négatives.
* **Win Rate & Trades** : Pourcentage de jours gagnants et nombre total d'ordres exécutés.

### 4.2 La Courbe d'Équité et le Sous-Graphique de Drawdown
* **Courbe d'équité (bleue)** : Montre l'évolution du portefeuille jour après jour comparée au benchmark S&P 500 (gris).
* **Sous-graphique de Drawdown (rouge)** : Met en évidence les creux d'équité. Une ligne plate à 0 % témoigne d'un capital continuellement préservé ou en nouveaux sommets.

### 4.3 Le Tableau d'Attribution : Qui a Payé, Qui a Coûté ?
L'attribution décompose le résultat net ligne par ligne sur le book de démonstration :

| Symbole | Actif | P&L Réalisé ($) | Rôle dans le book |
|---|---|---|---|
| `BZ=F` | Brent Crude Oil | **+283 621 $** | Ligne porteuse du choc haussier (take-profit au pic) |
| `DBC` | Matières Premières | **+61 026 $** | Contagion positive du complexe commodités |
| `^GSPC` | S&P 500 (Short) | **+55 143 $** | Couverture macroéconomique vendeuse |
| `TLT` | Obligations US 20+ | **+27 364 $** | Refuge obligataire sur tensions géopolitiques |
| `DX-Y.NYB` | Dollar Index | **+23 380 $** | Bid dollar de précaution |
| `HYG` | Crédit High Yield | **+6 021 $** | Portage de carry sur obligations énergie |
| `GC=F` | Or (Futures) | **−71 012 $** *(synthétique)* | **Pas un miss sur yfinance** (+53,0 k$). Le −71 k$ est un artefact du générateur. |

---

## 5. L'Anticipation et le Registre de Prévisions

### 5.1 Pourquoi anticiper ?
Le travers majeur de l'analyse quantitative est le *curve fitting* (sur-optimisation rétrospective). Dans ShockDesk, toute prévision macroéconomique est consignée dans un registre persistant `config/forecasts.json` avant d'être jouée.

```json
{
  "id": "shocklab-2026-07-oil",
  "name": "Choc pétrolier — Brent",
  "asset": "BZ=F",
  "benchmark": "^GSPC",
  "stop_date": "2026-08-05",
  "revisions": [
    {
      "rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.05,
      "peak_day": 7, "reversion": -0.03, "reversion_days": 21,
      "iv_shift": 0.10, "confidence": 0.60,
      "note": "v1 : Brent +5 % en 7 jours, pic J+7, puis reversion -3 % au stop."
    }
  ]
}
```

### 5.2 Les règles d'or de l'anticipation
1. **Pas de fuite d'information** : L'appel `get_forecast('BZ=F')` dans le code filtre automatiquement les révisions publiées postérieurement à la date simulée.
2. **Scorecard net du drift** : Le succès directionnel est mesuré après soustraction de l'effet de marché ($\text{Rendement actif} = \text{Rendement brut} - \beta \times \text{Drift S&P 500}$).
3. **Inviolabilité de l'évaluation** : Seule la première révision ($r_1$) est comptabilisée dans le Scorecard officiel pour interdire toute triche ex-post.

---

## 6. L'Exemple réel du choc pétrolier (Brent +18,5 % vs +5 %) & La révision de modèle

### 6.1 Ce qui a été prévu vs Ce qui s'est réellement passé
* **Publication (15 juillet 2026)** : Brent à 84,95 $. Scénario : hausse de +5 % en 7 jours (pic théorique à J+7, soit le 22 juillet), puis retournement baissier vers −3 % au stop calendar fixé d'avance au 5 août.
* **Réalité de marché** :
  * Le Brent a atteint son pic à **+18,5 % le 23 juillet (J+8)** à 100,69 $.
  * L'erreur de timing n'était que de **1 jour ouvré** !
  * Cependant, l'amplitude réelle a été **×3,7 plus violente** que prévue.
  * Au stop calendar du 5 août, le Brent s'était effondré à **−6,5 % sous son prix de publication initial**.

### 6.2 Les deux grandes leçons de desk
1. **Le signal de timing a de la valeur, la vue directionnelle brute n'en a pas** :
   * Sortir au jour de pic du modèle (J+7) figeait **+178 k$ (+0,70 %)** sur le book 25,5 M$.
   * Sortir au stop calendar du 5 août n'a figé que **+99 k$ (+0,39 %)**.
   * Le signal de timing a capturé à lui seul **+79 k$ (31 points de base)** de P&L.
2. **L'architecture multi-actifs protège contre l'erreur de modèle** :
   * Au stop, la ligne brute pétrole a terminé négative (−94 k$), mais le book global gagne grâce aux positions courtes actions (^GSPC +243 k$) et aux refuges.

### 6.3 La révision $r_2$ (28 août 2026) : La Grille d'Amplitudes
Pour corriger le modèle sans falsifier l'historique, la révision 2 remplace le chiffre fixe par une grille de stress :
```json
{
  "rev": 2, "date": "2026-08-28", "sign": 1,
  "amplitude": [0.05, 0.10, 0.185],
  "peak_day": [7, 9],
  "reversion": -0.065, "iv_shift": 0.14,
  "note": "Correction phase 1 : amplitude passée en grille, pic J+7 à J+9."
}
```

---

## 7. L'Atelier d'Options & Payoffs calculés

Dans l'onglet **Options**, ShockDesk propose un atelier complet de pricing Black-Scholes avec surface d'IV paramétrique.

Exemple complet sur **SPY** (Spot = 642,00 $, Maturité 30 jours, Taux sans risque $r = 4,1\ \%$) :

### 7.1 Long Strangle (Strikes 625 Put / 660 Call)
* **Jambes** : Achat 1 Put strike 625 (prime = 4,80 $) + Achat 1 Call strike 660 (prime = 5,88 $).
* **Débit net payé** : **10,69 $** par contrat (Perte maximale bornée à 10,69 $).
* **Points morts (Breakevens)** :
  * Point mort bas : $625 - 10,69 = \mathbf{614,31\ \$}$ (−4,3 %)
  * Point mort haut : $660 + 10,69 = \mathbf{670,69\ \$}$ (+4,5 %)
* **Payoff à l'échéance** :
  * Si SPY = 600 $ : P&L = $(625 - 600) - 10,69 = \mathbf{+14,31\ \$}$
  * Si SPY = 640 $ : P&L = $\mathbf{-10,69\ \$}$ (perte maximale)
  * Si SPY = 680 $ : P&L = $(680 - 660) - 10,69 = \mathbf{+9,31\ \$}$
* **Usage desk** : Acheter du gamma pur quand un choc d'amplitude violent est imminent.

### 7.2 Call Butterfly (Strikes 620 / 640 / 660)
* **Jambes** : +1 Call 620 (27,69 $) / −2 Calls 640 (14,27 $) / +1 Call 660 (5,88 $).
* **Débit net payé** : $27,69 - 2 \times 14,27 + 5,88 = \mathbf{5,03\ \$}$.
* **Gain maximal** : $(640 - 620) - 5,03 = \mathbf{14,97\ \$}$ (exactement au corps à 640 $).
* **Perte maximale** : **5,03 $** (si le cours finit sous 620 $ ou au-dessus de 660 $).
* **Points morts** : **625,03 $** et **654,97 $**.
* **Payoff à l'échéance** :
  * Si SPY = 640 $ : P&L = $\mathbf{+14,97\ \$}$ (rendement de **+297 %** sur le capital risqué !).
  * Si SPY $\le 620\ \$$ ou $\ge 660\ \$$ : P&L = $\mathbf{-5,03\ \$}$.
* **Usage desk** : Monétiser un timing exact sur un niveau de cours avec risque très borné.

### 7.3 Iron Condor (Strikes 620 / 630 / 650 / 660)
* **Jambes** : +1 Put 620 (3,61 $) / −1 Put 630 (6,27 $) / −1 Call 650 (9,45 $) / +1 Call 660 (5,88 $).
* **Crédit net encaissé** : $(6,27 - 3,61) + (9,45 - 5,88) = \mathbf{6,23\ \$}$.
* **Gain maximal** : **6,23 $** (si SPY reste confiné entre 630 $ et 650 $).
* **Perte maximale** : Écart de spread (10 $) − Crédit (6,23 $) = **3,77 $**.
* **Points morts** : **623,77 $** et **656,23 $**.
* **Payoff à l'échéance** :
  * Si SPY reste dans le range [630 ; 650] : P&L = $\mathbf{+6,23\ \$}$.
  * Si SPY décroche à 600 $ ou flambe à 680 $ : P&L = $\mathbf{-3,77\ \$}$.
* **Usage desk** : Vente de volatilité et récolte de prime (theta carry) en l'absence de choc.

---

## 8. Les 3 portes d'entrée & La boucle de revue mensuelle

ShockDesk applique une grammaire stricte et identique sur trois interfaces :

### 8.1 Les Trois Portes d'Entrée
1. **URL de recherche Blueshift** : Partage direct d'un backtest via query string :
   ```
   /research/strategies/<id>/code?name=global-macro&startCapital=25500000&startDate=2026-07-01&endDate=2026-08-28&action=backtest
   ```
2. **API HTTP REST** : Automatisation et intégration dans des scripts d'analyse :
   ```bash
   curl -X POST localhost:8050/api/backtest \
     -H 'Content-Type: application/json' \
     -d '{"strategy_id":"...","name":"global-macro","startCapital":25500000,"startDate":"2026-07-01","endDate":"2026-08-28"}'
   ```
3. **Ligne de Commande (CLI)** :
   ```bash
   python -m shockdesk.cli backtest --strategy shock-lab-oil --name global-macro --start-capital 25500000 --start-date 2026-07-01 --end-date 2026-08-28
   ```

### 8.2 La Boucle de Revue Mensuelle (`CLI revue`)
Chaque fin de mois, le quant lance la revue de desk :
```bash
python -m shockdesk.cli revue --name global-macro --asof 2026-08-28 --window 45
```
Cette commande exécute 4 audits automatisés :
1. **Score des prévisions échues** : Contrôle du taux d'accord de signe net du drift et de l'erreur médiane de pic.
2. **Révisions à écrire** : Génère automatiquement les requêtes `curl` JSON avec les nouvelles grilles d'amplitudes.
3. **Calibration à reprendre** : Compare la volatilité réalisée sur 1 an à la volatilité calibrée dans `config/calibration.json` et alerte si l'écart dépasse 15 %.
4. **Tournoi des stratégies** : Compare les stratégies actives face au benchmark de momentum us-equities.

---

## 9. Glossaire complet & Les 7 règles d'or

### 9.1 Glossaire de Desk
* **MFE (Maximum Favorable Excursion)** : Le plus grand gain latent atteint en cours de position.
* **MAE (Maximum Adverse Excursion)** : La plus grande perte latente essuyée en cours de position.
* **Smile & Skew de Volatilité** : La courbe des volatilités implicites par strike. Le skew reflète la prime accordée aux puts face au risque de krach.
* **Vega Crush** : Effondrement violent de la volatilité implicite consécutif au dénouement d'un événement macro attendu.
* **Slippage** : Écart d'exécution entre le cours théorique au moment de l'envoi de l'ordre et le cours réel d'exécution.

### 9.2 Les 7 Règles d'Or du Trader ShockDesk
1. **Zéro fuite d'information** : N'utilisez que des données et prévisions strictement antérieures à la date simulée.
2. **Nettoyer le drift de marché** : Un gain qui ne bat pas le benchmark passif pondéré par le beta n'est pas de l'alpha.
3. **Le timing bat la prédiction de cours** : Coupez vos positions au jour de pic prévu plutôt que d'attendre un cours chimérique.
4. **Stresser sur une grille d'amplitudes** : Ne pariez jamais votre book sur un chiffre unique, testez une fourchette complète.
5. **Borner son risque avec les options** : Préférez toujours les structures fermées (condors, butterflies) aux positions courtes nues.
6. **Inviolabilité du registre** : Corrigez vos hypothèses via une nouvelle révision sans jamais falsifier la révision originale $r_1$.
7. **Recalibration mensuelle** : Ajustez régulièrement les paramètres de volatilité et de corrélation pour rester synchronisé avec la réalité de marché.

5. **Borner son risque avec les options** : Préférez toujours les structures fermées (condors, butterflies) aux positions courtes nues.
6. **Inviolabilité du registre** : Corrigez vos hypothèses via une nouvelle révision sans jamais falsifier la révision originale $r_1$.
7. **Recalibration mensuelle** : Ajustez régulièrement les paramètres de volatilité et de corrélation pour rester synchronisé avec la réalité de marché.
