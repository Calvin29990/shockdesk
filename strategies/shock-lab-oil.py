"""Book multi-actifs du scénario de choc pétrolier (ShockLab, phase 1).

La stratégie publiée : entrée à la publication du scénario, sortie au stop
calendar fixé ex-ante. La v2 ajoute le take-profit au jour de pic du modèle —
c'est le signal qui valait le plus sur l'exercice de juillet 2026.

Paramètres en tête de fichier, à recalibrer à chaque revue mensuelle.
"""

# --- Paramètres de la phase 1 ------------------------------------------------
TAKE_PROFIT_AT_PEAK = True      # v2 : sortie au jour de pic du modèle (J+peak)
USE_STOP_DATE = True            # sortie au stop calendar publié
TARGET_SIGNAL = "BZ=F"          # sous-jacent qui porte le scénario
BASE_EXPOSURE = 0.85            # exposition brute totale du book
ONE_PASS = True                 # une seule passe par scénario

# Le book « delta uniquement » de l'exercice publié. Signe = sens de la vue :
# un choc pétrolier se couvre en vendant les actions, pas en achetant du brut.
BOOK = {
    "^GSPC": -0.45,     # couverture actions : c'est elle qui paie
    "GC=F": 0.10,       # or (le miss de l'exercice : cette ligne coûte)
    "HYG": 0.10,        # crédit HY, porté par l'énergie
    "TLT": 0.10,        # duration, refuge du choc d'offre
    "DBC": 0.06,        # contagion au complexe matières premières
    "DX-Y.NYB": 0.05,   # dollar de précaution
    "BZ=F": 0.08,       # la vue directionnelle brut — la ligne qui finit négative
}


def _tradable():
    """Sous-jacents du book réellement présents dans l'univers courant."""
    out = []
    for s in BOOK:
        try:
            out.append(symbol(s))
        except KeyError:
            pass
    return out


def initialize(context):
    context.universe_assets = _tradable()
    context.book = {s: w for s, w in BOOK.items() if s in context.universe_assets}
    if TARGET_SIGNAL not in context.universe_assets:
        log.warn(f"{TARGET_SIGNAL} absent de l'univers : la stratégie n'aura pas de signal.")
    context.entered_on = None
    context.traded = set()      # (id prévision, révision) déjà jouées
    schedule_function(trade, date_rules.every_day())


def _flatten(context, reason):
    for asset, pos in list(context.portfolio.positions.items()):
        if abs(pos.amount) > 1e-9:
            order(asset, -pos.amount, reason=reason)


def _gross_exposure(context):
    return (sum(abs(p.market_value) for p in context.portfolio.positions.values())
            / max(context.portfolio.portfolio_value, 1.0))


def trade(context, data):
    today = get_datetime().date()
    f = get_forecast(TARGET_SIGNAL)

    # --- sortie ------------------------------------------------------------ #
    if context.entered_on is not None:
        days_held = (today - context.entered_on).days
        peak = int(round(f.peak_base)) if f else 7
        hit_peak = TAKE_PROFIT_AT_PEAK and days_held >= peak
        hit_stop = bool(USE_STOP_DATE and f and f.stop_date
                        and today >= pd.Timestamp(f.stop_date).date())
        if hit_peak or hit_stop:
            _flatten(context, "take-profit pic modèle" if hit_peak else "stop calendar")
            log.info(f"Sortie J+{days_held} "
                     f"({'pic modèle' if hit_peak else 'stop calendar'}) — "
                     f"P&L {context.portfolio.pnl:+,.0f} "
                     f"({context.portfolio.returns:+.2%})")
            context.entered_on = None
            record(exposure=0.0, signal=0.0)
            return

    # --- entrée ------------------------------------------------------------ #
    if context.entered_on is None and f is not None:
        key = (f.id, f.rev)
        if ONE_PASS and key in context.traded:
            record(exposure=0.0, signal=f.sign)     # une passe par révision publiée
            return
        scale = BASE_EXPOSURE * max(min(f.confidence * 1.6, 1.0), 0.25)
        # Dénominateur en EXPOSITION BRUTE : les poids sont signés, les sommer
        # tel quel ferait exploser la taille dès qu'une ligne est vendeuse.
        total = sum(abs(w) for w in context.book.values()) or 1.0
        for s, w in context.book.items():
            weight = (w / total) * scale
            if s == TARGET_SIGNAL:
                weight *= f.sign
            order_target_percent(s, weight, reason=f"entrée scénario r{f.rev}")
        context.entered_on = today
        context.traded.add(key)
        log.info(f"Entrée book — scénario « {f.name} » r{f.rev} : sens {f.sign:+d}, "
                 f"amplitude prévue {f.amp_base:+.1%}, pic J+{f.peak_base:.0f}, "
                 f"stop {f.stop_date}. Exposition cible {scale:.0%}.")
        record(exposure=scale, signal=f.sign)
        return

    record(exposure=_gross_exposure(context), signal=(f.sign if f else 0.0))
