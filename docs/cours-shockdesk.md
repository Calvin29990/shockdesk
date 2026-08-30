<div class="cover">
<p class="cover-kicker">ShockDesk — Phase 1</p>
<h1 class="cover-title">Cours pratique<br/>des concepts de desk</h1>
<p class="cover-sub">Du scénario publié au trade testé : le vocabulaire, les objets,<br/>
le moteur, les options, les prévisions et la discipline de revue.</p>
<p class="cover-meta">Support de formation interne — 19 modules, 10 ateliers<br/>
Dépôt <span class="mono">Calvin29990/shockdesk</span> — version du 30 août 2026</p>
</div>

# Avant-propos

## À qui s'adresse ce cours

Ce cours s'adresse à quelqu'un qui sait lire du Python et qui veut travailler
comme un desk : publier une vue, la dimensionner, la tester, la corriger. Il ne
présente pas ShockDesk comme un produit, mais comme un poste de travail dont
chaque pièce correspond à un concept de salle de marché.

Il suppose seulement trois choses : savoir lire un script Python, connaître le
vocabulaire de base des actions et des taux, et avoir lancé l'application une
fois (`./run.sh`, puis ouvrir `/`).

## Ce que ce cours n'est pas

Ce n'est pas le guide d'installation (voir `docs/guide-utilisation.md`), ni le
carnet d'exercices (voir `docs/entrainement-progressif.md`), ni une théorie du
pricing. Quand une formule apparaît, c'est parce qu'un bouton de l'interface ou
une ligne de code en dépend.

Les six stratégies livrées dans `strategies/` sont des objets d'étude, pas des
recommandations. Les chiffres cités proviennent du jeu de données hors ligne de
l'exercice de juillet 2026 : ils ne sont pas reproductibles sur données réelles,
et la commande exacte qui les produit est donnée à chaque fois, pour qu'on puisse
les rejouer.

## Comment lire ce cours

Le cours est organisé en quatre parties, du plus concret au plus méthodologique.

| Partie | Modules | Ce qu'on y apprend |
|---|---|---|
| I — Le poste de travail | 1 à 5 | Le vocabulaire, les trois objets (stratégie, univers, prévision), l'interface, la provenance des données, le moteur et ses conventions |
| II — Les instruments | 6 à 9 | L'API de stratégie, le pricing d'options et la surface de volatilité, le catalogue de structures, l'anatomie d'une stratégie complète |
| III — L'anticipation | 10 à 13 | Les prévisions point-in-time, le scoring ex-post, le passage du signal à la structure, les métriques de performance |
| IV — La discipline | 14 à 19 | Le cas pratique chiffré, les pièges, la boucle mensuelle, les trois portes d'entrée, les ateliers, les annexes |

Chaque module suit la même forme : le concept, son implémentation dans le code,
ce qu'on en fait concrètement, et les erreurs classiques. Les encadrés
**Règle de la maison** énoncent les conventions non négociables. Les encadrés
**Pourquoi** expliquent une décision d'implémentation qui a coûté du temps.

## Conventions d'écriture

Les noms entre guillemets simples comme `'close'` ou `slippage_bps` sont des
identifiants du code. Les montants sont en dollars. Les pourcentages d'amplitude
sont des fractions du spot (`0.05` = 5 %). Les dates sont en ISO (`2026-07-15`).
« J+n » désigne n jours calendaires après la date de publication d'une prévision.

Une citation de code est toujours tronquée et simplifiée : le but est de montrer
la règle, pas de remplacer la lecture du fichier. Les numéros de ligne ne sont
pas donnés, ils bougent.

[[PAGEBREAK]]

# Sommaire

[[TOC]]

[[PAGEBREAK]]
# Partie I — Le poste de travail

## Module 1 — Qu'est-ce qu'un desk

### Le desk n'est pas un modèle

Un modèle produit une prévision. Un desk la transforme en position, la surveille,
la corrige et la clôt. La différence tient en trois contraintes que le desk ne
peut pas ignorer : le temps (une vue publiée le 15 juillet ne peut pas être
relue avec les connaissances du 28 août), le coût (une bonne idée trop chère à
exécuter est une mauvaise idée), et la responsabilité (il faut pouvoir expliquer
chaque ligne du P&L six mois plus tard).

ShockDesk matérialise ces trois contraintes : le registre de prévisions est
daté et ne se réécrit pas, le moteur facture le slippage et les commissions,
l'attribution par ligne explique le résultat.

### Le vocabulaire de base

Ces dix mots reviennent dans tout le cours. Il faut les lire comme des objets
techniques, pas comme des images.

| Mot | Sens précis dans ShockDesk |
|---|---|
| **Book** | L'ensemble des positions ouvertes à un instant, avec leur valeur de marché |
| **Ligne** | Une position sur un sous-jacent (`BZ=F`, `TLT`…) ou sur un contrat d'option |
| **Univers** | Ensemble de sous-jacents disponibles pour un backtest (`global-macro`, `us-equities`…) |
| **Benchmark** | La ligne de référence de l'univers (`^GSPC` pour `global-macro`) |
| **Attribution** | Décomposition du P&L par ligne : qui a payé, qui a coûté |
| **Exposition brute** | Somme des valeurs de marché en valeur absolue |
| **Levier** | Exposition brute divisée par l'actif net |
| **Mark** | Valorisation du book aux prix du jour |
| **P&L réalisé / latent** | Résultat des lignes débouclées / des lignes encore ouvertes |
| **Prévision** | Vue publiée sur un sous-jacent, avec son numéro de révision |

### Lire un P&L comme un desk

Un chiffre de P&L seul ne dit rien. Un desk le lit en quatre temps : combien
(dans l'absolu et en pourcentage de l'actif), d'où (attribution par ligne),
à quel prix (commissions et slippage), et par rapport à quoi (le benchmark de
l'univers, parce qu'une partie du mouvement est du marché, pas de la vue).

Ces quatre lectures correspondent exactement aux quatre blocs de l'onglet
Backtest : les cartes de métriques, le tableau d'attribution, la ligne
`turnover` et `avg_trade`, et la comparaison alpha/bêta.

> **Règle de la maison.** Un backtest sans attribution ne se commente pas. Un
> P&L positif porté par une seule ligne est un pari, pas une stratégie — et il
> faut le dire avant que le hasard s'en mêle.

## Module 2 — Les trois objets du desk

Tout ShockDesk tient dans trois objets. Les confondre est la première source
d'erreur.

### 1. La stratégie : un fichier Python

Une stratégie est un fichier `.py` dans `strategies/`, indexé par un UUID stable
dans `strategies/_index.json`. Le code est du vrai Python : on peut l'éditer
dans l'interface ou dans son éditeur, les deux voient le même fichier. L'index
est réconcilié avec le disque à chaque lecture — un fichier ajouté à la main
apparaît, un fichier supprimé disparaît de l'index.

```python
"""Ma stratégie — une phrase qui la résume."""

WEIGHT = 0.30

def initialize(context):
    context.asset = symbol('BZ=F')
    schedule_function(trade, date_rules.every_day())

def trade(context, data):
    f = get_forecast('BZ=F')
    if f is None:
        return
    if f.sign > 0:
        order_target_percent(context.asset, WEIGHT)
    record(signal=f.sign)
```

### 2. L'univers : le périmètre de ce qui est tradable

Un univers est une liste de symboles, un benchmark et un drapeau `options`.
Demander un symbole hors univers lève une `KeyError` explicite qui liste les
symboles disponibles : mieux vaut une erreur nette qu'une position silencieuse
sur un sous-jacent non calibré.

| Univers | Lignes | Benchmark | Options |
|---|---|---|---|
| `global-macro` | `BZ=F`, `^GSPC`, `TLT`, `GC=F`, `DX-Y.NYB`, `HYG`, `DBC` | `^GSPC` | non |
| `us-equities` | `SPY`, `QQQ`, `AAPL`, `MSFT`, `NVDA`, `XLE`, `XLF`, `TLT` | `SPY` | oui |
| `energy-shock` | `BZ=F`, `CL=F`, `XLE`, `XOP`, `UNG`, `TLT` | `XLE` | oui |
| `rates-fx` | `TLT`, `IEF`, `HYG`, `DX-Y.NYB`, `EURUSD=X` | `TLT` | oui |
| `options-lab` | `SPY`, `QQQ`, `TLT`, `GC=F`, `BZ=F` | `SPY` | oui |

Le `global-macro` est le seul univers sans options : c'est le book du scénario
publié, en delta pur. C'est un choix — le scénario de juillet 2026 a été joué
sans options, et rejouer l'exercice impose le même périmètre.

### 3. La prévision : une vue datée et révisable

Une prévision n'est pas un fichier de paramètres. C'est une publication : un
identifiant, un sous-jacent, un benchmark, une date d'arrêt, et une liste de
**révisions numérotées**. On n'édite jamais une révision publiée : on en ajoute
une. Le moteur, à une date donnée, ne voit que la dernière révision publiée
avant cette date.

### L'URL comme contrat

Les trois objets se rejoignent dans une URL. C'est la grammaire unique de
l'application : l'interface, l'API HTTP et le CLI acceptent les mêmes
paramètres, avec les mêmes noms.

```
/research/strategies/3395e5bb-…-d052adcf9023/code
    ?name=global-macro&startCapital=25500000
    &startDate=2026-07-01&endDate=2026-08-28&action=backtest
```

| Paramètre | Sens | Défaut |
|---|---|---|
| `name` | Nom de l'univers | `us-equities` |
| `startCapital` | Capital de départ en dollars | `10000` |
| `startDate` / `endDate` | Fenêtre du backtest | `2020-01-01` / `2021-09-01` |
| `action` | `backtest` pour exécuter au chargement | `backtest` |

> **Règle de la maison.** Une question de desk s'écrit en URL. Si on ne peut
> pas la formuler ainsi — univers, capital, fenêtre, stratégie —, on ne peut
> pas la rejouer, donc on ne peut pas la défendre en revue.

[[PAGEBREAK]]
## Module 3 — L'interface et ses cinq onglets

### Une seule page, cinq lectures

L'application tient dans une page. Elle redirige `/` vers la première stratégie
avec ses paramètres par défaut, et `action=backtest` déclenche l'exécution au
chargement. Les cinq onglets correspondent à cinq lectures distinctes du même
objet : ce qu'on a écrit, ce que ça donne, ce qu'on anticipe, ce que ça coûte, ce
qu'on peut appeler.

| Onglet | Ce qu'on y lit | La question à laquelle il répond |
|---|---|---|
| **Code** | L'éditeur Python, l'univers et les prévisions actives en regard | Qu'est-ce que je joue, sur quoi, avec quelle vue ? |
| **Backtest** | Métriques, équité contre benchmark, drawdown, attribution, grecs, signaux `record()`, positions, transactions, journal | Qu'est-ce que ça a donné, et pourquoi ? |
| **Anticipation** | Par sous-jacent : la prévision active, sa validation, les structures cohérentes et leur P&L par nœud | Que pense-t-on, et comment l'exprimer ? |
| **Options** | L'atelier de pricing : payoff, points morts, grecs, choc d'IV, régime de vol | Combien coûte cette structure, pour quel profil ? |
| **API & doc** | L'API disponible dans le code, les trois portes d'entrée, les règles de discipline | Comment refaire ça sans l'interface ? |

### L'éditeur

L'éditeur est un champ texte avec coloration et numéros de ligne. Deux
raccourcis : `Ctrl+S` enregistre le code dans le fichier de la stratégie,
`Ctrl+Entrée` lance le backtest. Enregistrer écrit sur le disque : le fichier
édité dans le navigateur et celui ouvert dans un éditeur sont le même.

À droite, l'univers et les prévisions actives. C'est un choix délibéré : on
n'écrit pas `get_forecast('BZ=F')` en regard d'une liste vide. Si la prévision
n'est pas publiée, la stratégie ne peut pas la voir, et il vaut mieux le
constater avant d'écrire le code qu'en lisant le journal après.

### L'onglet Backtest : l'ordre de lecture

Les blocs sont présentés dans un ordre, et cet ordre est une méthode.

1. **Les cartes de métriques.** Rendement, drawdown maximal, Sharpe, volatilité,
   taux sans risque utilisé. Le taux est affiché à côté des ratios : sans lui,
   un Sharpe n'est pas interprétable.
2. **La courbe d'équité contre le benchmark**, rescalé au même capital de
   départ, avec le drawdown en dessous.
3. **L'attribution par ligne**, triée du meilleur au pire contributeur.
4. **Les grecs du book jour par jour** : delta, gamma, vega, theta agrégés, plus
   l'équité et le P&L de la barre.
5. **Les signaux `record()`** tracés avec la courbe.
6. **Les positions et les transactions**, avec commission et motif
   (`entrée scénario r1`, `take-profit pic modèle`…).
7. **Le journal**, y compris les avertissements de levier, les échéances réglées
   et les positions ouvertes en fin de fenêtre.

> **Règle de la maison.** On lit le journal avant les métriques. Un résultat
> dont on n'a pas lu les avertissements est un résultat qu'on n'a pas lu.

### L'onglet Anticipation

Une ligne par sous-jacent de l'univers : le spot, la volatilité réalisée, le
régime de vol, l'IV ATM 30 jours avec le choc du scénario appliqué, la prévision
active avec sa révision et sa date, sa validation ex-post, et jusqu'à quatre
structures recommandées avec leur coût, leurs points morts et leur P&L par nœud
de la grille d'amplitudes.

C'est l'onglet qui matérialise le passage de la vue au trade : la prévision est à
gauche, l'instrument qui l'exprime est à droite, et l'écart entre les deux est
chiffré.

### L'onglet Options

L'atelier de pricing. On choisit un sous-jacent, une structure, une maturité,
une largeur, un choc d'IV et un régime de vol ; on obtient le payoff tracé, les
points morts, les grecs agrégés, chaque jambe avec sa prime et son IV, et les
alertes du pricer. Le spot par défaut est le niveau de calibration `s0` de
l'actif, sauf surcharge explicite — c'est à savoir quand on compare deux
structures sur des niveaux différents.

### L'onglet API & doc

La liste des fonctions disponibles dans le code, les trois portes d'entrée avec
leurs paramètres, et les règles de discipline. Cet onglet existe pour qu'on
n'ait jamais à deviner un nom de fonction : tout ce qui est appelable dans une
stratégie y est écrit.

[[PAGEBREAK]]
## Module 4 — Les données et leur provenance

### Trois sources, dans cet ordre

La couche données essaie trois sources et garde la première qui répond. Le mode
utilisé est renvoyé dans `panel.source` et affiché dans l'interface : aucun
chiffre ne doit pouvoir être lu comme une donnée réelle par erreur.

| Ordre | Source | Condition | `source_detail` |
|---|---|---|---|
| 1 | `yfinance` | paquet installé **et** Yahoo répond, plus de 5 barres | « données réelles Yahoo Finance » |
| 2 | `csv` | un fichier `data/<symbole>.csv` par ligne, aucune manquante | « cache CSV local (n sous-jacents) » |
| 3 | `synthetic` | toujours disponible | « modèle factoriel calibré ShockDesk (hors ligne, déterministe) » |

Le mode est forçable : `source=yfinance`, `csv` ou `synthetic` dans l'API,
`--source` en CLI. `auto` laisse la cascade décider.

Le cache CSV attend les colonnes `date,open,high,low,close`, séparateur `,` ou
`;`, dates ISO. C'est la voie à suivre pour travailler hors ligne sur des
données réelles exportées à la main.

### Le générateur synthétique

Le mode hors ligne n'est pas un bruit aléatoire : c'est un modèle factoriel
calibré, déterministe, avec injection d'événements de choc. Trois propriétés
comptent.

**Sept facteurs, des bêtas explicites.** `SPX`, `OIL`, `RATES`, `GOLD`, `USD`,
`CREDIT`, `VOL`. La convention est la suivante : la valeur du facteur est un
rendement journalier, et le signe du facteur porte déjà la direction économique.
`RATES` à +1 % signifie que les taux montent — donc que les prix obligataires
baissent. Chaque actif porte ses chargements dans sa fiche :

```python
AssetSpec("^GSPC", "S&P 500", "index", 6420.0, 0.150, 0.075,
          {"SPX": 1.00, "RATES": -0.35, "OIL": -0.25,
           "CREDIT": 0.35, "USD": -0.15}, iv_base=0.165)
```

**Volatilités factorielles.** Les sept facteurs ont une volatilité annuelle
cible : `SPX` 15,0 %, `OIL` 32,0 %, `RATES` 9,5 %, `GOLD` 12,0 %, `USD` 7,0 %,
`CREDIT` 6,0 %, `VOL` 80,0 %. Elles sont recalibrables dans
`config/calibration.json`.

**Déterminisme et indépendance à la fenêtre.** La trajectoire est générée depuis
une époque fixe (2015-01-01) puis découpée sur la fenêtre demandée. Changer
`startDate` ne change pas la trajectoire : deux backtests sur des fenêtres qui
se chevauchent voient les mêmes prix. Sans cette propriété, comparer deux
fenêtres reviendrait à comparer deux univers.

Le générateur cale le niveau de chaque sous-jacent sur son `s0` de calibration à
la date d'ancrage du 15 juillet 2026 — la date de publication du scénario
ShockLab. C'est pour cela que le Brent vaut 84,95 $ dans le jeu hors ligne.

### Ce que la provenance change dans la lecture

Un backtest sur données synthétiques teste la **logique** : l'ordre des
opérations, la sortie au pic, le calcul des frais. Il ne teste pas la **thèse** :
le Brent ne montera pas de 18,5 % parce que le générateur l'a décidé. La phrase
à écrire en revue est donc : « la règle de sortie fonctionne, sa performance sur
la fenêtre publiée est celle du scénario, pas du marché ».

> **Pourquoi cette insistance.** Le piège classique d'un outil de backtest est
> de produire de jolies courbes sur un générateur qu'on a oublié. Afficher la
> provenance à côté de chaque chiffre coûte une ligne de code et évite des
> heures de revue stérile.

## Module 5 — Le moteur de backtest

### Un bar par jour, exécution au close

Le moteur est journalier. Un ordre passé pendant le bar est exécuté au prix de
clôture de ce même jour, avec slippage et commission appliqués. C'est une
simplification assumée : pas de barres intraday, pas d'exécution au VWAP, pas
d'impact de marché. Les ordres ne voient jamais un prix meilleur que celui que
le code aurait pu connaître — la seule approximation est le coût, jamais
l'information.

### Les réglages par défaut

```python
@dataclass
class EngineSettings:
    commission_per_share: float = 0.005
    commission_min: float = 1.0
    commission_per_contract: float = 0.65
    slippage_bps: float = 5.0
    allow_short: bool = True
    max_leverage: float = 2.0
    risk_free: float = 0.041
```

Ces valeurs se règlent depuis la stratégie (`set_commission`, `set_slippage`)
ou depuis l'API (`settings`). Le `risk_free` est retiré du rendement dans le
Sharpe et le Sortino — le module 13 y revient, parce que ce détail change la
lecture d'une stratégie qui dort en liquidités.

### Le coût de transaction

Le slippage est symétrique : on achète à `prix × (1 + 5 bps)`, on vend à
`prix × (1 − 5 bps)`. La commission est `max(quantité × 0,005 $, 1,00 $)` par
ordre sur un sous-jacent, et `max(contrats × 0,65 $, 1,00 $)` sur une option.

Le point délicat est le diviseur des contrats d'options. Les quantités du moteur
sont en unités du sous-jacent, alors que le frais est facturé par contrat : une
option US sur action, ETF ou indice porte 100 parts, une option sur future porte
la taille du contrat à terme (1 000 barils pour le Brent, 100 onces pour l'or).

> **Pourquoi.** Confondre la taille du contrat d'option avec celle de la part
> facturait 738 parts d'option SPY comme 738 contrats, soit 479,70 $ de frais au
> lieu de 4,80 $ — un surcoût de 100× qui rendait toute stratégie d'options sur
> ETF structurellement perdante. Ce n'est pas une hypothèse : c'est un bug qui a
> été trouvé, corrigé et documenté dans la fiche d'actif.

### Le garde-fou de levier

L'exposition brute est plafonnée à `max_leverage` fois l'actif net, défaut 2×.
Un ordre qui ferait sauter le plafond n'est pas rejeté : il est **réduit** à ce
qui reste de place, avec un avertissement dans le journal. Le backtest reste
borné au lieu d'être absurde, et l'avertissement dit exactement ce qui a été
coupé.

`allow_short=False` interdit de passer vendeur : un ordre qui ferait basculer la
position en négatif est ramené à la clôture de la position.

### Le coût moyen pondéré

Chaque position porte un `cost_basis`, prix moyen pondéré des achats. Quand une
position est réduite ou retournée, la part débouclée passe en P&L réalisé ; la
part conservée garde son prix moyen. Quand une position augmente, le prix moyen
est recalculé sur la partie ajoutée uniquement. C'est la convention comptable
habituelle d'un desk, et c'est elle qui rend l'attribution lisible.

### L'ordre des opérations dans une barre

Cet ordre n'est pas un détail d'implémentation : il définit ce qu'une stratégie
peut voir et ce qu'elle paie.

1. Règlement des options échues à l'intrinsèque du jour.
2. Mark du book aux prix du jour.
3. `before_trading_start` si la stratégie le définit.
4. Les fonctions planifiées dont la `date_rule` est vraie.
5. `handle_data` **seulement si aucune fonction planifiée n'a tourné**.
6. Attribution du P&L de marché par ligne, avant exécution.
7. Exécution des ordres au close, avec frais.
8. Nouveau mark, calcul des grecs du book, ajout à la courbe d'équité.

Le point 5 est un piège classique : une stratégie qui planifie une fonction
quotidienne et définit aussi `handle_data` ne verra jamais `handle_data`
s'exécuter. Ce n'est pas un bug, c'est la règle — il faut choisir une des deux
formes.

### Les options échues

À chaque barre, toute position d'option dont l'échéance est atteinte est réglée
à sa valeur intrinsèque du jour (`max(0, S − K)` pour un call, `max(0, K − S)`
pour un put), créditée en cash, inscrite au P&L réalisé, et retirée du book. Une
ligne de journal le dit. Il n'y a pas d'exercice automatique sur le
sous-jacent : on ne se retrouve jamais long 100 barils sans l'avoir voulu.

### La fin du backtest

Une position encore ouverte à la dernière barre entre dans le P&L final par sa
seule valeur de marché, sans jamais avoir été débouclée. Le moteur le signale
explicitement, avec le montant latent :

```
Fin de backtest : 1 position(s) encore ouverte(s), P&L latent +21 412 $ compris
dans le résultat.
```

> **Règle de la maison.** Un P&L latent n'est pas un P&L. Sur l'exercice publié,
> la ré-entrée du 28/08 pesait environ 21 k$ sur le résultat affiché : sans
> l'avertissement, on aurait attribué à la stratégie un gain qui n'est qu'une
> valorisation.

[[PAGEBREAK]]
# Partie II — Les instruments

## Module 6 — L'API de stratégie

### La forme Blueshift, volontairement

L'API reprend la forme Zipline/Blueshift : `initialize`, `handle_data`,
`schedule_function`, `order_target_percent`, `data.history`, `record`. Un
utilisateur qui a déjà écrit une stratégie ailleurs reconnaît la grammaire, et
le seul apprentissage nouveau est la couche ShockDesk (`get_forecast`,
`option_contract`, `get_iv`, `vol_regime`).

### Les points d'entrée

| Fonction | Quand | Signature acceptée |
|---|---|---|
| `initialize(context)` | une fois, avant la première barre | `(context)` |
| `before_trading_start(context, data)` | chaque barre, avant les ordres | `(context)` ou `(context, data)` |
| `schedule_function(f, date_rule, time_rule)` | selon la règle de dates | `(context)` ou `(context, data)` |
| `handle_data(context, data)` | chaque barre si rien n'est planifié | `(context)` ou `(context, data)` |

Le moteur inspecte le nombre d'arguments de la fonction : on peut écrire
`def trade(context):` ou `def trade(context, data):`, les deux marchent.

Une exception dans `initialize` arrête le backtest et remonte dans `error`. Une
exception dans une fonction planifiée est journalisée, le backtest continue :
une erreur le 12 août ne doit pas effacer ce qui s'est passé avant.

### Les règles de dates

`date_rules.every_day()`, `every_n_days(n)` (un bar sur n), `week_start()`,
`month_start()`, `month_end()`. `month_end` est calculé comme « le jour ouvré
suivant change de mois », ce qui est la définition utile en journalier.

`time_rules` existe pour la compatibilité d'écriture mais ne change rien : avec
un seul bar par jour, `market_open()` et `market_close()` désignent le même
instant. Écrire `time_rules.market_close()` n'est pas une erreur, c'est une
intention documentée pour le jour où l'intraday arrivera.

### Passer des ordres

| Fonction | Effet |
|---|---|
| `order(asset, amount)` | Achète `amount` unités (négatif = vente) |
| `order_value(asset, value)` | Achète pour `value` dollars |
| `order_target(asset, target)` | Ramène la position à `target` unités |
| `order_target_value(asset, value)` | Ramène la position à `value` dollars |
| `order_target_percent(asset, pct)` | Ramène la position à `pct` de l'actif net |

Les fonctions `order_target_*` sont les bonnes pour un book : elles expriment un
état souhaité, pas une variation, donc elles sont idempotentes. Relancer la même
règle deux fois ne double pas la position.

Sur une option, `order_target_percent` calcule un pourcentage du portefeuille en
notionnel et arrondit au contrat, avec un avertissement dans le journal. Ce
n'est pas interdit, mais ce n'est presque jamais ce qu'on veut : la bonne
question sur une option est « combien de contrats », pas « quel pourcentage ».

### Lire les données

`data.current(asset, fields)` renvoie le prix du jour (par défaut `close`).
`data.history(asset, fields, bar_count)` renvoie une série des `bar_count`
derniers bars, bar courant inclus. `data.can_trade(asset)` dit si le sous-jacent
est dans l'univers — pour une option, elle teste le sous-jacent.

Le paramètre `frequency` de `history` est accepté et ignoré : il n'y a qu'une
fréquence. Le conserver évite de casser du code écrit pour un autre moteur.

### Enregistrer ses propres séries

`record(signal=1, exposure=0.85)` alimente des séries tracées avec la courbe
d'équité. Les jours sans appel héritent de la valeur précédente au moment du
rapport : une série de `record` est une série d'état, pas une série d'événements.
C'est pratique pour un signal qui ne change que rarement, trompeur pour compter
des occurrences.

### Le reste du namespace

`symbol`, `symbols` (validation contre l'univers), `get_datetime`,
`option_contract`, `get_iv`, `vol_regime`, `get_forecast`, `get_scenario`,
`set_commission`, `set_slippage`, `log` (`info`, `warn`, `error`), et les
modules `math`, `np`, `pd`, `config`, `options`, `structures`. Tout `print()`
d'une stratégie est capturé et versé au journal, dans la limite de 200 lignes.

> **Règle de la maison.** `log.info` pour les décisions, `record` pour les
> séries, `print` pour rien. Le journal est ce qu'on relit en revue ; une
> stratégie qui ne journalise pas sa sortie est une stratégie qu'on ne peut pas
> auditer.

## Module 7 — Options : pricing, surface, grecs

### Ce qui est modélisé

Tout est européen, pricé en Black-Scholes avec dividende continu `q`. Il n'y a
pas de chaîne d'options réelle en phase 1 : les contrats sont **synthétiques**,
construits de façon déterministe pour n'importe quel sous-jacent qui porte le
drapeau `options`. Cela permet de rejouer une vue de volatilité sans attendre un
flux de marché, et c'est la limite principale à connaître.

```python
def black_scholes(S, K, T, sigma, kind="call", r=RISK_FREE, q=0.0):
    if T <= 0:
        return max(0.0, (S - K) if kind == "c" else (K - S))
    d1, d2 = _d1_d2(S, K, T, r, q, sigma)
    disc_r, disc_q = math.exp(-r * T), math.exp(-q * T)
    if kind == "c":
        return S * disc_q * norm_cdf(d1) - K * disc_r * norm_cdf(d2)
    return K * disc_r * norm_cdf(-d2) - S * disc_q * norm_cdf(-d1)
```

Le taux sans risque du pricer est 4,1 % annuel. Il est à recalibrer comme le
reste.

### La surface de volatilité implicite

L'IV n'est pas une constante : c'est une fonction du moneyness et de la
maturité, avec trois effets et deux chocs.

```python
smile = 1.0 + spec.iv_smile * (m - 1.0) ** 2 + spec.iv_skew * (m - 1.0)
term  = 1.0 + spec.iv_term * math.log(max(years * 365.0, 1.0) / 30.0)
iv    = base * smile * term * vol_regime + iv_shift
return float(min(max(iv, 0.02), 4.0))
```

| Terme | Rôle | Défaut |
|---|---|---|
| `base` | Niveau ATM : `iv_base`, sinon `ann_vol × 1,12` | par actif |
| `iv_smile` | Convexité du sourire, en `(m − 1)²` | 0,55 |
| `iv_skew` | Pente : les puts OTM sont plus chers | −0,25 |
| `iv_term` | Structure en terme, en `log(jours / 30)` | 0,10 |
| `vol_regime` | Multiplicateur : régime de vol réalisée | 1,0 |
| `iv_shift` | Choc **additif en points** d'un scénario | 0,0 |

Deux choses à retenir. D'abord `iv_shift` est additif **après** le régime : un
scénario qui anticipe +10 points d'IV décale toute la surface, ce qui valorise
le book d'options même si le sous-jacent ne bouge pas. Ensuite la surface est
bornée à [2 %, 400 %] : un choc démesuré produit une IV plafonnée, et l'atelier
d'options le signale plutôt que de le corriger en silence.

### Le régime de volatilité

`vol_regime(symbol, window=20)` vaut vol réalisée sur `window` jours divisée par
la volatilité calibrée de l'actif, bornée à [0,55 ; 2,6]. 1,0 = régime normal.
Il faut au moins 6 points, sinon la fonction renvoie 1,0 — une série trop courte
ne doit pas inventer un régime.

C'est le multiplicateur de toute la surface : en régime 1,4, une option ATM 30
jours vaut environ 40 % plus cher. Toute structure comparée entre deux régimes
doit le dire.

### Les grecs

`greeks()` renvoie delta, gamma, vega, theta, rho, avec les conventions de
normalisation du desk :

| Grec | Unité | Convention |
|---|---|---|
| delta | unité de sous-jacent | par contrat |
| gamma | unité par point de sous-jacent | par contrat |
| vega | dollars **par point** de vol | vol divisée par 100 |
| theta | dollars **par jour calendaire** | annualisé divisé par 365 |
| rho | dollars **par point** de taux | taux divisés par 100 |

Lire un vega de +0,85 comme « 85 $ par point de vol » suppose le multiplicateur
du contrat appliqué au moment de l'ordre. À l'échéance (`T ≤ 0`), delta vaut ±1
selon la moneyness et les autres grecs sont nuls.

### La volatilité implicite inverse

`implied_vol(price, S, K, T, kind)` résout l'IV par bissection sur [0,01 %, 500 %]
avec 80 itérations. La bissection plutôt que Newton : elle ne diverge jamais, et
sur un pricer de desk la robustesse vaut mieux que la vitesse. Renvoie `None` si
le prix est sous l'intrinsèque actualisé ou hors du domaine.

### Les contrats synthétiques

Un contrat est un quadruplet immuable : sous-jacent, type, strike, échéance. Son
identifiant stable est `OPT|BZ=F|C|90.0000|2026-08-14`, ce qui permet de le
retrouver d'un bar à l'autre dans les positions et les transactions.

L'échéance est calculée comme la date courante plus `days`, ramenée au vendredi
suivant — approximation du troisième vendredi des options US. Le strike est
arrondi sur la grille usuelle du niveau de prix : pas de 5 $ au-dessus de 200 $,
2,50 $ au-dessus de 50 $, 1 $ au-dessus de 20 $, 0,50 $ au-dessus de 5 $, 0,25 $
en dessous, jamais moins que le tick de l'actif.

> **Pourquoi arrondir.** Une stratégie qui construirait un strike à 89,713 $ ne
> correspond à rien de négociable, et son prix ne serait pas comparable à celui
> d'une chaîne réelle. L'arrondi coûte quelques centimes de précision et rend
> tout le reste comparable.

[[PAGEBREAK]]
## Module 8 — Le catalogue de structures

### Dix structures, deux familles

Le catalogue `structures` (alias de `options.CATALOG`) porte dix structures.
Chacune déclare ses bornes : `max_loss_bounded` et `max_gain_bounded`. C'est
déclaré par structure, pas déduit d'une grille — sinon l'interface afficherait
« 4 213 $ de perte maximale » là où la réponse honnête est « illimitée ».

| Structure | Jambes | Perte max | Gain max | Ce qu'on joue |
|---|---|---|---|---|
| `strangle` | +1 call OTM, +1 put OTM | la prime | illimité | Long gamma, long vega : le mouvement |
| `short_strangle` | −1 call OTM, −1 put OTM | illimitée | la prime | Le range, le carry de prime |
| `straddle` | +1 call ATM, +1 put ATM | la prime | illimité | L'amplitude pure, au prix fort |
| `butterfly` | +1 / −2 / +1 calls équidistants | la prime | le corps | Le timing : finir sur le corps |
| `put_butterfly` | +1 / −2 / +1 puts équidistants | la prime | le corps | Miroir du call butterfly |
| `iron_condor` | put spread vendeur + call spread vendeur | l'écart des ailes | la prime | Le range, risque borné |
| `call_spread` | +1 call, −1 call plus haut | la prime | l'écart | Une vue haussière à coût réduit |
| `put_spread` | +1 put, −1 put plus bas | la prime | l'écart | Une vue baissière à coût réduit |
| `risk_reversal` | −1 put OTM, +1 call OTM | le sous-jacent qui tombe | illimité | Le directionnel financé par le put |
| `calendar` | −1 call court, +1 call long, même strike | limitée | le corps | La différence de theta et la remontée d'IV |

### Le payoff et ses points morts

Le payoff d'une structure est linéaire par morceaux et casse exactement sur les
strikes. La grille d'évaluation inclut donc explicitement les strikes, et même
leurs voisins immédiats, sinon le sommet d'un butterfly est raté de quelques
dixièmes :

```python
grid = [lo + i * (hi - lo) / n for i in range(n + 1)]
grid += [l.strike for l in self.legs]
grid += [l.strike * (1 + d) for l in self.legs for d in (-1e-6, 1e-6)]
```

Les points morts sont cherchés sur une grille de 4 001 points dont la fenêtre
est élargie par la prime nette : un choc d'IV démesuré repousse les points morts
loin des strikes, et la grille doit les suivre. Seuls les **franchissements**
sont retenus — un plateau exactement à zéro (les ailes d'un butterfly) ne
produit qu'un bord, pas une liste de points redondants.

### L'arrondi des écartements

Un butterfly dont les ailes ne sont pas symétriques n'est plus un butterfly :
sa perte maximale dépasse la prime payée, ce qui est une absurdité pour une
structure à risque borné. L'écartement est donc arrondi sur un multiple entier
du pas de strike avant de construire les jambes :

```python
spacing = max(step, round(spot * width / step) * step)
legs = [leg_at("call", body - spacing, 1.0),
        leg_at("call", body, -2.0),
        leg_at("call", body + spacing, 1.0)]
```

Même logique pour l'iron condor, où l'écart intérieur est arrondi et l'extérieur
est exactement le double : sans cela, l'arrondi des strikes rend les deux ailes
asymétriques et le « risque borné » ne l'est plus.

### Le calendar n'est pas une structure à l'échéance

Dans un calendar, la jambe longue n'est pas échue quand la jambe courte l'est.
Le payoff la marque donc à sa valeur Black-Scholes résiduelle, pas à
l'intrinsèque :

```python
residual = max((l.days or self.days) - self.days, 0) / 365.0
value = intr
if residual > 0:
    bs = black_scholes(S, l.strike, residual, max(l.iv, 0.02), l.kind)
    value = max(bs, intr)
```

La jambe longue par défaut est `max(jours × 3, jours + 30)`. Un calendar 30/90
jours joue deux choses à la fois : la différence de theta et, si l'IV remonte,
la valeur de la jambe longue. C'est la structure à regarder quand un scénario
anticipe un choc de volatilité.

### L'atelier d'options et ses alertes

`option_lab(underlying, structure, days, width, iv_shift, vol_regime)` price une
structure, trace son payoff sur 121 points entre 0,85× le strike le plus bas et
1,15× le plus haut, et renvoie des alertes pédagogiques. Le pricer ne corrige
jamais en silence :

| Alerte | Déclencheur |
|---|---|
| « IV plafonnée à 400 % par la surface » | une jambe touche le plafond |
| « IV au plancher de 2 % » | un choc négatif excessif |
| « prime nette > 50 % du spot » | structure hors du domaine réaliste |
| « points morts hors de la plage d'évaluation » | payoff nul partout sur la grille |

En ligne de commande :

```
python -m shockdesk.cli option-lab --underlying SPY \
    --structure strangle --days 30 --width 0.03 --iv-shift 0.10
```

La sortie donne la prime nette, la perte et le gain maxima (ou « non bornée » /
« illimité »), les points morts, les grecs agrégés et chaque jambe avec son prix
et son IV. C'est le moyen le plus rapide de vérifier qu'une idée de structure
est cohérente avant de l'écrire dans une stratégie.

### Lire une structure avant de la trader

Cinq lectures, dans cet ordre : le coût (débit ou crédit, et combien en
pourcentage du spot), les points morts (à quelle distance du spot, en
pourcentage), la perte maximale (bornée ou non, et en multiple de la prime), le
vega net (qui paie si l'IV monte), le theta net (qui paie si rien ne bouge).
Une structure dont on ne peut pas énoncer ces cinq nombres n'est pas une
structure, c'est un pari habillé.

### Six structures, mesurées

Les chiffres suivants sont la sortie réelle de l'atelier, mesurée le 30 août
2026 sur le niveau de calibration (`spot` = `s0` de la fiche d'actif : 84,95 $
pour le Brent, 642,00 $ pour SPY). La commande est la même à chaque ligne, seuls
les arguments changent :

```
python -m shockdesk.cli option-lab --underlying BZ=F \
    --structure strangle --days 30 --width 0.04 --iv-shift 0.10
```

| Structure | Prime | Perte max | Gain max | Points morts | Vega | Theta/j |
|---|---|---|---|---|---|---|
| Brent, strangle 30 j, ±4 % | 4,78 | 4,78 | 30,22 | 77,72 / 92,28 | +0,19 | −0,112 |
| Brent, strangle 30 j, ±4 %, IV +10 pts | 6,65 | 6,65 | 28,35 | 75,85 / 94,15 | +0,19 | −0,145 |
| Brent, butterfly 21 j, ±5 % | 1,36 | 1,36 | 3,64 | 81,36 / 88,64 | −0,04 | +0,030 |
| Brent, calendar 30 j, IV +10 pts | 4,17 | 4,15 | 2,95 | 78,87 / 93,22 | +0,07 | +0,028 |
| SPY, straddle 30 j | 24,40 | 24,40 | 231,60 | 615,60 / 664,40 | +1,45 | −0,405 |
| SPY, iron condor 30 j, ±3 % | −6,23 | 3,77 | 6,23 | 623,77 / 656,23 | −0,20 | +0,056 |

Signe de la prime : positif = débit (structure acheteuse), négatif = crédit.
L'iron condor encaisse 6,23 et risque 3,77 : c'est le profil classique d'une
vente de prime bornée.

Trois lectures à faire sur ce tableau. Le choc d'IV de +10 points renchérit le
strangle de 39 % (4,78 → 6,65) et repousse ses points morts de 1,87 $ vers
l'extérieur : acheter du gamma après l'annonce du choc coûte plus cher et
demande un mouvement plus fort. Le butterfly ne risque que sa prime de 1,36 pour
un gain plafonné à 3,64 : le ratio gain sur risque est de 2,7, mais la fenêtre
utile est étroite — entre 81,36 et 88,64. Le calendar, avec un choc d'IV
anticipé, est la seule des quatre structures Brent dont le theta est positif :
c'est la structure qui gagne quand le temps passe et que l'IV monte.

Le détail des jambes, pour le strangle à +10 points : `+1 call 87,50 @ 3,46
(IV 45,7 %)` et `+1 put 82,50 @ 3,19 (IV 46,3 %)`. Le put OTM est plus cher que
le call OTM en prime absolue malgré un écart plus faible au spot : c'est le skew
à −0,25, visible dans les chiffres.

> **Attention à la lecture du code.** Les propriétés `net_premium` et `cost`
> renvoient la même valeur, et leurs docstrings annoncent des conventions de
> signe opposées. Seule l'observation tranche : un strangle acheteur renvoie
> +4,78, donc positif = débit. Quand deux commentaires se contredisent, le
> chiffre mesuré a raison.

[[PAGEBREAK]]
## Module 9 — Anatomie d'une stratégie complète

### Un exemple entier, commenté

Voici une stratégie écrite pour ce cours — elle n'est pas dans le dépôt. Elle
reprend tous les concepts des modules précédents dans un seul fichier, ce qui
permet de voir comment ils s'articulent : une vue issue du registre, un
dimensionnement borné, une sortie décidée ex-ante, une couverture optionnelle,
et de quoi auditer le tout.

```python
"""Choc d'offre — book directionnel + couverture gamma.

Entre à la publication d'une prévision sur le sous-jacent signal, sort au
premier des deux événements décidés ex-ante : le pic du modèle ou le stop
calendar. Une jambe d'options n'est ajoutée que si l'amplitude attendue
dépasse le mouvement payé par l'IV.
"""

SIGNAL = "BZ=F"          # sous-jacent qui porte la vue
HEDGE = "^GSPC"          # couverture : c'est elle qui paie sur un choc
BOOK = {"BZ=F": 0.35, "^GSPC": -0.45, "TLT": 0.20}
GROSS = 0.70             # exposition brute cible
MAX_HOLD = 21            # garde-fou calendaire, en plus du stop publié
OPTION_RATIO = 1.15      # au-delà, on achète du gamma


def initialize(context):
    context.entered_on = None
    context.played = set()
    schedule_function(decide, date_rules.every_day())


def _scale(f):
    """Confiance transformée en exposition, bornée à [0,25 %, 100 %]."""
    return GROSS * max(min(f.confidence * 1.6, 1.0), 0.25)


def _flatten(context, reason):
    for asset, pos in list(context.portfolio.positions.items()):
        if abs(pos.amount) > 1e-9:
            order(asset, -pos.amount, reason=reason)
    log.info(f"Book aplati — {reason}.")


def decide(context, data):
    today = get_datetime().date()
    f = get_forecast(SIGNAL)

    # --- sortie : le premier des deux événements prévus ---------------- #
    if context.entered_on is not None:
        held = (today - context.entered_on).days
        peak = int(round(f.peak_base)) if f else 7
        stop = f.stop_date if f else None
        if held >= min(peak, MAX_HOLD) or (stop and today >= stop):
            _flatten(context, f"sortie J+{held} (pic {peak} / stop {stop})")
            context.entered_on = None
            record(exposure=0.0, gamma=0.0)
            return

    # --- entrée : une passe par révision publiée ---------------------- #
    if context.entered_on is None and f is not None:
        key = (f.id, f.rev)
        if key in context.played:
            return
        context.played.add(key)
        context.entered_on = today
        scale = _scale(f)
        total = sum(abs(w) for w in BOOK.values()) or 1.0
        for sym, w in BOOK.items():
            weight = (w / total) * scale * (f.sign if sym == SIGNAL else 1.0)
            order_target_percent(sym, weight, reason=f"entrée r{f.rev}")

        # --- la jambe optionnelle, seulement si le ratio le justifie --- #
        iv = get_iv(SIGNAL, 1.0, 30)
        implied = iv * (30 / 365.0) ** 0.5
        if f.amp_base / implied >= OPTION_RATIO:
            call = option_contract(SIGNAL, "call", moneyness=1.05, days=30)
            put = option_contract(SIGNAL, "put", moneyness=0.95, days=30)
            order(call, 10, reason=f"gamma r{f.rev}")
            order(put, 10, reason=f"gamma r{f.rev}")
            log.info(f"Ratio {f.amp_base / implied:.2f} : gamma ajouté.")
        record(exposure=scale, gamma=1.0)
        return

    record(exposure=0.0, gamma=0.0)
```

### Ce qu'il faut regarder, bloc par bloc

**Les paramètres en tête.** Tout ce qui se recalibre à la revue mensuelle est en
constantes de module, pas enfoui dans le corps des fonctions. Une revue qui
demande de lire vingt lignes pour trouver l'exposition cible est une revue qui
ne sera pas faite.

**`context.played`.** L'ensemble des `(identifiant, révision)` déjà jouées. Sans
lui, une stratégie re-entre tous les jours tant que la prévision est active — ce
qui n'est pas une erreur visible dans le code, seulement dans le turnover.

**`_scale`.** La confiance devient une exposition, bornée entre 25 % et 100 % de
la cible. La borne basse évite qu'une confiance de 0,4 produise une position si
petite que les frais la mangent ; la borne haute évite qu'une confiance de 1,0
dépasse l'exposition décidée.

**Le dénominateur.** `sum(abs(w) for w in BOOK.values())`, pas la somme signée.
Avec un poids de −0,45 sur la couverture, la somme signée vaut 0,10 : diviser
par elle multiplierait toutes les lignes par dix.

**La sortie avant l'entrée.** La règle de sortie est testée en premier dans la
fonction quotidienne. Inverser les deux blocs fait entrer et sortir le même
jour, avec deux allers-retours de frais.

**Le garde-fou calendaire.** `MAX_HOLD` existe parce que le stop publié peut
être lointain, ou absent. Une stratégie sans garde-fou de durée dépend
entièrement de la qualité d'un champ du registre.

**La jambe optionnelle conditionnelle.** Elle n'est ajoutée que si le ratio
amplitude attendue sur mouvement implicite dépasse 1,15 — exactement le seuil du
module 12. Une stratégie qui achète toujours du gamma paie du theta sans raison.

**`record` et `log`.** Deux séries enregistrées (`exposure`, `gamma`), un
`log.info` à chaque aplatissement et à chaque ajout de gamma. C'est ce qui
permet de rejouer la décision six mois plus tard.

### La checklist avant d'enregistrer

Une stratégie est enregistrable quand ces huit points sont vrais : les
paramètres sont en tête de fichier ; l'univers contient tous les symboles
utilisés ; la sortie est décidée ex-ante et testée avant l'entrée ; le
dénominateur d'exposition est brut ; une seule passe par révision ; chaque ordre
porte un `reason` ; les décisions sont journalisées ; le backtest a été lu —
journal compris — avant d'être commenté.

### Les six stratégies du dépôt

Elles couvrent six façons d'exprimer la même anticipation. Chacune est courte,
et chacune isole une idée : c'est pour cela qu'elles sont six.

| Fichier | Idée | Univers |
|---|---|---|
| `shock-lab-oil.py` | Le book multi-actifs du scénario publié, avec stop calendar **et** take-profit au pic | `global-macro` |
| `long-strangle-shock.py` | Acheter du gamma des deux côtés quand l'amplitude attendue dépasse la prime payée | `global-macro` |
| `butterfly-peak.py` | Le trade du timing : corps du butterfly sur le niveau de pic prévu | `global-macro` |
| `short-strangle-carry.py` | Vendre la prime quand aucune prévision de choc n'est active | `us-equities` |
| `iron-condor-range.py` | Même idée, risque borné par des ailes achetées | `us-equities` |
| `us-equities-momentum.py` | La référence : momentum 6-1 mensuel avec filtre de tendance | `us-equities` |

La dernière n'a aucune vue de scénario. Elle existe pour répondre à la seule
question qui vaille en revue : est-ce que l'anticipation rapporte plus que ce
qu'un momentum banal aurait rapporté sur la même fenêtre ?

[[PAGEBREAK]]
# Partie III — L'anticipation

## Module 10 — Les prévisions point-in-time

### L'objet Forecast

Une prévision est une vue publiée sur un sous-jacent. Ses champs :

| Champ | Type | Sens |
|---|---|---|
| `sign` | ±1 | Sens de la vue |
| `amplitude` | liste | Grille d'amplitudes, en fraction du spot |
| `peak_day` | liste | Fenêtre du jour de pic, en jours calendaires |
| `reversion` | float | Niveau cumulé **signé** en fin d'épisode |
| `reversion_days` | int | Durée de la reversion |
| `iv_shift` | float | Choc d'IV anticipé, en points décimaux |
| `confidence` | float | Confiance, utilisée pour dimensionner |
| `stop_date` | date | Sortie calendar fixée ex-ante |
| `published`, `rev` | date, int | Date de publication et numéro de révision |

Deux conventions sont faciles à rater. L'**amplitude est une magnitude** et
`sign` porte le sens : `sign=-1, amplitude=0.05` signifie « baisse de 5 % ». La
**reversion est un niveau cumulé signé**, pas une variation depuis le pic :
`reversion=-0.065` veut dire « on finit 6,5 % sous le niveau de publication »,
que le pic ait été à +18 % ou à +3 %.

### Amplitude en grille, pas en chiffre

Depuis la révision 2 de l'exercice de juillet 2026, l'amplitude est une liste :
`[0.05, 0.10, 0.185]`. Trois valeurs, lues comme bas / base / haut, et la grille
de stress est dérivée :

```python
out = sorted({round(x, 5) for x in list(self.amplitude) +
              [base * 0.5, base * 1.5, base * 2.0, base * 3.7]})
```

Le multiple 3,7 n'est pas arbitraire : c'est le facteur par lequel le Brent a
dépassé la prévision initiale de l'exercice. La grille de stress garde en
mémoire le miss.

Les deux grilles du pétrole, telles que le registre les calcule :

| Révision | Amplitudes publiées | Base | Grille de stress dérivée |
|---|---|---|---|
| r1 (15/07) | `[0,05]` | 5 % | 2,5 % · 5 % · 7,5 % · 10 % · **18,5 %** |
| r2 (28/08) | `[0,05 ; 0,10 ; 0,185]` | 10 % | 5 % · 10 % · 15 % · 18,5 % · 20 % · **37 %** |

Sur r1, la grille contient déjà 18,5 % — le scénario réalisé. La prévision
publiée était fausse, la grille qui en dérive contenait la bonne réponse : c'est
tout l'intérêt de stresser en grille plutôt qu'en chiffre. Sur r2, la base est
10 % et la grille monte jusqu'à 37 %, soit deux fois le choc observé : une
révision honnête élargit plus qu'elle ne recentre.

De même, `peak_day` peut être une fenêtre `[7, 9]`. Annoncer un pic à J+7 ± 0
est une fausse précision : la fenêtre est ce qu'on sait réellement.

### La trajectoire prévue

`Forecast.path(days, amplitude)` fabrique la trajectoire cumulée, jour
calendaire par jour calendaire : montée en cosinus jusqu'au pic, puis
interpolation linéaire du pic vers la reversion jusqu'à `reversion_days`, puis
palier.

```python
if i <= peak:
    t = i / peak
    out[i] = peak_val * (0.5 - 0.5 * np.cos(np.pi * t))
elif i <= rev_days:
    t = (i - peak) / max(rev_days - peak, 1)
    out[i] = peak_val * (1 - t) + self.reversion * t
else:
    out[i] = self.reversion
```

Le cosinus n'est pas décoratif : il impose une montée lente puis rapide, ce qui
ressemble à la propagation d'un choc d'offre, et il rend la corrélation de
trajectoire mesurable — on peut comparer la forme prévue à la forme réalisée,
pas seulement le niveau final.

### Le registre et la règle de non-réécriture

Le registre vit dans `config/forecasts.json`. Au 30 août 2026 il porte huit
prévisions pour dix révisions publiées : le pétrole et l'or ont deux révisions
chacun, les autres une seule.

```python
def add_revision(self, fid, **fields):
    rev = max((int(r["rev"]) for r in entry["revisions"]), default=0) + 1
    rec = {"rev": rev}
    rec.update(fields)
    rec.setdefault("date", pd.Timestamp.today().date().isoformat())
    entry["revisions"].append(rec)
    self.save()
```

On ajoute, on ne remplace pas. Corriger une prévision en écrasant la révision 1
rendrait impossible la seule mesure qui compte : l'écart entre ce qui a été
publié et ce qui s'est passé.

### La lecture point-in-time

C'est la règle la plus importante du moteur, et la plus simple :

```python
def active(self, on, asset):
    """Dernière révision publiée avant ``on`` pour ``asset``."""
    for f in self.revs[fid]:
        if pd.Timestamp(f.published) <= on:
            if best is None or (f.published, f.rev) > (best.published, best.rev):
                best = f
    return best
```

`get_forecast(symbol)` dans une stratégie appelle cette fonction à la date du
bar. Le 20 juillet, une stratégie voit la révision 1 publiée le 15 juillet ; le
29 août, elle voit la révision 2 publiée le 28. Jamais l'inverse.

> **Règle de la maison.** Aucune fuite d'information. Un backtest qui utilise
> une prévision corrigée après coup ne mesure pas une stratégie, il mesure
> l'honnêteté de celui qui l'a écrit.

## Module 11 — Le scoring ex-post

### Nettoyer le drift du benchmark

Comparer un rendement brut à une prévision est une erreur : une partie du
mouvement est du marché. La validation calcule un rendement **actif**, net du
drift du benchmark pondéré par le bêta :

```python
beta = asset.loadings["SPX"] / benchmark.loadings["SPX"]
active = ret - beta * benchmark_ret
```

Le bêta est déduit des chargements factoriels, pas estimé sur la fenêtre : avec
sept facteurs explicites, le rapport des chargements `SPX` est le bêta du modèle.
Pour le Brent face au S&P 500, cela donne −0,05 / 1,00 = −0,05 : le pétrole est
quasi neutre au marché, donc son rendement actif est presque son rendement brut.
Pour une ligne actions, le nettoyage change tout.

### Ce qui est mesuré

| Mesure | Définition | Lecture |
|---|---|---|
| `sign_ok_peak` | Signe du rendement actif au pic contre `sign` | La vue directionnelle |
| `sign_ok_end` | Signe du rendement actif en fin de fenêtre | Ce qui reste après reversion |
| `amplitude_ratio` | Pic réalisé / amplitude prévue | Le facteur de sous-estimation |
| `peak_error_days` | Pic réalisé − pic prévu, en jours | La qualité du timing |
| `mfe` / `mae` | Maximum / minimum du rendement actif | Le chemin, pas seulement l'arrivée |
| `path_correlation` | Corrélation avec la trajectoire prévue | La forme de l'épisode |
| `benchmark_drift` | Rendement du benchmark sur la fenêtre | Ce qu'on a retiré |

Le pic réalisé est `argmax` de la valeur absolue du rendement actif : pour une
vue baissière, le pic est le point le plus bas, pas le plus haut. C'est ce qui
permet de comparer des vues de signes opposés avec la même fonction.

### Ce qui est compté

`counted = (asset != benchmark) and rev == 1`. Deux exclusions, chacune avec sa
raison.

**Le benchmark n'est pas compté.** Le S&P 500 est le benchmark du
`global-macro` : le noter reviendrait à noter zéro contre zéro. Il est affiché
pour mémoire, jamais compté.

**Seule la révision 1 est comptée.** Les révisions suivantes sont des
corrections publiées après les faits : les laisser améliorer le score serait la
fuite d'information, version comptable. Elles restent affichées — ce sont elles
qui portent l'apprentissage — mais le score est celui de ce qui a été publié et
tradé.

### Hors univers n'est pas faux

Une prévision dont le sous-jacent n'est pas dans le panneau chargé n'est pas une
prévision fausse : elle n'est pas testable dans cet univers. Elle est marquée
`out_of_universe` et regroupée à part. Sans cela, un scorecard lancé sur
`us-equities` affiche neuf lignes sur dix en « non évaluable », et le mur de
croix se lit comme un échec alors qu'il n'y a rien à mesurer.

Le tableau de scorecard renvoie donc à la fois `lines_total`, `evaluable_total`,
`out_of_universe_total` et `non_test`. Lire un taux de réussite sans le
dénominateur est la faute de lecture la plus fréquente.

### Médiane plutôt que moyenne

L'erreur de timing est résumée par la **médiane** des valeurs absolues, pas la
moyenne. Une prévision dont le pic est monotone en fin de fenêtre produirait une
erreur de quarante jours qui ferait exploser la moyenne sans rien dire du
timing des six autres. La moyenne est quand même renvoyée, pour voir la
dispersion.

Sur l'exercice de juillet 2026 : accord de signe 5 sur 6, erreur de timing
médiane de 1 jour, ratio d'amplitude de 3,69 sur le Brent — médiane de 1,47 sur
les six lignes comptées —, et un miss net, l'or.

> **Règle de la maison.** Un miss se note dans la révision, pas dans un coin. La
> révision 2 de l'or le dit en toutes lettres : l'or n'est pas la couverture
> d'un choc d'offre quand le dollar et les taux réels montent. C'est la ligne la
> plus utile du registre.

[[PAGEBREAK]]
## Module 12 — Du signal à la structure

### La question unique

Toute la logique de recommandation tient dans une comparaison : le mouvement que
la prévision attend contre le mouvement que l'IV facture.

```python
expected_move = f.amp_base * spot
implied_move  = iv_atm * spot * np.sqrt(days / 365.0)
ratio         = expected_move / implied_move
```

`expected_move` est l'amplitude prévue en dollars. `implied_move` est le
mouvement d'un écart-type implicite à l'horizon choisi — ici
`jours = pic prévu + 7`, au minimum 14. Le ratio est un nombre sans unité :
1,0 veut dire que le marché facture exactement ce que la prévision attend.

### Les trois régimes de décision

| Ratio | Lecture | Structures proposées (score) |
|---|---|---|
| ≥ 1,15 | L'amplitude attendue dépasse ce que paie l'IV | `strangle` (100), `straddle` (70) |
| ≤ 0,75 | L'amplitude attendue est faible, ou reversion rapide | `short_strangle` (90), `iron_condor` (80), `butterfly` (60) |
| entre les deux | Sens marqué, amplitude proche de l'IV | `call_spread` / `put_spread` (85), `butterfly` (55) |

Deux ajouts conditionnels : si `iv_shift ≥ 0,05`, un `calendar` (65) entre —
choc d'IV anticipé, donc long vega court terme ; si le ratio est sous 1,0 et que
le sens est marqué, un `risk_reversal` (50) — la vue directionnelle financée par
la vente du put OTM. Les propositions sont triées par score décroissant, les
quatre premières sont conservées, chacune avec sa raison écrite en toutes
lettres.

Ce n'est pas un conseil automatique. C'est la transcription d'un raisonnement de
desk : on achète du gamma quand on pense que le marché sous-estime le mouvement,
on vend de la prime quand on pense l'inverse, on paie peu de vega quand on a une
vue de sens mais pas d'amplitude.

### Le P&L sous chaque nœud de la grille

Chaque structure proposée est évaluée sur la grille d'amplitudes de la
prévision, dans trois directions : le scénario, le contre-sens, le statique.

```python
for amp in f.grid:
    for mult, lbl in ((1.0, "scénario"), (-1.0, "contre-sens"),
                      (0.0, "statique")):
        end = spot * (1 + mult * amp * f.sign)
```

Le P&L d'un nœud n'est pas un payoff à l'échéance : c'est intrinsèque plus
valeur temps résiduelle au nouveau niveau d'IV, au jour de pic prévu.

```python
t_left = max(structure.days - days_held, 0) / 365.0
iv = max(leg.iv + iv_change, 0.02)
time_value = max(black_scholes(spot_end, leg.strike, t_left, iv, leg.kind)
                 - intrinsic, 0.0)
```

Cette approximation est volontaire : elle répond à la question « que vaut la
structure au jour où la prévision dit que l'épisode culmine », qui est la
question utile pour décider d'une sortie.

### Lire la table des nœuds

Trois colonnes à comparer, pas une. Le gain dans le scénario dit ce que l'idée
rapporte si elle a raison ; la perte dans le contre-sens dit ce qu'elle coûte si
elle a tort ; la valeur du nœud statique dit ce que le temps fait, sans
mouvement. Une structure dont le nœud statique est très négatif est une
structure qui paie du theta : il faut que le mouvement arrive vite.

Un strangle long sur le Brent à +18,5 % (le haut de la grille corrigée) gagne
beaucoup ; à −5 % (le contre-sens doux) il perd sa prime ; à 0 % il perd
lentement. C'est exactement le profil d'un achat de gamma : on paie pour un
événement, et on perd si rien ne se passe.

> **Règle de la maison.** Choisir une structure sans lire le nœud contre-sens,
> c'est acheter une option sans regarder le prix. Le tableau des nœuds est là
> pour ça : il met le pire cas à côté du meilleur.

### Une recommandation mesurée

Le 28 août 2026, sur le Brent, avec la révision 2 active et les paramètres
suivants — spot 86,65 $, volatilité réalisée 24,36 % sur 21 jours (régime
0,717), choc d'IV de +14 points portant l'IV ATM 30 jours à 39,80 % —, le calcul
donne :

```
mouvement attendu  = 10,0 % × 86,65 = 8,66 $
mouvement implicite = 39,80 % × 86,65 × √(16/365) = 7,22 $
ratio = 1,20   →   régime « long gamma »
```

Trois structures sont proposées, dans cet ordre de score :

| Structure | Score | Coût | Points morts |
|---|---|---|---|
| Long strangle 16 j, ±4 % | 100 | +3,80 | 78,70 / 93,80 |
| Long straddle 16 j | 70 | +6,95 | 80,55 / 94,45 |
| Calendar 16/48 j | 65 | +3,16 | 82,51 / 93,72 |

Et le P&L du strangle sous les nœuds de la grille, au jour de pic :

| Nœud | Spot final | P&L par contrat |
|---|---|---|
| Scénario +5 % | 90,98 | +0,29 |
| Scénario +10 % | 95,31 | +2,88 |
| Contre-sens −5 % | 82,32 | −2,14 |
| Contre-sens −10 % | 77,98 | +0,87 |
| Statique | 86,65 | −2,03 |

Quatre choses à lire dans ce tableau, et elles ne sont pas toutes rassurantes.

Le ratio de 1,20 est juste au-dessus du seuil de 1,15 : la recommandation « long
gamma » tient à 5 % près. Un desk ne traite pas un seuil comme une décision — il
le traite comme une indication qui demande un deuxième avis.

Le nœud à +5 % ne rapporte que 0,29 par contrat, pour une prime de 3,80. Autrement
dit : si la prévision r2 a raison mais que l'amplitude retombe sur le bas de la
grille, le trade est quasi nul. C'est le risque réel d'acheter du gamma sur une
prévision dont la base vient d'être relevée.

Le contre-sens à −10 % est **positif** (+0,87) : un strangle gagne des deux
côtés au-delà de ses points morts. Ce n'est pas une erreur de signe, c'est la
définition de la structure — et c'est pourquoi elle coûte cher quand rien ne
bouge.

Le calendar, proposé à cause du choc d'IV de +14 points, est négatif sur tous
les nœuds (de −2,97 à −3,15). Il ne devient intéressant que si l'IV monte plus
que prévu : c'est une position de volatilité, pas de direction, et le tableau des
nœuds ne la mesure qu'imparfaitement. Le signaler fait partie du travail — une
recommandation automatique n'est pas une validation.

## Module 13 — Les métriques de performance

### Le tableau complet

`metrics.compute(equity, benchmark, risk_free)` calcule tout à partir de la
courbe d'équité. Voici les définitions exactes, parce que deux d'entre elles
surprennent.

| Métrique | Définition |
|---|---|
| `total_return` | Dernier / premier − 1 |
| `cagr` | Rendement annualisé composé |
| `ann_volatility` | Écart-type des rendements journaliers × √252 (ddof = 0) |
| `sharpe` | Moyenne des rendements en excès / vol × √252 |
| `sortino` | Moyenne des excès / écart-type des seuls jours négatifs × √252 |
| `max_drawdown` | Minimum de `equity / cummax(equity) − 1` |
| `calmar` | CAGR / |max drawdown| |
| `win_rate` | Part des jours positifs |
| `profit_factor` | Somme des gains / somme des pertes, en valeur absolue |
| `skew`, `kurtosis` | Moments des rendements journaliers |
| `var_95` | 5e percentile des rendements journaliers |
| `cvar_95` | Moyenne des rendements au ou sous le 5e percentile |
| `alpha` | Rendement total − rendement du benchmark |
| `beta` | Covariance avec le benchmark / variance du benchmark |
| `information_ratio` | Excès sur benchmark annualisé / tracking error |

### Le piège du taux sans risque

Le Sharpe et le Sortino sont calculés sur `rets − risk_free / 252`. Le taux est
retiré **chaque barre**, y compris celles où le book dort en liquidités — or le
moteur ne rémunère pas le cash. Sur une stratégie qui entre, sort au pic, et
reste en cash, ce terme fixe écrase le ratio : une stratégie à +1,55 % en trois
semaines puis plate peut afficher un Sharpe négatif.

C'est pourquoi `risk_free` est paramétrable et renvoyé dans le payload, pour
être affiché à côté des deux ratios. Le mettre à 0 redonne un Sharpe brut. Le
lire sans savoir lequel des deux on regarde est l'erreur la plus coûteuse de ce
module.

### « n.d. » plutôt que « 0,0 »

Un ratio non défini — volatilité nulle, drawdown nul, moins de deux jours
négatifs — renvoie `None`, affiché « n.d. », jamais `0,0` :

```python
def _r(x, n):
    """Arrondi qui propage None au lieu de le transformer en 0.0."""
    v = _safe(x)
    return None if v is None else round(v, n)
```

Un Sharpe de 0,0 se lit comme « pas de performance ». Un Sharpe « n.d. » se lit
comme « la série ne permet pas de le calculer ». La deuxième phrase est vraie,
la première est une invention.

### Le benchmark est rescalé, pas comparé brut

La courbe de référence affichée est le benchmark ramené au capital de départ :
`(benchmark / premier) × startCapital`. On compare deux courbes qui partent du
même point, ce qui rend la lecture visuelle honnête. L'alpha, lui, est calculé
sur les rendements, pas sur les niveaux.

### Les rendements mensuels

`monthly_returns` rééchantillonne en fin de mois (`resample("ME")`). Le premier
mois est mesuré depuis la valeur initiale, pas depuis le premier bar : un
backtest qui commence le 3 juillet ne doit pas afficher un mois de juillet
calculé sur trois jours comme s'il était complet sans que ce soit visible.

### Ce qu'un desk regarde en premier

Dans l'ordre : le drawdown maximal (ce qu'on a encaissé), l'attribution
(est-ce une idée ou une ligne), le turnover et le coût moyen par transaction
(est-ce que le résultat survit aux frais), puis seulement le Sharpe. Un Sharpe
élevé sur 22 barres avec deux trades est un artefact ; un résultat modeste sur
18 mois avec une attribution stable est une stratégie.

### Un tableau réel, et pourquoi il est illisible

Voici les métriques réelles du book de l'exercice, règle de sortie au pic, sur la
fenêtre du 1er juillet au 28 août 2026 (43 barres, données synthétiques). C'est
le meilleur exemple disponible de ce qu'il ne faut pas lire au premier degré.

| Métrique | Valeur | Lecture honnête |
|---|---|---|
| `total_return` | +1,51 % | Le seul nombre solide du tableau |
| `cagr` | +9,42 % | Annualisation d'un épisode de cinq jours |
| `ann_volatility` | 2,19 % | Volatilité d'un book à plat 90 % du temps |
| `sharpe` | 2,256 | Calculé avec `risk_free` 4,1 % ; à lire avec |
| `sortino` | 168,097 | Artefact : un seul jour négatif sur 42 |
| `max_drawdown` | −0,044 % | Le book est sorti avant de baisser |
| `calmar` | 215,319 | Artefact du drawdown quasi nul |
| `win_rate` | 11,9 % | Ni bon ni mauvais : 37 jours à plat sur 42 |
| `profit_factor` | 18,954 | Ratio de cinq jours gagnants sur un perdant |
| `skew` / `kurtosis` | +4,785 / +25,47 | Une distribution à cinq points n'a pas de moments |
| `var_95` / `cvar_95` | 0,000 / −0,002 % | Le 5e percentile d'une série presque nulle |
| `alpha` | −1,00 % | Le benchmark a monté de 2,51 % pendant ce temps |
| `beta` | −0,145 | Cohérent avec un book short actions |
| `information_ratio` | −1,061 | Sous-performance relative au benchmark |

Un Sortino de 168 n'est pas une performance exceptionnelle : c'est un
dénominateur quasi nul. Un `win_rate` de 11,9 % n'est pas une stratégie qui se
trompe neuf fois sur dix : c'est une stratégie qui n'est en position que cinq
jours sur quarante-deux. Et l'alpha négatif est la vraie information du tableau :
sur la fenêtre, rester investi dans le benchmark aurait rapporté plus que le
scénario — ce qui ne contredit pas la leçon de timing, mais rappelle qu'une
stratégie événementielle se juge sur l'événement, pas sur la fenêtre.

> **Règle de la maison.** Sur une fenêtre courte et majoritairement à plat,
> seuls `total_return`, `max_drawdown`, l'attribution et le journal se lisent.
> Tout le reste est de l'arithmétique sur du vide, et l'afficher comme une
> performance est une faute.

[[PAGEBREAK]]
# Partie IV — La discipline

## Module 14 — Cas pratique : l'exercice de juillet 2026

### Le dispositif

Un scénario est publié le 15 juillet 2026 : choc pétrolier sur le Brent,
amplitude +5 %, pic à J+7, reversion −3 %, choc d'IV de +10 points, stop
calendar fixé au 5 août. Sept prévisions l'accompagnent, une par ligne du book.

Le book testé est celui de l'exercice, en delta pur, sur l'univers
`global-macro`, avec 25,5 M$ de capital, sur la fenêtre du 1er juillet au
28 août 2026 :

| Ligne | Poids | Rôle dans le scénario |
|---|---|---|
| `^GSPC` | −0,45 | Couverture actions : c'est elle qui paie |
| `GC=F` | +0,10 | Or vu comme couverture — le miss de l'exercice |
| `HYG` | +0,10 | Crédit HY, porté par l'énergie |
| `TLT` | +0,10 | Duration, refuge du choc d'offre |
| `BZ=F` | +0,08 | La vue directionnelle brut |
| `DBC` | +0,06 | Contagion au complexe matières |
| `DX-Y.NYB` | +0,05 | Dollar de précaution |

L'exposition brute cible est 85 %, réduite par la confiance de la prévision : le
journal annonce 82 % à l'entrée. Les poids sont normalisés par la somme de leurs
**valeurs absolues** : sommer des poids signés ferait exploser la taille dès
qu'une ligne est vendeuse.

### Les deux règles de sortie

La stratégie porte un interrupteur en tête de fichier, `TAKE_PROFIT_AT_PEAK`.
Deux exécutions, une seule différence : la règle de sortie.

| Règle de sortie | Fenêtre close au | P&L mesuré |
|---|---|---|
| Take-profit au pic (J+7) | 22/07, jour de sortie | **+395 919 $ (+1,55 %)** |
| Take-profit au pic (J+7) | 28/08, fenêtre complète | +385 544 $ (+1,51 %) |
| Stop calendar (05/08) | 05/08, jour de sortie | **−4 054 $ (−0,02 %)** |
| Stop calendar (05/08) | 28/08, fenêtre complète | −14 268 $ (−0,06 %) |

Les deux chiffres en gras sont ceux qui sont publiés dans le README. Les deux
autres s'en écartent parce que la fenêtre complète inclut la ré-entrée sur la
révision 2, publiée le 28 août : sept positions sont ouvertes le dernier jour,
avec un P&L latent de −9 685 $, et le journal le dit explicitement.

**La fenêtre fait partie de la question.** « Combien a rapporté la stratégie »
n'a pas de réponse sans date de fin. Publier un chiffre sans sa fenêtre, c'est
publier un chiffre qu'on ne peut pas rejouer.

### Rejouer l'exercice, chiffres en main

La commande est celle-ci, et elle est reproductible à l'identique :

```
python -m shockdesk.cli backtest --strategy shock-lab-oil \
    --name global-macro --start-capital 25500000 \
    --start-date 2026-07-01 --end-date 2026-08-28 --json
```

Pour la variante au stop, il suffit de basculer `TAKE_PROFIT_AT_PEAK` à `False`
en tête de stratégie — c'est l'atelier 1. Toutes les mesures de ce module ont
été prises le 30 août 2026, sur données synthétiques, avec cette commande.

### Ce que le journal ajoute aux métriques

Le journal de l'exécution au pic contient quatre lignes utiles :

```
2026-07-15 Entrée book — scénario « Choc pétrolier — Brent » r1 : sens +1,
           amplitude prévue +5.0%, pic J+7, stop 2026-08-05. Exposition 82%.
2026-07-22 Sortie J+7 (pic modèle) — P&L +407,216 (+1.60%)
2026-08-28 Entrée book — scénario « Choc pétrolier — Brent » r2 : sens +1,
           amplitude prévue +10.0%, pic J+9, stop 2026-08-05. Exposition 75%.
2026-08-28 Fin de backtest : 7 position(s) encore ouverte(s), P&L latent
           -9,685 $ compris dans le résultat.
```

La deuxième ligne annonce +407 216 $ alors que le backtest clos au 22/07 finit à
+395 919 $. L'écart de 11 297 $ n'est pas une incohérence : c'est le coût de la
sortie. Le P&L journalisé est calculé au mark, avant exécution des ordres
d'aplatissement ; les sept ordres passent ensuite au close avec 5 bps de
slippage sur environ 21,1 M$ de notionnel (10,5 k$) et 754 $ de commissions. Un
desk qui ignore cet écart surestime systématiquement le résultat de ses sorties.

### Les deux attributions, côte à côte

Même book, même entrée, deux sorties. L'attribution change de signe ligne par
ligne.

| Ligne | Sortie au pic (22/07) | Sortie au stop (05/08) |
|---|---|---|
| `BZ=F` | **+283 621 $** | **−117 935 $** |
| `DBC` | +61 026 $ | +13 084 $ |
| `^GSPC` | +55 143 $ | +105 046 $ |
| `TLT` | +27 364 $ | +22 957 $ |
| `DX-Y.NYB` | +23 380 $ | +22 559 $ |
| `HYG` | +6 021 $ | +5 210 $ |
| `GC=F` | −71 012 $ | −65 188 $ |

Sortir au pic transforme la ligne pétrole de −118 k$ en +284 k$ : tout le gain
directionnel était là, à J+7, et il a été rendu au marché en deux semaines. La
couverture actions, elle, paie dans les deux cas — elle est moins bonne au pic
(+55 k$) qu'au stop (+105 k$), parce que la baisse des actions s'est poursuivie
après le pic du pétrole. Et l'or coûte dans les deux cas, ce qui en fait le miss
le plus cher du book.

C'est la démonstration la plus nette du cours : **l'attribution ne décrit pas le
book, elle décrit le book et sa règle de sortie.**

### Ce que l'attribution dit de l'idée

La ligne qui porte le scénario — la vue directionnelle sur le brut — est la plus
négative du book quand on reste jusqu'au stop. La couverture actions, elle, paie.
Et l'or, ajouté comme couverture de confort, coûte plus que le pétrole ne
rapporte.

La leçon, rejouée chaque fois qu'on bascule l'interrupteur : **le signal de
timing vaut de l'argent, la vue directionnelle sur le brut non**. Ce qui a payé
n'est ni le pétrole ni l'or : c'est l'architecture du book, et le fait d'en être
sorti à temps.

### La validation des prévisions

Sur la même fenêtre, le scorecard donne : accord de signe 5 sur 6 (net du
drift), erreur de timing du pic de 1 jour en médiane, amplitude réalisée de
+18,46 % sur le Brent pour +5 % prévus — un facteur 3,69 —, et un miss : l'or,
qui a corrigé de −3,46 % pendant que le dollar et les taux réels montaient.

Le détail ligne par ligne vaut d'être lu, parce qu'il montre que « sous-estimé »
n'est pas un mot vague :

| Ligne | Amplitude prévue | Réalisée | Ratio | Pic prévu | Pic réel | Erreur |
|---|---|---|---|---|---|---|
| `BZ=F` | +5,0 % | +18,46 % | 3,69 | J+7 | J+8 | +1 j |
| `DBC` | +3,0 % | +5,66 % | 1,89 | J+7 | J+8 | +1 j |
| `DX-Y.NYB` | +2,0 % | +2,60 % | 1,30 | J+7 | J+8 | +1 j |
| `TLT` | +2,0 % | +1,72 % | 0,86 | J+7 | J+8 | +1 j |
| `HYG` | +0,5 % | +0,82 % | 1,64 | J+7 | J+21 | +14 j |
| `GC=F` | +3,0 % | −3,46 % | −1,15 | J+7 | J+8 | +1 j |

Le timing était bon — un jour d'écart partout, sauf le crédit HY dont le pic est
arrivé trois semaines plus tard. Les niveaux étaient trop prudents. Une ligne
était à l'envers. Trois constats distincts, qui appellent trois corrections
distinctes.

### La révision 2, publiée le 28 août

Le Brent : amplitude passée en grille `[0,05 ; 0,10 ; 0,185]`, fenêtre de pic
`[7 ; 9]`, reversion −6,5 % en 14 jours au lieu de −3 % en 21, choc d'IV porté à
+14 points, confiance abaissée de 0,60 à 0,55. La note est explicite : « le
signal de timing est conservé, le niveau non ».

L'or : sens inversé (`sign = -1`), amplitude 4 %, pic J+15, reversion −2 % en
25 jours. La note dit pourquoi : « l'or n'est pas la couverture d'un choc
d'offre quand le dollar et les taux réels montent ».

Rien de la révision 1 n'a été effacé. Un backtest dont la fenêtre précède le
28 août voit toujours r1 ; un backtest qui inclut le 28 voit r2, et re-entre —
c'est exactement ce qui explique l'écart entre les deux dernières lignes du
tableau de résultats.

### Ce qu'il faut retenir de l'exercice

1. Le score n'est pas le résultat. Un P&L de +1,55 % avec une attribution
   concentrée sur une ligne et une sortie à J+7 est un résultat fragile, même
   positif.
2. La règle de sortie fait partie de la stratégie. Elle change le signe du P&L
   et le signe de l'attribution, à entrée identique.
3. La fenêtre fait partie de la question. Un chiffre sans date de fin n'est pas
   reproductible.
4. Une prévision se corrige en trois dimensions distinctes : le sens, le niveau,
   le timing. Les confondre empêche d'apprendre.
5. Le registre est la mémoire du desk. Sans lui, la révision 2 n'est qu'une
   opinion de plus.

## Module 15 — Les pièges classiques

### 1. La fuite d'information

Symptôme : un backtest trop beau, qui entre exactement au bon moment. Cause
presque toujours : une lecture du futur — une moyenne calculée sur la fenêtre
entière, un paramètre calé sur le résultat, une prévision révisée avant sa date
de publication. Contre-mesure : `get_forecast` est point-in-time par
construction ; tout ce qui ne passe pas par lui doit être vérifié à la main.

### 2. Le dénominateur de l'exposition

```python
# Faux : la somme des poids signés s'effondre dès qu'une ligne est vendeuse
total = sum(w for w in book.values())
# Juste : l'exposition brute
total = sum(abs(w) for w in book.values())
```

### 3. `order_target_percent` sur une option

Le pourcentage est calculé en notionnel puis arrondi au contrat, avec un
avertissement. Sur une option, la question utile est le nombre de contrats :
`order(call, 10)`.

### 4. `handle_data` qui ne tourne jamais

Si une fonction est planifiée et qu'elle s'exécute, `handle_data` est ignoré
pour ce bar. Les deux formes sont exclusives dans la pratique : choisir l'une.

### 5. Les frais sur les contrats d'options

Une stratégie d'options sur ETF dont les frais sont calculés en parts plutôt
qu'en contrats perd 100× trop. Le moteur le fait correctement via
`effective_option_contract_size` ; une stratégie qui passe par
`set_commission(per_contract=…)` doit savoir que le diviseur est appliqué avant.

### 6. Les positions ouvertes en fin de fenêtre

Un P&L latent entre dans le résultat final. Le journal le signale ; il faut le
lire. Comparer deux stratégies dont l'une finit plate et l'autre pleine, c'est
comparer un résultat et une valorisation.

### 7. Les strikes non arrondis

Construire un strike à la main sans passer par `option_contract` ou
`round_strike` produit un contrat non négociable. Les structures du catalogue
arrondissent l'écartement sur un multiple du pas : ne pas le faire casse la
symétrie d'un butterfly.

### 8. Le choc d'IV en multiplicateur

`iv_shift` est additif en points, pas multiplicatif. Passer 0,10 à la place d'un
régime de 1,10 ne décale pas la surface de 10 %, il la décale de 10 points. La
différence est considérable sur une option OTM — le module 8 la chiffre.

### 9. Le Sharpe lu sans son `risk_free`

Voir module 13. Le même backtest affiche deux Sharpe selon la valeur du taux, et
le payload renvoie celui qui a été utilisé.

### 10. Le scorecard sans dénominateur

Un taux de réussite de 83 % sur 6 lignes et 4 lignes hors univers n'est pas la
même chose que 83 % sur 10 lignes testables. `evaluable_total` et
`out_of_universe_total` sont là pour ça.

> **Règle de la maison.** Chaque piège de cette liste a été rencontré pour de
> vrai. La règle n'est pas « faites attention » : c'est « relisez le journal
> avant de relire les métriques ».

[[PAGEBREAK]]
## Module 16 — La boucle mensuelle et la phase 2

### Les cinq étapes, dans cet ordre

La boucle n'est pas une checklist de confort : c'est ce qui transforme un
backtest en méthode. Chaque mois, dans cet ordre.

**1. Rejouer** les prévisions publiées sur données réelles :

```
python -m shockdesk.cli scenarios --name global-macro
```

**2. Corriger par révision.** Amplitude en grille plutôt qu'en chiffre, fenêtre
de pic plutôt qu'un jour, choc d'IV. Une révision par correction, datée.

**3. Recalibrer** `config/calibration.json` : niveaux de référence, volatilités
réalisées, bêtas, IV de base. Le fichier a priorité sur les valeurs par défaut du
code, et sa note est affichée dans l'interface.

**4. Comparer** chaque stratégie de scénario au momentum de référence sur la
même fenêtre. Ce qui ne bat pas la référence ne passe pas en phase 2. La
stratégie `us-equities-momentum.py` existe pour ça : un momentum 6-1 mensuel
avec filtre de tendance, sans aucune vue de scénario.

**5. Journaliser** les misses dans la note de révision. Pas dans un coin : dans
le champ `note` de la révision, qui est versionné avec le reste.

### La commande `revue`

`python -m shockdesk.cli revue --name global-macro --window 120` fait le travail
de mise en forme : elle met sous les yeux l'écart entre ce qui a été publié et ce
qui s'est passé, et propose ce qu'il faut recalibrer. Elle ne décide rien — c'est
un outil de revue, pas un arbitre.

### Un compte rendu de revue, rempli

La sortie de `revue` ne s'envoie pas telle quelle. Voici la forme du paragraphe
qui en sort, écrite à partir des mesures réelles de ce cours. C'est un modèle à
recopier, pas un texte à admirer.

> **Revue de septembre 2026 — scénario `shocklab-2026-07-oil`.**
>
> *Fenêtre.* 01/07 → 28/08/2026, univers `global-macro`, 25,5 M$, données
> synthétiques (le dire est obligatoire).
>
> *Prévisions.* 10 lignes publiées, 6 comptées (r1, hors benchmark), 0 hors
> univers. Signe : 5 sur 6. Timing : 1 jour d'écart en médiane. Amplitude :
> ×3,69 sur le Brent, ×1,89 sur `DBC`, ×0,86 sur `TLT`. Miss : `GC=F`, à
> l'envers.
>
> *Résultat.* Sortie au pic : +395 919 $ (+1,55 %), fenêtre close au 22/07.
> Sortie au stop : −4 054 $ (−0,02 %), fenêtre close au 05/08. Sur la fenêtre
> complète, la ré-entrée r2 du 28/08 laisse 7 positions ouvertes pour −9 685 $
> de latent.
>
> *Attribution.* La ligne pétrole passe de −118 k$ (stop) à +284 k$ (pic). La
> couverture actions paie dans les deux cas (+105 k$ / +55 k$). L'or coûte dans
> les deux cas (−65 k$ / −71 k$).
>
> *Décisions.* (1) Publier la révision 2 du Brent : amplitude en grille, pic en
> fenêtre, reversion plus rapide. (2) Publier la révision 2 de l'or : sens
> inversé. (3) Recalibrer `ann_vol` du Brent à la hausse — la vol réalisée sur
> 21 jours est de 24,4 % contre 34 % calibrés, le régime tombe à 0,72 et
> sous-évalue la surface. (4) Ne pas passer en phase 2 : le book ne bat pas le
> momentum de référence sur la fenêtre, l'alpha est de −1,0 %.
>
> *À trancher à la prochaine revue.* Le signal de pic comme règle de sortie
> systématique, testé sur plus d'un scénario.

Quatre propriétés de ce texte. Chaque affirmation porte un chiffre ou une date.
Les décisions sont numérotées et chacune a un verbe. Ce qui n'est pas tranché
est dit, et daté de la prochaine revue. La provenance des données est écrite
dans la première ligne — sans elle, tout le reste est invérifiable.

### Ce qui manque pour trader sérieusement

La feuille de route est explicite, et il faut la lire comme une liste de
limites, pas comme une promesse.

| Bloc | Manque principal |
|---|---|
| Données | Chaîne d'options réelle au lieu de la surface paramétrique, smile calé par sous-jacent, stockage local des historiques, rolls de contrats |
| Moteur | Barres intraday et exécution au VWAP, collatéral et appels de marge, coût de financement, contraintes de liquidité, walk-forward |
| Anticipation | Grille de stress factorielle propagée à tout le book, VaR/ES par nœud, suivi du Brier score, journal des décisions |
| Desk | Comparaison côte à côte de deux stratégies, export CSV/PDF, sauvegarde des runs, authentification |

Deux de ces manques changent la lecture des résultats actuels. L'absence de
collatéral signifie qu'une position vendeuse n'immobilise rien : les structures
vendeuses sont plus attractives qu'elles ne le seraient en vrai. L'absence de
coût de financement signifie qu'un book qui dort en cash pendant trois semaines
ne gagne rien et ne coûte rien — alors qu'en vrai il coûte.

### Les idées notées, non priorisées

Trois pistes sont écrites dans la feuille de route et n'ont pas été tranchées :
le signal de pic comme règle de sortie systématique backtestée sur plusieurs
scénarios historiques plutôt que sur un seul exercice ; la vente de volatilité
après le pic (crush) plutôt que pendant, la structure et le timing n'étant pas
les mêmes ; le lien entre chaque trade et la révision de prévision qui l'a
déclenché, pour mesurer la contribution de chaque génération de prévisions.

La troisième est la plus intéressante méthodologiquement : c'est la seule qui
permettrait de répondre à la question « est-ce que nos prévisions s'améliorent ».

## Module 17 — Les trois portes d'entrée

### 1. L'URL

Pour un humain qui veut rejouer une question. L'URL de recherche porte la
stratégie, l'univers, le capital, la fenêtre, et `action=backtest` pour exécuter
au chargement. C'est la forme à coller dans un compte rendu : elle contient tout
le contexte.

```
http://localhost:8050/research/strategies/<sid>/code
    ?name=global-macro&startCapital=25500000
    &startDate=2026-07-01&endDate=2026-08-28&action=backtest
```

### 2. L'API HTTP

Pour un script ou un notebook. Mêmes noms de paramètres que l'URL.

| Route | Méthode | Rôle |
|---|---|---|
| `/` | GET | Redirige vers la première stratégie avec ses défauts |
| `/research/strategies/<sid>/code` | GET | L'interface, avec ses paramètres d'URL |
| `/health` | GET | Sonde de vie |
| `/api/universes` | GET | Univers et fiches d'actifs |
| `/api/strategies` | GET, POST | Liste ; création (`name`, `code`) |
| `/api/strategies/<sid>` | GET | Métadonnées et code |
| `/api/strategies/<sid>/code` | PUT, POST | Enregistrement du code, défauts, nom |
| `/api/backtest` | POST, GET | Exécution : `strategy_id` ou `code`, plus les paramètres d'URL |
| `/api/scenarios` | GET | Tableau d'anticipation (`name`, `asof`, `horizon`, `width`) |
| `/api/options/quote` | POST, GET | Atelier de pricing (`underlying`, `structure`, `days`, `width`, `iv_shift`, `vol_regime`, `spot`) |
| `/api/ledger` | GET, POST | Registre ; création d'une prévision |
| `/api/ledger/<fid>/revision` | POST | Ajout d'une révision datée |

```bash
curl -s -X POST http://localhost:8050/api/backtest \
  -H 'Content-Type: application/json' \
  -d '{"strategy_id":"<sid>","name":"global-macro",
       "startCapital":25500000,"startDate":"2026-07-01",
       "endDate":"2026-08-28","source":"synthetic"}'
```

Ajouter une révision sans réécrire l'historique :

```bash
curl -s -X POST http://localhost:8050/api/ledger/shocklab-2026-09-oil-roll/revision \
  -H 'Content-Type: application/json' \
  -d '{"sign":-1,"amplitude":[0.03,0.06,0.11],"peak_day":[15,22],
       "reversion":-0.02,"reversion_days":30,"iv_shift":-0.03,
       "confidence":0.45,"note":"Revue de fin septembre : amplitude en grille."}'
```

Les champs requis d'une révision sont `sign`, `amplitude`, `peak_day`. Tout le
reste a un défaut. La date est celle du jour si elle n'est pas fournie.

### 3. Le CLI

Pour les revues et les scripts sans interface.

```
python -m shockdesk.cli serve --host 0.0.0.0 --port 8050
python -m shockdesk.cli strategies
python -m shockdesk.cli backtest --strategy shock-lab-oil \
    --name global-macro --start-capital 25500000 \
    --start-date 2026-07-01 --end-date 2026-08-28 --json
python -m shockdesk.cli scenarios --name global-macro --asof 2026-08-28
python -m shockdesk.cli option-lab --underlying BZ=F --structure strangle \
    --days 30 --width 0.04 --iv-shift 0.10
python -m shockdesk.cli revue --name global-macro --window 120
```

`--strategy` accepte un UUID, un slug ou un nom de fichier. `--json` donne le
payload complet, qui est exactement celui de l'interface : la même grammaire
partout, c'est ce qui permet de passer d'une porte à l'autre sans réapprendre
les noms.

> **Règle de la maison.** Ce qui se fait dans l'interface doit pouvoir se faire
> en CLI, et inversement, avec les mêmes noms de paramètres. Une revue mensuelle
> automatisable est une revue qui a lieu.

[[PAGEBREAK]]
## Module 18 — Ateliers dirigés

Dix ateliers, du plus mécanique au plus méthodologique. Chacun se fait en moins
d'une heure et se valide par un observable précis. Les fichiers cités sont ceux
du dépôt ; aucun atelier ne demande de modifier le moteur.

### Atelier 1 — La leçon du timing

**But.** Voir de ses yeux que la règle de sortie fait le résultat.

Ouvrir `strategies/shock-lab-oil.py`, basculer `TAKE_PROFIT_AT_PEAK` de `True` à
`False`, relancer le backtest sur la fenêtre publiée, comparer le P&L figé et
l'attribution.

**On vérifie.** Le signe du P&L change à entrée identique. **Réussi quand** on
sait énoncer la date de sortie dans les deux cas et citer les deux lignes qui
portent l'écart.

### Atelier 2 — Dimensionner l'exposition

**But.** Comprendre le levier et le garde-fou du moteur.

Faire varier `BASE_EXPOSURE` de 0,40 à 2,00 par pas de 0,40 et observer le P&L,
le drawdown maximal et les avertissements de levier dans le journal.

**On vérifie.** Au-delà de 2× d'exposition brute, les ordres sont réduits et le
journal le dit. **Réussi quand** on peut expliquer pourquoi le résultat ne
continue pas de croître linéairement.

### Atelier 3 — Neutraliser le miss

**But.** Mesurer la contribution d'une ligne qu'on soupçonne.

Mettre le poids de `GC=F` à 0,00, puis à −0,10, et comparer avec l'attribution
de référence.

**On vérifie.** L'attribution par ligne change exactement du montant attendu.
**Réussi quand** on distingue l'effet de la ligne de l'effet de la
renormalisation des autres poids.

### Atelier 4 — Acheter du gamma

**But.** Passer du delta aux options.

Exécuter `strategies/long-strangle-shock.py`, puis refaire le même backtest avec
`iv_shift` de la prévision mis à zéro (via une révision de test sur une copie du
registre).

**On vérifie.** Le coût d'entrée et la valeur du book changent avec l'IV, sans
que le sous-jacent bouge. **Réussi quand** on sait dire quelle part du résultat
vient du vega et quelle part du gamma.

### Atelier 5 — Straddle contre strangle

**But.** Payer l'ATM ou ne pas le payer.

Pricer les deux structures dans l'atelier d'options sur le même sous-jacent, la
même maturité, la même largeur, et comparer prime, points morts et perte
maximale.

**On vérifie.** Le straddle coûte plus cher et gagne plus tôt. **Réussi quand**
on peut donner, en pourcentage du spot, l'écart entre les points morts des deux
structures.

### Atelier 6 — Le butterfly de timing

**But.** Transformer une prévision de pic en structure.

Exécuter `strategies/butterfly-peak.py` puis déplacer le corps du butterfly de
±2 % et observer le résultat.

**On vérifie.** Le gain dépend de la distance entre le corps et le niveau de pic
réalisé. **Réussi quand** on constate que la perte maximale reste bornée par la
prime payée, quels que soient les strikes.

### Atelier 7 — Le choc de volatilité

**But.** Isoler l'effet d'un `iv_shift`.

```
python -m shockdesk.cli option-lab --underlying BZ=F \
    --structure strangle --days 30 --width 0.04 --iv-shift 0.00
python -m shockdesk.cli option-lab --underlying BZ=F \
    --structure strangle --days 30 --width 0.04 --iv-shift 0.20
```

**On vérifie.** À +20 points, la prime double presque et l'alerte de plafond
d'IV peut apparaître. **Réussi quand** on sait que `iv_shift` est additif, et
qu'on peut expliquer pourquoi une option OTM réagit plus qu'une ATM.

### Atelier 8 — Vendre de la prime en range

**But.** Lire une structure vendeuse sans se mentir.

Exécuter `strategies/iron-condor-range.py` et relever le gain maximal, la perte
maximale et le theta net.

**On vérifie.** Le gain est borné par la prime, la perte par l'écart des ailes.
**Réussi quand** on peut énoncer le ratio perte maximale sur prime encaissée, et
dire à quel mouvement il est atteint.

### Atelier 9 — Publier une révision

**But.** Corriger sans réécrire.

Ajouter une révision à la prévision de rouleau de septembre, via l'interface ou
l'API, avec une amplitude en grille et une fenêtre de pic.

**On vérifie.** `GET /api/ledger` montre les deux révisions ; un backtest dont
la fenêtre précède la révision ne voit que la première. **Réussi quand** on peut
montrer les deux lectures point-in-time côte à côte.

### Atelier 10 — L'audit en ligne de commande

**But.** Rendre la revue automatisable.

Enchaîner `scenarios`, `revue` et un `backtest --json`, et en tirer un
paragraphe de revue : signe, timing, amplitude, attribution, décision.

**On vérifie.** Les trois sorties racontent la même histoire. **Réussi quand** le
paragraphe cite des nombres extraits des sorties, pas des impressions.

## Module 19 — Annexes

### Annexe A — Lexique de desk

| Terme | Sens |
|---|---|
| Attribution | Décomposition du P&L par ligne |
| Bêta | Sensibilité au benchmark ; ici, rapport des chargements factoriels |
| Book | Ensemble des positions à un instant |
| Carry | Ce que rapporte le temps qui passe, sans mouvement |
| Crush | Effondrement de l'IV après un événement |
| Drawdown | Perte depuis le plus haut de la courbe d'équité |
| Exposition brute | Somme des valeurs de marché en valeur absolue |
| Gamma | Sensibilité du delta au sous-jacent |
| Grille d'amplitudes | Ensemble des amplitudes d'un stress test |
| IV (volatilité implicite) | Volatilité qui reproduit le prix de marché |
| Levier | Exposition brute sur actif net |
| Line / ligne | Position sur un sous-jacent ou un contrat |
| Mark | Valorisation du book aux prix du jour |
| MFE / MAE | Excursion maximale favorable / défavorable |
| Moneyness | Rapport strike / spot |
| Notionnel | Valeur du sous-jacent couvert |
| Payoff | P&L d'une structure en fonction du spot final |
| Point mort | Niveau de sous-jacent où le payoff est nul |
| Prime | Prix payé ou encaissé à l'entrée |
| Révision | Correction datée d'une prévision publiée |
| Scorecard | Tableau de validation ex-post des prévisions |
| Skew | Pente du sourire : les puts OTM plus chers |
| Theta | Perte de valeur par jour calendaire |
| Turnover | Volume total échangé sur la période |
| Vega | Sensibilité du prix à un point de volatilité |

### Annexe B — Les valeurs par défaut et où les changer

| Valeur | Défaut | Où la changer |
|---|---|---|
| Commission par part | 0,005 $ | `set_commission(per_share=…)` |
| Commission minimale | 1,00 $ | `set_commission(min_trade_cost=…)` |
| Commission par contrat | 0,65 $ | `set_commission(per_contract=…)` |
| Slippage | 5 bps | `set_slippage(bps=…)` |
| Vente à découvert | autorisée | `settings.allow_short` |
| Levier maximal | 2,0× | `settings.max_leverage` |
| Taux sans risque | 4,1 % | `settings.risk_free` (et le pricer) |
| Jours de bourse par an | 252 | `config.TRADING_DAYS` |
| Smile / skew / terme | 0,55 / −0,25 / 0,10 | fiche d'actif, ou `calibration.json` |
| Bornes d'IV | [2 %, 400 %] | `options.iv_surface` |
| Bornes du régime de vol | [0,55 ; 2,6] | `engine.vol_regime` |
| Horizon du tableau d'anticipation | 45 jours | `horizon_days` |
| Largeur des structures | 3 % | `width` |

### Annexe C — Les fiches d'actifs de la calibration

Extrait des fiches utilisées par le générateur synthétique et le pricer.

| Actif | Type | `s0` | Vol | `iv_base` | Options |
|---|---|---|---|---|---|
| `BZ=F` Brent | future | 84,95 | 34 % | 36 % | oui (1 000 bbl) |
| `CL=F` WTI | future | 80,50 | 35 % | 37 % | oui (1 000 bbl) |
| `^GSPC` S&P 500 | index | 6 420 | 15,0 % | 16,5 % | oui (100) |
| `SPY` | etf | 642,0 | 15,0 % | 16,5 % | oui (100) |
| `QQQ` | etf | 561,0 | 20,0 % | 22,5 % | oui (100) |
| `NVDA` | equity | 176,0 | 42,0 % | 44,0 % | oui (100) |
| `TLT` | etf | 88,20 | 15,0 % | dérivée | oui (100) |
| `HYG` | etf | 78,10 | 5,5 % | dérivée | oui (100) |
| `GC=F` or | future | 3 350 | 14,5 % | 17,5 % | oui (100 oz) |
| `DBC` | etf | 21,10 | 18,5 % | dérivée | oui (100) |
| `DX-Y.NYB` | index | 97,80 | 7,2 % | — | non |
| `^VIX` | index | 16,40 | 85,0 % | — | non |

« Dérivée » signifie `ann_vol × 1,12`. La colonne `s0` est le niveau de la
calibration à la date d'ancrage du 15 juillet 2026, pas un prix courant.

### Annexe D — Checklists

**Publier une prévision.** Le sous-jacent est dans un univers existant ; le sens
et l'amplitude sont écrits ; l'amplitude est une grille ; le pic est une
fenêtre ; la reversion est un niveau signé ; le choc d'IV est en points ; la
confiance est justifiée ; la date d'arrêt est fixée ex-ante ; la note dit
pourquoi.

**Relire un backtest.** La provenance des données est lue ; le journal est lu
avant les métriques ; l'attribution est commentée ligne par ligne ; le turnover
et le coût moyen sont rapportés au résultat ; les positions ouvertes en fin de
fenêtre sont signalées ; le Sharpe est lu avec son `risk_free` ; la comparaison
au benchmark est faite.

**Préparer une revue mensuelle.** Les prévisions publiées sont rejouées sur
données réelles ; le scorecard est lu avec son dénominateur ; les misses sont
écrits dans une note de révision ; la calibration est mise à jour ; chaque
stratégie est comparée à la référence momentum ; ce qui ne bat pas la référence
est dit à voix haute.

### Annexe E — Les chargements factoriels du book

Les sept lignes du `global-macro` et leurs chargements sur les sept facteurs.
C'est la table qui permet de raisonner sur les corrélations sans lancer de
backtest : deux lignes dont les chargements se ressemblent sont une seule
position déguisée en deux.

| Actif | SPX | OIL | RATES | GOLD | USD | CREDIT |
|---|---|---|---|---|---|---|
| `BZ=F` | −0,05 | **1,00** | — | — | −0,10 | — |
| `^GSPC` | **1,00** | −0,25 | −0,35 | — | −0,15 | +0,35 |
| `TLT` | +0,15 | — | **−1,00** | — | — | +0,25 |
| `GC=F` | +0,05 | — | −0,25 | **1,00** | −0,35 | — |
| `DX-Y.NYB` | — | — | +0,30 | — | **1,00** | — |
| `HYG` | +0,35 | — | −0,20 | — | — | **1,00** |
| `DBC` | +0,20 | +0,55 | — | +0,20 | −0,20 | — |

Deux lectures utiles. Le Brent et le `DBC` partagent le facteur `OIL` (1,00 et
0,55) : la ligne matières premières est un demi-pari pétrolier, pas une
diversification. Le crédit HY porte +0,35 de `SPX` et +1,00 de `CREDIT` : dans
un choc d'offre qui fait baisser les actions, la ligne crédit n'est pas neutre.

Le facteur `VOL` (volatilité 80 % annuelle) n'apparaît dans aucune de ces sept
lignes : il est porté par `^VIX`, qui n'est pas dans l'univers. Un book qui
voudrait se couvrir en volatilité ne peut pas le faire dans le `global-macro` —
c'est le rôle des structures d'options.

### Annexe F — Où lire la suite

| Document | Contenu |
|---|---|
| `README.md` | Démarrage, API, stratégies livrées, résultat de l'exercice |
| `ROADMAP.md` | Ce qui est fait, la boucle mensuelle, la phase 2 |
| `docs/guide-utilisation.md` | Prise en main détaillée, glossaire, règles d'or |
| `docs/entrainement-progressif.md` | Les dix ateliers en version longue |
| `docs/journal-de-bord-recherche.md` | Le journal de recherche, décision par décision |

### Un dernier mot

Rien dans ce cours n'est une vérité de marché. Les sept facteurs sont une
hypothèse, la surface d'IV est paramétrique, le générateur est un jouet calibré,
et l'exercice de juillet 2026 est un seul épisode. Ce qui est réel, c'est la
méthode : publier avant de savoir, mesurer net du marché, corriger par révision,
et garder la trace. C'est cela, un desk — et c'est portable ailleurs.

### Colophon

Ce cours est écrit en markdown (`docs/cours-shockdesk.md`) et rendu en PDF
(`docs/cours-shockdesk.pdf`) : les deux fichiers sont versionnés ensemble, et le
markdown est la source. Le sommaire est paginé à la deuxième passe de rendu, ce
qui explique que les numéros de page du sommaire soient exacts et non
approximatifs.

Toutes les mesures citées — P&L, attributions, métriques, primes d'options,
grilles d'amplitudes — ont été produites le 30 août 2026 par le code du dépôt,
sur l'univers `global-macro` et le jeu de données synthétique, avec les
commandes indiquées. Elles sont reproductibles à l'identique tant que la
calibration et le registre ne changent pas ; dès qu'une révision est publiée ou
qu'un `s0` est recalibré, elles changent, et c'est voulu.

Ce document ne contient aucun conseil en investissement. Les structures, les
sous-jacents et les scénarios cités sont des objets pédagogiques.
