"""Iron condor — le range borné.

Même idée que le short strangle (vendre de la prime quand aucune prévision de
choc n'est active), mais avec des ailes achetées qui bornent le risque : put
spread vendeur + call spread vendeur. On gagne moins, on dort mieux, et surtout
la perte maximale est connue — ce qui permet de dimensionner sur le risque et
non sur le collatéral.

La largeur du range est calée sur le mouvement implicite : les ailes courtes sont
vendues autour d'un multiple du mouvement attendu, les ailes longues achetées
plus loin.
"""

# --- Paramètres à recalibrer -------------------------------------------------
UNDERLYING = "SPY"
DAYS = 30
SHORT_WIDTH = 0.03         # ailes courtes (vendues), en fraction du spot
LONG_WIDTH = 0.06          # ailes longues (achetées)
RISK_BUDGET = 0.01         # perte maximale tolérée, en fraction de l'actif net
MAX_NOTIONAL_PCT = 0.50    # plafond de notionnel sous-jacent, en fraction de l'actif net
MAX_VOL_REGIME = 1.15
EXIT_IF_FORECAST = True
# Signaux surveillés pour la sortie « prévision de choc ». SPY n'a pas de
# prévision dans le registre, mais ^GSPC (l'indice que SPY suit) en porte une
# (r1 · choc pétrolier · sens ↓ · pic J+7). Sans ce deuxième symbole, le garde-fou
# EXIT_IF_FORECAST était un no-op : il ne se déclenchait jamais.
FORECAST_SYMBOLS = ["SPY", "^GSPC"]


def _shock_active():
    """Vrai dès qu'une prévision de choc active existe sur les symboles surveillés."""
    if not EXIT_IF_FORECAST:
        return False
    return any(get_forecast(s) is not None for s in FORECAST_SYMBOLS)



def initialize(context):
    context.asset = symbol(UNDERLYING)
    context.legs = {}
    context.entry = None
    context.max_loss = 0.0
    schedule_function(trade, date_rules.every_day())


def _flat(context, reason):
    for c in list(context.legs):
        pos = context.portfolio.positions.get(c)
        if pos is not None and abs(pos.amount) > 1e-9:
            order(c, -pos.amount, reason=reason)
    context.legs = {}
    context.entry = None


def trade(context, data):
    today = get_datetime().date()

    if context.entry is not None:
        expiry_hit = any(pd.Timestamp(c.expiry).date() <= today for c in context.legs)
        forecast_hit = _shock_active()
        held = (today - context.entry).days
        if expiry_hit or forecast_hit or held >= DAYS - 2:
            why = ("échéance" if expiry_hit else
                   "prévision de choc active" if forecast_hit else "sortie avant gamma")
            pnl = sum(context.portfolio.positions[c].unrealized_pnl
                      for c in context.legs if c in context.portfolio.positions)
            log.info(f"Sortie iron condor J+{held} ({why}) — P&L latent {pnl:+,.0f} "
                     f"(perte max théorique {context.max_loss:,.0f})")
            _flat(context, f"sortie {why}")
            record(condors=0.0)
            return

    if context.entry is None and not _shock_active():
        regime = vol_regime(UNDERLYING)
        if regime > MAX_VOL_REGIME:
            record(condors=0.0, vol_regime=regime)
            return
        spot = data.current(UNDERLYING, "close")
        if not spot:
            record(condors=0.0, vol_regime=regime)
            return

        legs = [
            (option_contract(UNDERLYING, "put", moneyness=1 - LONG_WIDTH, days=DAYS), +1),
            (option_contract(UNDERLYING, "put", moneyness=1 - SHORT_WIDTH, days=DAYS), -1),
            (option_contract(UNDERLYING, "call", moneyness=1 + SHORT_WIDTH, days=DAYS), -1),
            (option_contract(UNDERLYING, "call", moneyness=1 + LONG_WIDTH, days=DAYS), +1),
        ]
        unit = 0.0
        for c, q in legs:
            unit += (data.current(c, "close") or 0.0) * q
        credit = -unit                              # prime nette encaissée
        width = (LONG_WIDTH - SHORT_WIDTH) * spot
        if width <= 0:
            record(condors=0.0, vol_regime=regime)
            return
        loss_per_unit = max(width - credit, 0.0)
        if loss_per_unit <= 0:
            record(condors=0.0, vol_regime=regime)
            return
        pv = context.portfolio.portfolio_value
        qty = int(min(pv * RISK_BUDGET // loss_per_unit,
                      pv * MAX_NOTIONAL_PCT / spot))
        if qty < 1:
            record(condors=0.0, vol_regime=regime)
            return

        for c, q in legs:
            order(c, q * qty, reason="iron condor jambe")
        context.legs = {c: q * qty for c, q in legs}
        context.entry = today
        context.max_loss = loss_per_unit * qty
        log.info(f"Vente iron condor {UNDERLYING} : {qty} unités, range "
                 f"{legs[1][0].strike:.2f}–{legs[2][0].strike:.2f}, protection "
                 f"{legs[0][0].strike:.2f}/{legs[3][0].strike:.2f}, crédit "
                 f"{credit * qty:,.0f}, perte max {context.max_loss:,.0f}, "
                 f"régime de vol {regime:.2f}x.")
        record(condors=float(qty), vol_regime=regime)
        return

    record(condors=0.0, vol_regime=vol_regime(UNDERLYING))
