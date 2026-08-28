"""Momentum cross-actif — la stratégie de référence (benchmark de sanity).

Pas de scénario, pas d'options : chaque mois, on achète les N meilleures
performances à 3 mois de l'univers, à parts égales, et on se met en cash si le
benchmark est sous sa moyenne mobile 200 jours.

Son rôle dans ShockDesk : servir de point de comparaison. Une stratégie de
scénario qui ne bat pas ce momentum-là sur la même fenêtre n'apporte rien —
c'est le premier test à passer avant de parler d'alpha.

Pour que la comparaison soit loyale, la référence reste toujours investie :
sans sélection éligible, elle se replie sur le benchmark au lieu d'aller en
cash. Une référence qui passe son temps en cash ne mesure rien.
"""

# --- Paramètres --------------------------------------------------------------
LOOKBACK = 126             # fenêtre de momentum (~6 mois de séances)
SKIP = 21                  # on saute le dernier mois (effet de reversal court terme)
TOP_N = 3                  # nombre de lignes détenues
TREND_MA = 200             # filtre de tendance sur le benchmark
ASSET_TREND_FILTER = False # filtre par ligne : dégradait la référence ici
WEIGHT_CAP = 0.30          # poids maximum d'une ligne
CASH_BUFFER = 0.02         # poche de cash conservée pour les frais


def initialize(context):
    bench = _benchmark()
    context.pool = []
    for s in CANDIDATES:
        try:
            a = symbol(s)
        except KeyError:
            continue                      # absent de l'univers courant
        if a != bench:
            context.pool.append(a)
    log.info(f"Pool momentum : {', '.join(context.pool)}")
    schedule_function(rebalance, date_rules.month_start())


# Candidats : seuls ceux présents dans l'univers courant sont retenus.
CANDIDATES = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "XLE", "XLF", "TLT",
              "BZ=F", "GC=F", "HYG", "DBC", "XOP", "CL=F", "UNG", "IEF"]


def _benchmark():
    try:
        return symbol("SPY")
    except KeyError:
        return None


def _momentum(data, asset):
    """Momentum 6-1 ajusté du risque : performance sur 6 mois (dernier mois
    exclu) divisée par la volatilité de la période.

    Le classement brut est dominé par les lignes les plus volatiles, qui
    apparaissent en tête à chaque retournement. Diviser par la vol ne change pas
    l'idée, ça évite de confondre « ça monte » et « ça bouge »."""
    h = data.history(asset, "close", LOOKBACK + 1)
    if h is None or len(h) < LOOKBACK // 2:
        return None
    perf = float(h.iloc[-1 - SKIP] / h.iloc[0] - 1.0)
    vol = float(h.pct_change().std())
    return perf / vol if vol > 0 else 0.0


def _fmt(score):
    """Score = momentum / vol journalière. Grandeur sans unité : on l'affiche
    telle quelle, ce n'est pas un nombre de sigmas."""
    return f"{score:+.1f}"


def rebalance(context, data):
    bench = _benchmark()
    trend_ok = True
    if bench is not None:
        hb = data.history(bench, "close", TREND_MA)
        if hb is not None and len(hb) >= 20:
            trend_ok = bool(hb.iloc[-1] > hb.mean())

    scores = {}
    for a in context.pool:
        m = _momentum(data, a)
        if m is not None:
            scores[a] = m
    if not scores:
        return

    # Deux filtres avant de prendre une ligne :
    #   1. momentum positif (sinon on achète une baisse qui dure) ;
    #   2. prix au-dessus de sa propre moyenne mobile — sans ça, le momentum
    #      6-1 achète des sommets locaux et se fait retourner à chaque
    #      rééquilibrage (c'est le crash de momentum classique).
    eligibles = {}
    for a, m in scores.items():
        if m <= 0:
            continue
        if ASSET_TREND_FILTER:
            h = data.history(a, "close", TREND_MA)
            if h is not None and len(h) >= 20 and h.iloc[-1] < h.mean():
                continue
        eligibles[a] = m
    picks = sorted(eligibles, key=eligibles.get, reverse=True)[:TOP_N] if trend_ok else []
    fallback = (not picks) and bench is not None
    weight = min(1.0 / max(len(picks), 1), WEIGHT_CAP)

    for a in list(context.portfolio.positions):
        if a not in picks:
            pos = context.portfolio.positions[a]
            if abs(pos.amount) > 1e-9:
                order(a, -pos.amount, reason="sortie momentum")
    for a in picks:
        order_target_percent(a, weight, reason="momentum mensuel")
    if fallback:
        order_target_percent(bench, 1.0 - CASH_BUFFER, reason="repli benchmark")

    record(n_picks=len(picks) or (-1 if fallback else 0),
           best_score=max(scores.values()),
           worst_score=min(scores.values()),
           trend=1.0 if trend_ok else 0.0)
    # Le benchmark de sanity doit être lisible : on trace aussi le benchmark.
    if bench is not None:
        hb = data.history(bench, "close", 2)
        if hb is not None and len(hb) == 2:
            record(benchmark=float(hb.iloc[-1] / hb.iloc[0] - 1.0))
    log.info(f"Rééquilibrage : tendance {'haussière' if trend_ok else 'baissière'} · "
             f"sélection "
             + (", ".join(f"{a} ({_fmt(eligibles[a])})" for a in picks)
                if picks else f"repli {bench}"))
