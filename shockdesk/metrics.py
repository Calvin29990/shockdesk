"""Métriques de performance, calculées à partir de la courbe d'équité."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd


def _safe(x) -> Optional[float]:
    if x is None:
        return None
    x = float(x)
    return None if (np.isnan(x) or np.isinf(x)) else x


def drawdown(equity: pd.Series) -> pd.Series:
    peak = equity.cummax()
    return equity / peak - 1.0


def compute(equity: pd.Series, benchmark: Optional[pd.Series] = None,
            risk_free: float = 0.041, periods_per_year: int = 252) -> Dict:
    """Métriques standard de desk. Renvoie un dict JSON-sérialisable."""
    equity = equity.dropna()
    if len(equity) < 2:
        return {"error": "série trop courte"}

    rets = equity.pct_change().dropna()
    n = len(rets)
    years = n / periods_per_year
    total = equity.iloc[-1] / equity.iloc[0] - 1.0
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1 if years > 0 else 0.0
    ann_vol = rets.std(ddof=0) * np.sqrt(periods_per_year)
    rf_daily = risk_free / periods_per_year
    excess = rets - rf_daily
    sharpe = (excess.mean() / rets.std(ddof=0) * np.sqrt(periods_per_year)
              if rets.std(ddof=0) > 0 else 0.0)
    downside = rets[rets < 0]
    sortino = (excess.mean() / downside.std(ddof=0) * np.sqrt(periods_per_year)
               if len(downside) > 1 and downside.std(ddof=0) > 0 else 0.0)
    dd = drawdown(equity)
    max_dd = float(dd.min())
    calmar = cagr / abs(max_dd) if max_dd < 0 else 0.0

    wins = rets[rets > 0]
    losses = rets[rets < 0]
    gross_win = float(wins.sum())
    gross_loss = float(-losses.sum())

    out = {
        "start_date": str(equity.index[0].date()),
        "end_date": str(equity.index[-1].date()),
        "trading_days": int(n + 1),
        "years": round(years, 3),
        "total_return": round(float(total), 6),
        "cagr": round(_safe(cagr), 6),
        "ann_volatility": round(_safe(ann_vol), 6),
        "sharpe": round(_safe(sharpe), 3),
        "sortino": round(_safe(sortino), 3),
        "max_drawdown": round(max_dd, 6),
        "calmar": round(_safe(calmar), 3),
        "win_rate": round(len(wins) / n, 4) if n else None,
        "best_day": round(float(rets.max()), 6),
        "worst_day": round(float(rets.min()), 6),
        "profit_factor": round(gross_win / gross_loss, 3) if gross_loss > 1e-12 else None,
        "skew": round(float(rets.skew()), 3) if n > 3 else None,
        "kurtosis": round(float(rets.kurt()), 3) if n > 3 else None,
        "var_95": round(float(np.percentile(rets, 5)), 6),
        "cvar_95": round(float(rets[rets <= np.percentile(rets, 5)].mean()), 6)
        if len(rets[rets <= np.percentile(rets, 5)]) else None,
        "final_equity": round(float(equity.iloc[-1]), 2),
    }

    if benchmark is not None and len(benchmark) > 1:
        b = benchmark.reindex(equity.index).ffill().dropna()
        if len(b) > 2:
            br = b.pct_change().dropna()
            common = rets.index.intersection(br.index)
            out["benchmark_return"] = round(float(b.iloc[-1] / b.iloc[0] - 1.0), 6)
            out["alpha"] = round(out["total_return"] - out["benchmark_return"], 6)
            cov = np.cov(rets.loc[common].to_numpy(), br.loc[common].to_numpy())
            out["beta"] = round(float(cov[0, 1] / cov[1, 1]), 3) if cov[1, 1] > 0 else None
            out["information_ratio"] = round(
                float((rets.loc[common] - br.loc[common]).mean() /
                      (rets.loc[common] - br.loc[common]).std(ddof=0) *
                      np.sqrt(periods_per_year)), 3) \
                if (rets.loc[common] - br.loc[common]).std(ddof=0) > 0 else None
    return out


def monthly_returns(equity: pd.Series) -> List[dict]:
    if len(equity) < 2:
        return []
    m = equity.resample("ME").last().dropna()
    first = equity.iloc[0]
    prev = None
    out = []
    for ts, v in m.items():
        base = first if prev is None else prev
        out.append({"month": ts.strftime("%Y-%m"), "return": round(float(v / base - 1.0), 6),
                    "equity": round(float(v), 2)})
        prev = v
    return out
