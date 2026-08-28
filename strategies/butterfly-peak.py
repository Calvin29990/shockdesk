"""Butterfly centré sur le pic prévu — le trade du TIMING.

Un modèle de choc ne donne pas un niveau fiable, il donne une date de pic. Le
butterfly est la structure qui monetise exactement ça : corps sur le niveau
anticipé au jour de pic, ailes de part et d'autre. Si le pic tombe là où on l'a
dit, on sort au corps et la structure vaut son maximum ; si le sous-jacent part
au-delà des ailes, la perte est bornée à la prime payée.

Coût faible, gain plafonné : c'est l'expression la plus directe d'une vue de
timing, et la moins exposée à l'erreur d'amplitude.
"""

# --- Paramètres à recalibrer -------------------------------------------------
UNDERLYING = "BZ=F"
WING_WIDTH = 0.06          # écart des ailes au corps, en fraction du corps
DAYS = 21                  # maturité (doit couvrir le jour de pic prévu)
PREMIUM_BUDGET = 0.01      # budget de prime, en fraction de l'actif net
MAX_NOTIONAL_PCT = 0.25    # plafond de notionnel sous-jacent, en fraction de l'actif net
CENTER_ON_PEAK = True      # True = corps sur le niveau de pic prévu
                           # False = corps ATM (butterfly « pin » classique)


def initialize(context):
    context.asset = symbol(UNDERLYING)
    context.legs = []
    context.entry = None
    context.traded = set()
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
            spot = data.current(UNDERLYING, "close")
            body = min(context.legs, key=lambda c: abs(c.strike - spot)).strike
            log.info(f"Sortie butterfly J+{held} ({why}) — sous-jacent {spot:.2f} "
                     f"vs corps {body:.2f} — P&L latent {pnl:+,.0f}")
            _flat(context, f"sortie {why}")
            record(flies=0.0)
            return

    if context.entry is None and f is not None:
        key = (f.id, f.rev)
        if key in context.traded:
            record(flies=0.0)
            return
        context.traded.add(key)

        spot = data.current(UNDERLYING, "close")
        if not spot:
            record(flies=0.0)
            return
        center = spot * (1 + f.amp_base * f.sign) if CENTER_ON_PEAK else spot
        body = option_contract(UNDERLYING, "call", strike=None,
                               moneyness=center / spot, days=DAYS)
        wing = body.strike * WING_WIDTH
        low = option_contract(UNDERLYING, "call", strike=body.strike - wing, days=DAYS)
        high = option_contract(UNDERLYING, "call", strike=body.strike + wing, days=DAYS)

        p_low = data.current(low, "close") or 0.0
        p_body = data.current(body, "close") or 0.0
        p_high = data.current(high, "close") or 0.0
        unit = p_low - 2 * p_body + p_high
        if unit <= 0:
            log.info("Butterfly à prime négative ou nulle : abandon.")
            record(flies=0.0)
            return
        pv = context.portfolio.portfolio_value
        qty = int(min(pv * PREMIUM_BUDGET // unit,
                      pv * MAX_NOTIONAL_PCT / body.strike))
        if qty < 1:
            log.info("Budget de prime insuffisant pour un butterfly.")
            record(flies=0.0)
            return

        order(low, qty, reason=f"butterfly aile basse r{f.rev}")
        order(body, -2 * qty, reason=f"butterfly corps r{f.rev}")
        order(high, qty, reason=f"butterfly aile haute r{f.rev}")
        context.legs = [low, body, high]
        context.entry = today
        log.info(f"Entrée butterfly {UNDERLYING} : {qty} unités, corps {body.strike:.2f} "
                 f"(pic prévu à {center:.2f}, J+{f.peak_base:.0f}), ailes "
                 f"{low.strike:.2f}/{high.strike:.2f}, prime {unit * qty:,.0f}, "
                 f"gain max {(wing - unit) * qty:,.0f}.")
        record(flies=float(qty))
        return

    record(flies=0.0)
