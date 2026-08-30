"""
Pricing d'options, surface de volatilité implicite, grecs et structures.

Tout est européen, pricé en Black-Scholes avec dividende continu ``q``. La
surface d'IV est paramétrique (sourire quadratique + skew + structure en
terme), ce qui permet :

* de construire un contrat d'option de façon déterministe pour n'importe quel
  sous-jacent de l'univers (même sans chaîne d'options réelle) ;
* de rejouer une vue de volatilité : un scénario qui anticipe un choc d'IV
  décale la surface et donc la valorisation du book d'options.

Convention de signe : une jambe en quantité positive = longue, négative =
courte. Les prix, grecs et P&L sont exprimés par contrat *avant* multiplicateur
(``AssetSpec.multiplier`` s'applique au moment du passage d'ordre).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from . import config

RISK_FREE = 0.041        # taux sans risque annuel (à recalibrer)


# --------------------------------------------------------------------------- #
# Black-Scholes
# --------------------------------------------------------------------------- #
def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _d1_d2(S: float, K: float, T: float, r: float, q: float, sigma: float):
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return None, None
    root = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / root
    return d1, d1 - root


def black_scholes(S: float, K: float, T: float, sigma: float, kind: str = "call",
                  r: float = RISK_FREE, q: float = 0.0) -> float:
    """Prix d'une option européenne. ``T`` en années, ``sigma`` en décimal."""
    kind = kind.lower()[0]
    if T <= 0:
        return max(0.0, (S - K) if kind == "c" else (K - S))
    if sigma <= 0:
        return math.exp(-r * T) * max(0.0, (S - K) if kind == "c" else (K - S))
    d1, d2 = _d1_d2(S, K, T, r, q, sigma)
    disc_r, disc_q = math.exp(-r * T), math.exp(-q * T)
    if kind == "c":
        return S * disc_q * norm_cdf(d1) - K * disc_r * norm_cdf(d2)
    return K * disc_r * norm_cdf(-d2) - S * disc_q * norm_cdf(-d1)


def greeks(S: float, K: float, T: float, sigma: float, kind: str = "call",
           r: float = RISK_FREE, q: float = 0.0) -> Dict[str, float]:
    """Grecs par contrat : delta, gamma, vega (par point de vol), theta (par
    jour calendaire), rho (par point de taux)."""
    kind = kind.lower()[0]
    out = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}
    if T <= 0:
        intrinsic = max(0.0, (S - K) if kind == "c" else (K - S))
        out["delta"] = (1.0 if S > K else 0.0) if kind == "c" else (-1.0 if S < K else 0.0)
        return out
    d1, d2 = _d1_d2(S, K, T, r, q, sigma)
    sqT = math.sqrt(T)
    disc_r, disc_q = math.exp(-r * T), math.exp(-q * T)
    pdf_d1 = norm_pdf(d1)
    gamma = disc_q * pdf_d1 / (S * sigma * sqT)
    vega = S * disc_q * pdf_d1 * sqT                       # par unité de vol
    if kind == "c":
        delta = disc_q * norm_cdf(d1)
        theta = (-S * disc_q * pdf_d1 * sigma / (2 * sqT)
                 - r * K * disc_r * norm_cdf(d2) + q * S * disc_q * norm_cdf(d1))
        rho = K * T * disc_r * norm_cdf(d2)
    else:
        delta = -disc_q * norm_cdf(-d1)
        theta = (-S * disc_q * pdf_d1 * sigma / (2 * sqT)
                 + r * K * disc_r * norm_cdf(-d2) - q * S * disc_q * norm_cdf(-d1))
        rho = -K * T * disc_r * norm_cdf(-d2)
    out.update(delta=delta, gamma=gamma, vega=vega / 100.0,
               theta=theta / 365.0, rho=rho / 100.0)
    return out


def implied_vol(price: float, S: float, K: float, T: float, kind: str = "call",
                r: float = RISK_FREE, q: float = 0.0,
                lo: float = 1e-4, hi: float = 5.0) -> Optional[float]:
    """Vol implicite par bissection (robuste, pas de divergence de Newton)."""
    if T <= 0 or price <= 0:
        return None
    intrinsic = max(0.0, (S - K) if kind.lower()[0] == "c" else (K - S)) * math.exp(-r * T)
    if price < intrinsic - 1e-8:
        return None

    def f(s):
        return black_scholes(S, K, T, s, kind, r, q) - price

    if f(lo) > 0 or f(hi) < 0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------- #
# Surface de volatilité implicite
# --------------------------------------------------------------------------- #
def iv_surface(spec: config.AssetSpec, moneyness: float, years: float,
               vol_regime: float = 1.0, iv_shift: float = 0.0) -> float:
    """IV implicite pour un moneyness ``K/S`` et une maturité donnée.

    * ``vol_regime`` multiplie la surface : 1.2 = régime de vol +20 %.
    * ``iv_shift`` est un choc de vol **additif en points** (0.10 = +10 pts),
      appliqué après le régime : c'est ce qu'utilise un scénario ShockLab.
    """
    years = max(years, 1 / 365.0)
    m = max(moneyness, 0.05)
    base = spec.effective_iv_base
    smile = 1.0 + spec.iv_smile * (m - 1.0) ** 2 + spec.iv_skew * (m - 1.0)
    term = 1.0 + spec.iv_term * math.log(max(years * 365.0, 1.0) / 30.0)
    iv = base * smile * term * vol_regime + iv_shift
    return float(min(max(iv, 0.02), 4.0))


def strike_step(price: float, spec: config.AssetSpec) -> float:
    """Pas de la grille de strikes pour ce niveau de prix."""
    if price >= 200:
        step = 5.0
    elif price >= 50:
        step = 2.5
    elif price >= 20:
        step = 1.0
    elif price >= 5:
        step = 0.5
    else:
        step = 0.25
    return max(step, spec.tick)


def round_strike(price: float, spec: config.AssetSpec) -> float:
    """Arrondit un strike sur la grille usuelle (relative au niveau de prix)."""
    step = strike_step(price, spec)
    return round(round(price / step) * step, 4)


# --------------------------------------------------------------------------- #
# Contrats
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class OptionContract:
    """Contrat d'option synthétique, identifié de façon stable."""

    underlying: str
    kind: str            # 'call' | 'put'
    strike: float
    expiry: str          # ISO
    sid: str = ""

    def __post_init__(self):
        object.__setattr__(self, "kind", self.kind.lower())
        if not self.sid:
            object.__setattr__(self, "sid", self.make_sid(
                self.underlying, self.kind, self.strike, self.expiry))

    @staticmethod
    def make_sid(underlying: str, kind: str, strike: float, expiry: str) -> str:
        return f"OPT|{underlying}|{kind.lower()[0].upper()}|{strike:.4f}|{expiry}"

    @property
    def label(self) -> str:
        return (f"{self.underlying} {pd_label(self.expiry)} "
                f"{self.strike:g} {self.kind.upper()}")

    def days_to_expiry(self, on) -> int:
        import pandas as pd
        return max(int((pd.Timestamp(self.expiry) - pd.Timestamp(on)).days), 0)


def pd_label(iso: str) -> str:
    import pandas as pd
    return pd.Timestamp(iso).strftime("%d%b%y").upper()


def build_contract(underlying: str, on, kind: str = "call",
                   strike: Optional[float] = None, moneyness: float = 1.0,
                   days: int = 30, vol_regime: float = 1.0) -> OptionContract:
    """Construit un contrat à partir du spot courant du sous-jacent."""
    import pandas as pd
    spec = config.get_asset(underlying)
    if not spec.options:
        raise ValueError(f"{underlying} n'a pas d'options dans l'univers ShockDesk.")
    spot = spec.s0
    expiry = (pd.Timestamp(on) + pd.Timedelta(days=int(days))).normalize()
    expiry = expiry + pd.Timedelta(days=(4 - expiry.weekday()) % 7)   # 3e vendredi approx.
    if strike is None:
        strike = round_strike(spot * float(moneyness), spec)
    return OptionContract(underlying=underlying, kind=kind, strike=float(strike),
                          expiry=str(pd.Timestamp(expiry).date()))


def contract_price(contract: OptionContract, spot: float, years: float,
                   spec: config.AssetSpec, vol_regime: float = 1.0,
                   iv_shift: float = 0.0) -> Tuple[float, Dict[str, float]]:
    iv = iv_surface(spec, contract.strike / spot if spot else 1.0, years,
                    vol_regime=vol_regime, iv_shift=iv_shift)
    price = black_scholes(spot, contract.strike, years, iv, contract.kind)
    g = greeks(spot, contract.strike, years, iv, contract.kind)
    g["iv"] = iv
    return price, g


# --------------------------------------------------------------------------- #
# Structures (strangle, butterfly, condor, spreads...)
# --------------------------------------------------------------------------- #
@dataclass
class Leg:
    kind: str
    strike: float
    qty: float
    premium: float = 0.0
    iv: float = 0.0
    days: int = 0            # maturité propre de la jambe (calendar)
    greeks: Dict[str, float] = field(default_factory=dict)


@dataclass
class Structure:
    name: str
    underlying: str
    legs: List[Leg]
    days: int
    spot: float
    note: str = ""
    # Bornes théoriques du payoff (déclarées par structure, pas déduites d'une
    # grille d'évaluation) : permettent à l'interface d'afficher « illimité »
    # au lieu d'un artefact de grille.
    max_loss_bounded: bool = True
    max_gain_bounded: bool = True

    @property
    def net_premium(self) -> float:
        """Prime nette par unité de sous-jacent : négatif = débit (on paie)."""
        return sum(l.premium * l.qty for l in self.legs)

    @property
    def cost(self) -> float:
        """Coût d'entrée : positif = débit (structure acheteuse), négatif = crédit."""
        return self.net_premium

    def payoff(self, S: float) -> float:
        """P&L évalué à l'échéance de la structure.

        Une jambe plus longue (calendar) n'est pas échue : elle est marquée à sa
        valeur Black-Scholes résiduelle, pas à l'intrinsèque.
        """
        out = 0.0
        for l in self.legs:
            intr = max(0.0, (S - l.strike) if l.kind == "call" else (l.strike - S))
            residual = max((l.days or self.days) - self.days, 0) / 365.0
            value = intr
            if residual > 0:
                bs = black_scholes(S, l.strike, residual, max(l.iv, 0.02), l.kind)
                value = max(bs, intr)
            out += (value - l.premium) * l.qty
        return out

    def greeks(self) -> Dict[str, float]:
        tot = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}
        for l in self.legs:
            for k in tot:
                tot[k] += l.greeks.get(k, 0.0) * l.qty
        return tot

    def breakevens(self) -> List[float]:
        """Points morts de la structure (payoff nul).

        La fenêtre de recherche est étendue par la prime nette : une prime
        extrême (choc d'IV démesuré) repousse les points morts loin des
        strikes, et la grille doit les suivre — sinon l'interface affiche un
        résultat vide au lieu d'un vrai point mort.
        """
        lo = min(l.strike for l in self.legs)
        hi = max(l.strike for l in self.legs)
        span = max(hi - lo, max(self.spot * 0.05, 1e-9))
        pad = 2.0 * span + abs(self.net_premium)
        start = max(lo - pad, self.spot * 0.01)
        end = hi + pad
        grid = [start + i * (end - start) / 4000 for i in range(4001)]
        vals = [self.payoff(s) for s in grid]
        # On ne conserve que les franchissements : les plateaux exactement à
        # zéro (ailes de butterfly, plages plates) ne produisent qu'un seul
        # point de bord au lieu d'une liste de points de grille redondants.
        out: List[float] = []
        prev_s: Optional[float] = None
        prev_v: Optional[float] = None
        for s, v in zip(grid, vals):
            if v == 0.0:
                if prev_v is not None and prev_v != 0.0:
                    out.append(s)
            elif prev_v is not None and prev_v != 0.0 and prev_v * v < 0.0:
                t = abs(prev_v) / (abs(prev_v) + abs(v))
                out.append(prev_s + t * (s - prev_s))
            prev_s, prev_v = s, v
        return out

    def _eval_grid(self, n: int = 1200) -> List[float]:
        """Grille d'évaluation du payoff.

        Les strikes y sont inclus explicitement : le payoff d'une structure est
        linéaire par morceaux et casse exactement sur les strikes, donc une
        grille purement régulière rate le sommet d'un butterfly de quelques
        dixièmes.
        """
        lo = min(l.strike for l in self.legs) * 0.6
        hi = max(l.strike for l in self.legs) * 1.4
        grid = [lo + i * (hi - lo) / n for i in range(n + 1)]
        grid += [l.strike for l in self.legs]
        grid += [l.strike * (1 + d) for l in self.legs for d in (-1e-6, 1e-6)]
        return sorted(grid)

    def max_loss(self, n: int = 1200) -> float:
        return min(self.payoff(s) for s in self._eval_grid(n))

    def max_profit(self, n: int = 1200) -> float:
        return max(self.payoff(s) for s in self._eval_grid(n))

    def as_dict(self, spot_grid: Optional[Sequence[float]] = None) -> dict:
        g = self.greeks()
        be = self.breakevens()
        d = {
            "name": self.name,
            "underlying": self.underlying,
            "days": self.days,
            "spot": self.spot,
            "net_premium": self.net_premium,
            "cost": self.cost,
            "max_loss": self.max_loss(),
            "max_profit": self.max_profit(),
            "max_loss_bounded": self.max_loss_bounded,
            "max_gain_bounded": self.max_gain_bounded,
            "breakevens": be,
            "greeks": g,
            "note": self.note,
            "legs": [{"kind": l.kind, "strike": l.strike, "qty": l.qty,
                      "premium": l.premium, "iv": l.iv, "days": l.days,
                      "greeks": l.greeks} for l in self.legs],
        }
        if spot_grid:
            d["payoff_curve"] = [{"s": s, "pnl": self.payoff(s)} for s in spot_grid]
        return d


CATALOG: Dict[str, dict] = {
    "strangle": {"label": "Long strangle", "max_loss_bounded": True, "max_gain_bounded": False, "desc": "Call OTM + put OTM. Long gamma / long vega : paie si le sous-jacent bouge fort dans un sens ou dans l'autre, sans payer l'ATM."},
    "short_strangle": {"label": "Short strangle", "max_loss_bounded": False, "max_gain_bounded": True, "desc": "Vente call OTM + put OTM. Encaisse la prime, gagne si le sous-jacent reste dans le range. Risque illimité."},
    "straddle": {"label": "Long straddle", "max_loss_bounded": True, "max_gain_bounded": False, "desc": "Call ATM + put ATM. Le plus pur pari sur l'amplitude, le plus cher en prime."},
    "butterfly": {"label": "Call butterfly", "max_loss_bounded": True, "max_gain_bounded": True, "desc": "+1 / -2 / +1 calls équidistants. Gagne si le sous-jacent finit sur le corps, coût faible, gain plafonné."},
    "put_butterfly": {"label": "Put butterfly", "max_loss_bounded": True, "max_gain_bounded": True, "desc": "+1 / -2 / +1 puts équidistants. Miroir du call butterfly."},
    "iron_condor": {"label": "Iron condor", "max_loss_bounded": True, "max_gain_bounded": True, "desc": "Put spread vendeur + call spread vendeur. Range borné, risque borné, carry de prime."},
    "call_spread": {"label": "Bull call spread", "max_loss_bounded": True, "max_gain_bounded": True, "desc": "Achat call + vente call plus haut. Vue haussière à coût réduit, gain plafonné."},
    "put_spread": {"label": "Bear put spread", "max_loss_bounded": True, "max_gain_bounded": True, "desc": "Achat put + vente put plus bas. Vue baissière à coût réduit, gain plafonné."},
    "risk_reversal": {"label": "Risk reversal", "max_loss_bounded": True, "max_gain_bounded": False, "desc": "Vente put OTM + achat call OTM. Directionnel haussier quasi gratuit, finance le call par le put."},
    "calendar": {"label": "Calendar spread", "max_loss_bounded": True, "max_gain_bounded": True, "desc": "Vente court terme + achat long terme même strike. Joue la différence de theta et la remontée d'IV."},
}


def _leg(underlying: str, kind: str, strike: float, qty: float, years: float,
         spec: config.AssetSpec, spot: float, vol_regime: float,
         iv_shift: float) -> Leg:
    iv = iv_surface(spec, strike / spot, years, vol_regime=vol_regime, iv_shift=iv_shift)
    premium = black_scholes(spot, strike, years, iv, kind)
    g = greeks(spot, strike, years, iv, kind)
    g["iv"] = iv
    return Leg(kind=kind, strike=strike, qty=qty, premium=premium, iv=iv,
               days=int(round(years * 365)), greeks=g)


def build_structure(kind: str, underlying: str, spot: float, days: int = 30,
                    width: float = 0.03, vol_regime: float = 1.0,
                    iv_shift: float = 0.0, long_days: Optional[int] = None
                    ) -> Structure:
    """Construit une structure d'options standardisée.

    ``width`` est l'écart en % du spot entre le spot et les strikes extrêmes
    (3 % = strikes à ±3 %). ``long_days`` ne sert qu'au calendar.
    """
    spec = config.get_asset(underlying)
    T = max(days, 1) / 365.0
    kind = kind.lower()

    step = strike_step(spot, spec)

    def strike(mult: float) -> float:
        return round_strike(spot * mult, spec)

    def leg(k, m, q, d=None, t=None):
        return _leg(underlying, k, strike(m), q, (t if t else T), spec, spot,
                    vol_regime, iv_shift)

    def leg_at(k, price_strike, q):
        """Jambe à un strike explicite — indispensable pour garder les ailes
        symétriques après l'arrondi sur la grille."""
        return _leg(underlying, k, float(price_strike), q, T, spec, spot,
                    vol_regime, iv_shift)

    # Écart arrondi sur un multiple entier du pas : sans ça, l'arrondi des
    # strikes rend les ailes asymétriques et la structure n'est plus un
    # butterfly (perte maximale > prime payée).
    spacing = max(step, round(spot * width / step) * step)

    legs: List[Leg] = []
    note = ""
    if kind == "strangle":
        legs = [leg("call", 1 + width, 1.0), leg("put", 1 - width, 1.0)]
    elif kind == "short_strangle":
        legs = [leg("call", 1 + width, -1.0), leg("put", 1 - width, -1.0)]
    elif kind == "straddle":
        legs = [leg("call", 1.0, 1.0), leg("put", 1.0, 1.0)]
    elif kind == "butterfly":
        body = strike(1.0)
        legs = [leg_at("call", body - spacing, 1.0), leg_at("call", body, -2.0),
                leg_at("call", body + spacing, 1.0)]
    elif kind == "put_butterfly":
        body = strike(1.0)
        legs = [leg_at("put", body - spacing, 1.0), leg_at("put", body, -2.0),
                leg_at("put", body + spacing, 1.0)]
    elif kind == "iron_condor":
        body = strike(1.0)
        inner = max(step, round(spot * width / 2 / step) * step)
        outer = inner * 2
        legs = [leg_at("put", body - outer, 1.0), leg_at("put", body - inner, -1.0),
                leg_at("call", body + inner, -1.0), leg_at("call", body + outer, 1.0)]
    elif kind == "call_spread":
        legs = [leg("call", 1.0, 1.0), leg("call", 1 + width, -1.0)]
    elif kind == "put_spread":
        legs = [leg("put", 1.0, 1.0), leg("put", 1 - width, -1.0)]
    elif kind == "risk_reversal":
        legs = [leg("put", 1 - width, -1.0), leg("call", 1 + width, 1.0)]
    elif kind == "calendar":
        ld = long_days or max(days * 3, days + 30)
        body = strike(1.0)
        legs = [_leg(underlying, "call", body, -1.0, T, spec, spot,
                     vol_regime, iv_shift),
                _leg(underlying, "call", body, 1.0, ld / 365.0, spec, spot,
                     vol_regime, iv_shift)]
        note = f"court {days} j vendu / long {ld} j acheté, même strike"
    else:
        raise KeyError(f"Structure inconnue : {kind!r}. Catalogue : {', '.join(CATALOG)}")

    return Structure(name=CATALOG.get(kind, {}).get("label", kind), underlying=underlying,
                     legs=legs, days=days, spot=spot,
                     max_loss_bounded=bool(CATALOG.get(kind, {}).get("max_loss_bounded", True)),
                     max_gain_bounded=bool(CATALOG.get(kind, {}).get("max_gain_bounded", True)),
                     note=note or CATALOG.get(kind, {}).get("desc", ""))
