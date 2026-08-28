"""
Le cœur « anticipation » de ShockDesk : scénarios, prévisions révisables et
scoring ex-post.

Trois objets :

``Forecast``
    Une vue publiée sur un sous-jacent (sens, amplitude, jour de pic, reversion,
    choc d'IV), avec un **numéro de révision**. Le registre ne renvoie à une date
    donnée que la dernière révision publiée *avant* cette date : un backtest ne
    peut donc jamais tricher avec une prévision corrigée après coup.

``ForecastLedger``
    Le registre persistant (``config/forecasts.json``). C'est là que la phase 1
    se corrige au fil des mois : on ajoute une révision, on ne réécrit pas
    l'histoire.

``scoring``
    La validation honnête : accord de signe **net du drift du benchmark**,
    erreur de timing du pic, ratio d'amplitude, MFE/MAE, corrélation de
    trajectoire.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

from . import config

Number = Union[int, float]
FORECAST_PATH = os.path.join(config.REPO_ROOT, "config", "forecasts.json")

DEFAULT_LEDGER = {
    "note": "Registre des prévisions ShockLab. Chaque prévision porte une liste de "
            "révisions datées : la phase 1 se corrige ici, mois par mois, sans "
            "réécrire l'historique. Un backtest ne voit que la dernière révision "
            "publiée avant la date du bar.",
    "forecasts": [
        {
            "id": "shocklab-2026-07-oil",
            "name": "Choc pétrolier — Brent",
            "asset": "BZ=F", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "énergie"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.05,
                 "peak_day": 7, "reversion": -0.03, "reversion_days": 21,
                 "iv_shift": 0.10, "confidence": 0.60,
                 "note": "v1 publiée : +5 % en 7 jours, pic J+7, puis reversion -3 %."},
                {"rev": 2, "date": "2026-08-28", "sign": 1,
                 "amplitude": [0.05, 0.10, 0.185], "peak_day": [7, 9],
                 "reversion": -0.065, "reversion_days": 14,
                 "iv_shift": 0.14, "confidence": 0.55,
                 "note": "Correction phase 1 : amplitude passée en grille (sous-estimée "
                         "d'un facteur ~3,7), pic J+7 a J+9, reversion plus rapide et "
                         "plus profonde. Le signal de timing est conservé, le niveau non."},
            ],
        },
        {
            "id": "shocklab-2026-07-rates",
            "name": "Choc pétrolier — duration (TLT)",
            "asset": "TLT", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "taux"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.02,
                 "peak_day": 7, "reversion": 0.01, "reversion_days": 21,
                 "iv_shift": 0.03, "confidence": 0.50,
                 "note": "Refuge taux sur choc d'offre : duration longue."},
            ],
        },
        {
            "id": "shocklab-2026-07-usd",
            "name": "Choc pétrolier — dollar",
            "asset": "DX-Y.NYB", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "devises"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.02,
                 "peak_day": 7, "reversion": 0.015, "reversion_days": 21,
                 "iv_shift": 0.01, "confidence": 0.50, "note": "Bid dollar de précaution."},
            ],
        },
        {
            "id": "shocklab-2026-07-credit",
            "name": "Choc pétrolier — crédit HY",
            "asset": "HYG", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "crédit"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.005,
                 "peak_day": 7, "reversion": 0.004, "reversion_days": 21,
                 "iv_shift": 0.0, "confidence": 0.40,
                 "note": "Énergie = grosse part de l'indice HY : le choc pétrolier porte le carry."},
            ],
        },
        {
            "id": "shocklab-2026-07-commodities",
            "name": "Choc pétrolier — matières premières",
            "asset": "DBC", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "matières"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.03,
                 "peak_day": 7, "reversion": 0.005, "reversion_days": 21,
                 "iv_shift": 0.02, "confidence": 0.50, "note": "Contagion au complexe."},
            ],
        },
        {
            "id": "shocklab-2026-07-gold",
            "name": "Choc pétrolier — or",
            "asset": "GC=F", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "métaux", "miss"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": 1, "amplitude": 0.03,
                 "peak_day": 7, "reversion": 0.01, "reversion_days": 21,
                 "iv_shift": 0.02, "confidence": 0.45,
                 "note": "Or vu comme couverture du choc. C'est le miss de l'exercice : "
                         "l'or a corrigé, taux réels et dollar trop forts."},
                {"rev": 2, "date": "2026-08-28", "sign": -1, "amplitude": 0.04,
                 "peak_day": 15, "reversion": -0.02, "reversion_days": 25,
                 "iv_shift": 0.0, "confidence": 0.40,
                 "note": "Correction phase 1 : sens inverse. L'or n'est pas la couverture "
                         "d'un choc d'offre quand le dollar et les taux réels montent."},
            ],
        },
        {
            "id": "shocklab-2026-07-equities",
            "name": "Choc pétrolier — actions US",
            "asset": "^GSPC", "benchmark": "^GSPC", "stop_date": "2026-08-05",
            "tags": ["exercice-juillet-2026", "actions", "benchmark"],
            "revisions": [
                {"rev": 1, "date": "2026-07-15", "sign": -1, "amplitude": 0.015,
                 "peak_day": 7, "reversion": -0.01, "reversion_days": 21,
                 "iv_shift": 0.04, "confidence": 0.45,
                 "note": "Non-test par construction : c'est le benchmark de drift. "
                         "Affiché pour mémoire, exclu du score de signe."},
            ],
        },
        {
            "id": "shocklab-2026-09-oil-roll",
            "name": "Pétrole — rouleau septembre (phase 1, à valider)",
            "asset": "BZ=F", "benchmark": "^GSPC", "stop_date": "2026-10-15",
            "tags": ["phase-1", "énergie", "à-corriger"],
            "revisions": [
                {"rev": 1, "date": "2026-09-01", "sign": -1, "amplitude": 0.06,
                 "peak_day": 20, "reversion": -0.02, "reversion_days": 30,
                 "iv_shift": -0.05, "confidence": 0.40,
                 "note": "Vue de rentrée : reversion post-choc et IV qui se détend. "
                         "Première révision prévue à la revue de fin septembre."},
            ],
        },
    ],
}

# --------------------------------------------------------------------------- #
# Prévisions
# --------------------------------------------------------------------------- #
def _as_range(v) -> List[float]:
    if v is None:
        return [0.0]
    if isinstance(v, (list, tuple)):
        return [float(x) for x in v]
    return [float(v)]


@dataclass
class Forecast:
    """Une prévision, figée à une révision donnée."""

    id: str
    name: str
    asset: str
    published: str
    rev: int
    sign: int = 1
    amplitude: List[float] = field(default_factory=lambda: [0.05])
    peak_day: List[float] = field(default_factory=lambda: [7])
    reversion: float = -0.03
    reversion_days: int = 21
    iv_shift: float = 0.0
    confidence: float = 0.5
    note: str = ""
    benchmark: str = "^GSPC"
    stop_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @property
    def amp_low(self) -> float:
        return min(self.amplitude)

    @property
    def amp_base(self) -> float:
        a = self.amplitude
        return a[len(a) // 2]

    @property
    def amp_high(self) -> float:
        return max(self.amplitude)

    @property
    def peak_base(self) -> float:
        return float(self.peak_day[len(self.peak_day) // 2])

    @property
    def grid(self) -> List[float]:
        """Grille d'amplitudes pour le stress test (du plus doux au plus violent)."""
        base = self.amp_base or 0.05
        out = sorted({round(x, 5) for x in list(self.amplitude) +
                      [base * 0.5, base * 1.5, base * 2.0, base * 3.7]})
        return [x for x in out if x > 0]

    def path(self, days: int, amplitude: Optional[float] = None) -> np.ndarray:
        """Trajectoire cumulée prévue, en fraction du spot, jour calendaire par
        jour calendaire.

        Convention : ``amplitude`` est une magnitude, ``sign`` son sens ;
        ``reversion`` est le niveau cumulé **signé** en fin d'épisode (ex.
        -0.065 = on finit 6,5 % sous le niveau de publication).
        """
        amp = self.amp_base if amplitude is None else float(amplitude)
        peak_val = amp * self.sign
        peak = max(int(round(self.peak_base)), 1)
        rev_days = max(int(self.reversion_days), peak + 1)
        out = np.zeros(days)
        for i in range(days):
            if i <= peak:
                t = i / peak
                out[i] = peak_val * (0.5 - 0.5 * np.cos(np.pi * t))
            elif i <= rev_days:
                t = (i - peak) / max(rev_days - peak, 1)
                out[i] = peak_val * (1 - t) + self.reversion * t
            else:
                out[i] = self.reversion
        return out

    def as_dict(self) -> dict:
        d = asdict(self)
        d["amp_base"] = self.amp_base
        d["peak_base"] = self.peak_base
        d["grid"] = self.grid
        return d


class ForecastLedger:
    def __init__(self, path: Optional[str] = None, materialize: bool = True):
        self.path = path or FORECAST_PATH
        self.raw = self._load()
        if materialize and not os.path.exists(self.path):
            # Le registre est matérialisé sur le disque dès le premier appel :
            # c'est le fichier que l'on corrige mois par mois.
            try:
                self.save()
            except OSError:
                pass
        self._build()

    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return json.loads(json.dumps(DEFAULT_LEDGER))
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not data.get("forecasts"):
                return json.loads(json.dumps(DEFAULT_LEDGER))
            return data
        except (OSError, ValueError):
            return json.loads(json.dumps(DEFAULT_LEDGER))

    def _build(self):
        self.items: Dict[str, dict] = {}
        self.revs: Dict[str, List[Forecast]] = {}
        for entry in self.raw.get("forecasts", []):
            fid = entry["id"]
            self.items[fid] = entry
            built = []
            for r in entry.get("revisions", []):
                built.append(Forecast(
                    id=fid, name=entry["name"], asset=entry["asset"],
                    published=r["date"], rev=int(r["rev"]),
                    sign=int(r.get("sign", 1)),
                    amplitude=_as_range(r.get("amplitude", 0.05)),
                    peak_day=_as_range(r.get("peak_day", 7)),
                    reversion=float(r.get("reversion", -0.03)),
                    reversion_days=int(r.get("reversion_days", 21)),
                    iv_shift=float(r.get("iv_shift", 0.0)),
                    confidence=float(r.get("confidence", 0.5)),
                    note=r.get("note", ""),
                    benchmark=entry.get("benchmark", "^GSPC"),
                    stop_date=entry.get("stop_date"),
                    tags=entry.get("tags", []),
                ))
            built.sort(key=lambda f: f.published)
            self.revs[fid] = built

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.raw, fh, ensure_ascii=False, indent=2)

    # -- lecture ------------------------------------------------------- #
    def all(self) -> List[Forecast]:
        return [f for fid in self.revs for f in [self.latest(fid)]]

    def latest(self, fid: str) -> Forecast:
        return self.revs[fid][-1]

    def get(self, fid_or_name: str) -> Optional[Forecast]:
        if fid_or_name in self.revs:
            return self.latest(fid_or_name)
        for fid, entry in self.items.items():
            if entry["name"] == fid_or_name:
                return self.latest(fid)
        return None

    def for_asset(self, asset: str) -> List[Forecast]:
        return [self.latest(fid) for fid, e in self.items.items() if e["asset"] == asset]

    def active(self, on, asset: str) -> Optional[Forecast]:
        """Dernière révision publiée avant ``on`` pour ``asset`` (point-in-time)."""
        on = pd.Timestamp(on)
        best = None
        for fid, entry in self.items.items():
            if entry["asset"] != asset:
                continue
            for f in self.revs[fid]:
                if pd.Timestamp(f.published) <= on:
                    if best is None or (f.published, f.rev) > (best.published, best.rev):
                        best = f
        return best

    def as_of(self, on) -> List[Forecast]:
        on = pd.Timestamp(on)
        out = []
        for fid in self.revs:
            elig = [f for f in self.revs[fid] if pd.Timestamp(f.published) <= on]
            if elig:
                out.append(elig[-1])
        return out

    def revisions(self, fid: str) -> List[Forecast]:
        return list(self.revs.get(fid, []))

    # -- écriture ------------------------------------------------------ #
    def add_revision(self, fid: str, **fields) -> Forecast:
        entry = self.items.get(fid)
        if entry is None:
            raise KeyError(f"Prévision inconnue : {fid}")
        rev = max((int(r["rev"]) for r in entry["revisions"]), default=0) + 1
        rec = {"rev": rev}
        rec.update(fields)
        rec.setdefault("date", pd.Timestamp.today().date().isoformat())
        entry["revisions"].append(rec)
        self.save()
        self._build()
        return self.latest(fid)

    def add_forecast(self, fid: str, name: str, asset: str, benchmark: str = "^GSPC",
                     stop_date: Optional[str] = None, tags: Optional[List[str]] = None,
                     **rev_fields) -> Forecast:
        entry = {"id": fid, "name": name, "asset": asset, "benchmark": benchmark,
                 "stop_date": stop_date, "tags": tags or [], "revisions": [
                     dict({"rev": 1}, **rev_fields)]}
        self.raw.setdefault("forecasts", []).append(entry)
        self.save()
        self._build()
        return self.latest(fid)


# --------------------------------------------------------------------------- #
# Scoring ex-post (la validation honnête)
# --------------------------------------------------------------------------- #
def _beta_to_benchmark(asset: str, benchmark: str) -> float:
    a = config.ASSETS.get(asset)
    b = config.ASSETS.get(benchmark)
    if a is None or b is None:
        return 1.0
    ba = a.loadings.get("SPX", 0.0)
    bb = b.loadings.get("SPX", 0.0)
    if abs(bb) < 1e-9:
        return 0.0
    return ba / bb


def validate(f: Forecast, panel, asof: Optional[str] = None) -> dict:
    """Compare une prévision à la réalité observée dans le panneau de prix.

    Renvoie un dictionnaire de score : tout est mesuré **net du drift du
    benchmark**, sauf mention contraire.
    """
    close = panel.close
    pub = pd.Timestamp(f.published)
    stop = pd.Timestamp(asof or f.stop_date
                        or pub + pd.Timedelta(days=int(f.reversion_days) + 14))
    meta = {"id": f.id, "rev": f.rev, "asset": f.asset, "name": f.name,
            "published": f.published, "is_original": int(f.rev) == 1,
            "is_benchmark": f.asset == f.benchmark, "counted": False}
    if f.asset not in close.columns:
        return dict(meta, error=f"{f.asset} absent du panneau")

    w = close[(close.index >= pub) & (close.index <= stop)]
    if len(w) < 2:
        return dict(meta, error="pas assez de données après publication "
                                "(révision publiée après la fin des données)")

    base = float(w[f.asset].iloc[0])
    ret = w[f.asset] / base - 1.0

    beta = _beta_to_benchmark(f.asset, f.benchmark)
    if f.benchmark in w.columns:
        b = w[f.benchmark] / float(w[f.benchmark].iloc[0]) - 1.0
        active = ret - beta * b
    else:
        active, b = ret, None

    is_benchmark = (f.asset == f.benchmark)
    i_peak = int(np.argmax(np.abs(active.to_numpy())))
    peak_date = active.index[i_peak]
    actual_peak = float(active.iloc[i_peak])
    amp_base = f.amp_base or 0.05
    sign_ok = bool(np.sign(actual_peak) == np.sign(f.sign)) if actual_peak != 0 else False
    end_active = float(active.iloc[-1])
    end_ok = bool(np.sign(end_active) == np.sign(f.sign)) if end_active != 0 else False

    horizon_days = (stop - pub).days
    model = f.path(max(horizon_days, 1))
    model_idx = pd.date_range(pub, periods=len(model), freq="D")
    model_s = pd.Series(model, index=model_idx)
    common = active.index.intersection(model_s.index)
    corr = float("nan")
    if len(common) > 3:
        # Attention : ne pas réutiliser `b` (la série benchmark) comme variable
        # locale ici, elle sert plus bas.
        xa = active.loc[common].to_numpy()
        xb = model_s.loc[common].to_numpy()
        if xa.std() > 1e-12 and xb.std() > 1e-12:
            corr = float(np.corrcoef(xa, xb)[0, 1])

    return {
        "id": f.id, "rev": f.rev, "asset": f.asset, "name": f.name,
        "published": f.published,
        "window": [str(w.index[0].date()), str(w.index[-1].date())],
        "sign_forecast": f.sign,
        "sign_ok_peak": sign_ok,
        "sign_ok_end": end_ok,
        "amplitude_forecast": amp_base,
        "amplitude_realized": round(actual_peak, 5),
        "amplitude_ratio": round(actual_peak / amp_base, 3) if amp_base else None,
        "peak_forecast_days": f.peak_base,
        "peak_realized_days": (peak_date - pub).days,
        "peak_error_days": (peak_date - pub).days - f.peak_base,
        "peak_date": str(peak_date.date()),
        "mfe": round(float(active.max()), 5),
        "mae": round(float(active.min()), 5),
        "end_return_active": round(end_active, 5),
        "end_return_raw": round(float(ret.iloc[-1]), 5),
        "benchmark_drift": round(float(b.iloc[-1]), 5) if b is not None else None,
        "beta_to_benchmark": round(beta, 3),
        "path_correlation": None if np.isnan(corr) else round(corr, 3),
        "in_perimeter": bool(pd.Timestamp(f.stop_date) >= w.index[-1]) if f.stop_date else True,
        # Le benchmark sert à nettoyer le drift : le noter reviendrait à noter
        # zéro contre zéro. Il est affiché pour mémoire, jamais compté.
        "is_benchmark": is_benchmark,
        "is_original": int(f.rev) == 1,
        "counted": (not is_benchmark) and int(f.rev) == 1,
    }


def scorecard(ledger: ForecastLedger, panel, asof: Optional[str] = None) -> dict:
    """Note TOUTES les révisions publiées, mais ne compte dans le score que la
    révision originale (r1) : c'est elle qui a été publiée et tradée.

    Les révisions ultérieures restent affichées — ce sont les corrections de la
    phase 1 — mais elles ne peuvent pas améliorer un score ex-post.
    """
    rows = []
    for fid in sorted(ledger.revs):
        for f in ledger.revisions(fid):
            rows.append(validate(f, panel, asof))

    scored = [r for r in rows if r.get("counted") and "sign_ok_peak" in r]
    evaluated = [r for r in rows if "sign_ok_peak" in r]
    hits = sum(1 for r in scored if r["sign_ok_peak"])
    errs = [abs(r["peak_error_days"]) for r in scored
            if r.get("peak_error_days") is not None]
    ratios = [r["amplitude_ratio"] for r in scored if r.get("amplitude_ratio")]
    return {
        "rows": rows,
        "sign_hits": hits,
        "sign_total": len(scored),
        "lines_total": len(rows),
        "non_test": sum(1 for r in evaluated if r.get("is_benchmark")),
        "sign_rate": round(hits / len(scored), 3) if scored else None,
        # Médiane plutôt que moyenne : une série monotone « pic » en fin de
        # fenêtre et ferait exploser la moyenne sans rien dire du timing.
        "median_peak_error_days": round(float(np.median(errs)), 2) if errs else None,
        "avg_peak_error_days": round(float(np.mean(errs)), 2) if errs else None,
        "median_amplitude_ratio": round(float(np.median(ratios)), 2) if ratios else None,
        "misses": [r["asset"] for r in scored if not r["sign_ok_peak"]],
        "asof": asof or (str(panel.close.index[-1].date()) if len(panel.close) else None),
    }


# --------------------------------------------------------------------------- #
# Structures recommandées par scénario
# --------------------------------------------------------------------------- #
def pnl_at(structure, spot_end: float, iv_change: float = 0.0,
           days_held: int = 0) -> float:
    """P&L d'une structure si le sous-jacent finit à ``spot_end``.

    ``iv_change`` revalorise la valeur temps résiduelle (choc de vol),
    ``days_held`` le temps écoulé. Approximation desk : intrinsèque + valeur
    temps restante au nouveau niveau d'IV.
    """
    from . import options as opt
    total = 0.0
    for leg in structure.legs:
        intrinsic = max(0.0, (spot_end - leg.strike) if leg.kind == "call"
                        else (leg.strike - spot_end))
        t_left = max(structure.days - days_held, 0) / 365.0
        time_value = 0.0
        if t_left > 0:
            iv = max(leg.iv + iv_change, 0.02)
            bs = opt.black_scholes(spot_end, leg.strike, t_left, iv, leg.kind)
            time_value = max(bs - intrinsic, 0.0)
        total += (intrinsic + time_value - leg.premium) * leg.qty
    return total


def recommend(f: Forecast, spot: float, iv_atm: float, width: float = 0.03,
              days: Optional[int] = None) -> List[dict]:
    """Choisit les structures d'options cohérentes avec une prévision.

    La logique desk :

    * amplitude attendue **large** par rapport à ce que paie l'IV → on est long
      gamma (strangle / straddle) ;
    * amplitude attendue **faible** ou reversion rapide → on vend de la prime
      (short strangle, iron condor, butterfly) ;
    * sens marqué mais amplitude incertaine → spreads directionnels ou risk
      reversal (on paie peu de vega) ;
    * choc d'IV anticipé → on est long vega (straddle/strangle), et l'inverse
      après le pic (crush).
    """
    from . import options as opt
    days = int(days or max(round(f.peak_base) + 7, 14))
    expected_move = f.amp_base * spot
    implied_move = iv_atm * spot * np.sqrt(days / 365.0)
    ratio = expected_move / implied_move if implied_move else 1.0

    picks: List[tuple] = []
    if ratio >= 1.15:
        picks.append(("strangle", 100, f"amplitude attendue {f.amp_base:+.1%} ≈ {ratio:.1f}x le mouvement payé par l'IV → long gamma"))
        picks.append(("straddle", 70, "si l'on veut le maximum de gamma au détriment du coût"))
    elif ratio <= 0.75:
        picks.append(("short_strangle", 90, f"amplitude attendue {f.amp_base:+.1%} ≈ {ratio:.1f}x le mouvement payé par l'IV → vente de prime"))
        picks.append(("iron_condor", 80, "même idée, risque borné"))
        picks.append(("butterfly", 60, f"reversion prévue à {f.reversion:+.1%} → viser le corps"))
    else:
        picks.append(("call_spread" if f.sign > 0 else "put_spread", 85,
                      "sens marqué, amplitude proche de l'IV → structure directionnelle peu chère en vega"))
        picks.append(("butterfly", 55, "alternative si la reversion prime"))
    if f.iv_shift >= 0.05:
        picks.append(("calendar", 65, f"choc d'IV anticipé de {f.iv_shift:+.0%} pts → long vega court terme"))
    if f.sign != 0 and abs(f.sign) == 1 and ratio < 1.0:
        picks.append(("risk_reversal", 50, "financement de la vue directionnelle par la vente du put OTM"))

    picks.sort(key=lambda t: -t[1])
    out = []
    for kind, score, why in picks[:4]:
        st = opt.build_structure(kind, f.asset, spot, days=days, width=width,
                                 iv_shift=f.iv_shift)
        d = st.as_dict()
        d["kind"] = kind
        d["score"] = score
        d["rationale"] = why
        d["expected_move"] = expected_move
        d["implied_move"] = implied_move
        d["pnl_scenarios"] = []
        for amp in f.grid:
            for mult, lbl in ((1.0, "scénario"), (-1.0, "contre-sens"), (0.0, "statique")):
                end = spot * (1 + mult * amp * f.sign)
                d["pnl_scenarios"].append({
                    "label": f"{lbl} {amp:+.1%}",
                    "amplitude": mult * amp * f.sign,
                    "spot_end": round(end, 4),
                    "pnl": round(pnl_at(st, end, iv_change=f.iv_shift * mult if mult else 0.0,
                                        days_held=min(days, int(round(f.peak_base)))), 4),
                })
        out.append(d)
    return {
        "expected_move": expected_move,
        "implied_move": implied_move,
        "ratio": round(ratio, 3),
        "structures": out,
    }
