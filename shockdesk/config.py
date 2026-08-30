"""
Univers de trading, calibration du modèle factoriel et calibration des options.

Tout ce qui est « à corriger au fil des mois » vit ici (ou dans
``config/calibration.json``, qui a priorité sur les valeurs par défaut ci-dessous) :

* niveaux de référence des sous-jacents (``s0``),
* volatilités annuelles,
* betas factoriels,
* volatilité implicite de base et forme du sourire.

Le modèle factoriel est volontairement simple et transparent : 7 facteurs,
des betas explicites, un bruit idiosyncratique. Un desk peut lire, discuter et
recalibrer chaque nombre.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, replace
from typing import Dict, List

TRADING_DAYS = 252

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIBRATION_PATH = os.path.join(REPO_ROOT, "config", "calibration.json")
DATA_DIR = os.path.join(REPO_ROOT, "data")
STRATEGY_DIR = os.path.join(REPO_ROOT, "strategies")


# --------------------------------------------------------------------------- #
# Facteurs
# --------------------------------------------------------------------------- #
# Convention : la valeur du facteur est un RENDEMENT journalier du facteur.
#   SPX    : +1 % = actions +1 %
#   OIL    : +1 % = pétrole +1 %
#   RATES  : +1 % = les taux MONTENT (donc les prix obligataires baissent)
#   GOLD   : +1 % = or +1 %
#   USD    : +1 % = dollar +1 %
#   CREDIT : +1 % = spreads HY se resserrent (HYG monte)
#   VOL    : +1 % = volatilité +1 %
FACTORS: Dict[str, float] = {
    "SPX": 0.150,
    "OIL": 0.320,
    "RATES": 0.095,
    "GOLD": 0.120,
    "USD": 0.070,
    "CREDIT": 0.060,
    "VOL": 0.800,
}


@dataclass(frozen=True)
class AssetSpec:
    """Fiche d'un sous-jacent (ou d'un produit)."""

    symbol: str
    name: str
    asset_type: str                      # equity | etf | index | future | fx
    s0: float                            # niveau de référence de la calibration
    ann_vol: float                       # vol annuelle cible (après normalisation)
    ann_drift: float                     # dérive annuelle
    loadings: Dict[str, float] = field(default_factory=dict)
    iv_base: float = 0.0                 # vol implicite ATM de base (0 -> dérivée de ann_vol)
    iv_smile: float = 0.55               # convexité du sourire (par unité de (m-1)^2)
    iv_skew: float = -0.25               # pente du sourire (put plus chers)
    iv_term: float = 0.10                # pente de la structure en terme (log(T/30j))
    multiplier: float = 1.0
    # Taille d'un contrat réel, exprimée en unités du sous-jacent. Le moteur
    # raisonne en unités (1 unité = 1 baril, 1 once, 1 part d'ETF) ; ce champ
    # sert à ramener une quantité en nombre de contrats pour les frais par
    # contrat. 1 000 barils pour le Brent, 100 onces pour l'or, 1 pour un ETF.
    contract_size: float = 1.0
    tick: float = 0.05
    options: bool = True
    asset_class: str = "autres"          # classe d'actif, pour l'attribution
    unit: str = "USD"

    @property
    def effective_iv_base(self) -> float:
        return self.iv_base if self.iv_base > 0 else self.ann_vol * 1.12


# --------------------------------------------------------------------------- #
# Univers (l'équivalent des « bundles » Blueshift : name=us-equities, etc.)
# --------------------------------------------------------------------------- #
_ASSETS: List[AssetSpec] = [
    # --- Énergie ----------------------------------------------------------- #
    AssetSpec("BZ=F", "Brent Crude", "future", 84.95, 0.34, 0.00,
              {"OIL": 1.00, "SPX": -0.05, "USD": -0.10}, iv_base=0.36,
              asset_class="Énergie", unit="USD/bbl",
              contract_size=1000.0),          # 1 contrat Brent = 1 000 barils
    AssetSpec("CL=F", "WTI Crude", "future", 80.50, 0.35, 0.00,
              {"OIL": 0.98, "SPX": -0.05, "USD": -0.10}, iv_base=0.37,
              asset_class="Énergie", unit="USD/bbl",
              contract_size=1000.0),          # 1 contrat WTI = 1 000 barils
    AssetSpec("XLE", "Energy Select SPDR", "etf", 92.40, 0.24, 0.05,
              {"OIL": 0.72, "SPX": 0.55}, asset_class="Énergie"),
    AssetSpec("XOP", "SPDR S&P Oil & Gas E&P", "etf", 78.10, 0.32, 0.04,
              {"OIL": 0.88, "SPX": 0.48}, asset_class="Énergie"),
    AssetSpec("UNG", "United States Natural Gas", "etf", 17.20, 0.55, -0.10,
              {"OIL": 0.30}, asset_class="Énergie"),
    # --- Actions / indices ------------------------------------------------- #
    AssetSpec("^GSPC", "S&P 500", "index", 6420.0, 0.150, 0.075,
              {"SPX": 1.00, "RATES": -0.35, "OIL": -0.25, "CREDIT": 0.35, "USD": -0.15},
              iv_base=0.165, asset_class="Actions"),
    AssetSpec("SPY", "SPDR S&P 500 ETF", "etf", 642.0, 0.150, 0.075,
              {"SPX": 1.00, "RATES": -0.35, "OIL": -0.25, "CREDIT": 0.35, "USD": -0.15},
              iv_base=0.165, asset_class="Actions"),
    AssetSpec("QQQ", "Invesco QQQ (Nasdaq 100)", "etf", 561.0, 0.200, 0.100,
              {"SPX": 1.25, "RATES": -0.60, "CREDIT": 0.30}, iv_base=0.225,
              asset_class="Actions"),
    AssetSpec("AAPL", "Apple", "equity", 226.0, 0.235, 0.090,
              {"SPX": 1.10}, asset_class="Actions"),
    AssetSpec("MSFT", "Microsoft", "equity", 481.0, 0.225, 0.095,
              {"SPX": 1.05}, asset_class="Actions"),
    AssetSpec("NVDA", "NVIDIA", "equity", 176.0, 0.420, 0.160,
              {"SPX": 1.40}, iv_base=0.44, asset_class="Actions"),
    AssetSpec("XLF", "Financial Select SPDR", "etf", 55.30, 0.190, 0.070,
              {"SPX": 0.90, "RATES": 0.35}, asset_class="Actions"),
    # --- Taux / crédit ----------------------------------------------------- #
    AssetSpec("TLT", "iShares 20+ Year Treasury", "etf", 88.20, 0.150, 0.010,
              {"RATES": -1.00, "SPX": 0.15, "CREDIT": 0.25}, asset_class="Taux"),
    AssetSpec("IEF", "iShares 7-10 Year Treasury", "etf", 94.60, 0.085, 0.015,
              {"RATES": -0.60, "SPX": 0.05}, asset_class="Taux"),
    AssetSpec("HYG", "iShares iBoxx $ High Yield", "etf", 78.10, 0.055, 0.045,
              {"CREDIT": 1.00, "SPX": 0.35, "RATES": -0.20}, asset_class="Crédit"),
    # --- Métaux / matières ------------------------------------------------- #
    AssetSpec("GC=F", "Gold", "future", 3350.0, 0.145, 0.060,
              {"GOLD": 1.00, "USD": -0.35, "RATES": -0.25, "SPX": 0.05},
              iv_base=0.175, asset_class="Métaux", unit="USD/oz",
              contract_size=100.0),           # 1 contrat or = 100 onces
    AssetSpec("SI=F", "Silver", "future", 38.20, 0.290, 0.050,
              {"GOLD": 0.70, "SPX": 0.30}, asset_class="Métaux",
              contract_size=5000.0),          # 1 contrat argent = 5 000 onces
    AssetSpec("DBC", "Invesco DB Commodity Index", "etf", 21.10, 0.185, 0.020,
              {"OIL": 0.55, "SPX": 0.20, "USD": -0.20, "GOLD": 0.20},
              asset_class="Matières premières"),
    # --- Devises ----------------------------------------------------------- #
    AssetSpec("DX-Y.NYB", "US Dollar Index", "index", 97.80, 0.072, -0.010,
              {"USD": 1.00, "RATES": 0.30}, options=False, asset_class="Devises"),
    AssetSpec("EURUSD=X", "EUR/USD", "fx", 1.1640, 0.065, 0.005,
              {"USD": -1.00, "RATES": -0.15}, options=False, asset_class="Devises"),
    # --- Volatilité (référence d'IV, non tradable en direct) ---------------- #
    AssetSpec("^VIX", "CBOE Volatility Index", "index", 16.40, 0.850, -0.050,
              {"VOL": 1.00, "SPX": -0.45}, options=False, asset_class="Volatilité"),
]

ASSETS: Dict[str, AssetSpec] = {a.symbol: a for a in _ASSETS}


UNIVERSES: Dict[str, dict] = {
    "global-macro": {
        "label": "Global macro (le book ShockLab)",
        "description": "Les 7 lignes du post ShockLab : Brent, actions US, duration, or, dollar, crédit HY, matières premières.",
        "symbols": ["BZ=F", "^GSPC", "TLT", "GC=F", "DX-Y.NYB", "HYG", "DBC"],
        "benchmark": "^GSPC",
        "options": False,
    },
    "us-equities": {
        "label": "US equities",
        "description": "Actions et ETF US, options activées (bundle par défaut de la forme Blueshift).",
        "symbols": ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "XLE", "XLF", "TLT"],
        "benchmark": "SPY",
        "options": True,
    },
    "energy-shock": {
        "label": "Energy shock",
        "description": "Complexe pétrolier complet : brut, E&P, gaz + couverture taux.",
        "symbols": ["BZ=F", "CL=F", "XLE", "XOP", "UNG", "TLT"],
        "benchmark": "XLE",
        "options": True,
    },
    "rates-fx": {
        "label": "Rates & FX",
        "description": "Duration, crédit et dollar.",
        "symbols": ["TLT", "IEF", "HYG", "DX-Y.NYB", "EURUSD=X"],
        "benchmark": "TLT",
        "options": True,
    },
    "options-lab": {
        "label": "Options lab",
        "description": "Sous-jacents liquides pour tester les structures (strangle, butterfly, condor...).",
        "symbols": ["SPY", "QQQ", "TLT", "GC=F", "BZ=F"],
        "benchmark": "SPY",
        "options": True,
    },
}


def list_universes() -> List[dict]:
    out = []
    for name, u in UNIVERSES.items():
        out.append({
            "name": name,
            "label": u["label"],
            "description": u["description"],
            "symbols": u["symbols"],
            "benchmark": u["benchmark"],
            "options": u["options"],
            "assets": [asset_dict(s) for s in u["symbols"]],
        })
    return out


def asset_dict(symbol: str) -> dict:
    a = ASSETS[symbol]
    return {
        "symbol": a.symbol,
        "name": a.name,
        "asset_type": a.asset_type,
        "asset_class": a.asset_class,
        "s0": a.s0,
        "ann_vol": a.ann_vol,
        "ann_drift": a.ann_drift,
        "iv_base": a.effective_iv_base,
        "options": a.options,
        "unit": a.unit,
        "multiplier": a.multiplier,
        "loadings": dict(a.loadings),
    }


def get_asset(symbol: str) -> AssetSpec:
    if symbol not in ASSETS:
        raise KeyError(
            f"Sous-jacent inconnu : {symbol!r}. Univers disponibles : "
            f"{', '.join(sorted(ASSETS))}"
        )
    return ASSETS[symbol]


def get_universe(name: str) -> dict:
    if name not in UNIVERSES:
        raise KeyError(f"Univers inconnu : {name!r}. Disponibles : {', '.join(UNIVERSES)}")
    return UNIVERSES[name]


# --------------------------------------------------------------------------- #
# Surcharge de calibration (config/calibration.json) — la boucle mensuelle
# --------------------------------------------------------------------------- #
def _apply_calibration() -> None:
    """Relit config/calibration.json et remplace les fiches concernées.

    Format attendu::

        {
          "assets": { "BZ=F": {"s0": 78.4, "ann_vol": 0.31, "loadings": {"OIL": 1.0}} },
          "factors": {"OIL": 0.29},
          "note": "recalibration du 01/09/2026"
        }
    """
    global ASSETS
    if not os.path.exists(CALIBRATION_PATH):
        return
    try:
        with open(CALIBRATION_PATH, "r", encoding="utf-8") as fh:
            calib = json.load(fh)
    except (OSError, ValueError):
        return

    for symbol, patch in (calib.get("assets") or {}).items():
        if symbol not in ASSETS:
            continue
        spec = ASSETS[symbol]
        loadings = dict(spec.loadings)
        loadings.update(patch.pop("loadings", {}) or {})
        ASSETS[symbol] = replace(spec, loadings=loadings, **patch)

    for factor, sigma in (calib.get("factors") or {}).items():
        if factor in FACTORS:
            FACTORS[factor] = float(sigma)


CALIBRATION_NOTE = ""
if os.path.exists(CALIBRATION_PATH):
    try:
        with open(CALIBRATION_PATH, "r", encoding="utf-8") as _fh:
            CALIBRATION_NOTE = json.load(_fh).get("note", "")
    except (OSError, ValueError):
        pass

_apply_calibration()
