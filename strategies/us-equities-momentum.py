"""Momentum cross-actif — la stratégie de référence (benchmark de sanity).

Pas de scénario, pas d'options : chaque mois, on achète les N meilleures
performances à 3 mois de l'univers, à parts égales, et on se met en cash si le
benchmark est sous sa moyenne mobile 200 jours.

Son rôle dans ShockDesk : servir de point de comparaison. Une stratégie de
scénario qui ne bat pas ce momentum-là sur la même fenêtre n'apporte rien —
c'est le premier test à passer avant de parler d'alpha.
"""

# --- Paramètres --------------------------------------------------------------
LOOKBACK = 126             # fenêtre de momentum (~6 mois de séances)
SKIP = 21                  # on saute le dernier mois (effet de reversal court terme)
TOP_N = 3                  # nombre de lignes détenues
TREND_MA = 200             # filtre de tendance sur le benchmark
WEIGHT_CAP = 0.30          # poids maximum d'une ligne


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
    """Momentum 6-1 : performance sur 6 mois, dernier mois exclu."""
    h = data.history(asset, "close", LOOKBACK + 1)
    if h is None or len(h) < LOOKBACK // 2:
        return None
    return float(h.iloc[-1 - SKIP] / h.iloc[0] - 1.0)


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

    # On ne détient que des momentum positifs : sinon, cash.
    positives = {a: m for a, m in scores.items() if m > 0}
    picks = sorted(positives, key=positives.get, reverse=True)[:TOP_N] if trend_ok else []
    weight = min(1.0 / max(len(picks), 1), WEIGHT_CAP)

    for a in list(context.portfolio.positions):
        if a not in picks:
            pos = context.portfolio.positions[a]
            if abs(pos.amount) > 1e-9:
                order(a, -pos.amount, reason="sortie momentum")
    for a in picks:
        order_target_percent(a, weight, reason="momentum mensuel")

    record(n_picks=len(picks),
           best_score=max(scores.values()),
           worst_score=min(scores.values()),
           trend=1.0 if trend_ok else 0.0)
    log.info(f"Rééquilibrage : tendance {'haussière' if trend_ok else 'baissière'} · "
             f"sélection {', '.join(f'{a} ({scores[a]:+.1%})' for a in picks) or 'cash'}")
