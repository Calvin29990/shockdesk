"""Long strangle sur scénario de choc — trader l'amplitude, pas le niveau.

La logique desk : un modèle de choc vend du TIMING et une amplitude, jamais un
niveau. Quand l'amplitude attendue par la prévision dépasse ce que paie la
volatilité implicite, on achète du gamma des deux côtés (call OTM + put OTM) :
on est payé si ça bouge fort, dans un sens comme dans l'autre.

Sortie au jour de pic du modèle, au stop calendar, ou à l'échéance — le premier
des trois.

MODE = "strangle" | "straddle" : le straddle paie l'ATM, donc plus de gamma pour
plus de prime. À comparer dans l'onglet Backtest.
"""

# --- Paramètres à recalibrer -------------------------------------------------
UNDERLYING = "BZ=F"       # sous-jacent du scénario
MODE = "strangle"         # "strangle" (OTM) ou "straddle" (ATM)
WIDTH = 0.05              # écart des strikes au spot (strangle)
DAYS = 30                 # maturité des contrats
PREMIUM_BUDGET = 0.015    # budget de prime, en fraction de l'actif net
MAX_NOTIONAL_PCT = 0.25   # plafond de notionnel sous-jacent, en fraction de l'actif net
MIN_EDGE = 1.00           # amplitude attendue / prime payée (% du spot) minimum
MAX_VOL_REGIME = 2.2      # au-delà, la surface est déjà trop chère


def initialize(context):
    context.symbol_asset = symbol(UNDERLYING)
    context.entry = None
    context.legs = []
    context.traded = set()
    context.budget_qty = 0
    schedule_function(trade, date_rules.every_day())


def _flat(context, reason):
    for c in list(context.legs):
        pos = context.portfolio.positions.get(c)
        if pos is not None and abs(pos.amount) > 1e-9:
            order(c, -pos.amount, reason=reason)
    context.legs = []
    context.entry = None


def trade(context, data):
    today = get_datetime().date()
    f = get_forecast(UNDERLYING)

    # --- sortie ------------------------------------------------------------ #
    if context.entry is not None:
        held = (today - context.entry).days
        peak = int(round(f.peak_base)) if f else 7
        expiry_hit = any(pd.Timestamp(c.expiry).date() <= today for c in context.legs)
        stop_hit = bool(f and f.stop_date and today >= pd.Timestamp(f.stop_date).date())
        if held >= peak or stop_hit or expiry_hit:
            why = ("échéance" if expiry_hit else
                   "stop calendar" if stop_hit else "pic modèle")
            pnl = sum(context.portfolio.positions[c].unrealized_pnl
                      for c in context.legs if c in context.portfolio.positions)
            log.info(f"Sortie strangle J+{held} ({why}) — P&L latent {pnl:+,.0f}")
            _flat(context, f"sortie {why}")
            record(structures=0.0, edge=0.0)
            return

    # --- entrée ------------------------------------------------------------ #
    if context.entry is None and f is not None:
        key = (f.id, f.rev)
        if key in context.traded:
            record(structures=0.0, edge=0.0)
            return
        context.traded.add(key)

        spot = data.current(UNDERLYING, "close")
        iv = get_iv(UNDERLYING, 1.0, DAYS)
        regime = vol_regime(UNDERLYING)
        expected = f.amp_base
        if not spot:
            record(structures=0.0, edge=0.0)
            return
        if regime > MAX_VOL_REGIME:
            log.info(f"Pas d'entrée : régime de vol à {regime:.2f}x, surface trop chère.")
            record(structures=0.0, edge=0.0)
            return

        if MODE == "straddle":
            call = option_contract(UNDERLYING, "call", moneyness=1.0, days=DAYS)
            put = option_contract(UNDERLYING, "put", moneyness=1.0, days=DAYS)
        else:
            call = option_contract(UNDERLYING, "call", moneyness=1.0 + WIDTH, days=DAYS)
            put = option_contract(UNDERLYING, "put", moneyness=1.0 - WIDTH, days=DAYS)

        pc = data.current(call, "close") or 0.0
        pp = data.current(put, "close") or 0.0
        unit = pc + pp
        if unit <= 0:
            record(structures=0.0, edge=0.0)
            return

        # Le bon comparateur d'un strangle n'est pas le mouvement implicite ATM
        # mais la prime payée : on gagne si le mouvement dépasse ce qu'on a payé.
        paid = unit / spot
        implied = iv * math.sqrt(DAYS / 365.0)
        edge = expected / paid if paid > 0 else 0.0
        if edge < MIN_EDGE:
            log.info(f"Pas d'entrée : amplitude attendue {expected:.1%} vs prime payée "
                     f"{paid:.1%} du spot (edge {edge:.2f} < {MIN_EDGE:.2f}). "
                     f"Mouvement implicite ATM {implied:.1%} pour mémoire.")
            record(structures=0.0, edge=edge)
            return

        pv = context.portfolio.portfolio_value
        qty = int(min(pv * PREMIUM_BUDGET // unit,
                      pv * MAX_NOTIONAL_PCT / spot))
        if qty < 1:
            log.info("Budget de prime ou plafond de notionnel insuffisant pour un contrat.")
            record(structures=0.0, edge=edge)
            return

        order(call, qty, reason=f"{MODE} scénario r{f.rev}")
        order(put, qty, reason=f"{MODE} scénario r{f.rev}")
        context.legs = [call, put]
        context.entry = today
        log.info(f"Entrée {MODE} {UNDERLYING} : {qty} paires, strikes "
                 f"{put.strike:.2f}/{call.strike:.2f}, échéance {call.expiry}, "
                 f"prime {unit * qty:,.0f} ({unit * qty / context.portfolio.portfolio_value:.2%} "
                 f"de l'actif), notionnel {qty * spot:,.0f}. "
                 f"Amplitude attendue {expected:.1%} vs prime payée {paid:.1%} "
                 f"= edge {edge:.2f}. IV {iv:.1%}, régime {regime:.2f}x.")
        record(structures=float(qty), edge=edge)
        return

    record(structures=0.0, edge=0.0)
