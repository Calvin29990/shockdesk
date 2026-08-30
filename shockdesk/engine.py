"""
Moteur de backtest de ShockDesk.

L'API utilisateur reprend la forme Blueshift / Zipline, volontairement :

.. code-block:: python

    def initialize(context):
        context.oil = symbol('BZ=F')
        schedule_function(rebalance, date_rules.every_day())

    def rebalance(context, data):
        f = get_forecast(context.oil)          # prévision ShockLab, point-in-time
        if f and f.sign > 0:
            order_target_percent(context.oil, 0.25)

Différences assumées avec Zipline :

* un seul bar par jour (exécution au close du jour de l'ordre, slippage +
  commission appliqués) ;
* les options sont des contrats synthétiques pricés Black-Scholes sur la surface
  du sous-jacent (voir ``options.py``) — elles se marquent au modèle chaque
  jour et se règlent à l'intrinsèque à l'échéance ;
* ``get_forecast`` ne renvoie que les révisions publiées **avant** la date du
  bar : aucune fuite d'information, c'est la règle de la maison.
"""

from __future__ import annotations

import io
import math
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from . import config, options as opt
from .marketdata import PricePanel
from .scenarios import Forecast, ForecastLedger

AssetKey = Union[str, opt.OptionContract]


# --------------------------------------------------------------------------- #
# Positions & portefeuille
# --------------------------------------------------------------------------- #
@dataclass
class Position:
    asset: AssetKey
    amount: float = 0.0
    cost_basis: float = 0.0          # prix moyen pondéré (par unité de sous-jacent)
    last_sale_price: float = 0.0
    realized_pnl: float = 0.0
    opened_on: Optional[str] = None

    @property
    def multiplier(self) -> float:
        if isinstance(self.asset, opt.OptionContract):
            return config.get_asset(self.asset.underlying).multiplier
        return config.get_asset(self.asset).multiplier

    @property
    def market_value(self) -> float:
        return self.amount * self.last_sale_price * self.multiplier

    @property
    def unrealized_pnl(self) -> float:
        return (self.last_sale_price - self.cost_basis) * self.amount * self.multiplier

    def as_dict(self) -> dict:
        a = self.asset
        if isinstance(a, opt.OptionContract):
            sym, label, kind = a.underlying, a.label, "option"
        else:
            spec = config.get_asset(a)
            sym, label, kind = a, f"{a} — {spec.name}", spec.asset_type
        return {
            "sid": a.sid if isinstance(a, opt.OptionContract) else a,
            "symbol": sym, "label": label, "type": kind,
            "amount": round(self.amount, 6),
            "cost_basis": round(self.cost_basis, 6),
            "last_sale_price": round(self.last_sale_price, 6),
            "market_value": round(self.market_value, 2),
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "opened_on": self.opened_on,
        }


class Portfolio:
    def __init__(self, cash: float):
        self.start_cash = float(cash)
        self.cash = float(cash)
        self.positions: Dict[AssetKey, Position] = {}
        self.portfolio_value = float(cash)
        self.pnl = 0.0
        self.returns = 0.0

    def as_dict(self) -> dict:
        return {
            "cash": round(self.cash, 2),
            "portfolio_value": round(self.portfolio_value, 2),
            "pnl": round(self.pnl, 2),
            "returns": round(self.returns, 6),
            "start_cash": round(self.start_cash, 2),
            "positions": [p.as_dict() for p in self.positions.values() if abs(p.amount) > 1e-12],
        }


@dataclass
class Order:
    asset: AssetKey
    amount: float
    reason: str = "user"


@dataclass
class Trade:
    date: str
    sid: str
    symbol: str
    side: str
    amount: float
    price: float
    commission: float
    gross: float
    reason: str


# --------------------------------------------------------------------------- #
# Contextes exposés au code utilisateur
# --------------------------------------------------------------------------- #
class DataContext:
    def __init__(self, engine: "BacktestEngine"):
        self._e = engine

    def current(self, asset: AssetKey, fields="close"):
        return self._e.current_price(asset, fields)

    def can_trade(self, asset: AssetKey) -> bool:
        if isinstance(asset, opt.OptionContract):
            return self._e.current_price(asset.underlying) is not None
        return asset in self._e.panel.close.columns

    def history(self, asset: AssetKey, fields="close", bar_count: int = 5,
                frequency: str = "1d") -> Any:
        return self._e.history(asset, fields, bar_count)


class _DateRules:
    """Règles de planification (fermetures avec état, donc sans effet de bord
    partagé entre stratégies)."""

    @staticmethod
    def every_day():
        return lambda dt, i: True

    @staticmethod
    def every_n_days(n: int):
        n = max(int(n), 1)
        return lambda dt, i: i % n == 0

    @staticmethod
    def week_start(days_offset: int = 0):
        state = {}

        def rule(dt, i):
            iso = dt.isocalendar()
            key = (iso[0], iso[1])
            if state.get("key") != key:
                state["key"] = key
                return True
            return False
        return rule

    @staticmethod
    def month_start(days_offset: int = 0):
        state = {}

        def rule(dt, i):
            key = (dt.year, dt.month)
            if state.get("key") != key:
                state["key"] = key
                return True
            return False
        return rule

    @staticmethod
    def month_end(days_offset: int = 0):
        return lambda dt, i: (dt + pd.tseries.offsets.BDay(1)).month != dt.month


class _TimeRules:
    """Un seul bar par jour : les règles horaires sont conservées pour la
    compatibilité d'écriture, elles ne changent rien à l'exécution."""

    @staticmethod
    def market_open(hours: int = 0, minutes: int = 0):
        return lambda dt: dt

    @staticmethod
    def market_close(hours: int = 0, minutes: int = 0):
        return lambda dt: dt

    @staticmethod
    def every_minute():
        return lambda dt: dt


_SEEN: Dict[str, Any] = {}


def _is_first_seen(dt, period, offset) -> bool:
    key = f"{period}-{dt.year}-{dt.month}"
    if _SEEN.get(key) == dt:
        return False
    return True


def _nth_of_month_week(dt, period, offset) -> bool:
    return dt.weekday() == offset % 5


class _Logger:
    def __init__(self, engine: "BacktestEngine"):
        self._e = engine

    def info(self, msg: str):
        self._e.log_line(str(msg), "info")

    def warn(self, msg: str):
        self._e.log_line(str(msg), "warning")

    def error(self, msg: str):
        self._e.log_line(str(msg), "error")


# --------------------------------------------------------------------------- #
# Moteur
# --------------------------------------------------------------------------- #
@dataclass
class EngineSettings:
    commission_per_share: float = 0.005
    commission_min: float = 1.0
    commission_per_contract: float = 0.65
    slippage_bps: float = 5.0
    allow_short: bool = True
    max_leverage: float = 2.0
    # Taux sans risque annualisé, retiré du rendement dans le Sharpe et le
    # Sortino. Il est retiré CHAQUE barre, y compris celles où le book dort en
    # liquidités — or le moteur ne rémunère pas le cash. Sur une stratégie qui
    # sort au pic et reste en cash, ce terme fixe écrase le ratio : le rendre
    # paramétrable (et l'afficher) permet au moins de le lire en connaissance
    # de cause. Le mettre à 0 redonne un Sharpe « brut ».
    risk_free: float = 0.041


class BacktestEngine:
    """Boucle de backtest journalière."""

    def __init__(self, panel: PricePanel, universe: str, capital: float,
                 settings: Optional[EngineSettings] = None,
                 ledger: Optional[ForecastLedger] = None):
        self.panel = panel
        self.universe = universe
        self.settings = settings or EngineSettings()
        self.ledger = ledger or ForecastLedger()
        self.portfolio = Portfolio(capital)
        self.log = _Logger(self)

        self._date: pd.Timestamp = panel.dates[0]
        self._i = 0
        self._records: Dict[str, Dict[str, float]] = {}
        self._logs: List[dict] = []
        self._orders: List[Order] = []
        self._trades: List[Trade] = []
        self._sched: List[Tuple[Callable, Callable, Callable]] = []
        self._equity: List[float] = []
        self._attribution: Dict[str, float] = {}
        self._greek_history: List[dict] = []
        self._contract_cache: Dict[str, opt.OptionContract] = {}
        self._marks: Dict[AssetKey, float] = {}
        self._closed_contracts: Dict[str, dict] = {}
        self._error: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Prix & séries
    # ------------------------------------------------------------------ #
    def _spot(self, symbol: str) -> Optional[float]:
        if symbol not in self.panel.close.columns:
            return None
        v = self.panel.close.at[self._date, symbol]
        return None if pd.isna(v) else float(v)

    def current_price(self, asset: AssetKey, fields: str = "close") -> Optional[float]:
        if isinstance(asset, opt.OptionContract):
            return self.option_price(asset)
        if fields and fields != "close":
            frame = getattr(self.panel, fields, None)
            if frame is not None and asset in frame.columns:
                v = frame.at[self._date, asset]
                return None if pd.isna(v) else float(v)
        return self._spot(asset)

    def history(self, asset: AssetKey, fields="close", bar_count: int = 5):
        i = self.panel.dates.get_loc(self._date)
        lo = max(0, i - int(bar_count) + 1)
        window = self.panel.dates[lo:i + 1]
        if isinstance(asset, opt.OptionContract):
            series = pd.Series({d.date(): self.option_price(asset, on=d) for d in window})
            series.index = window
            return series
        frame = getattr(self.panel, fields if isinstance(fields, str) else "close")
        if isinstance(fields, (list, tuple)):
            return frame.loc[window, [asset]] if asset in frame.columns else None
        if asset not in frame.columns:
            return None
        return frame.loc[window, asset]

    def vol_regime(self, symbol: str, window: int = 20) -> float:
        """Vol réalisée / vol calibrée. 1.0 = régime normal."""
        s = self.history(symbol, "close", window + 1)
        if s is None or len(s) < 6:
            return 1.0
        rv = float(np.std(np.diff(np.log(s.to_numpy())), ddof=0) * np.sqrt(config.TRADING_DAYS))
        base = config.get_asset(symbol).ann_vol
        return float(min(max(rv / base, 0.55), 2.6)) if base > 0 else 1.0

    # ------------------------------------------------------------------ #
    # Options
    # ------------------------------------------------------------------ #
    def iv_shift(self, symbol: str, on=None) -> float:
        """Choc d'IV (en points décimaux) actif à la date courante, si un
        scénario en prévoit un."""
        f = self.ledger.active(self._date if on is None else pd.Timestamp(on), symbol)
        return float(f.iv_shift) if f else 0.0

    def get_iv(self, symbol: str, moneyness: float = 1.0, days: int = 30) -> float:
        spec = config.get_asset(symbol)
        return opt.iv_surface(spec, moneyness, days / 365.0,
                              vol_regime=self.vol_regime(symbol),
                              iv_shift=self.iv_shift(symbol))

    def option_price(self, contract: opt.OptionContract, on=None) -> float:
        d = self._date if on is None else pd.Timestamp(on)
        spot = self._spot(contract.underlying)
        if spot is None:
            return 0.0
        years = max((pd.Timestamp(contract.expiry) - d).days, 0) / 365.0
        spec = config.get_asset(contract.underlying)
        price, _ = opt.contract_price(contract, spot, years, spec,
                                      vol_regime=self.vol_regime(contract.underlying),
                                      iv_shift=self.iv_shift(contract.underlying))
        return float(price)

    def make_contract(self, underlying: str, kind: str = "call",
                      strike: Optional[float] = None, moneyness: float = 1.0,
                      days: int = 30) -> opt.OptionContract:
        spot = self._spot(underlying)
        if spot is None:
            raise ValueError(f"{underlying} n'est pas dans l'univers du backtest "
                             f"({self.universe}).")
        spec = config.get_asset(underlying)
        if not spec.options:
            raise ValueError(f"{underlying} n'a pas d'options modélisées.")
        expiry = (self._date + pd.Timedelta(days=int(days))).normalize()
        expiry = expiry + pd.Timedelta(days=(4 - expiry.weekday()) % 7)
        if strike is None:
            strike = opt.round_strike(spot * float(moneyness), spec)
        strike = float(strike)
        c = opt.OptionContract(underlying=underlying, kind=kind, strike=strike,
                               expiry=str(pd.Timestamp(expiry).date()))
        self._contract_cache[c.sid] = c
        return c

    # ------------------------------------------------------------------ #
    # Journal
    # ------------------------------------------------------------------ #
    def log_line(self, msg: str, level: str = "info"):
        self._logs.append({"date": self._date.date().isoformat(), "level": level,
                           "message": msg[:800]})

    # ------------------------------------------------------------------ #
    # Ordres
    # ------------------------------------------------------------------ #
    def _submit(self, asset: AssetKey, amount: float, reason: str = "user"):
        if amount is None or (isinstance(amount, float) and math.isnan(amount)):
            return None
        if abs(amount) < 1e-9:
            return None
        if isinstance(asset, opt.OptionContract):
            amount = float(int(round(amount)))         # les contrats sont entiers
            if amount == 0:
                return None
        o = Order(asset=asset, amount=float(amount), reason=reason)
        self._orders.append(o)
        return o

    def order(self, asset, amount, reason="user"):
        return self._submit(asset, amount, reason)

    def order_value(self, asset, value, reason="user"):
        p = self.current_price(asset)
        if not p:
            return None
        mult = self._multiplier(asset)
        qty = value / (p * mult)
        if isinstance(asset, opt.OptionContract):
            qty = int(round(qty))
        return self._submit(asset, qty, reason)

    def order_target(self, asset, target, reason="user"):
        cur = self.portfolio.positions.get(asset)
        return self._submit(asset, float(target) - (cur.amount if cur else 0.0), reason)

    def order_target_value(self, asset, value, reason="user"):
        p = self.current_price(asset)
        if not p:
            return None
        return self.order_target(asset, value / (p * self._multiplier(asset)), reason)

    def order_target_percent(self, asset, pct, reason="user"):
        if isinstance(asset, opt.OptionContract):
            self.log.warn("order_target_percent sur une option : pourcentage du "
                          "portefeuille en notionnel, arrondi au contrat.")
        target_value = self.portfolio.portfolio_value * float(pct)
        return self.order_target_value(asset, target_value, reason)

    @staticmethod
    def _multiplier(asset: AssetKey) -> float:
        if isinstance(asset, opt.OptionContract):
            return config.get_asset(asset.underlying).multiplier
        return config.get_asset(asset).multiplier

    @staticmethod
    def _contract_size(asset: AssetKey) -> float:
        """Unités du sous-jacent couvertes par un contrat (1 pour une part d'ETF)."""
        try:
            return float(config.get_asset(asset.underlying).contract_size) or 1.0
        except Exception:
            try:
                return float(config.get_asset(asset).contract_size) or 1.0
            except Exception:
                return 1.0

    # ------------------------------------------------------------------ #
    # Exécution
    # ------------------------------------------------------------------ #
    def _gross_exposure(self) -> float:
        return sum(abs(p.market_value) for p in self.portfolio.positions.values())

    def _execute(self) -> float:
        """Exécute les ordres au close du jour. Renvoie le P&L de coût de
        transaction (négatif).

        Garde-fou : l'exposition brute est plafonnée à ``max_leverage`` fois
        l'actif net. Un ordre qui ferait sauter le plafond est réduit d'autant,
        avec un avertissement dans le journal — mieux vaut un backtest borné
        qu'un résultat absurde.
        """
        if not self._orders:
            return 0.0
        s = self.settings
        slip = s.slippage_bps / 10000.0
        cost_total = 0.0
        for o in self._orders:
            asset = o.asset
            close_px = self._spot(asset.underlying) if isinstance(asset, opt.OptionContract) else self._spot(asset)
            if close_px is None:
                continue
            px = self.option_price(asset) if isinstance(asset, opt.OptionContract) else close_px
            if px <= 0 and not isinstance(asset, opt.OptionContract):
                continue
            cap = s.max_leverage * max(self.portfolio.portfolio_value, 1.0)
            mult_chk = self._multiplier(asset)
            projected = self._gross_exposure() + abs(o.amount) * px * mult_chk
            if projected > cap:
                room = max(cap - (self._gross_exposure()
                                  - abs((self.portfolio.positions.get(asset).amount
                                         if self.portfolio.positions.get(asset) else 0.0)
                                        * px * mult_chk)), 0.0)
                allowed = room / (px * mult_chk) if px > 0 else 0.0
                if isinstance(asset, opt.OptionContract):
                    allowed = float(int(allowed))
                if abs(o.amount) > allowed:
                    kept = allowed if o.amount > 0 else -allowed
                    self.log_line(f"Ordre sur {getattr(asset, 'sid', asset)} réduit de "
                                  f"{o.amount:,.2f} à {kept:,.2f} : plafond de levier "
                                  f"{s.max_leverage:g}x atteint.", "warning")
                    o.amount = kept
                if abs(o.amount) < 1e-9:
                    continue
            if not s.allow_short:
                pos = self.portfolio.positions.get(asset)
                held = pos.amount if pos else 0.0
                if held + o.amount < 0:
                    o.amount = -held
                    if abs(o.amount) < 1e-9:
                        continue
            exec_px = px * (1 + slip) if o.amount > 0 else px * (1 - slip)
            mult = self._multiplier(asset)
            gross = o.amount * exec_px * mult
            if isinstance(asset, opt.OptionContract):
                # Les quantités du moteur sont en unités du sous-jacent, alors que
                # le frais est facturé par contrat : on ramène donc la quantité au
                # nombre de contrats réels. Sans ça, une option à 4,25 $ l'unité
                # payait 0,65 $ de frais, soit ~15 % de la prime (et ~30 % l'aller-
                # retour), ce qui rendait toute stratégie d'options structurellement
                # perdante. 1 contrat Brent = 1 000 barils, 1 contrat or = 100 onces.
                commission = abs(o.amount) / self._contract_size(asset) \
                    * s.commission_per_contract
            else:
                commission = max(abs(o.amount) * s.commission_per_share, s.commission_min)
            self.portfolio.cash -= gross
            self.portfolio.cash -= commission

            pos = self.portfolio.positions.setdefault(asset, Position(asset=asset))
            if pos.opened_on is None and pos.amount == 0:
                pos.opened_on = self._date.date().isoformat()
            new_amount = pos.amount + o.amount
            if pos.amount * o.amount < 0:                       # réduction / retournement
                closed = min(abs(pos.amount), abs(o.amount))
                direction = 1 if pos.amount > 0 else -1
                pos.realized_pnl += direction * (exec_px - pos.cost_basis) * closed * mult
            if new_amount != 0:
                if abs(new_amount) > abs(pos.amount) or pos.amount == 0:
                    # prix moyen pondéré sur la partie qui augmente
                    added = abs(new_amount) - abs(pos.amount) if pos.amount != 0 else abs(new_amount)
                    total = abs(new_amount)
                    pos.cost_basis = ((pos.cost_basis * (total - added)) + exec_px * added) / total
            else:
                pos.cost_basis = 0.0
            pos.amount = new_amount
            pos.last_sale_price = px

            cost_total += -abs(commission) + o.amount * (px - exec_px) * mult
            sym = asset.underlying if isinstance(asset, opt.OptionContract) else asset
            self._trades.append(Trade(
                date=self._date.date().isoformat(),
                sid=asset.sid if isinstance(asset, opt.OptionContract) else sym,
                symbol=sym,
                side="buy" if o.amount > 0 else "sell",
                amount=round(o.amount, 6), price=round(exec_px, 6),
                commission=round(commission, 2), gross=round(gross, 2), reason=o.reason))
            self._attribution[sym] = self._attribution.get(sym, 0.0) + \
                o.amount * (px - exec_px) * mult - commission
        self._orders = []
        return cost_total

    def _settle_expiries(self):
        """Règle les options échues à l'intrinsèque du jour."""
        today = self._date
        for asset, pos in list(self.portfolio.positions.items()):
            if not isinstance(asset, opt.OptionContract) or abs(pos.amount) < 1e-9:
                continue
            if pd.Timestamp(asset.expiry) <= today:
                spot = self._spot(asset.underlying) or 0.0
                intrinsic = max(0.0, (spot - asset.strike) if asset.kind == "call"
                                else (asset.strike - spot))
                mult = self._multiplier(asset)
                direction = 1 if pos.amount > 0 else -1
                pos.realized_pnl += direction * (intrinsic - pos.cost_basis) * abs(pos.amount) * mult
                self.portfolio.cash += pos.amount * intrinsic * mult
                self._attribution[asset.underlying] = self._attribution.get(asset.underlying, 0.0) + \
                    pos.amount * (intrinsic - pos.last_sale_price) * mult
                self.log_line(f"Échéance {asset.label} réglée à l'intrinsèque "
                              f"{intrinsic:.2f} (spot {spot:.2f}).")
                del self.portfolio.positions[asset]

    def _mark(self):
        for asset, pos in self.portfolio.positions.items():
            px = self.option_price(asset) if isinstance(asset, opt.OptionContract) \
                else self._spot(asset)
            if px is None:
                continue
            pos.last_sale_price = px
        mv = sum(p.market_value for p in self.portfolio.positions.values())
        self.portfolio.portfolio_value = self.portfolio.cash + mv
        self.portfolio.pnl = self.portfolio.portfolio_value - self.portfolio.start_cash
        self.portfolio.returns = (self.portfolio.portfolio_value / self.portfolio.start_cash - 1.0)

    def _book_greeks(self) -> dict:
        g = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}
        for asset, pos in self.portfolio.positions.items():
            if isinstance(asset, opt.OptionContract):
                spot = self._spot(asset.underlying) or 0.0
                years = max((pd.Timestamp(asset.expiry) - self._date).days, 0) / 365.0
                _, gr = opt.contract_price(asset, spot, years,
                                           config.get_asset(asset.underlying),
                                           vol_regime=self.vol_regime(asset.underlying),
                                           iv_shift=self.iv_shift(asset.underlying))
                for k in ("delta", "gamma", "vega", "theta"):
                    g[k] += gr[k] * pos.amount
                g["delta"] += 0.0
            else:
                g["delta"] += pos.amount
        return g

    # ------------------------------------------------------------------ #
    # API utilisateur
    # ------------------------------------------------------------------ #
    def get_forecast(self, symbol: str) -> Optional[Forecast]:
        return self.ledger.active(self._date, symbol)

    def build_namespace(self) -> Dict[str, Any]:
        engine = self
        ns: Dict[str, Any] = {}

        def symbol(s: str) -> str:
            if s not in engine.panel.close.columns:
                raise KeyError(f"{s!r} n'est pas dans l'univers « {engine.universe} » "
                               f"(disponibles : {', '.join(engine.panel.close.columns)}).")
            return s

        def symbols(*args) -> List[str]:
            flat = [a for arg in args for a in (arg if isinstance(arg, (list, tuple)) else [arg])]
            return [symbol(s) for s in flat]

        def schedule_function(func, date_rule=None, time_rule=None, half_days=True):
            engine._sched.append((func, date_rule or _DateRules.every_day(),
                                  time_rule or _TimeRules.market_open()))

        def record(**kwargs):
            """Séries personnalisées, indexées par date de bar (les jours sans
            appel héritent de la valeur précédente au moment du rapport)."""
            for k, v in kwargs.items():
                engine._records.setdefault(k, {})[str(engine._date.date())] = float(v)

        def get_datetime():
            return engine._date.to_pydatetime()

        def option_contract(underlying, kind="call", strike=None, moneyness=1.0, days=30):
            return engine.make_contract(underlying, kind, strike, moneyness, days)

        def get_iv(underlying, moneyness=1.0, days=30):
            return engine.get_iv(underlying, moneyness, days)

        def vol_regime(underlying, window=20):
            return engine.vol_regime(underlying, window)

        def get_forecast(underlying):
            return engine.get_forecast(underlying)

        def get_scenario(name):
            return engine.ledger.get(name)

        def set_commission(**kw):
            if "per_share" in kw:
                engine.settings.commission_per_share = float(kw["per_share"])
            if "min_trade_cost" in kw:
                engine.settings.commission_min = float(kw["min_trade_cost"])
            if "per_contract" in kw:
                engine.settings.commission_per_contract = float(kw["per_contract"])

        def set_slippage(**kw):
            if "bps" in kw:
                engine.settings.slippage_bps = float(kw["bps"])
            if "fixed" in kw:
                engine.settings.slippage_bps = float(kw["fixed"]) / 100.0

        class _Ctx:
            pass

        ctx = _Ctx()
        ctx.portfolio = engine.portfolio
        ctx.cash = engine.portfolio.cash
        ctx.universe = engine.universe
        ctx.data_source = engine.panel.source
        ns.update({
            "symbol": symbol, "symbols": symbols,
            "order": engine.order, "order_value": engine.order_value,
            "order_target": engine.order_target,
            "order_target_value": engine.order_target_value,
            "order_target_percent": engine.order_target_percent,
            "schedule_function": schedule_function,
            "date_rules": _DateRules, "time_rules": _TimeRules,
            "record": record, "get_datetime": get_datetime,
            "option_contract": option_contract, "get_iv": get_iv,
            "vol_regime": vol_regime, "get_forecast": get_forecast,
            "get_scenario": get_scenario,
            "set_commission": set_commission, "set_slippage": set_slippage,
            "log": engine.log, "math": math, "np": np, "pd": pd,
            "config": config, "options": opt,
            "structures": opt.CATALOG,
        })
        return ns, ctx

    # ------------------------------------------------------------------ #
    # Boucle principale
    # ------------------------------------------------------------------ #
    def run(self, source: str, start=None, end=None) -> dict:
        ns, ctx = self.build_namespace()
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = compile(source, "<strategie>", "exec")
                exec(code, ns)
        except Exception as exc:
            self._error = f"Erreur de compilation : {exc}\n{traceback.format_exc(limit=4)}"
            return self.report(error=self._error)

        for hook in ("initialize",):
            if hook in ns and callable(ns[hook]):
                try:
                    with redirect_stdout(buf):
                        ns[hook](ctx)
                except Exception as exc:
                    self._error = f"initialize() : {exc}\n{traceback.format_exc(limit=4)}"
                    return self.report(error=self._error)

        ctx.portfolio = self.portfolio
        data = DataContext(self)
        self._mark()
        self._equity.append(self.portfolio.portfolio_value)

        dates = list(self.panel.dates)
        for i, dt in enumerate(dates):
            self._date = dt
            self._i = i
            ctx.cash = self.portfolio.cash

            self._settle_expiries()
            self._mark()
            prev_equity = self.portfolio.portfolio_value

            if "before_trading_start" in ns and callable(ns["before_trading_start"]):
                try:
                    with redirect_stdout(buf):
                        sig = ns["before_trading_start"].__code__.co_argcount
                        if sig >= 2:
                            ns["before_trading_start"](ctx, data)
                        else:
                            ns["before_trading_start"](ctx)
                except Exception as exc:
                    self.log_line(f"before_trading_start : {exc}", "error")

            ran = False
            for func, drule, _trule in self._sched:
                try:
                    if drule(dt, i):
                        with redirect_stdout(buf):
                            sig = func.__code__.co_argcount
                            func(ctx, data) if sig >= 2 else func(ctx)
                        ran = True
                except Exception as exc:
                    self.log_line(f"{getattr(func, '__name__', 'func')} : {exc}", "error")
                    self._error = self._error or f"{getattr(func, '__name__', 'func')} : {exc}"

            if not ran and "handle_data" in ns and callable(ns["handle_data"]):
                try:
                    with redirect_stdout(buf):
                        sig = ns["handle_data"].__code__.co_argcount
                        ns["handle_data"](ctx, data) if sig >= 2 else ns["handle_data"](ctx)
                except Exception as exc:
                    self.log_line(f"handle_data : {exc}", "error")
                    self._error = self._error or f"handle_data : {exc}"

            # P&L de marché par ligne, avant exécution
            for asset, pos in self.portfolio.positions.items():
                sym = asset.underlying if isinstance(asset, opt.OptionContract) else asset
                prev_px = self._marks.get(asset)
                px = pos.last_sale_price
                if prev_px is not None and abs(pos.amount) > 1e-12:
                    self._attribution[sym] = self._attribution.get(sym, 0.0) + \
                        pos.amount * (px - prev_px) * pos.multiplier
            self._execute()
            self._mark()
            for asset, pos in self.portfolio.positions.items():
                self._marks[asset] = pos.last_sale_price

            greeks = self._book_greeks()
            self._greek_history.append({
                "date": dt.date().isoformat(),
                "equity": round(self.portfolio.portfolio_value, 2),
                "pnl": round(self.portfolio.portfolio_value - prev_equity, 2),
                **{k: round(v, 4) for k, v in greeks.items()},
            })
            self._equity.append(self.portfolio.portfolio_value)

        out = buf.getvalue().strip()
        if out:
            for line in out.splitlines()[:200]:
                self.log_line(line, "stdout")

        # Une position encore ouverte à la dernière barre entre dans le P&L final
        # par sa seule valeur de marché, sans jamais avoir été débouclée. On le
        # signale au lieu de le laisser se fondre dans le résultat : sur l'exercice
        # publié, la ré-entrée r2 du 28/08 pesait ainsi ~21 k$ sur le P&L affiché.
        open_pos = [(a, pos) for a, pos in self.portfolio.positions.items()
                    if abs(pos.amount) > 1e-9]
        if open_pos:
            latent = sum(pos.unrealized_pnl for _a, pos in open_pos)
            self.log_line(
                f"Fin de backtest : {len(open_pos)} position(s) encore ouverte(s), "
                f"P&L latent {latent:+,.0f} $ compris dans le résultat.", "warning")
        return self.report()

    # ------------------------------------------------------------------ #
    def report(self, error: Optional[str] = None) -> dict:
        dates = [d.date().isoformat() for d in self.panel.dates]
        eq = np.array(self._equity, dtype=float)
        idx = [dates[0]] + dates[:-1] if len(dates) > 1 else dates
        # _equity a len(dates)+1 éléments : valeur initiale puis fin de chaque
        # jour. Si l'exécution a échoué avant la boucle, on renvoie une série
        # vide plutôt qu'une erreur de longueur.
        idx = pd.to_datetime(dates)
        series = (pd.Series(eq[1:], index=idx) if len(eq) - 1 == len(idx)
                  else pd.Series(dtype=float))
        recs = {}
        for k, values in self._records.items():
            s = pd.Series(values)
            s.index = pd.to_datetime(s.index)
            recs[k] = s.reindex(pd.to_datetime(dates)).ffill()
        return {
            "error": error,
            "equity": series,
            "records": recs,
            "logs": self._logs,
            "trades": [t.__dict__ for t in self._trades],
            "attribution": {k: round(v, 2) for k, v in sorted(self._attribution.items(),
                                                              key=lambda kv: -kv[1])},
            "greeks": self._greek_history,
            "portfolio": self.portfolio.as_dict(),
            "settings": self.settings.__dict__,
        }
