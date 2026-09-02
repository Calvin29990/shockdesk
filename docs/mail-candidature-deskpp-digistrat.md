# 📧 Mail candidature — Desk++ (Calvin Minang)

> **Cible :** BA Produits Structurés (Equity) — Digistrat Consulting, Paris (75)
> **Poste vérifié comme publié le 01/09/2026** (filtre Indeed « 24 dernières heures »)
> Lien : https://fr.indeed.com/viewjob?jk=2112f7990a40d809
> Salaire affiché : 58 000 – 73 000 € / an · CDI · Démarrage ASAP · Paris (pas de full remote)

---

## 🔎 Postes publiés aujourd'hui (01/09/2026) — ce que j'ai trouvé

| # | Poste | Employeur | Lieu / Type | Match Desk++ |
|---|-------|-----------|-------------|--------------|
| 1 | **BA Produits Structurés (Equity)** — modélisation de produits via un langage de payoff quants (SPL : call, autocall, barrières), validation de pricing avec trading/structuration/quants, intégration plateforme pricing & booking, BDD/DevOps, documentation | **Digistrat Consulting** | Paris (75) · CDI 58–73 k€ · ASAP | ⭐⭐⭐⭐⭐ Match direct : simulateur de book exotique (autocalls, barrières), pricing Reiner-Rubinstein validé vs Monte-Carlo, backtester, tests + CI, docs |

**Vérifications faites** : Indeed (filtre 24 h, 4 requêtes : « equity derivatives structuration », « produits structurés exotiques », « junior trader », « stage trading dérivés ») → **1 seul poste réellement publié aujourd'hui** correspondant au profil. Les autres offres trouvées sont antérieures : CIC « Stagiaire Développeur Commando — Desk trading de Volatilité » (publiée le 28/08/2026), HSBC « Alternance Assistant Trader Corporate Equity Derivatives » (publiée en mai 2026), HSBC « Stage Recherche Quant Equity Derivatives » (2025).
- LinkedIn et eFinancialCareers n'ont pas pu être scannés (accès bloqué / maintenance) — à revérifier à la main si besoin.

---

## ✉️ EMAIL A — Version technique, ciblée Digistrat (recommandée)

**Objet :** Candidature BA Produits Structurés (Equity) — j'ai déjà codé la chaîne : pricing exotiques → validation → intégration (Desk++)

---

Bonjour,

Je candidate au poste de **BA Produits Structurés (Equity)** publié aujourd'hui. Plutôt qu'un CV listant des mots-clés, je vous propose directement les outils que j'ai construits et qui couvrent vos 6 missions, ligne par ligne.

**1. Modélisation produit (votre SPL) — j'ai déjà implémenté un moteur de payoff exotique**
Ma plateforme [Exotic Desk Simulator](https://github.com/Calvin29990/calvin-exotic-desk) (démo live : https://calvin-exotic-desk.netlify.app) modélise un book fictif de **195 M€** de produits structurés : **autocalls Athena, Phoenix, Reverse Convertible**, avec mécanique complète — barrières knock-in en observations, mémoire de coupon, rappels d'autocall. Pricing **Black-Scholes (r=0) + formules de Reiner-Rubinstein** pour les barrières continues, digitales et knock-in européens — **validé contre Monte-Carlo (écart < 5 %)**. C'est exactement le périmètre « call / autocall / options à barrières » demandé dans l'annonce.

**2. Validation de pricing avec trading / structuration / quants**
Chaque action recalcule les **grecs par différences finies** (delta/gamma/vega/theta) agrégés au niveau book, avec **P&L explain en waterfall** (delta, gamma, vega, theta, événements, inexpliqué) et **stress test spot × vol** — le fameux tableau du soir envoyé au risk. Je sais donc lire et challenger un priced deal, pas seulement le saisir.

**3. Intégration dans une plateforme de pricing / booking**
Le simulateur tourne dans un **fichier HTML unique (~82 Ko), sans serveur ni dépendance**, build reproductible depuis `sources/` (`build_sim.py` → `index.html`). Sur [ShockDesk](https://github.com/Calvin29990/shockdesk), j'applique la même rigueur à l'échelle macro : backtest multi-actifs de **25,5 M$** avec API REST + CLI + interface, catalogue de structures (strangle, straddle, butterfly, iron condor, spreads, risk reversal, calendar), prévisions révisables en lecture **point-in-time** et attribution de P&L par ligne.

**4. BDD / DevOps pour automatiser les tests**
ShockDesk embarque **44 tests (pytest)** et une CI GitHub Actions ; mes stratégies sont des fichiers Python testables et rejouables (résultat publié : **+395 919 $ (+1,55 %)** en sortie au pic, **−4 054 $** sans la règle de timing — la différence se mesure, elle ne se raconte pas).

**5. Documentation et suivi utilisateurs**
Le dépôt Exotic Desk contient une **documentation de reprise technique** (conçue pour un humain ou une IA qui reprend le projet sans contexte), un guide débutant et **83 pages de cours** (structuration, Black-Scholes, métier du desk, 40 questions d'entretien). Documenter et faire monter l'équipe en compétence fait partie de ma méthode.

**6. Réunions / conf-calls FR-EN**
Français natif, anglais professionnel courant ; logiciel : **Python** (pandas, numpy, scikit-learn), JavaScript/TypeScript, React/Vite, CI, SQL, Excel/VBA.

**En complément, ce que Desk++ couvre en amont :** [ShockLab](https://github.com/Calvin29990/ShockLab-Fade-or-Cascade-) (stress-testing multi-actifs composé à partir de **25 chocs réels 2001→2025** — méthode « fade or cascade », sévérité + canal crédit/liquidité) et [CalvinX Market Terminal](https://github.com/Calvin29990/calvinx-market-terminal) (terminal type Bloomberg : données live, indicateurs techniques, sentiment news, **export Excel 3 feuilles**, mode démo sans crash). Le tout est public et vérifiable sur mon [GitHub](https://github.com/Calvin29990).

**Disponibilité :** je suis actuellement **hors de France jusqu'au 9 septembre** — joignable par **e-mail, WhatsApp et visio** au **+33 7 52 97 58 09** ; à partir du 9 septembre, joignable par téléphone et disponible sur site à Paris. Je peux vous faire une **démo en visio de 5 minutes** du simulateur (book exotique, grecs en temps réel, stress test) si vous souhaitez valider le niveau technique avant un échange.

Je suis à votre disposition pour un premier échange dès cette semaine.

Cordialement,
**Calvin Minang** — SKEMA BS
📞 +33 7 52 97 58 09 (WhatsApp / e-mail / visio jusqu'au 09/09, puis téléphone)
🔗 GitHub : https://github.com/Calvin29990 · LinkedIn : https://www.linkedin.com/in/calvin-minang
🖥️ Démo live : https://calvin-exotic-desk.netlify.app

---

## ✉️ EMAIL B — Version courte (si la boîte mail est limitée ou pour un premier contact rapide)

**Objet :** Candidature BA Produits Structurés (Equity) — Desk++ : 4 outils open-source qui couvrent la chaîne complète

---

Bonjour,

Je candidate au poste de **BA Produits Structurés (Equity)** publié aujourd'hui (Digistrat, Paris). Je code moi-même la chaîne qu'il faut intégrer :

- **Modélisation exotique** : moteur d'autocalls (Athena, Phoenix, Reverse Convertible), barrières KI, pricing **Reiner-Rubinstein validé vs Monte-Carlo (< 5 %)**, grecs temps réel, P&L explain, stress test spot × vol — [simulateur live](https://calvin-exotic-desk.netlify.app).
- **Validation & intégration** : backtester multi-actifs 25,5 M$ avec API/CLI, attribution de P&L, prévisions point-in-time ([ShockDesk](https://github.com/Calvin29990/shockdesk)).
- **Tests & DevOps** : 44 tests pytest + CI GitHub Actions.
- **Documentation** : reprise technique, guides, cours (83 p.) + terminal marché & export Excel ([CalvinX](https://github.com/Calvin29990/calvinx-market-terminal)).

Connaissance exigée (call, autocall, barrières) : **explicite dans mon dossier** — 6 produits structurés réels modélisés et testés.
Stack : Python, TS/React, SQL, CI, FR/EN.

**Disponibilité :** hors de France jusqu'au 09/09 — **e-mail / WhatsApp / visio au +33 7 52 97 58 09** ; téléphone et disponibilité sur site dès le 09/09. Démo visio de 5 min possible à tout moment.

Cordialement,
**Calvin Minang** — GitHub : https://github.com/Calvin29990

---

## ✉️ EMAIL C — Version anglaise (à utiliser pour une agence/banque en English-first)

**Subject :** Application — Equity Structured Products BA — I already built the full pricing → validation → integration chain (Desk++)

---

Dear Sir/Madam,

I am applying for the **Business Analyst – Equity Structured Products** role published today (Digistrat Consulting, Paris). Instead of keywords on a CV, here is what I have actually built and published:

- **Product modelling (SPL-like)** : [Exotic Desk Simulator](https://calvin-exotic-desk.netlify.app) — a fictional €195M book of **Athena / Phoenix / Reverse Convertible autocalls**, knock-in barriers, coupon memory, pricing via **Black-Scholes + Reiner-Rubinstein, validated against Monte-Carlo (< 5% error)**, Greeks by finite differences, **P&L explain waterfall**, spot × vol stress test. Exactly the call / autocall / barrier scope your posting requires.
- **Pricing validation & platform integration** : [ShockDesk](https://github.com/Calvin29990/shockdesk) — multi-asset backtester ($25.5M book) with REST API + CLI + UI, strategy catalogue (strangle, straddle, butterfly, iron condor, calendar…), point-in-time forecast registry, per-line P&L attribution.
- **BDD / DevOps** : 44 pytest tests + GitHub Actions CI; reproducible build (single 82 KB HTML file, no server).
- **Documentation** : technical takeover guide, beginner guide, 83 pages of courses; plus [ShockLab](https://github.com/Calvin29990/ShockLab-Fade-or-Cascade-) (stress-testing from 25 real 2001–2025 shock analogues, fade vs cascade classification) and [CalvinX](https://github.com/Calvin29990/calvinx-market-terminal) (Bloomberg-like terminal, Excel auto-export).

Main technical results: **+$395,919 (+1.55%)** with the published timing exit vs **−$4,054** without it — the edge is measured, not claimed.

**Availability :** abroad until **9 September** — reachable by **e-mail, WhatsApp, video call (+33 7 52 97 58 09)**; phone and on-site availability from 9 September. I can demo the simulator end-to-end in a 5-minute video call.

Best regards,
**Calvin Minang** — SKEMA BS
GitHub: https://github.com/Calvin29990 · LinkedIn: https://www.linkedin.com/in/calvin-minang

---

## ✅ Checklist avant envoi

1. [ ] Piéger l'objet : préférer EMAIL A ou C (chiffré, orienté « je l'ai déjà fait »).
2. [ ] Joindre/lier le **CV PDF** avec la mention explicite : *« connaissance produits structurés type call, autocall, options à barrières »* (exigence de l'annonce — la mettre telle quelle, mot pour mot).
3. [ ] Mettre le lien de la démo **en cliquable** : https://calvin-exotic-desk.netlify.app
4. [ ] Signature avec **WhatsApp +33 7 52 97 58 09** et la mention de disponibilité (jusqu'au 09/09 : WhatsApp / mail / visio ; après : téléphone).
5. [ ] Mentionner que la **démo visio est dispo dès aujourd'hui** (bon argument vu la contrainte « ASAP »).
6. [ ] Envoi **aujourd'hui** : l'annonce date du 01/09, les candidatures précoces sur un poste « ASAP » ont l'avantage du premier regard.
