# Programme élite — 5 → 30 septembre 2026

**Cible :** candidat S&T / Quant / Risk qui parle FR et EN, écrit au tableau,
code le modèle, et *montre* le trade sur ShockDesk.
**Périmètre :** 100 % du Drive. Rien d'autre, sauf approfondir un fichier
déjà ouvert.
**Stage :** pause jusqu'au 30/09. Zéro LinkedIn, zéro candidature, zéro
relance. La seule « vente » du mois, c'est le trade pitch du 30.
**Lab :** ShockDesk (onglets réels uniquement) + `calvin-exotic-desk` pour
les structurés. Pas d'onglet ALM, pas d'onglet Risk, pas de galerie
d'autocalls — ils n'existent pas.

Septembre n'a pas de 31. Fin = **mercredi 30**.

---

## 1. Contrat de journée

| Mode | Durée | Quand |
|---|---|---|
| **Élite (défaut)** | **5 h 30** | 22 jours ouvrés |
| Compressé | 4 h 00 | jour de panne, jamais deux jours de suite |
| Off | 0 h (+ 20 min flashcards optionnelles) | **dimanches 6, 13, 20, 27** |

Si un livrable du jour n'est pas fait, le dimanche suivant n'est plus off :
c'est un rattrapage. Un élite ne « reporte pas à octobre » un oral de
septembre.

### Découpage élite (5 h 30)

| Bloc | Temps | Règle |
|---|---|---|
| A. Cours Drive | 1 h 30 | chapitres listés, crayon en main, **pas de surlignage passif** |
| B. TD manuscrit | 1 h 00 | papier, pas d'écran. Preuve ou calcul. |
| C. Lab | 0 h 45 | ShockDesk *ou* exotic-desk, exercice du jour, capture + 5 lignes au journal |
| D. Marché | 0 h 30 | *voir* le concept du jour (courbe, smile, Brent, 2s10s, coton) |
| E. Oral WORDS | 0 h 45 | minuterie 90 s FR + 90 s EN par question, à voix haute |
| F. Brainteasers | 0 h 30 | 3 problèmes, solutions fermées, re-faire ceux ratés le lendemain |
| G. Python | 0 h 30 | le fichier du jour **existe** dans `masterclass/livrables/` sinon le jour n'est pas clos |

### Découpage compressé (4 h)

A 60 · B 45 · C 30 · D 15 · E 40 · F 25 · G 25.

---

## 2. Ce que « élite » veut dire le 30/09 au soir

Tu dois pouvoir, sans notes, en 8 minutes, dans les deux langues :

1. Prouver la parité call-put et citer les 6 hypothèses de Black-Scholes (Hull).
2. Donner le signe de Δ, Γ, ν, Θ sur un long straddle et *montrer* le choc
   +10 pts d'IV sur ShockDesk (Atelier 7, nombres 10,69 → 23,91).
3. Choisir la structure pour : haussier, baissier, range, choc d'amplitude,
   timing de niveau — et dire pourquoi le strangle gagne *par dollar* et le
   straddle *par structure* (Atelier 5).
4. Décomposer un Phoenix / Athéna / reverse convertible (WORDS + Bouzoubaa)
   et ouvrir exotic-desk pour le P&L explain.
5. Pricer une obligation, duration, convexité, dire pourquoi on achète le
   zéro si on est long taux (fixed income.pdf + Entrainement questions).
6. Expliquer un repo, un gap ALM, un DV01, un xVA en une phrase chacun.
7. Contango vs backwardation, convenience yield, et le book pétrole
   ShockDesk (timing = 617 520 $ sur données réelles).
8. VaR vs ES, pourquoi ES est cohérente (Skoglund + oral Basel).
9. 10 brainteasers Heard / Joshi / Jane Street / Optiver chrono.
10. Pitcher le trade ShockDesk : vue, catalyseur, structure, grecs, stop,
    miss. C'est le livrable public du mois.

---

## 3. Chiffres ShockDesk à connaître par cœur

Provenance : **yfinance**, `shock-lab-oil`, 25,5 M$, 2026-07-01 → 2026-08-29,
42 barres. Jamais les chiffres synthétiques.

| | Sortie pic J+7 | Stop calendar J+21 |
|---|---|---|
| P&L | **+337 887 $ (+1,32 %)** | **−279 633 $ (−1,10 %)** |
| Valeur du timing | **617 520 $** | |
| Brent | +187,1 k$ | −117,5 k$ |
| S&P (short) | +82,0 k$ | −213,4 k$ |
| Or | **+53,0 k$** (pas un miss) | +107,2 k$ |
| Misses scorecard | HYG, TLT | |
| Signe net du drift | 4/6 | |
| Brent réalisé vs prévu | +18,4 % vs +5 % → **×3,68** | |

Règle : un chiffre sans provenance n'est pas un chiffre.

---

## 4. Planning — 22 jours

```
         lu ma me je ve sa di
Sep 2026          05 06off
         07 08 09 10 11 12 13off
         14 15 16 17 18 19 20off
         21 22 23 24 25 26 27off
         28 29 30
```

| Bloc | Dates | Thème Drive | Jours |
|---|---|---|---|
| **A** | 5, 7–11 | Vanilles, grecs, vol, structures (Hull, Natenberg, Gatheral intro) | 6 |
| **B** | 12, 14–18 | Exotiques, structurés, surface, FX (de Weert, Bouzoubaa, Gatheral, Clark) | 6 |
| **C** | 19, 21–25 | Taux, ALM, repo, commo | 6 |
| **D** | 26, 28–30 | Quant interview, risque, synthèse, pitch | 4 |

---

# BLOC A — Vanilles (5 → 11 septembre)

## Sam 05/09 — J1 · Parité, forward, Black-Scholes

**Drive P :** Hull *Fundamentals* — chapitres options / BS / parité.
**Drive S :** WORDS *Questions de base* (forward, futures, repo, Sharpe) +
*Questions Produits dérivés* (call/put, EU/US).

| Bloc | Consigne |
|---|---|
| Cours | Hypothèses BS (6). Parité call-put. Forward \(F=S e^{(r-q)T}\), FX \(F=S e^{(r-r_f)T}\), commo \(F=S e^{(r+u-y)T}\). Forward vs futures (marge, MTM). |
| TD | Preuve no-arbitrage de la parité, papier. Trois numericals Hull : action avec q, FX, pétrole avec storage + convenience yield. |
| Lab | ShockDesk onglet **Options** : long call, long put, call spread. Noter prime, BE, payoff. *Ne pas* toucher iv_shift aujourd'hui. |
| Marché | Une chaîne d'options SPY : spot vs 2–3 strikes, sentir ITM/ATM/OTM. |
| Oral | FR : « Pourquoi un call vaut plus cher si la vol monte ? » EN : *Prove put-call parity by no-arbitrage.* Chrono 90 s. |
| Brain | Heard on The Street × 3 (markets / options). |
| Python | `livrables/j01_bs_closed_form.py` — call, put, parité numérique (écart < 1e-10). |

**Ticket de sortie :** tu récites les 6 hypothèses et tu écris la parité les
yeux fermés.

---

## Dim 06/09 — OFF

20 min optionnel : 5 flashcards hypothèses BS + parité. Pas de Drive nouveau.

---

## Lun 07/09 — J2 · Grecs 1 et 2

**Drive P :** Natenberg (delta, gamma, vega, theta) + Hull grecs.
**Drive S :** WORDS *Questions greeks*.

| Bloc | Consigne |
|---|---|
| Cours | Δ = vitesse, Γ = accélération, ν = vol, Θ = loyer du temps, ρ = taux. Signe acheteur vs vendeur. On ne thêta-hedge pas. |
| TD | Signe des 5 grecs : long call, long put, short call, long straddle. Région où Γ explose (ATM, courte maturité). Lien Γ–Θ dans BS si \(r=0\). |
| Lab | ShockDesk : **straddle** puis **strangle** SPY 30 j. Choc IV **+10 pts** (pas 0.10, pas 10=1000). Cibles : prime 10,69 → 23,91 ; vega 1,242 → 1,374 ; theta −0,344 → −0,608. Contre-épreuve maturité 1 j : vega ≈ 0. |
| Marché | VIX vs IV ATM SPY. |
| Oral | FR : « Signe du theta d'un long straddle ? » EN : *Gamma vs theta in the BS PDE when r = 0.* |
| Brain | Practical Guide × 3 (calculus / BS). |
| Python | `livrables/j02_greeks.py` — Δ Γ ν Θ analytiques, check vs ShockDesk à 1e-3. |

**Piège déjà vécu :** le champ choc IV lit des **points**. Un « 10 » = +10 pts.

---

## Mar 08/09 — J3 · Structures et vues de marché

**Drive P :** Natenberg stratégies + Hull spreads.
**Drive S :** WORDS *FICHE-ENTRETIEN* (collar, greeks, barrière) + *Questions Produits dérivés*.

| Bloc | Consigne |
|---|---|
| Cours | Straddle, strangle, butterfly, iron condor, risk reversal / zero-cost collar. Matrice 2×2 : direction × vol. |
| TD | Pour chaque structure : payoff, max gain, max perte, Δ Γ ν Θ. Client long cash-equity, protection baissière, coût zéro → collar. |
| Lab | ShockDesk : construire les 5. Noter débit/crédit (convention : prime nette ≥ 0 = **débit**). Comparer straddle vs strangle : prime ×2,3 (24,40 vs 10,69) ; à +18,4 % le straddle gagne *par structure*, le strangle *par dollar* (×2,13). |
| Marché | Skew 25-delta put vs call sur un indice. |
| Oral | FR/EN : *Client wants downside protection, zero cost. What do you sell him?* |
| Brain | Heard × 2 + Mosteller × 1. |
| Python | `livrables/j03_payoffs.py` — payoff à l'échéance butterfly + condor, graphe. |

---

## Mer 09/09 — J4 · Smile, skew, surface

**Drive P :** Natenberg vol + Gatheral ch. 1–3 (sticky strike / sticky delta, term structure).
**Drive S :** — (pas de papier d'arbitrage aujourd'hui, c'est J16).

| Bloc | Consigne |
|---|---|
| Cours | IV vs HV. Smile actions (skew put depuis 1987) vs smile FX (U). Surface K × T. Régime vs choc d'IV. |
| TD | Pourquoi le put OTM SPX est cher depuis 87. Sticky strike vs sticky delta en une phrase chacun. |
| Lab | ShockDesk : `iv_shift` et `vol_regime`. Observer OTM, vega local, BE. Relier au filtre `MIN_EDGE` de `long-strangle-shock.py` (edge 0,52 < 1,00 → **0 trade**). Le marché prix 18,4 %, le modèle r1 prix 5 %. |
| Marché | Surface SPX ou EURUSD si tu y as accès ; sinon VIX term structure. |
| Oral | EN trader : *Why has SPX skew been put-biased since 1987?* |
| Brain | Practical Guide vol/BS × 3. |
| Python | `livrables/j04_surface.py` — surface 3D paramétrique (même famille que ShockDesk), pas une surface marché. |

---

## Jeu 10/09 — J5 · Hedge dynamique et P&L

**Drive P :** Hull hedging + Natenberg gamma scalping.
**Drive S :** WORDS *Questions greeks* (ordre de hedge) + *Projet recherche pricing* (MC, lecture ciblée).

| Bloc | Consigne |
|---|---|
| Cours | Delta-hedge, fréquence, gamma scalping. P&L = ΔS + ½Γ(ΔS)² + νΔσ + ΘΔt + … Long gamma + delta-neutre : tu gagnes sur le réalisé si \|move\| > move implicite. |
| TD | Short call, Δ = 0,45, 50 contrats → combien de titres ? Saut du spot : quel sens avantage le short call delta-hedgé ? (WORDS FICHE-ENTRETIEN). |
| Lab | ShockDesk **Backtest** `shock-lab-oil` True vs False. Recoller **+337 887** vs **−279 633**. Attribution : Brent 49 % de la casse, S&P 48 %. L'or **n'est pas** le miss. |
| Marché | Un jour de realized vs implied sur SPY (move du jour vs IV 30 j / √252). |
| Oral | FR/EN : *Long gamma, delta-neutral : how do you make money day to day?* |
| Brain | Dés × 2 + Heard × 1. |
| Python | `livrables/j05_delta_hedge_mc.py` — 1 call, hedge quotidien, P&L de réplication. |

---

## Ven 11/09 — J6 · Intégration vanille

**Drive P :** relire tes notes A, pas de livre nouveau.
**Drive S :** WORDS *Entrainement questions* + *Entrainement questions1* + matrix cookbook (antisèche algèbre).

| Bloc | Consigne |
|---|---|
| Cours | 30 min : carte mentale unique vanille. |
| TD | 8 calculs mixtes (parité, grecs, BE strangle, duration *pas encore* — reste sur options). |
| Lab | `long-strangle-shock` + `butterfly-peak` + `iron-condor-range`. Pour chacun : 3 lignes « pourquoi ça trade / refuse / borne ». |
| Marché | RAS — temps rendu à l'oral. |
| Oral | **20 questions** WORDS, 90 s FR puis 90 s EN, sans notes. Celles ratées → liste « redites ». |
| Brain | 5 chrono (Heard + Practical Guide). |
| Python | Ranger j01–j05, README de 10 lignes dans `livrables/`. |

---

# BLOC B — Exotiques (12 → 18 septembre)

ShockDesk ne price pas les barrières. Lab = **papier + calvin-exotic-desk**.

## Sam 12/09 — J7 · Barrières

**Drive P :** *Pricing Barrier Options* + de Weert (barrier chapters).
**Drive S :** Chen *Pricing Hedging Exotic* (barrières).

| Bloc | Consigne |
|---|---|
| Cours | KI / KO, up / down, in / out. Barrière EU (in fine) vs US (continue) vs discrète (close). Une barrière **vaut moins** qu'une vanille (plus contraignante). |
| TD | Payoff down-and-in put = reverse convertible. Pourquoi KO < vanille < KI en prix, selon les cas. Continu vs discret : qui est plus risqué pour l'investisseur ? (US). |
| Lab | exotic-desk : repérer un knock-in, une alerte barrière, le P&L explain le jour du KI. |
| Marché | RAS. |
| Oral | FR : « Option barrière, plus chère ou moins chère qu'une vanille ? » EN : *American vs European barrier for the investor.* |
| Brain | Mosteller × 2 + dés × 1. |
| Python | `livrables/j07_barrier_mc.py` — down-and-out call, MC naïf, vs vanille. |

---

## Dim 13/09 — OFF

Flashcards barrières (8 vocables) + 1 question actualité WORDS.

---

## Lun 14/09 — J8 · Famille exotique

**Drive P :** de Weert (digital, asian, lookback, bermudan) + Bouzoubaa *Equity Derivatives Explained*.
**Drive S :** WORDS *Questions Produits dérivés*.

| Bloc | Consigne |
|---|---|
| Cours | Asian (moyenne), lookback, digitale (cash-or-nothing / asset-or-nothing), bermudéenne, quanto vs composite, worst-of. |
| TD | Définir chacune en 20 s. Digitale ≈ limite d'un call spread étroit. Worst-of : panier corrélé ou non — **corrélé est moins risqué** pour le vendeur de worst-of. |
| Lab | exotic-desk : identifier digitale / mémoire de coupon si présent. |
| Marché | RAS. |
| Oral | Lister 8 exotiques chrono. EN : *What is a quanto?* |
| Brain | Practical Guide × 3. |
| Python | `livrables/j08_asian_vs_eu.py` — MC asian arithmétique vs européen. |

---

## Mar 15/09 — J9 · Structurés de desk

**Drive P :** Bouzoubaa.pdf + *Fiche Produits Structurés* + *Fiche Produits Structurés1*.
**Drive S :** WORDS *Questions produits structurés*.

| Bloc | Consigne |
|---|---|
| Cours | Familles : protection / optimisation / participation / levier. Reverse convertible = cash + short put DI. Phoenix = ZC + digitale + short put DI + mémoire. Athéna. Autocall trigger, barrière coupon, worst-of. |
| TD | Écrire le payoff Phoenix en 3 régimes. Clean vs dirty. Termsheet vs ISIN. |
| Lab | exotic-desk : 1 Athéna + 1 Phoenix + 1 reverse. Waterfall P&L. Dire le grec dominant de chacun. |
| Marché | RAS. |
| Oral | FR : explique un Phoenix à un non-financier (tu as la fiche). EN : *Walk me through a reverse convertible.* |
| Brain | Heard × 3. |
| Python | `livrables/j09_phoenix_payoff.py` — 3 régimes, pas un pricer complet. |

---

## Mer 16/09 — J10 · Surface praticien

**Drive P :** Gatheral (suite) + Bossu/Carr (vol & corrélation, extraits smile / dispersion).
**Drive S :** *Arbitrage-free smoothing of the implied volatility surface*.

| Bloc | Consigne |
|---|---|
| Cours | Butterfly arb (convexité de C(K)). Calendar arb. Pourquoi on lisse. Volga déjà mesurée (Atelier 7 : +0,80 au-dessus de vega×choc). |
| TD | Condition de no-arb sur trois strikes. Une phrase sur le papier de smoothing (ce qu'il *fait*, pas le détailler). |
| Lab | ShockDesk Options : 3 chocs IV (0, +5, +10) sur le même strangle. Table prime / vega / theta. Constater que vega n'est pas constant. |
| Marché | Skew 25d. |
| Oral | EN : *What would a negative butterfly on the smile mean?* |
| Brain | Joshi (vol) × 2 + Practical Guide × 1. |
| Python | `livrables/j10_butterfly_arb.py` — test de convexité C(K) sur une grille BS. |

---

## Jeu 17/09 — J11 · FX options

**Drive P :** Clark *FX Option Pricing* — conventions, delta, smile FX, RR / strangle / ATM.
**Drive S :** WORDS *Questions-SG* (Forex, Powell/Lagarde, hedge USD).

| Bloc | Consigne |
|---|---|
| Cours | Pair, pips, premium ccy, delta FX (spot / forward / premium-adjusted). Smile FX en RR + butterfly, pas en skew actions. Put-call FX via la parité. |
| TD | 1 numerical Clark simple (ATM vol, 25d RR, 25d fly → vols put/call). |
| Lab | ShockDesk univers `rates-fx` : EURUSD, DX-Y.NYB. Pas de chaîne FX : on observe le book, on ne fake pas un pricer FX. |
| Marché | EURUSD spot + 2s10s US. Présidents Fed/BCE (WORDS SG) — à jour 2026. |
| Oral | SG : particularité du FX, hedge dépréciation USD, paires. Fit : stress. |
| Brain | Dés × 2 + Heard FX/rates × 1. |
| Python | `livrables/j11_fx_rr_fly.py` — reconstruire vols 25d put/call depuis ATM, RR, fly. |

---

## Ven 18/09 — J12 · Convertibles + synthèse exotiques

**Drive P :** *Convertible Arbitrage* ch. 1–3 + `research_pdf0ConvDB`.
**Drive S :** Ramirez (1 fiche corporate eq. deriv.) + `trading strat.pdf` (ce qui est *actionnable* en 20 min).

| Bloc | Consigne |
|---|---|
| Cours | Convertible ≈ bond + call ( rast + crédit + vol). Asymétrie upside equity / downside bond. Pourquoi un arb desk est long vol / long crédit parfois. |
| TD | Diagramme payoff convertible vs bond vs equity. 5 questions structurés WORDS chrono. |
| Lab | exotic-desk : rejouer 1 journée de krach, lire le risk report. |
| Marché | RAS. |
| Oral | 15 questions structurés + exotiques, bilingue. |
| Brain | 5 chrono mix. |
| Python | `livrables/j12_convertible_decomposition.py` — schéma numérique toy (bond floor + option). |

Le reste Convertible Arbitrage et Ramirez → **octobre**.

---

# BLOC C — Taux, ALM, repo, commo (19 → 25 septembre)

## Sam 19/09 — J13 · Obligation

**Drive P :** `fixed income.pdf` (début : prix, yield, effet prix / revenu).
**Drive S :** WORDS *Questions de base* (forward déjà fait) + *Entrainement questions* (ZC, actuariel).

| Bloc | Consigne |
|---|---|
| Cours | PV, ZC, DF, dirty vs clean, YTM. Relation prix/yield inverse, **non linéaire**. |
| TD | 6 bonds à la main (PV + YTM Newton 3 itérations). Perpétuité \(P=C/y\). ZC perpétuel = 0. |
| Lab | ShockDesk univers `rates-fx` : TLT, IEF. Observer, ne pas inventer un pricer obligataire dans l'UI. |
| Marché | US 2Y, 10Y, Bund 10Y, 2s10s. |
| Oral | EN : *Yield up, price? Linear?* FR : dirty vs clean. |
| Brain | Heard bonds × 3. |
| Python | `livrables/j13_bond_ytm.py` — prix + Newton-Raphson YTM. |

---

## Dim 20/09 — OFF

Actualité WORDS 20 min (taux, pétrole, dollar). Une courbe 2s10s.

---

## Lun 21/09 — J14 · Duration, convexité

**Drive P :** `fixed income.pdf` **entier** (c'est un cours, pas un livre).
**Drive S :** Treasury Markets (HKIB) — duration / DV01 si le chapitre est là.
**WORDS :** *Entrainement questions* (duration, zéro vs coupon si taux baissent).

| Bloc | Consigne |
|---|---|
| Cours | Macaulay, modifiée, convexité, Taylor. Règles : ZC → D=T ; coupon bas → D longue ; yield bas → D longue ; perpétuité \(D=(1+y)/y\). |
| TD | Deux bonds même D, convexités différentes : on **achète** la plus convexe. Zéro 10Y vs coupon 10Y si on est long taux. Immunisation : D_actif = D_passif. |
| Lab | Pas d'onglet FI. Calculer à la main un choc +100 / +200 / −100 bps sur un bond du TD, comparer D vs D+C vs reprice. |
| Marché | TLT vs IEF (duration). |
| Oral | FR/EN : *Same duration, different convexity — which do you buy?* |
| Brain | Practical Guide rates × 3. |
| Python | `livrables/j14_duration_convexity.py`. |

---

## Mar 22/09 — J15 · Courbe, FRA, IRS

**Drive P :** Treasury Markets and Operations (HKIB) — money markets, swaps, curve.
**Drive S :** WORDS Entrainement (swap — le trader notait « je maîtrise pas » : c'est **le** jour où ça se ferme).

| Bloc | Consigne |
|---|---|
| Cours | Expectations + term premium. Normal / inverted / flat / steepener / flattener. FRA. IRS payer vs receiver. Swap rate. NPV=0 à l'origine. Bootstrap ZC sur dépôts + swaps. |
| TD | Diagramme de flux payer. Pourquoi NPV 0. 2s10s inversion = quoi sur le cycle. |
| Lab | ShockDesk `rates-fx`. TLT / HYG sur la fenêtre juillet (misses du book). |
| Marché | 2s10s US + EUR. |
| Oral | FR/EN : *Why is an IRS worth zero at inception?* |
| Brain | Heard rates × 3. |
| Python | `livrables/j15_bootstrap.py` — toy 4 piliers, courbe ZC. |

---

## Mer 23/09 — J16 · ALM, liquidité, xVA (vue desk)

**Drive P :** Corlosquet-Habart (ALM, chapitres banque : gap, IRRBB) + Banks *Liquidity Risk* (définition, funding vs market liquidity) + Gregory *xVA* ch. 1–4 (CVA, DVA, FVA — vocabulaire).
**Drive S :** Duttweiler (1 chapitre top-down) + Skoglund (firmwide / ALM, extraits).

Pas Rejda, pas Solvency — **octobre**.

| Bloc | Consigne |
|---|---|
| Cours | Gap de taux, duration gap, DV01 / BPV. Liquidité marché ≠ liquidité financement. xVA = ajustement du prix vanille au contra, funding, collatéral, capital, IM. |
| TD | Banque : actifs longs / passifs courts. Hausse des taux : comment immuniser. Une phrase par xVA. |
| Lab | **Pas d'onglet ALM.** À la place : journal ShockDesk — le book sort au pic et dort en cash **non rémunéré** pendant que le Sharpe retire 4,1 %. C'est un vrai sujet funding / opportunity cost. Note-le comme analogie ALM. |
| Marché | Courbe + LIBOR/SOFR vs T-bill (spread de funding, ordre de grandeur). |
| Oral | FR/EN : *How does a commercial bank immunize against a sudden rise in rates?* + *What does CVA capture?* |
| Brain | Mosteller × 2 + dés × 1. |
| Python | `livrables/j16_rate_gap.py` — échéancier actif/passif, gap, DV01. |

---

## Jeu 24/09 — J17 · Repo & securities finance

**Drive P :** Choudhry *Repo Handbook* (mécanique, haircut, GC vs special, open vs term) + Fabozzi *Securities Finance* (sbl, collateral).

| Bloc | Consigne |
|---|---|
| Cours | Repo = prêt cash vs collatéral. Reverse repo. Haircut. Special vs GC. Pourquoi un special trade rich. SBL côté actions. Lien avec le taux repo dans le forward (WORDS *Questions de base* mélangeait repo BCE et repo titres — **corrige cette fiche** aujourd'hui par écrit). |
| TD | Bilan d'un repo : qui détient le titre, qui a le cash, que se passe-t-il en défaut. |
| Lab | Relire `ROADMAP.md` ShockDesk : « pas de coût de financement (repo, emprunt de titres) ». Écrire 8 lignes : ce que ça biaise sur un short et sur un cash idle. |
| Marché | Taux repo GC US si dispo, sinon skip. |
| Oral | EN : *Walk me through a repo. What is a special?* FR : différence repo titres / taux refi. |
| Brain | Heard × 3. |
| Python | `livrables/j17_repo_pnl.py` — cash + collatéral + haircut, P&L 1 période. |

---

## Ven 25/09 — J18 · Commo : pétrole + coton

**Drive P :** Garner & Brittain *Commodity Options* + Townsend *Cotton Trading Manual* (mécanique contrat, qualité, calendrier).
**Drive S :** ICAC Cotton Situation + WASDE Nov 2025 + ShockDesk `energy-shock` / `global-macro`.

| Bloc | Consigne |
|---|---|
| Cours | Contango / backwardation (WORDS structurés a **inversé** backwardation — corrige). Convenience yield, storage. Saisonnalité coton. Options commo vs options indice (marge, multiplier 1000 sur BZ=F déjà corrigé dans le moteur). |
| TD | Forward commo \(F=S e^{(r+u-y)T}\). Quand y > r+u → backwardation. |
| Lab | ShockDesk `energy-shock` + rejouer le book pétrole. Dire en 4 phrases le trade : timing, pas niveau ; couverture S&P ; or n'est pas un miss ; amplitude ×3,68. |
| Marché | Courbe Brent (1er vs 3e mois si dispo) + un chiffre WASDE / ICAC (stock / prod). |
| Oral | FR/EN contango vs backwardation, *without mixing them*. Pitch pétrole 3 min. |
| Brain | 3 mix. |
| Python | `livrables/j18_forward_curve.py` — toy curve r,u,y → contango/backwardation. |

Coton profond + WASDE série → **octobre** (desk commo).

---

# BLOC D — Quant, risque, synthèse (26 → 30 septembre)

## Sam 26/09 — J19 · Brainteasers massif

**Drive P :** Jane Street Guide + Optiver Guide (2023) **entiers** (ce sont des guides, pas des pavés).
**Drive S :** Glassdoor txt + Heard + Practical Guide + Mosteller + Dice — banque du mois.

| Bloc | Consigne |
|---|---|
| Cours | 30 min : formats JS (EV, marchés, estimation) vs Optiver (market-making, mental math, speed). |
| TD | **Aucun.** |
| Lab | RAS. |
| Oral | 0 — la voix est pour les teasers. |
| Brain | **3 h.** 25 problèmes. Journal : énoncé, ta réponse, la bonne, temps. Ceux > 3 min ou faux → paquet « 30/09 ». |
| Python | `livrables/j19_mental_math.md` — 20 identités (×11, %, expected value dés) écrites à la main puis tapées. |

---

## Dim 27/09 — OFF

Paquet redites. 1 actualité.

---

## Lun 28/09 — J20 · Quant interview

**Drive P :** Joshi *Quant Job Interview Q&A* (black-scholes, stochastic calc ciblé, MC) + Wilmott FAQ + *Paul Wilmott quant questions*.
**Drive S :** matrix cookbook (formules que tu as réellement utilisées) + WORDS *Entrainement questions* (proba risque-neutre, parité).

| Bloc | Consigne |
|---|---|
| Cours | Mesure risque-neutre. GBM. Avantages/limites MC vs PDE vs closed-form. 10 FAQ Wilmott les plus « entretien ». |
| TD | 8 questions Joshi papier (pas tout le livre). |
| Lab | Relancer `cli revue --name global-macro --asof 2026-08-28`. Lire les 4 sections. |
| Marché | RAS. |
| Oral | EN : *MC vs PDE vs closed form.* FR : proba risque-neutre en 60 s. |
| Brain | Joshi teasers × 4. |
| Python | `livrables/j20_mc_european.py` — call EU MC, IC 95 %, vs BS. |

ML, Quant Investing Python, Trading with R → **octobre**.

---

## Mar 29/09 — J21 · VaR, ES, stress

**Drive P :** Skoglund & Chen — VaR / ES / stress (chapitres market risk).
**Drive S :** Gregory déjà vu (xVA n'est pas VaR). ShockDesk scenarios = **stress de prévision**, pas une VaR moteur.

| Bloc | Consigne |
|---|---|
| Cours | VaR 95/99, historical / parametric / MC. ES / CVaR. Sous-additivité : VaR n'est pas cohérente, ES l'est. Pourquoi FRTB / Basel préfère ES. |
| TD | 1 portefeuille 2 lignes, VaR histo vs param. Montrer un cas où VaR(A+B) > VaR(A)+VaR(B) (idée). |
| Lab | ShockDesk Anticipation : grille Brent [0.05, 0.10, 0.185]. C'est un **stress de modèle**, tu le dis comme ça à l'oral. Scénario maison : Brent +20 %, S&P −10 % — le calculer à la main sur les betas du book (`config.py`), **ne pas** inventer un onglet. |
| Marché | VIX. |
| Oral | FR/EN : *Why ES over VaR under Basel III / FRTB?* |
| Brain | 3 mix. |
| Python | `livrables/j21_var_es.py` — histo + param + MC, 95 et 99, ES. |

---

## Mer 30/09 — J22 · Grand oral + pitch + GitHub

**Drive P :** *Why Quant.pdf* (motivation, 45 min max) + WORDS *FICHE-ENTRETIEN* + *Questions-SG* + *Aide Maxime* + *Questions générales stage* (fit **uniquement**, tu ne candidatures pas).
**Drive S :** *Questions d'actualités* — 3 sujets 2026, pas 2022.

| Bloc | Consigne |
|---|---|
| Cours | Why Quant + 1 relecture de ta carte mentale unique. |
| TD | 0. |
| Lab | Backtest final `shock-lab-oil` + `cli revue`. Rédiger le **Desk Monthly Review** 1 page : scorecard, timing 617 520 $, misses HYG/TLT, amplitude ×3,68, ce que octobre corrigera. |
| Oral | **Grand oral 90 min.** 15 tech FR, 15 tech EN, 10 teasers du paquet 26/09, 5 fit. Enregistre-toi. |
| Pitch | 1 page + 3 min à voix haute : vue, catalyseur, structure, grecs, stop, miss, provenance. |
| Python | Nettoyer `livrables/` : un README, plus de scripts orphelins, plus de chiffres sans source. |

**Fin du sprint.** Octobre = recherche (fichier `03`). Pas de candidature avant que le pitch tienne 3 min sans bégayer.

---

## 5. Rotation brainteasers (rappel)

| Jour | Source |
|---|---|
| Impair (5, 7, 9…) | Heard on The Street |
| Pair | Practical Guide to Quant Interviews |
| 2× / semaine | Dice Problems |
| 1 / 2 jours | Mosteller |
| 26 et 30 | Jane Street + Optiver + Glassdoor |

Trois problèmes par jour hors J19. Un problème raté est re-fait le lendemain **avant** les nouveaux.

---

## 6. Ce que tu n'ouvres pas en septembre (volontaire)

Rejda · Sandström Solvency · Lopez de Prado · ML finance · Quant Investing Python · Trading with R · Convertible Arbitrage au-delà des ch. 1–3 · Gregory au-delà des ch. 1–4 · WASDE en série · Cotton au-delà d'une journée.

C'est dans `03-octobre-base-recherche.md`. Ce n'est pas un oubli.
