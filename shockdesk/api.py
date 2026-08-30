"""
Point d'entrée fonctionnel de ShockDesk.

C'est ce module que parlent l'interface web et la ligne de commande. Les noms
de paramètres suivent la forme de l'URL de recherche (``name``,
``startCapital``, ``startDate``, ``endDate``, ``action``) pour que l'URL,
l'API et le CLI racontent la même chose.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from . import config, metrics as metrics_mod, options as opt, registry
from .engine import BacktestEngine, EngineSettings
from .marketdata import load_panel
from .scenarios import ForecastLedger, recommend, scorecard, validate


def _params(name: str = "us-equities", startCapital=10000,
            startDate: str = "2020-01-01", endDate: str = "2021-09-01",
            action: str = "backtest") -> dict:
    return {
        "name": name,
        "startCapital": float(startCapital),
        "startDate": str(startDate),
        "endDate": str(endDate),
        "action": action,
    }


def run_backtest(code: str, name: str = "us-equities", startCapital=10000,
                 startDate: str = "2020-01-01", endDate: str = "2021-09-01",
                 action: str = "backtest", source: str = "auto",
                 strategy_id: Optional[str] = None,
                 settings: Optional[dict] = None) -> dict:
    """Exécute un backtest et renvoie le payload complet de l'onglet Backtest."""
    p = _params(name, startCapital, startDate, endDate, action)
    started = pd.Timestamp.now()

    uni = config.get_universe(name)
    panel = load_panel(name, p["startDate"], p["endDate"], source=source)

    st = EngineSettings()
    for k, v in (settings or {}).items():
        if hasattr(st, k):
            setattr(st, k, type(getattr(st, k))(v))

    ledger = ForecastLedger()
    engine = BacktestEngine(panel, name, p["startCapital"], settings=st, ledger=ledger)
    result = engine.run(code)

    equity = result["equity"]
    bench_col = uni["benchmark"]
    bench = None
    if bench_col in panel.close.columns and len(panel.close) > 1:
        b = panel.close[bench_col]
        bench = (b / float(b.iloc[0])) * float(p["startCapital"])

    perf = metrics_mod.compute(equity, bench, risk_free=st.risk_free)
    perf["benchmark_symbol"] = bench_col
    # Le taux sans risque est retiré du Sharpe et du Sortino : on le renvoie
    # pour que l'interface puisse l'afficher à côté des deux ratios.
    perf["risk_free"] = st.risk_free
    exposure = []
    for row in result["greeks"]:
        exposure.append(row)

    # Exposition brute et levier, jour par jour.
    lev = []
    pos_hist = []
    for row in result["greeks"]:
        lev.append(row["equity"])

    trades = result["trades"]
    n_trades = len(trades)
    turnover = sum(abs(t["gross"]) for t in trades)
    perf["trades"] = n_trades
    perf["turnover"] = round(turnover, 2)
    perf["avg_trade"] = round(turnover / n_trades, 2) if n_trades else 0.0

    sc = scorecard(ledger, panel)
    payload = {
        "ok": result.get("error") is None,
        "params": p,
        "universe": {
            "name": name, "label": uni["label"], "description": uni["description"],
            "symbols": uni["symbols"], "benchmark": uni["benchmark"],
            "assets": [config.asset_dict(s) for s in uni["symbols"]],
        },
        "data": {
            "source": panel.source,
            "detail": panel.source_detail,
            "start": str(panel.close.index[0].date()),
            "end": str(panel.close.index[-1].date()),
            "bars": int(len(panel.close)),
        },
        "metrics": perf,
        "equity": {"dates": [d.date().isoformat() for d in equity.index],
                   "values": [round(float(v), 2) for v in equity.to_numpy()]},
        "benchmark": None if bench is None else {
            "symbol": bench_col,
            "dates": [d.date().isoformat() for d in bench.index],
            "values": [round(float(v), 2) for v in bench.to_numpy()]},
        "drawdown": {"dates": [d.date().isoformat() for d in equity.index],
                     "values": [round(float(v), 6) for v in
                                metrics_mod.drawdown(equity).to_numpy()]},
        "monthly": metrics_mod.monthly_returns(equity),
        "attribution": result["attribution"],
        "greeks": result["greeks"],
        "positions": result["portfolio"]["positions"],
        "portfolio": {k: v for k, v in result["portfolio"].items() if k != "positions"},
        "trades": trades,
        "records": {k: {"dates": [str(d.date()) for d in v.index],
                        "values": [None if pd.isna(x) else round(float(x), 6)
                                   for x in v.to_numpy()]}
                    for k, v in result["records"].items()},
        "logs": result["logs"],
        "scorecard": sc,
        "forecasts": [f.as_dict() for f in ledger.all()],
        "error": result.get("error"),
        "runtime_ms": int((pd.Timestamp.now() - started).total_seconds() * 1000),
        "strategy_id": strategy_id,
    }
    return payload


def strategy_payload(strategy_id: str, **params) -> dict:
    """Charge une stratégie du registre et l'exécute avec les paramètres d'URL."""
    meta = registry.get(strategy_id)
    if not meta:
        raise KeyError(f"Stratégie inconnue : {strategy_id}")
    code = registry.read_code(strategy_id)
    defaults = meta.get("defaults") or {}
    for k in ("name", "startCapital", "startDate", "endDate"):
        params.setdefault(k, defaults.get(k))
    params = {k: v for k, v in params.items() if v is not None}
    payload = run_backtest(code, strategy_id=strategy_id, **params)
    payload["strategy"] = {"id": strategy_id, "name": meta.get("name"),
                           "file": meta.get("file"), "code": code,
                           "updated": meta.get("updated")}
    return payload


# --------------------------------------------------------------------------- #
# Tableau d'anticipation (onglet Scénarios)
# --------------------------------------------------------------------------- #
def scenario_board(universe: str = "global-macro", asof: Optional[str] = None,
                   horizon_days: int = 45, width: float = 0.03) -> dict:
    """Pour chaque sous-jacent de l'univers : prévision active, spot, IV,
    structures recommandées et P&L par nœud de la grille d'amplitudes."""
    uni = config.get_universe(universe)
    end = pd.Timestamp(asof) if asof else pd.Timestamp.today()
    start = end - pd.Timedelta(days=max(horizon_days * 4, 120))
    panel = load_panel(universe, start, end)
    ledger = ForecastLedger()

    asof_ts = panel.close.index[-1]
    rows = []
    for sym in uni["symbols"]:
        spec = config.get_asset(sym)
        spot = float(panel.close[sym].iloc[-1])
        s = panel.close[sym].tail(21)
        rv = float(np.std(np.diff(np.log(s.to_numpy())), ddof=0) * np.sqrt(config.TRADING_DAYS)) \
            if len(s) > 3 else spec.ann_vol
        vol_regime = float(min(max(rv / spec.ann_vol, 0.55), 2.6)) if spec.ann_vol else 1.0
        f = ledger.active(asof_ts, sym)
        iv_shift = f.iv_shift if f else 0.0
        iv_atm = opt.iv_surface(spec, 1.0, 30 / 365.0, vol_regime=vol_regime,
                                iv_shift=iv_shift)
        row = {
            "symbol": sym, "name": spec.name, "asset_class": spec.asset_class,
            "spot": round(spot, 4), "unit": spec.unit,
            "realized_vol": round(rv, 4), "vol_regime": round(vol_regime, 3),
            "iv_atm_30d": round(iv_atm, 4),
            "iv_base": round(spec.effective_iv_base, 4),
            "iv_shift": round(iv_shift, 4),
            "options": spec.options,
            "forecast": f.as_dict() if f else None,
        }
        if f is not None:
            days = int(max(round(f.peak_base) + 7, 14))
            row["path"] = [{"day": i, "value": round(float(v), 5)}
                           for i, v in enumerate(f.path(horizon_days))]
            row["validation"] = validate(f, panel)
            if spec.options:
                rec = recommend(f, spot, iv_atm, width=width, days=days)
                row["recommendation"] = rec
                row["structures"] = rec["structures"]
        rows.append(row)

    return {
        "universe": {"name": universe, "label": uni["label"]},
        "asof": str(asof_ts.date()),
        "data_source": panel.source,
        "horizon_days": horizon_days,
        "rows": rows,
        "scorecard": scorecard(ledger, panel),
        "catalog": opt.CATALOG,
    }


def option_lab(underlying: str, structure: str = "strangle", days: int = 30,
               width: float = 0.03, iv_shift: float = 0.0,
               vol_regime: float = 1.0, spot_override: Optional[float] = None,
               n_points: int = 121) -> dict:
    """Pricer une structure et tracer son payoff — l'atelier d'options."""
    spec = config.get_asset(underlying)
    spot = float(spot_override) if spot_override else spec.s0
    st = opt.build_structure(structure, underlying, spot, days=days, width=width,
                             vol_regime=vol_regime, iv_shift=iv_shift)
    lo = min(l.strike for l in st.legs) * 0.85
    hi = max(l.strike for l in st.legs) * 1.15
    grid = [lo + i * (hi - lo) / (n_points - 1) for i in range(n_points)]
    d = st.as_dict(grid)
    d["underlying_name"] = spec.name
    d["vol_regime"] = vol_regime
    d["iv_shift"] = iv_shift
    d["catalog"] = opt.CATALOG
    return d
