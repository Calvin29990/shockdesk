# Feuille de route — ShockDesk

## Phase 1 (ce dépôt) — le poste de travail

Ce qui est en place :

- [x] Backtest multi-actifs à la forme Blueshift (URL, éditeur, métriques,
      attribution, journal)
- [x] Couche options synthétique : pricing Black-Scholes, surface d'IV, grecs,
      règlement à l'échéance
- [x] Catalogue de structures : strangle, straddle, butterfly, iron condor,
      call/put spread, risk reversal, calendar
- [x] Registre de prévisions révisables, lecture point-in-time
- [x] Scoring ex-post : signe net du drift, erreur de timing du pic, ratio
      d'amplitude, MFE/MAE, corrélation de trajectoire
- [x] Recommandation de structures à partir d'une prévision (amplitude attendue
      contre prime payée)
- [x] Trois sources de données (yfinance, CSV, synthétique) avec provenance
      affichée
- [x] CLI + API + interface, une seule grammaire de paramètres
- [x] 44 tests

## La boucle mensuelle (à faire tourner dès maintenant)

Chaque mois, dans cet ordre :

1. **Rejouer** les prévisions publiées sur données réelles
   (`python -m shockdesk.cli scenarios --name global-macro`).
2. **Corriger par révision** : amplitude en grille plutôt qu'en chiffre, fenêtre
   de pic plutôt qu'un jour, choc d'IV.
3. **Recalibrer** `config/calibration.json` : niveaux de référence, volatilités
   réalisées, betas, IV de base.
4. **Comparer** chaque stratégie de scénario au momentum de référence sur la même
   fenêtre. Ce qui ne bat pas la référence ne passe pas en phase 2.
5. **Journaliser** les misses dans la note de révision — pas dans un coin.

## Phase 2 — ce qui manque pour trader sérieusement

### Données
- [ ] Chaîne d'options réelle (chaîne CBOE / broker) au lieu de la surface
      paramétrique
- [ ] Smile et structure en terme calés sur le marché, par sous-jacent
- [ ] Stockage local des historiques (parquet) pour ne pas re-télécharger
- [ ] Dividendes discrets, rolls de contrats futures

### Moteur
- [ ] Barres intraday et exécution au VWAP/à l'ouverture
- [ ] Collatéral de marge et appels de marge sur les positions vendeuses
- [ ] Coût de financement (repo, emprunt de titres)
- [ ] Contraintes de liquidité : taille max par ligne, impact de marché
- [ ] Walk-forward et échantillonnage bootstrap des fenêtres

### Anticipation
- [ ] Grille de stress factorielle (choc sur les facteurs, pas seulement sur le
      sous-jacent) propagée à tout le book
- [ ] VaR / ES conditionnelle du book sous chaque nœud de la grille
- [ ] Suivi du Brier score et de la calibration des probabilités publiées
- [ ] Journal de bord des décisions (pourquoi ce sens, cette taille, ce stop)

### Desk
- [ ] Comparaison côte à côte de deux stratégies sur la même fenêtre
- [ ] Export des résultats (CSV, PDF) pour la revue mensuelle
- [ ] Sauvegarde des runs (un backtest = un identifiant conservé)
- [ ] Multi-utilisateur et authentification si déploiement partagé

## Idées notées, non priorisées

- Signal de pic comme règle de sortie systématique, backtestée sur plusieurs
  scénarios historiques plutôt que sur un seul exercice.
- Vendre la volatilité *après* le pic (crush) plutôt que pendant : la structure
  et le timing ne sont pas les mêmes.
- Relier chaque trade à la révision de prévision qui l'a déclenché, pour mesurer
  la contribution de chaque génération de prévisions.
