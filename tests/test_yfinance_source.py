"""
Tests unitaires et d'intégration pour la source de données Yahoo Finance (yfinance).

Ces tests valident le chargement, le parsing, le repli gracieux (fallback)
en cas d'erreur réseau, et l'intégration avec le moteur de backtest.
Le téléchargement Yahoo est simulé (mocked) afin de garantir des tests
déterministes, rapides et isolés du réseau externe.
"""

import math
import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shockdesk import api, config
from shockdesk.engine import BacktestEngine, EngineSettings
from shockdesk.marketdata import PricePanel, _load_yfinance, load_panel


# --------------------------------------------------------------------------- #
# Fixtures & Données simulées
# --------------------------------------------------------------------------- #
def _make_mock_yfinance_df(symbols, start="2026-07-01", periods=40):
    """Génère un DataFrame simulé au format multi-index retourné par yf.download."""
    dates = pd.bdate_range(start=start, periods=periods)
    data = {}
    for col in ("Open", "High", "Low", "Close", "Volume"):
        sub_df = pd.DataFrame(index=dates)
        for i, sym in enumerate(symbols):
            base_price = 100.0 + i * 50.0
            # Petite marche aléatoire déterministe
            trend = np.linspace(0, 5.0, periods) + np.sin(np.linspace(0, 3, periods))
            sub_df[sym] = base_price + trend + (0.5 if col == "High" else (-0.5 if col == "Low" else 0.0))
        data[col] = sub_df
    
    # yfinance retourne un DataFrame avec colonnes MultiIndex (Price, Ticker)
    # ou un dictionnaire selon la version
    tuples = [(field, sym) for field in data for sym in symbols]
    multi_cols = pd.MultiIndex.from_tuples(tuples, names=["Price", "Ticker"])
    df = pd.DataFrame(index=dates, columns=multi_cols)
    for field in ("Open", "High", "Low", "Close", "Volume"):
        for sym in symbols:
            df[(field, sym)] = data[field][sym]
    return df


# --------------------------------------------------------------------------- #
# Tests du chargeur yfinance (_load_yfinance)
# --------------------------------------------------------------------------- #
def test_load_yfinance_succes_multi_actifs():
    """Vérifie que _load_yfinance extrait correctement les tables OHLC."""
    symbols = ["SPY", "TLT", "^GSPC"]
    mock_df = _make_mock_yfinance_df(symbols, start="2026-07-01", periods=30)

    with patch("yfinance.download", return_value=mock_df) as mock_dl:
        res = _load_yfinance(symbols, "2026-07-01", "2026-08-15")
        assert res is not None
        assert set(res.keys()) == {"open", "high", "low", "close"}
        for f in ("open", "high", "low", "close"):
            assert isinstance(res[f], pd.DataFrame)
            assert list(res[f].columns) == symbols
            assert len(res[f]) == 30
        mock_dl.assert_called_once()


def test_load_yfinance_single_symbol():
    """Vérifie le parsing pour un sous-jacent unique."""
    symbols = ["BZ=F"]
    dates = pd.bdate_range(start="2026-07-01", periods=20)
    df = pd.DataFrame({
        "Open": np.linspace(80, 85, 20),
        "High": np.linspace(81, 86, 20),
        "Low": np.linspace(79, 84, 20),
        "Close": np.linspace(80.5, 85.5, 20),
    }, index=dates)

    with patch("yfinance.download", return_value=df):
        res = _load_yfinance(symbols, "2026-07-01", "2026-07-28")
        assert res is not None
        assert "close" in res
        assert "BZ=F" in res["close"].columns
        assert len(res["close"]) == 20


def test_load_yfinance_retourne_none_si_vide():
    """Un retour vide de Yahoo doit retourner None sans lever d'exception."""
    with patch("yfinance.download", return_value=pd.DataFrame()):
        res = _load_yfinance(["SPY"], "2026-07-01", "2026-08-01")
        assert res is None

    with patch("yfinance.download", return_value=None):
        res = _load_yfinance(["SPY"], "2026-07-01", "2026-08-01")
        assert res is None


def test_load_yfinance_gere_les_erreurs_reseau():
    """Une exception levée par yf.download (ex: SSL / timeout) doit être rattrapée."""
    with patch("yfinance.download", side_effect=ConnectionError("Yahoo finance inaccessible")):
        res = _load_yfinance(["SPY", "TLT"], "2026-07-01", "2026-08-01")
        assert res is None


# --------------------------------------------------------------------------- #
# Tests de l'intégration dans load_panel
# --------------------------------------------------------------------------- #
def test_load_panel_source_yfinance_explicite():
    """load_panel avec source='yfinance' utilise le panneau extrait de Yahoo."""
    symbols = config.get_universe("us-equities")["symbols"]
    bench = config.get_universe("us-equities")["benchmark"]
    all_syms = list(symbols) + ([bench] if bench not in symbols else [])
    mock_df = _make_mock_yfinance_df(all_syms, start="2026-07-01", periods=30)

    with patch("shockdesk.marketdata._load_yfinance") as mock_loader:
        mock_loader.return_value = {
            "open": mock_df["Open"],
            "high": mock_df["High"],
            "low": mock_df["Low"],
            "close": mock_df["Close"],
        }
        panel = load_panel("us-equities", "2026-07-01", "2026-08-10", source="yfinance")
        assert panel.source == "yfinance"
        assert "Yahoo Finance" in panel.source_detail
        assert len(panel.close) == 30
        assert set(panel.symbols) == set(all_syms)


def test_load_panel_auto_fallback_vers_synthetique_si_yfinance_echoue():
    """En mode auto, si Yahoo échoue, le système bascule sur le modèle synthétique."""
    with patch("shockdesk.marketdata._load_yfinance", return_value=None):
        panel = load_panel("global-macro", "2026-07-01", "2026-08-28", source="auto")
        assert panel.source in ("synthetic", "csv")
        assert len(panel.close) > 20
        # Vérifie que les données synthétiques sont cohérentes
        assert "BZ=F" in panel.close.columns


# --------------------------------------------------------------------------- #
# Test de bout en bout : Exécution d'un backtest sur données yfinance
# --------------------------------------------------------------------------- #
def test_backtest_moteur_sur_donnees_yfinance():
    """Un backtest complet s'exécute parfaitement sur un panel yfinance."""
    symbols = ["SPY", "TLT", "^GSPC"]
    mock_df = _make_mock_yfinance_df(symbols, start="2026-07-01", periods=35)
    
    frames = {
        "open": mock_df["Open"],
        "high": mock_df["High"],
        "low": mock_df["Low"],
        "close": mock_df["Close"],
    }
    
    with patch("shockdesk.marketdata._load_yfinance", return_value=frames):
        panel = load_panel("us-equities", "2026-07-01", "2026-08-15", source="yfinance")
        assert panel.source == "yfinance"
        
        # Stratégie simple de momentum / buy & hold
        code = """
def initialize(context):
    context.asset = symbol('SPY')
    schedule_function(trade, date_rules.every_day())

def trade(context, data):
    if not context.portfolio.positions:
        order_target_percent(context.asset, 0.5)
"""
        eng = BacktestEngine(panel, "us-equities", 100000)
        res = eng.run(code)
        
        assert res["error"] is None
        assert "equity" in res
        assert len(res["equity"]) == len(panel.close)
        assert res["equity"].iloc[-1] > 0
        assert "SPY" in res["attribution"]
