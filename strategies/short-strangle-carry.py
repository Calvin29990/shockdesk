"""Short strangle de carry — vendre la prime quand il ne se passe rien.

Le miroir du long strangle : quand aucune prévision de choc n'est active et que
la volatilité réalisée est dans son régime normal, la prime des ailes OTM est
structurellement plus chère que le mouvement qui suit. On vend le call et le put
OTM, on encaisse le theta, on roule à l'échéance.

⚠️ Risque illimité sur les deux ailes. Le moteur ne modélise pas le collatéral
de marge : la seule borne est le plafond de levier (`max_leverage`). En
production, dimensionner cette stratégie sur le collatéral réellement exigé.
"""

# --- Paramètres à recalibrer -------------------------------------------------
UNDERLYING = "SPY"
WIDTH = 0.04              # écart des ailes au spot
DAYS = 30                 # maturité vendue
PREMIUM_TARGET = 0.02     # prime visée, en fraction de l'actif net
MAX_NOTIONAL_PCT = 0.30   # plafond de notionnel sous-jacent, en fraction de l'actif net
MAX_VOL_REGIME = 1.10     # au-delà, on ne vend pas : le régime est anormal
STOP_LOSS_MULT = 2.0      # on rachète si la prime a été multipliée par ce facteur
EXIT_IF_FORECAST = True   # on déboucle dès qu'une prévision de choc apparaît


def initialize(context):
    context.asset = symbol(UNDERLYING)
    context.legs = {}
    context.entry = None
    context.entry_premium = 0.0
    schedule_function(trade, date_rules.every_day())


def _flat(context, reason):
    for c, _ in list(context.legs.items()):
        pos = context.portfolio.positions.get(c)
        if pos is not None and abs(pos.amount) > 1e-9:
            order(c, -pos.amount, reason=reason)
    context.legs = {}
    context.entry = None
    context.entry_premium = 0.0


def trade(context, data):
    today = get_datetime().date()
    f = get_forecast(UNDERLYING)

    # --- gestion de la position ouverte ------------------------------------ #
    if context.entry is not None:
        expiry_hit = any(pd.Timestamp(c.expiry).date() <= today
                         for c in context.legs)
        mark = sum((context.portfolio.positions[c].last_sale_price * abs(q))
                   for c, q in context.legs.items()
                   if c in context.portfolio.positions)
        stop_hit = (context.entry_premium > 0
                    and mark > STOP_LOSS_MULT * context.entry_premium)
        forecast_hit = EXIT_IF_FORECAST and f is not None
        if expiry_hit or stop_hit or forecast_hit:
            why = ("échéance" if expiry_hit else
                   "stop-loss prime" if stop_hit else "prévision de choc active")
            log.info(f"Sortie short strangle ({why}) — P&L "
                     f"{context.portfolio.pnl:+,.0f} cumulés")
            _flat(context, f"sortie {why}")
            record(short_premium=0.0, vol_regime=0.0)
            return

    # --- recherche d'entrée ------------------------------------------------ #
    if context.entry is None:
        if f is not None:
            record(short_premium=0.0, vol_regime=vol_regime(UNDERLYING))
            return
        regime = vol_regime(UNDERLYING)
        if regime > MAX_VOL_REGIME:
            record(short_premium=0.0, vol_regime=regime)
            return

        spot = data.current(UNDERLYING, "close")
        call = option_contract(UNDERLYING, "call", moneyness=1.0 + WIDTH, days=DAYS)
        put = option_contract(UNDERLYING, "put", moneyness=1.0 - WIDTH, days=DAYS)
        pc = data.current(call, "close") or 0.0
        pp = data.current(put, "close") or 0.0
        unit = pc + pp
        if unit <= 0 or not spot:
            record(short_premium=0.0, vol_regime=regime)
            return

        pv = context.portfolio.portfolio_value
        qty = int(min(pv * PREMIUM_TARGET // unit,
                      pv * MAX_NOTIONAL_PCT / spot))
        if qty < 1:
            record(short_premium=0.0, vol_regime=regime)
            return

        order(call, -qty, reason="short strangle aile haute")
        order(put, -qty, reason="short strangle aile basse")
        context.legs = {call: -qty, put: -qty}
        context.entry = today
        context.entry_premium = unit * qty
        log.info(f"Vente strangle {UNDERLYING} : {qty} paires, ailes "
                 f"{put.strike:.2f}/{call.strike:.2f}, échéance {call.expiry}, "
                 f"prime encaissée {unit * qty:,.0f}, régime de vol {regime:.2f}x, "
                 f"IV {get_iv(UNDERLYING, 1.0, DAYS):.1%}.")
        record(short_premium=unit * qty, vol_regime=regime)
        return

    record(short_premium=context.entry_premium, vol_regime=vol_regime(UNDERLYING))
