# Post LinkedIn — ShockLab : le scénario vs la réalité (angle desk)

> Fichier de travail du 28/08/2026. Données réelles via yfinance (Brent BZ=F, ^GSPC, TLT, GC=F, DX-Y.NYB, HYG, DBC).

---

## 🖼️ Plan visuel (2–3 graphs, dans l'ordre)

| # | Fichier | Contenu | Rôle dans le post |
|---|---|---|---|
| 1 | `chart1_validation_pct.png` | Courbe réalité (plein) vs modèle (pointillé), **en %**, base 0 = publication. Pré-pub en gris (le choc avait déjà démarré — assumé), après-stop en gris pointillé | La validation honnête : timing du pic à 1 jour près, amplitude ×3,7 sous-estimée |
| 2 | `chart2_pnl_cumule.png` | P&L cumulé **réel** du book 25,5 M$ (delta), entrée = pub, stop ex-ante, pic annoté J+7 | Le graph desk : la trajectoire du trade, pas une opinion |
| 3 | `chart3_delta_pnl.png` | Delta (M$) et P&L réel (k$) par ligne au stop | L'attribution : qui a payé, qui a protégé |

**Les 3 charts sont en % / en k$ — jamais en niveau de prix.** Pas de magie : le pré-pub et le post-stop sont visibles, en gris, étiquetés « hors périmètre ».

---

## 📊 Les chiffres à connaître (tous réels)

| Élément | Valeur |
|---|---|
| Publication | 15 juillet 2026, Brent 84,95 $ |
| Scénario modèle | +5 % en 7 jours (pic J+7), puis reversion −3 % |
| **Pic réel du Brent** | **+18,5 % le 23 juillet (J+8)** — le pic modèle tombait le 22 (J+7) : **1 jour d'écart** |
| Amplitude | modèle +5 % vs réel +18,5 % → **sous-estimée ×3,7** |
| Au stop (5 août, fixé ex-ante) | Brent −6,5 % vs pub · réel sous le niveau de publication |
| Accord de signe (net du drift SPX) | **5/7** — Brent ✔ TLT ✔ USD ✔ HYG ✔ DBC ✔ · Or ✘ · SPX ✘* |
| **P&L book réel — pic** | **+178 k$ (+0,70 %) le 22 juillet = J+7, le jour du pic modèle** |
| **P&L book réel — stop** | **+99 k$ (+0,39 %) figés** |
| Après le stop (hors périmètre) | +663 k$ au 27 août — surtout du drift actions, **on ne se l'approprie pas** |
| Attribution au stop | S&P +243 k$ · Or +69 k$ · HYG +9 k$ · DBC −6 k$ · USD −25 k$ · TLT −43 k$ · **Brent −94 k$** |

\* SPX = benchmark de drift → non-test par construction (en brut : −1,2 % dans le sens prédit).

**L'insight desk** : sortir à la date de pic du modèle (J+7) figeait +178 k$ ; le stop calendar a figé +99 k$. Le signal de pic vaut **+79 k$ (31 pb)** sur un seul exercice — c'est monétisable. Et la ligne Brent finit négative (−94 k$) : c'est l'**architecture multi-actifs** qui porte le P&L, pas la vue directionnelle pétrole.

---

## ✍️ VERSION A — Récit honnête, angle desk (recommandée)

Le 15 juillet, j'ai publié un scénario de choc pétrolier avec une règle : stop du backtest au 5 août, date fixée avant de regarder quoi que ce soit.

Le marché a répondu. Voici le score, en %, sans filtre. 👇

→ Mon scénario datait le pic à J+7. Le Brent a pic à J+8 : +18,5 % le 23 juillet. Le timing est tombé à un jour près.

→ Mais mon amplitude était ×3,7 trop faible (+5 % prédits), et la reversion a tout emporté : au stop du 5 août, le Brent était SOUS son niveau de publication (−6,5 %).

→ Sens du choc, net du drift marché : 5/7 classes d'actifs dans le sens prédit (Brent, obligations, dollar, crédit HY, matières premières). Miss sur l'or.

La partie que un desk voudra lire : le P&L réel du book 25,5 M$, delta uniquement.

▪️ Pic : +178 k$ (+0,70 %) le 22 juillet — précisément J+7, le jour de pic du modèle
▪️ Stop calendar du 5 août : +99 k$ (+0,39 %) figés
▪️ Attribution : les actions ont payé (+243 k$), la ligne Brent a fini à −94 k$. La valeur n'est pas dans la vue directionnelle — elle est dans l'architecture du book et dans le signal de pic.

3 leçons :

1️⃣ Un modèle de choc vend du TIMING, pas des niveaux. « +100,69 $ le 23 juillet », personne ne peut. « Le pic est dans 7 jours » : c'est ça qu'un desk peut trader.

2️⃣ Le sens se mesure net du drift. Sans déduire le marché, un backtest ne valide rien — il raconte la marée.

3️⃣ La discipline remplace la précision. Stop fixé ex-ante, périmètre figé, misses affichés (l'or, l'amplitude). Un scénario qu'on ne peut pas perdre, ce n'est plus un scénario.

La v2 de ShockLab : le signal de pic devient règle de sortie (take-profit à J+7) et grille d'amplitudes en stress test.

Et vous, sur vos desks : vous préférez un modèle qui cible le niveau ou le timing ?

#quant #markets #riskmanagement #commodities #backtesting #trading

---

## ✍️ VERSION B — Courte, punchy

J'ai daté le pic d'un choc pétrolier au jour près. Et sous-estimé son amplitude ×3,7.
Les deux sont vrais — et c'est exactement ce qu'un desk doit savoir. 🎯

15 juillet : je publie un scénario Brent +5 % en 7 jours, pic J+7, puis reversion. Stop du backtest fixé d'avance au 5 août.

La réalité :
▪️ Pic réel le 23 juillet (J+8) : +18,5 %
▪️ Reversion totale : Brent SOUS le niveau de pub au stop
▪️ Sens du choc net du drift : 5/7 ✔
▪️ P&L réel du book 25,5 M$ : +178 k$ au pic (le jour J+7 du modèle), +99 k$ figés au stop

Ce que j'en retiens :
→ Un timing à ±1 jour, ça se trade. Une amplitude, ça se couvre (grille de stress, pas un chiffre).
→ Sans nettoyage du drift, un backtest ne mesure rien.
→ La ligne « Brent » finit à −94 k$ : le P&L vient de l'architecture du book, pas de la vue directionnelle. C'est la vraie leçon desk.

v2 en route : take-profit au signal de pic + grille d'amplitudes.

#quant #markets #riskmanagement #backtesting #trading

---

## 💡 Conseils de publication

1. **Ordre des images** : chart1 (validation %) → chart2 (P&L) → chart3 (attribution). Le 1 crée la tension (le pointillé vs le plein), le 2 la résout (le trade), le 3 crédibilise (le détail).
2. **Accroche** : tenir en 3 lignes avant le « …voir plus », sans donner le chiffre final.
3. **Commentaires préparés** : anticiper « +0,39 % c'est peu » → réponse : 39 pb en 3 semaines sur un book diversifié, et le signal de pic vaut +79 k$ à lui seul ; et « pourquoi montrer les misses ? » → parce qu'un backtest sans miss n'est pas un backtest.
4. **Hashtags** : 4–6, à la fin. Répondre aux premiers commentaires dans l'heure (créneau conseillé : mardi–jeudi 8h30–9h30).
5. **Chiffres à ne pas confondre** : +18,5 % = vs publication (le bon repère) ; +40,7 % = vs 1er juillet (contexte, pas de la prédiction). Le +663 k$ post-stop : surtout du drift actions → hors périmètre, on ne se l'approprie pas.
