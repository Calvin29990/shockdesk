"""
Couche données de ShockDesk.

Trois sources, essayées dans cet ordre :

1. **yfinance** (données réelles) — utilisé si le paquet est installé *et* que
   Yahoo répond. C'est le mode nominal sur le poste de l'utilisateur.
2. **cache CSV** dans ``data/`` — un fichier ``<symbole>.csv`` avec les colonnes
   ``date,open,high,low,close`` (séparateur ``,`` ou ``;``, dates ISO). Utile pour
   travailler hors ligne sur des données réelles exportées à la main.
3. **générateur synthétique** — modèle factoriel calibré (voir ``config.py``),
   déterministe, avec injection d'événements de choc. Toujours disponible :
   c'est le mode « hors ligne » de la sandbox.

Le mode utilisé est renvoyé dans ``panel.source`` et affiché dans l'interface :
aucun chiffre ne doit pouvoir être lu comme une donnée réelle par erreur.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from . import config

EPOCH = pd.Timestamp("2015-01-01")
# Date d'ancrage de la calibration : le générateur synthétique cale le niveau de
# chaque sous-jacent sur ``AssetSpec.s0`` à cette date. C'est la date de
# publication du scénario ShockLab de juillet 2026 (Brent à 84,95 $).
ANCHOR_DATE = pd.Timestamp("2026-07-15")
OHLC = ("open", "high", "low", "close")


@dataclass
class PricePanel:
    """Panneau de prix OHLC pour un univers, plus la provenance."""

    close: pd.DataFrame
    open: pd.DataFrame
    high: pd.DataFrame
    low: pd.DataFrame
    source: str                          # 'yfinance' | 'csv' | 'synthetic'
    source_detail: str = ""
    symbols: List[str] = field(default_factory=list)
    benchmark: str = "^GSPC"

    @property
    def dates(self) -> pd.DatetimeIndex:
        return self.close.index

    def slice(self, start, end) -> "PricePanel":
        m = (self.close.index >= pd.Timestamp(start)) & (self.close.index <= pd.Timestamp(end))
        return PricePanel(
            close=self.close[m], open=self.open[m], high=self.high[m], low=self.low[m],
            source=self.source, source_detail=self.source_detail,
            symbols=self.symbols, benchmark=self.benchmark,
        )


# --------------------------------------------------------------------------- #
# Événements de choc injectés dans l'historique synthétique
# --------------------------------------------------------------------------- #
@dataclass
class ShockEvent:
    """Trajectoire CUMULÉE cible d'un facteur entre trois dates.

    ``peak_move`` est le mouvement cumulé du facteur au pic, ``end_move`` le
    mouvement cumulé en fin d'épisode. Le générateur convertit la trajectoire en
    incréments journaliers et les ajoute aux rendements factoriels aléatoires.
    """

    name: str
    factor: str
    start: str
    peak: str
    end: str
    peak_move: float
    end_move: float


SHOCK_EVENTS: List[ShockEvent] = [
    # --- Autres épisodes de l'historique ---------------------------------- #
    ShockEvent("Cycle de hausse des taux", "RATES",
               "2022-02-01", "2023-10-20", "2024-06-28", 0.30, 0.06),
    ShockEvent("Correction actions août 2024", "SPX",
               "2024-07-15", "2024-08-05", "2024-09-30", -0.085, -0.015),
    ShockEvent("Rallye or 2025-2026 puis correction", "GOLD",
               "2025-01-06", "2026-06-15", "2026-08-28", 0.26, 0.15),
]


@dataclass
class PathOverlay:
    """Trajectoire imposée sur une fenêtre, pour les épisodes documentés.

    Le générateur factoriel fournit le bruit de fond de tout l'historique ; sur
    la fenêtre d'un épisode documenté (l'exercice ShockLab publié en juillet
    2026), le prix suit la trajectoire publiée, exprimée en fraction du niveau de
    publication. La transition vers le chemin bruité se fait en cosinus sur
    ``ramp_days`` jours ouvrés, donc sans cassure visible dans les séries.

    C'est un jeu de **démonstration hors ligne**. En production, la source
    ``yfinance`` ou ``csv`` fournit les prix réels et les overlays sont ignorés
    (voir ``load_panel``).
    """

    symbol: str
    window: Tuple[str, str]
    waypoints: List[Tuple[str, float]]
    ramp_days: int = 5


PRICE_OVERLAYS: List[PathOverlay] = [
    # --- Exercice ShockLab publié le 15/07/2026, stop ex-ante au 05/08 ------- #
    PathOverlay("BZ=F", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.185),
                 ("2026-08-05", -0.065), ("2026-08-28", 0.020)]),
    PathOverlay("CL=F", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.175),
                 ("2026-08-05", -0.060), ("2026-08-28", 0.022)]),
    PathOverlay("XLE", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.070),
                 ("2026-08-05", 0.005), ("2026-08-28", 0.020)]),
    PathOverlay("XOP", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.085),
                 ("2026-08-05", 0.000), ("2026-08-28", 0.025)]),
    PathOverlay("^GSPC", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", -0.008),
                 ("2026-08-05", -0.012), ("2026-08-28", 0.015)]),
    PathOverlay("SPY", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", -0.008),
                 ("2026-08-05", -0.012), ("2026-08-28", 0.015)]),
    PathOverlay("QQQ", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", -0.014),
                 ("2026-08-05", -0.020), ("2026-08-28", 0.012)]),
    PathOverlay("TLT", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.016),
                 ("2026-08-05", 0.012), ("2026-08-28", 0.004)]),
    PathOverlay("GC=F", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", -0.035),
                 ("2026-08-05", -0.028), ("2026-08-28", -0.045)]),
    PathOverlay("DX-Y.NYB", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.026),
                 ("2026-08-05", 0.022), ("2026-08-28", 0.010)]),
    PathOverlay("HYG", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.005),
                 ("2026-08-05", 0.004), ("2026-08-28", 0.008)]),
    PathOverlay("DBC", ("2026-07-13", "2026-08-28"),
                [("2026-07-15", 0.0), ("2026-07-23", 0.055),
                 ("2026-08-05", 0.012), ("2026-08-28", 0.030)]),
]


def _interp_target(ov: PathOverlay, dates: pd.DatetimeIndex) -> Tuple[np.ndarray, np.ndarray]:
    """Renvoie (cible interpolée, poids de la fenêtre 0..1) pour chaque date."""
    target = np.zeros(len(dates))
    weight = np.zeros(len(dates))
    wp_dates = [pd.Timestamp(d) for d, _ in ov.waypoints]
    wp_vals = np.array([v for _, v in ov.waypoints])
    w0, w1 = pd.Timestamp(ov.window[0]), pd.Timestamp(ov.window[1])
    ordinal = np.array([d.toordinal() for d in dates], dtype=float)
    wp_ord = np.array([d.toordinal() for d in wp_dates], dtype=float)
    target = np.interp(ordinal, wp_ord, wp_vals,
                       left=wp_vals[0], right=wp_vals[-1])
    for i, ts in enumerate(dates):
        if ts < w0 or ts > w1:
            continue
        # poids en cosinus : rampe sur les ramp_days premiers/derniers jours ouvrés
        idx = list(dates)
        lo = idx.index(w0) if w0 in idx else 0
        hi = idx.index(w1) if w1 in idx else len(idx) - 1
        r = max(ov.ramp_days, 1)
        # Pas de rampe de sortie si la fenêtre couvre la fin de l'historique :
        # toute la période de démonstration reste pilotée par la trajectoire.
        ramp_out = w1 < dates[-1]
        if i - lo < r:
            weight[i] = 0.5 - 0.5 * np.cos(np.pi * (i - lo) / r)
        elif ramp_out and hi - i < r:
            weight[i] = 0.5 - 0.5 * np.cos(np.pi * (hi - i) / r)
        else:
            weight[i] = 1.0
    return target, weight


def _apply_overlay(series: pd.Series, ov: PathOverlay, dates: pd.DatetimeIndex,
                   anchor_level: float) -> pd.Series:
    target, weight = _interp_target(ov, dates)
    noisy = series.to_numpy() / anchor_level           # chemin bruité normalisé
    with np.errstate(divide="ignore", invalid="ignore"):
        wanted = np.where(noisy > 0, (1.0 + target) / noisy, 1.0)
    mult = 1.0 + weight * (wanted - 1.0)
    return series * mult


def _event_increments(dates: pd.DatetimeIndex) -> Dict[str, np.ndarray]:
    extra = {f: np.zeros(len(dates)) for f in config.FACTORS}
    for ev in SHOCK_EVENTS:
        s, p, e = pd.Timestamp(ev.start), pd.Timestamp(ev.peak), pd.Timestamp(ev.end)
        up = (dates >= s) & (dates <= p)
        down = (dates > p) & (dates <= e)
        arr = extra[ev.factor]
        n_up, n_down = int(up.sum()), int(down.sum())
        if n_up:
            w = np.linspace(1.4, 0.6, n_up)          # montée concave
            arr[up] += ev.peak_move * w / w.sum()
        if n_down:
            w = np.linspace(0.6, 1.4, n_down)        # reversion convexe
            arr[down] += (ev.end_move - ev.peak_move) * w / w.sum()
    return extra


def _factor_returns(dates: pd.DatetimeIndex, seed: int = 20260715) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    names = list(config.FACTORS)
    sigmas = np.array([config.FACTORS[k] for k in names]) / np.sqrt(config.TRADING_DAYS)
    idx = {k: i for i, k in enumerate(names)}

    corr = np.eye(len(names))

    def link(a, b, v):
        corr[idx[a], idx[b]] = v
        corr[idx[b], idx[a]] = v

    link("SPX", "OIL", -0.20)
    link("SPX", "RATES", 0.15)
    link("SPX", "VOL", -0.60)
    link("SPX", "CREDIT", 0.55)
    link("SPX", "GOLD", -0.05)
    link("SPX", "USD", 0.10)
    link("OIL", "RATES", 0.30)
    link("OIL", "USD", 0.15)
    link("OIL", "VOL", 0.25)
    link("GOLD", "USD", -0.45)
    link("GOLD", "RATES", -0.30)
    link("CREDIT", "VOL", -0.40)
    link("RATES", "VOL", 0.15)

    vals, vecs = np.linalg.eigh(corr)                # nettoyage PSD
    corr = vecs @ np.diag(np.clip(vals, 1e-6, None)) @ vecs.T
    d = np.sqrt(np.diag(corr))
    corr = corr / np.outer(d, d)

    chol = np.linalg.cholesky(np.outer(sigmas, sigmas) * corr)
    f = rng.standard_normal((len(dates), len(names))) @ chol.T

    # Cluster de volatilité sur le facteur VOL.
    vi = idx["VOL"]
    f[:, vi] = pd.Series(f[:, vi]).ewm(alpha=0.35).mean().to_numpy() * 1.9

    out = pd.DataFrame(f, index=dates, columns=names)
    for k, v in _event_increments(dates).items():
        out[k] = out[k] + v
    return out


def _synthetic_close(symbols: Iterable[str], dates: pd.DatetimeIndex,
                     seed: int = 20260715) -> pd.DataFrame:
    symbols = list(symbols)
    factors = _factor_returns(dates, seed=seed)
    names = list(config.FACTORS)
    fsig = {k: config.FACTORS[k] / np.sqrt(config.TRADING_DAYS) for k in names}

    rng = np.random.default_rng(seed + 7)
    F = factors[names].to_numpy()
    rets = {}
    for s in symbols:
        spec = config.get_asset(s)
        expo = np.array([spec.loadings.get(k, 0.0) for k in names])
        sys_ret = F @ expo
        sys_var = float(((expo * np.array([fsig[k] for k in names])) ** 2).sum())
        target_var = (spec.ann_vol / np.sqrt(config.TRADING_DAYS)) ** 2
        idio_var = max(target_var - sys_var, 0.25 * target_var)
        raw = sys_ret + rng.standard_normal(len(dates)) * np.sqrt(idio_var)
        std = raw.std(ddof=0)
        if std > 0:                                  # vol réalisée == vol cible
            raw = raw * (target_var ** 0.5) / std
        rets[s] = raw + spec.ann_drift / config.TRADING_DAYS - raw.mean()

    close = pd.DataFrame(index=dates)
    for s in symbols:
        close[s] = np.exp(np.cumsum(rets[s]))

    # 1. Ancrage des niveaux : close[ANCHOR_DATE] == s0 pour chaque sous-jacent.
    anchor_idx = close.index[close.index <= ANCHOR_DATE]
    if len(anchor_idx):
        ref = close.loc[anchor_idx[-1]]
        for s in symbols:
            if ref[s] > 0:
                close[s] = close[s] * (config.get_asset(s).s0 / float(ref[s]))
    # 2. Trajectoires imposées des épisodes documentés (démonstration hors ligne).
    for ov in PRICE_OVERLAYS:
        if ov.symbol in close.columns:
            close[ov.symbol] = _apply_overlay(close[ov.symbol], ov, dates,
                                              config.get_asset(ov.symbol).s0)
    return close


def _ohlc_from_close(close: pd.DataFrame, seed: int = 99
                     ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    prev = close.shift(1)
    open_ = prev.where(prev.notna(), close) * (1 + rng.normal(0, 0.0022, close.shape))
    spread = close.abs().to_numpy() * np.abs(rng.normal(0, 0.0075, close.shape))
    high = pd.DataFrame(np.maximum(close.to_numpy(), open_.to_numpy()) + spread,
                        index=close.index, columns=close.columns)
    low = pd.DataFrame(np.minimum(close.to_numpy(), open_.to_numpy()) - spread,
                       index=close.index, columns=close.columns)
    return open_, high, low


# --------------------------------------------------------------------------- #
# Sources
# --------------------------------------------------------------------------- #
def _business_days(start, end) -> pd.DatetimeIndex:
    return pd.bdate_range(start=pd.Timestamp(start).normalize(),
                          end=pd.Timestamp(end).normalize())


def _csv_cache_path(symbol: str) -> str:
    safe = symbol.replace("^", "_").replace("=", "_").replace("/", "_")
    return os.path.join(config.DATA_DIR, safe + ".csv")


def _load_csv(symbol: str) -> Optional[pd.DataFrame]:
    path = _csv_cache_path(symbol)
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path, sep=None, engine="python")
    except Exception:
        return None
    cols = {str(c).lower().strip(): c for c in df.columns}
    if "date" not in cols or "close" not in cols:
        return None
    out = pd.DataFrame({"close": pd.to_numeric(df[cols["close"]], errors="coerce")})
    for f in ("open", "high", "low"):
        out[f] = (pd.to_numeric(df[cols[f]], errors="coerce") if f in cols
                  else out["close"])
    out.index = pd.to_datetime(df[cols["date"]], errors="coerce")
    out = out.dropna().sort_index()
    return out if len(out) > 20 else None


def _load_yfinance(symbols: List[str], start, end) -> Optional[Dict[str, pd.DataFrame]]:
    try:
        import yfinance as yf  # type: ignore
    except Exception:
        return None
    try:
        raw = yf.download(list(symbols),
                          start=str(pd.Timestamp(start).date()),
                          end=str((pd.Timestamp(end) + pd.Timedelta(days=1)).date()),
                          auto_adjust=True, progress=False, threads=True, timeout=15)
        if raw is None or len(raw) == 0:
            return None
        out = {}
        for f in OHLC:
            if f.capitalize() not in raw:
                continue
            block = raw[f.capitalize()]
            out[f] = block if isinstance(block, pd.DataFrame) else block.to_frame(symbols[0])
        if "close" not in out or out["close"].dropna(how="all").empty:
            return None
        close = out["close"].dropna(how="all")
        for f in OHLC:
            out[f] = out.get(f, close).reindex(index=close.index, columns=close.columns)
        return out
    except Exception:
        return None


def load_panel(universe: str, start, end, source: str = "auto") -> PricePanel:
    """Charge le panneau OHLC d'un univers entre deux dates.

    ``source`` : ``auto`` (yfinance → csv → synthétique), ``yfinance``, ``csv``
    ou ``synthetic``.
    """
    uni = config.get_universe(universe)
    symbols = list(uni["symbols"])
    bench = uni["benchmark"]
    if bench not in symbols:
        symbols.append(bench)

    lo, hi = pd.Timestamp(start), pd.Timestamp(end)
    used = "synthetic"
    detail = "modèle factoriel calibré ShockDesk (hors ligne, déterministe)"
    frames: Optional[Dict[str, pd.DataFrame]] = None

    if source in ("auto", "yfinance"):
        got = _load_yfinance(symbols, lo, hi)
        if got is not None and len(got["close"]) > 5:
            frames, used = got, "yfinance"
            detail = "données réelles Yahoo Finance"

    if frames is None and source in ("auto", "csv"):
        loaded: Dict[str, pd.DataFrame] = {}
        missing: List[str] = []
        for s in symbols:
            df = _load_csv(s)
            if df is None:
                missing.append(s)
            else:
                loaded[s] = df
        if loaded and not missing:
            frames = {f: pd.DataFrame({s: loaded[s][f] for s in symbols}).sort_index()
                      for f in OHLC}
            frames = {f: v.loc[(v.index >= lo) & (v.index <= hi)] for f, v in frames.items()}
            if len(frames["close"]) > 5:
                used, detail = "csv", f"cache CSV local ({len(symbols)} sous-jacents)"
            else:
                frames = None

    if frames is None:
        # Génération depuis l'époque : la trajectoire est identique quelle que
        # soit la fenêtre demandée (pas de dépendance à `start`).
        dates = _business_days(EPOCH, hi)
        full = _synthetic_close(symbols, dates)
        full = full.loc[(full.index >= lo) & (full.index <= hi)]
        if len(full) < 2:
            raise ValueError(
                "Fenêtre trop courte ou hors périmètre du générateur "
                f"(historique synthétique disponible à partir du {EPOCH.date()}).")
        open_, high, low = _ohlc_from_close(full)
        frames = {"open": open_, "high": high, "low": low, "close": full}

    close = frames["close"].dropna(how="any")
    if close.empty:
        raise ValueError("Aucune donnée sur la fenêtre demandée.")
    frames = {f: frames[f].reindex(index=close.index, columns=close.columns)
              for f in OHLC}

    return PricePanel(close=frames["close"], open=frames["open"], high=frames["high"],
                      low=frames["low"], source=used, source_detail=detail,
                      symbols=list(close.columns), benchmark=bench)
