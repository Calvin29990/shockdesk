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

> ✅ **Vérifié le 30/08/2026 sur données réelles** (mesure A, `0.40`) : les prédictions du
> carnet étaient **bonnes** — P&L **+159 040 $**, volatilité **1,13 %**, drawdown **−0,04 %**.
>
> ⚠️ **Mais le carnet oubliait le piège du Sharpe**, et c'est la vraie leçon de l'atelier :
>
> | | `0.40` | `0.85` | `1.00` |
> |---|---|---|---|
> | Exposition cible | 38 % | 82 % | 96 % |
> | **P&L** | +159 040 $ | +337 887 $ | **+397 485 $** |
> | Volatilité | 1,13 % | 2,40 % | 2,83 % |
> | Drawdown max | −0,04 % | −0,08 % | −0,10 % |
> | Échangé | 28,7 M$ | 60,6 M$ | 72,0 M$ |
> | **Sharpe** | **−0,24** | **1,67** | **1,93** |
> | **Sortino** | **−2,29** | **15,91** | **18,32** |
>
> Le P&L et la volatilité sont **rigoureusement proportionnels** à l'exposition. Le Sharpe,
> lui, s'effondre et **passe en négatif** alors que la stratégie a gagné 159 040 $.
> Pourquoi ? Parce que ShockDesk retire un **taux sans risque de 4,1 % par an** à votre
> rendement, **y compris les jours où le book dort en cash** — alors que le moteur ne vous
> paie aucun intérêt sur ce cash. À `0.40`, votre CAGR (3,90 %) passe juste sous 4,1 % :
> l'excédent devient négatif, donc le Sharpe aussi.
>
> **À retenir** : sur un book qui sort au pic et reste en liquidités, **le Sharpe et le
> Sortino ne mesurent pas la qualité de votre trade** — ils mesurent surtout le coût
> d'opportunité du cash. Ne les utilisez jamais seuls pour classer deux variantes.
>
> 🔬 **La preuve, en trois chiffres.** Si l'on recalcule le Sharpe *sans* retirer le taux
> sans risque, on obtient :
>
> | `BASE_EXPOSURE` | 0.40 | 0.85 | 1.00 |
> |---|---|---|---|
> | Sharpe affiché | −0,24 | 1,67 | 1,93 |
> | **Sharpe hors sans-risque** | **3,36** | **3,36** | **3,36** |
>
> **La qualité risque-ajustée du trade est strictement identique dans les trois cas.**
> Toute la variation du Sharpe affiché vient de la soustraction d'une constante. Le levier
> change la *taille* du trade, jamais sa *qualité* — c'est la définition même d'un bouton
> de volume.

---

### 📌 Atelier 3 : Neutraliser le "Miss" (L'Or `GC=F`)
* **Objectif** : Mesurer ce que rapporte le book lorsqu'on corrige un actif dont le comportement divergeait de la thèse.
* **Paramètre à tester** : Ligne 21 dans le dictionnaire `BOOK` :
  ```python
  "GC=F": 0.00,   # Mettez le poids de l'or à 0.00 (au lieu de 0.10)
  ```
* **Ce qu'il faut observer** — valeurs **vérifiées le 30/08/2026** sur données réelles Yahoo
  (25,5 M$, 42 barres, `BASE_EXPOSURE = 0.85`, `TAKE_PROFIT_AT_PEAK = True`) :

  | | Avec l'or (`0.10`) | Sans l'or (`0.00`) | Écart |
  |---|---|---|---|
  | **P&L** | **+337 887 $ (+1,32 %)** | **+318 756 $ (+1,25 %)** | **−19 131 $** |
  | Sharpe | 1,67 | 1,47 | dégradé |
  | Sortino | 15,91 | **4,44** | ÷3,6 |
  | Drawdown max | −0,08 % | **−0,15 %** | ×1,9 |
  | Calmar | 102,37 | 53,24 | ÷1,9 |
  | Alpha | −1,73 % | −1,80 % | dégradé |
  | Trades | 21 | 18 | une ligne en moins |

  Attribution sans l'or : `BZ=F` **+209,4 k$** · `^GSPC` **+91,8 k$** · `DBC` **+52,3 k$** ·
  `DX-Y.NYB` +5,9 k$ · `TLT` −27,6 k$ · `HYG` −13,1 k$.

* **Diagnostic Desk — entièrement réécrit le 30/08/2026.** Le carnet annonçait une perte de
  −71 k$ sur l'or et un P&L grimpant à « plus de +400 k$ ». **Tout était faux sur données
  réelles.** Les trois vraies leçons :

  1. **L'or n'était pas une perte, c'était un gain de +53,0 k$** (+4,9 % réalisés contre 3,0 %
     prévus, scorecard ✔). Le chiffre de −71 k$ venait du générateur synthétique.
  2. **Retirer une ligne ne supprime pas son P&L — ça le redistribue.** Les poids sont
     normalisés par l'exposition brute (`total = Σ|w|`, ligne 92). Passer de 0,94 à 0,84
     multiplie **chaque ligne restante par 1,119** : vérifié au dollar sur les six lignes
     (187,1 → 209,4 · 82,0 → 91,8 · 46,7 → 52,3 · 5,3 → 5,9 · −11,7 → −13,1 · −24,6 → −27,6).
     Formule : `P&L_après = (P&L_avant − contribution_retirée) × 1,119`.
  3. **Le retrait dégrade aussi le risque** : drawdown −0,08 % → **−0,15 %**, Sortino 15,91 →
     **4,44**. L'or était un **diversifiant**, pas un boulet.

  → **La vraie leçon** : dans un book normalisé, « nettoyer » une ligne n'est jamais neutre —
  on retire sa contribution *et* on redimensionne tout le reste. Et une ligne classée « miss »
  sur données synthétiques peut être un diversifiant sur données réelles. C'est pour ça que
  la source des données reste le premier réflexe du desk.
* **Action** : remettez `"GC=F": 0.10` pour revenir à l'état de référence.

---

# ⚔️ NIVEAU 2 — EXPLORATION DES STRATÉGIES ALTERNATIVES

> 🔧 **Le moteur a changé le 30/08/2026** (commit `bad72a2`) : les frais par contrat sont
> désormais calculés sur la **taille réelle du contrat** (1 000 barils pour le Brent) et non
> plus sur l'unité. Conséquence : **tous les repères chiffrés des Ateliers 4, 6, 7 et 8,
> établis avant cette date, sont périmés.** Ne les cherchez plus : re-mesurez-les. C'est une
> bonne nouvelle — c'est la première fois que ces ateliers vont produire des montants
> réalistes. Le book delta, lui, n'est pas affecté (P&L identique au dollar près).
> *(L'Atelier 5, laboratoire d'options, a été re-mesuré le 30/08/2026 ; l'Atelier 7 l'a été
> aussi — voir leurs fiches.)*
>
> 🔧 **Second changement de frais le 30/08/2026** : la correction ci-dessus divisait par la
> taille du contrat *au comptant* — exacte pour le Brent (1 000 barils), fausse pour les ETF,
> actions et indices, dont le contrat d'option porte **100 parts**. Les frais d'options sur
> ETF étaient donc encore **100× trop élevés** (410,80 $ sur une jambe de 1 233 $).
> Les repères de l'**Atelier 8** (iron condor sur SPY) établis avant cette date sont
> **périmés une deuxième fois** : re-mesurez-les. Les ateliers 4, 6 et 7 portent sur
> `BZ=F`/`GC=F` et ne sont **pas** affectés.

### 📌 Atelier 4 : Le Long Strangle (`long-strangle-shock.py`)
* **Objectif** : Découvrir comment gagner sur une explosion de volatilité sans parier sur la direction.
* **Procédure** :
  1. Sélectionnez la stratégie `long-strangle-shock.py`.
  2. Univers : `global-macro`, Capital : `1000000` (1 M$).
  3. Lancer le backtest (`Ctrl + Entrée`).
* **Ce qu'il faut observer** — vérifié le 30/08/2026 sur **données réelles** :
  * **La stratégie refuse de trader : 0 trade, P&L 0 $.** Ce n'est pas un bug.
  * Le journal d'exécution l'explique : `Pas d'entrée : amplitude attendue 5.0% vs prime
    payée 9.6% du spot (edge 0.52 < 1.00). Mouvement implicite ATM 18.4% pour mémoire.`
* **Diagnostic Desk (écrit le 30/08/2026)** : la stratégie impose une discipline —
  `MIN_EDGE = 1.00` (ligne 22) — **on n'achète du gamma que si l'amplitude attendue par la
  prévision dépasse la prime payée**. Ici, le marché faisait payer **9,6 % du spot** pour un
  strangle 30 jours, alors que la prévision r1 n'annonçait que **5,0 %**. Payer 9,6 % pour
  espérer 5 % est une mauvaise affaire : la stratégie a raison de s'abstenir.
  * **Le marché avait raison et le modèle avait tort** : le marché prix un mouvement implicite
    de **18,4 %** là où le modèle annonçait 5,0 %. Et le mouvement réalisé a été de **18,4 %**.
    C'est exactement le facteur **×3,68** déjà consigné au journal : l'erreur est dans la
    **prévision**, pas dans l'exécution.
  * **Le filtre a même évité une perte.** Avec des strikes à ±5 % et 9,6 % de prime payée, le
    point mort haut est à **+14,6 %**. Or à la sortie J+7 (22/07), le Brent valait 94,02
    contre 84,99 à l'entrée, soit **+10,6 %** — *sous le point mort*. Le pic (+18,4 %) est
    arrivé à J+8, un jour trop tard. Le trade, tel qu'il est configuré, **aurait perdu**.
* **Expérience faite le 30/08** (`MIN_EDGE = 0.50`) : **P&L −6 211 $ (−0,62 %), 6 trades**.
  Mais la perte ne vient pas du marché :
  | | |
  |---|---|
  | P&L brut des deux opérations | **+594 $** |
  | Commissions | **−6 805 $** |
  | **Net** | **−6 211 $** |

  ⚠️ **Les frais représentent 14,9 % du volume échangé.** Cause : le multiplicateur de
  contrat vaut **1.0** pour tous les sous-jacents du dépôt, alors que la commission de
  0,65 $ par contrat est calibrée pour un vrai contrat (1 000 barils pour le Brent).
  L'option vaut ~4,25 $ et le frais 0,65 $ : **15 % de la prime à l'achat, ~30 %
  aller-retour**. Consigné au journal comme **correctif prioritaire de phase 2**.
* 🔬 **Preuve que le repère du carnet était faux** : en générateur synthétique, cette
  stratégie donne **exactement +12 084 $ (+1,21 %), 6 trades, Sharpe 0,846** — les chiffres
  mêmes de l'ancien carnet. Ce repère n'a jamais été un résultat de marché.
* **Action** : remettez `MIN_EDGE = 1.00` (ligne 22).

---

### 📌 Atelier 5 : Straddle vs Strangle (ATM vs OTM)
* **Objectif** : Comparer l'achat à la monnaie (Straddle, plus de gamma mais plus cher) et hors de la monnaie (Strangle, moins cher).
* **Paramètre à tester** : Onglet Options, structure `Long strangle` → `Long straddle`
  (SPY, 30 j, largeur 0.03, choc d'IV 0).
* **Ce qu'il faut observer** — vérifié le 30/08/2026 (lab déterministe, reproductible) :

  | | Strangle | Straddle | Écart |
  |---|---|---|---|
  | Prime nette | **10,69** | **24,40** | ×2,3 |
  | Jambes | call 660 (5,88) + put 625 (4,80) | call 640 (14,27) + put 640 (10,12) | — |
  | Gamma | 0,02222 | 0,02592 | +17 % |
  | Vega | 1,242 | 1,450 | +17 % |
  | Theta | −0,344 | −0,405 | +18 % (mais 1,7 %/j de la prime vs 3,2 %) |
  | Delta | 0,056 | 0,128 | — |
  | Points morts | 614,3 / 670,7 | 615,6 / 664,4 | resserrés (±3,8 %) |

* **Diagnostic Desk — le verdict en deux lames** :
  1. **Par structure, le straddle gagne sur tout mouvement au-delà de ±2,1 %.** À +18,4 %
     (642 → 760,13) : straddle **+95,73** vs strangle **+89,44** (+6,29). Son strike est
     20 pts plus proche, ce qui rapporte plus que les 13,71 de prime en plus. Le strangle
     ne gagne que pour les mouvements **inférieurs à ±2,1 %** (il ne perd que sa prime,
     moins chère). La question du carnet (« le gamma ATM compense-t-il la prime ? ») → oui,
     par structure.
  2. **Par dollar déployé, le strangle gagne : 2,13× plus de rendement.** 24,40 $ achètent
     1 straddle ou 2,28 strangles. Sur +18,4 % : straddle ×3,92 de la prime, strangle
     ×8,37. Le straddle ne gagne « par structure » que parce qu'il engage 2,3 fois plus de
     capital.
  → **Leçon** : pour un desk à capital fixe, le strangle OTM reste le meilleur pari sur un
  choc — le moins de prime par unité d'amplitude attendue (logique `MIN_EDGE` de
  l'Atelier 4). Le straddle, lui, est plus patient (theta = 1,7 %/j de la prime vs 3,2 %)
  mais coûte cher à l'entrée.

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
  2. Choisissez `SPY`, structure `Long Strangle`, maturité `30 jours`, largeur `0.03`.
  3. Observez la courbe de payoff et la prime nette.
  4. Notez le **Vega** (gain par point de hausse d'IV) et le **Theta** (coût journalier du temps).
* **⚠️ Piège d'unités — découvert puis corrigé le 30/08/2026** : le champ « choc d'IV
  (pts) » lisait une **fraction** (`0.10` = +10 pts) alors que son libellé promettait des
  points : taper `10` envoyait +1000 pts, écrêtés en silence au plafond d'IV de 400 %
  (prime délirante de 84 % du spot). **Corrigé** : le champ accepte désormais des points
  (10 = +10 pts), et le lab **alerte** quand l'IV atteint le plafond ou que la prime
  dépasse 50 % du spot — plus de cotation hors marché silencieuse. Réflexe desk conservé :
  un résultat hors domaine = chercher l'unité, pas un signal de marché.
* **Ce qu'il faut observer** — vérifié le 30/08/2026 (lab déterministe, reproductible) :

  | | Choc 0 pt | Choc +10 pts | Écart |
  |---|---|---|---|
  | Prime nette | **10,69** | **23,91** | **+13,22 (+124 %)** |
  | Vega | 1,242 | 1,374 | ⤴ +10,6 % |
  | Theta | −0,344 | −0,608 | ×1,77 |
  | Gamma | 0,02222 | 0,01530 | ÷1,45 |
  | Delta | 0,056 | 0,056 | inchangé |
  | Points morts | 614,3 / 670,7 | 601,1 / 683,9 | élargis |
  | IV de la surface | 16,4 / 16,6 % | 26,4 / 26,6 % | +10 pts, additif |

* **Contre-épreuve du Theta (maturité 30 → 1 j, choc 0)** — vérifiée le 30/08/2026 :
  prime **0,00**, vega/theta/gamma **≈ 0**, points morts **= strikes** (625 / 660).
  À 1 jour, l'option 3 % OTM n'a plus de valeur temps : le vega et le theta meurent
  ensemble — un choc d'IV ne vaut que ce que vaut le temps restant.
* **Diagnostic Desk** : l'écart de prime (13,22) dépasse vega × choc (10 × 1,242 = 12,42)
  : les 0,80 restants sont la **volga** — le vega augmente lui-même avec l'IV (végétarien
  moyen ≈ 1,308). Un vega affiché est une **pente locale** : il culmine vers 25-30 % de
  vol puis décroît. Le choc d'IV est un trade directionnel sur la volatilité elle-même :
  +10 pts font payer la structure **+124 % plus cher** pour la même exposition au spot —
  c'est le mécanisme exact que filtre `MIN_EDGE` de l'Atelier 4 (prime ÷ amplitude).

---

### 📌 Atelier 8 : L'Iron Condor en Régime de Range (`iron-condor-range.py`)
* **Objectif** : Récolter la prime du temps qui passe (Theta carry) quand aucune crise n'est annoncée.
* **Procédure** :
  1. Sélectionnez la stratégie `iron-condor-range.py`.
  2. Univers : `us-equities`, Capital : `100000`.
  3. Fenêtre : `2026-01-01` au `2026-08-28`.
* **Ce qu'il faut observer** :
  * La courbe d'équité progresse régulièrement à la hausse grâce à l'érosion continue de la prime des options vendues.
* **Repère mesuré le 30/08/2026** (`us-equities`, 1 000 000 $, 2026-01-01 → 2026-08-28,
  après le correctif des frais par contrat d'option) :
  | Source | Trades | Volume | Frais | P&L |
  |---|---|---|---|---|
  | `synthetic` (lab déterministe) | 68 | 138 773 $ | **313 $** (0,23 %) | **+1 434 $** |
  | `yfinance` (données réelles, avant correctif) | 60 | 85 725 $ | **25 392 $** (29,6 %) | −10 158 $ |
* **La leçon de l'atelier, et elle vaut plus que le chiffre** : avant le correctif, une jambe
  de 1 233 $ payait **410,80 $** de frais. Le P&L négatif n'était pas un verdict de marché,
  c'était une erreur de modélisation — le moteur comptait 632 *parts* d'option comme 632
  *contrats*, alors qu'un contrat d'option US en porte 100. **Toujours lire la colonne
  « commission » du journal des transactions avant de commenter un P&L d'options** : si le
  rapport frais/volume dépasse ~1 %, ce n'est pas la stratégie qu'il faut revoir.
* **Action** : relancez le run sur données réelles et notez le P&L obtenu au tableau de bord ;
  le repère « ≈ +15 000 $ » annoncé au journal est une attente à vérifier, pas un résultat.

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
| **Atelier 2** | Exposition globale | `BASE_EXPOSURE = 0.40 / 1.00` | ✅ Fait · 30/08 | +159 040 $ / +337 887 $ / +397 485 $. Tout scale au même facteur. Sharpe affiché −0,24 / 1,67 / 1,93 mais **3,36 / 3,36 / 3,36** hors taux sans risque → le levier change la taille, pas la qualité. |
| **Atelier 3** | Nettoyage du Miss | `BOOK['GC=F'] = 0.00` | ✅ Fait · 30/08 | +337 887 $ → **+318 756 $** (−19 131). L'or rapportait **+53,0 k$**, il ne coûtait rien. Retrait = redistribution ×1,119 des autres lignes + drawdown ×1,9. Diagnostic du carnet **faux** : corrigé. |
| **Atelier 4** | Long Strangle | Stratégie gamma | ✅ Fait · 30/08 | Refuse de trader (edge 0,52 < 1,00). Forcé à `MIN_EDGE` 0,50 : **−6 211 $**, dont **6 805 $ de frais** pour 594 $ de P&L brut. Repère « +12 084 $ » = artefact synthétique, reproduit au dollar. |
| **Atelier 5** | Straddle vs Strangle | Onglet Options | ✅ Fait · 30/08 | Prime ×2,3 (10,69 → 24,40), gamma/vega +17 %, theta +18 %. À ±18,4 % : straddle gagne **par structure** (+6,29) mais strangle gagne **par dollar** (×2,13). Le levier du strangle = capital efficiency, le straddle = strike proche. |
| **Atelier 6** | Butterfly | Plafond de risque | 🔲 À faire | |
| **Atelier 7** | Vega & IV | Onglet Options | ✅ Fait · 30/08 | Choc 0 → +10 pts : prime 10,69 → 23,91, vega 1,242 → 1,374, theta −0,344 → −0,608, gamma ÷1,45, delta inchangé, points morts 601/684. Écart 13,22 > 10×1,242 : **volga**. ⚠️ Piège d'unités du champ : il lit une fraction (`0.10` = +10 pts) ; un « 10 » = +1000 pts, écrêtés en silence à 400 % d'IV. |
| **Atelier 8** | Iron Condor | Carry de prime | 🟡 Lancé · 30/08 | 1 M$ : **−10 158 $** sur données réelles, dont **25 392 $ de frais** pour 85 725 $ échangés → frais d'options sur ETF surcomptés ×100 (contrat d'option = 100 parts, corrigé le 30/08). Repère à re-mesurer : ≈ +15 k$ attendu. |
| **Atelier 9** | Révision $r_2$ | Onglet Anticipation | 🔲 À faire | |
| **Atelier 10** | CLI Revue | Revue mensuelle | 🔲 À faire | |
