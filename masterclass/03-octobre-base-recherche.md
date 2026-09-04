# Base de recherche — octobre 2026

Septembre = candidat oral. Octobre = desk qui *produit*.
On ne reprend pas le Drive au kilomètre. On ouvre ce qui a été **parké**
et on branche ShockDesk palier 2.

Recherche de stage : **reprise au 1er octobre**, pas avant, et seulement
si le pitch du 30/09 tient.

---

## 1. Drive restant (volontairement hors septembre)

| Fichier | Pourquoi octobre | Livrable recherche |
|---|---|---|
| Financial machine learning (LdP) | Trop lourd, et ce n'est pas un oral S&T | 1 note : purged K-fold, CUSUM, triple barrier — ce qu'on *n'implémente pas* encore dans ShockDesk |
| Machine learning finance | Idem | Fiche 2 pages « ce que ML ne remplace pas sur un desk vol » |
| Introduction to Quant Investing With Python | Backtest générique, on a déjà ShockDesk | Uniquement si on veut un momentum hors `us-equities-momentum.py` |
| Quantitative Trading With R | Langage hors stack | Skip sauf besoin école |
| Rejda — Risk Management and Insurance | Piste assurance, pas S&T | Si un entretien ALM assureur apparaît |
| Sandström — Solvency | Idem | SCR, MCR : fiche 1 page le jour J-2 d'un entretien |
| Gregory xVA ch. 5+ | Septembre = vocabulaire | Mini-pricer CVA toy sur 1 call |
| Convertible Arbitrage ch. 4+ | Septembre = décomposition | Un convertible toy + greek credit |
| Ramirez (reste) | Corporate eq. deriv. | Warrants, collars corporate : fiche |
| Cotton Trading Manual (reste) + ICAC + WASDE | Desk commo différenciant | **Projet octobre A** |
| Projet recherche pricing EU | Déjà servi au MC J5/J20 | Archive |

---

## 2. Trois projets octobre (dans l'ordre)

### Projet A — Desk coton (Drive COMMO à 100 %)

Le Drive a un angle que personne n'attend d'un junior SKEMA : coton.
Objectif : une note 4 pages + un univers ShockDesk `soft-commo` si les
données tiennent.

- Townsend : contrat, qualité, calendrier, hedges producteurs.
- ICAC + WASDE : stock/use, hémisphères, ce qui a bougé depuis nov. 2025.
- Garner : structures d'options déjà vues en J18, appliquées au coton.
- Lien pétrole : pas forcé. Si tu n'as pas de canal, tu le dis.

Livrable : `recherche/2026-10-cotton.md` + éventuellement une prévision
ShockDesk datée, **r1 inviolable**.

### Projet B — ShockDesk palier 2 (journal déjà écrit)

Rien d'inventé : c'est le backlog du 30/08.

Priorité 1 (1 semaine) :

1. Filtre `MIN_EDGE` sur le **nœud haut** de la grille, pas la médiane.
2. Sortie échelonnée (½ au pic, ½ qui court).
3. Créditer le cash au sans-risque **ou** afficher Sharpe hors rf.
4. Identifiant de run + export CSV.

Priorité 2 :

5. Vol targeting.
6. Univers `XLE` / `XOP` déjà recommandé.
7. Walk-forward.
8. Comparaison côte à côte de deux variantes.

Hors octobre (palier 3) : chaîne CBOE, smile calé, VaR/ES dans le moteur,
marge, intraday.

### Projet C — xVA + convertible (Drive ALM + EXOTICS restants)

- Gregory : CVA d'un call EU, 1 contrepartie, intensité constante.
- Convertible : bond floor + option, 1 choc crédit, 1 choc vol.
- Relier au ROADMAP ShockDesk « pas de coût de financement » : note
  « ce que le backtest ment ».

---

## 3. Boucle mensuelle ShockDesk (inchangée)

Chaque 1er vendredi du mois :

```
python -m shockdesk.cli revue --name global-macro --asof YYYY-MM-DD
```

1. Scorecard r1 seulement.
2. Révision datée, jamais de réécriture.
3. Recalibrer `config/calibration.json`.
4. Battre `us-equities-momentum` sur la même fenêtre, sinon la stratégie
   ne passe pas.
5. Journal : provenance sur **chaque** chiffre.

Octobre ouvre aussi `energy-shock` et `rates-fx` dans la revue.

---

## 4. Ce que septembre doit laisser à octobre

Dans le zip (après validation) :

```
masterclass/
  01-programme-…          ← gelé
  02-catalogue-drive.md   ← gelé
  03-octobre-…            ← cette feuille, vivante
  livrables/              ← 22 scripts
  suivi/fiche-septembre.md
recherche/                ← vide le 30/09, première note le 02/10
```

Le journal ShockDesk (`docs/journal-de-bord-recherche.md`) reste dans
shockdesk, pas dans le pack. On n'y mélange pas les oraux.
