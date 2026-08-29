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
*Fin du log de veille du 30/08/2026. Ce fichier sera mis à jour à chaque cycle mensuel de révision.*
