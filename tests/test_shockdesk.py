"""
Tests ShockDesk.

Ils couvrent les quatre couches qui portent le projet :

* les **données** (ancrage, reconstruction de l'exercice publié) ;
* le **pricing d'options** (parité call/put, symétrie des structures, IV) ;
* le **moteur de backtest** (P&L, coûts, échéance d'option, plafond de levier,
  attribution qui se réconcilie avec l'équité) ;
* l'**anticipation** (prévisions point-in-time, scoring net du drift).
"""

import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shockdesk import api, cli, config, metrics, options as opt, registry  # noqa: E402
from shockdesk.engine import BacktestEngine, EngineSettings  # noqa: E402
from shockdesk.marketdata import load_panel  # noqa: E402
from shockdesk.scenarios import ForecastLedger, scorecard, validate  # noqa: E402

STRAT_DIR = os.path.join(config.REPO_ROOT, "strategies")


# --------------------------------------------------------------------------- #
# Données
# --------------------------------------------------------------------------- #
def test_panel_charge_et_ancre_les_niveaux():
    p = load_panel("global-macro", "2026-07-01", "2026-08-28")
    assert p.source == "synthetic"
    assert len(p.close) > 30
    # Le niveau de publication du scénario est exactement le niveau calibré.
    assert p.close.at[pd.Timestamp("2026-07-15"), "BZ=F"] == pytest.approx(84.95, abs=1e-6)
    assert p.close.at[pd.Timestamp("2026-07-15"), "^GSPC"] == pytest.approx(6420.0, abs=1e-3)


def test_exercice_publie_juillet_2026_reconstruit():
    """La fenêtre de démonstration rejoue l'exercice publié."""
    p = load_panel("global-macro", "2026-07-01", "2026-08-28")
    c = p.close
    pub = c.loc["2026-07-15"]
    peak = c.loc["2026-07-23"] / pub - 1
    stop = c.loc["2026-08-05"] / pub - 1
    assert peak["BZ=F"] == pytest.approx(0.185, abs=2e-3)     # pic réel +18,5 %
    assert stop["BZ=F"] == pytest.approx(-0.065, abs=2e-3)    # reversion sous la pub
    assert stop["^GSPC"] == pytest.approx(-0.012, abs=2e-3)
    assert stop["DX-Y.NYB"] == pytest.approx(0.022, abs=2e-3)
    assert stop["GC=F"] < 0                                    # l'or : le miss
    # Le pic du Brent tombe bien le 23/07, soit J+8 calendrier après publication.
    window = c.loc["2026-07-15":"2026-08-05", "BZ=F"]
    assert window.idxmax() == pd.Timestamp("2026-07-23")
    assert (window.idxmax() - pd.Timestamp("2026-07-15")).days == 8


def test_vol_realisee_proche_de_la_calibration():
    p = load_panel("global-macro", "2020-01-01", "2024-12-31")
    for sym in ("BZ=F", "^GSPC", "TLT"):
        r = np.diff(np.log(p.close[sym].to_numpy()))
        realized = r.std(ddof=0) * math.sqrt(config.TRADING_DAYS)
        assert realized == pytest.approx(config.get_asset(sym).ann_vol, rel=0.15)


# --------------------------------------------------------------------------- #
# Options
# --------------------------------------------------------------------------- #
def test_parite_call_put():
    S, K, T, sig, r, q = 100.0, 100.0, 0.5, 0.25, 0.04, 0.01
    c = opt.black_scholes(S, K, T, sig, "call", r, q)
    p = opt.black_scholes(S, K, T, sig, "put", r, q)
    assert c - p == pytest.approx(S * math.exp(-q * T) - K * math.exp(-r * T), abs=1e-9)


def test_black_scholes_limites():
    # À l'échéance : l'intrinsèque.
    assert opt.black_scholes(110, 100, 0.0, 0.3, "call") == pytest.approx(10.0)
    assert opt.black_scholes(90, 100, 0.0, 0.3, "put") == pytest.approx(10.0)
    # Vol nulle : valeur actualisée de l'intrinsèque.
    assert opt.black_scholes(110, 100, 1.0, 0.0, "call", 0.05) == pytest.approx(
        10 * math.exp(-0.05), abs=1e-9)


def test_greeks_signes_coherents():
    c = opt.greeks(100, 100, 0.5, 0.25, "call")
    p = opt.greeks(100, 100, 0.5, 0.25, "put")
    assert 0 < c["delta"] < 1
    assert -1 < p["delta"] < 0
    assert c["gamma"] > 0 and p["gamma"] > 0
    assert c["vega"] > 0 and p["vega"] > 0
    assert c["theta"] < 0 and p["theta"] < 0
    assert c["delta"] - p["delta"] == pytest.approx(1.0, abs=1e-6)  # put-call en delta


def test_vol_implicite_aller_retour():
    price = opt.black_scholes(100, 105, 0.25, 0.31, "put")
    iv = opt.implied_vol(price, 100, 105, 0.25, "put")
    assert iv == pytest.approx(0.31, abs=1e-4)


def test_surface_sourire_et_skew():
    spec = config.get_asset("SPY")
    atm = opt.iv_surface(spec, 1.0, 30 / 365)
    otm_put = opt.iv_surface(spec, 0.95, 30 / 365)
    otm_call = opt.iv_surface(spec, 1.05, 30 / 365)
    assert otm_put > atm > otm_call            # skew : le put coûte plus cher
    assert opt.iv_surface(spec, 1.0, 30 / 365, iv_shift=0.10) == pytest.approx(atm + 0.10)


def test_butterfly_symetrique_et_borne():
    st = opt.build_structure("butterfly", "SPY", 642.0, days=30, width=0.03)
    strikes = [l.strike for l in st.legs]
    assert strikes[1] - strikes[0] == pytest.approx(strikes[2] - strikes[1])
    # Perte maximale == prime payée, gain maximal == écart - prime.
    assert st.max_loss() == pytest.approx(-st.net_premium, abs=1e-6)
    spacing = strikes[1] - strikes[0]
    assert st.max_profit() == pytest.approx(spacing - st.net_premium, abs=1e-3)
    assert st.payoff(strikes[1]) == pytest.approx(st.max_profit(), abs=1e-6)


def test_iron_condor_risque_borne():
    st = opt.build_structure("iron_condor", "SPY", 642.0, days=30, width=0.06)
    assert st.net_premium < 0                        # crédit
    assert st.max_loss() > -1e6                      # borné
    width = st.legs[1].strike - st.legs[0].strike
    assert abs(st.max_loss()) == pytest.approx(width + st.net_premium, abs=1e-6)


def test_strangle_long_coute_et_short_encaisse():
    long_ = opt.build_structure("strangle", "SPY", 642.0, days=30, width=0.04)
    short = opt.build_structure("short_strangle", "SPY", 642.0, days=30, width=0.04)
    assert long_.net_premium > 0 and short.net_premium < 0
    assert long_.net_premium == pytest.approx(-short.net_premium)
    be = long_.breakevens()
    assert len(be) == 2 and be[0] < 642 < be[1]
    assert long_.payoff(be[0]) == pytest.approx(0.0, abs=1e-6)


# --------------------------------------------------------------------------- #
# Atelier options — verrous anti-artefacts (30/08/2026)
# --------------------------------------------------------------------------- #
def test_lab_reference_stable():
    """Les valeurs de référence de l'atelier Options ne doivent pas bouger."""
    q = api.option_lab("SPY", "strangle", days=30, width=0.03)
    assert q["net_premium"] == pytest.approx(10.69, abs=0.01)
    assert q["greeks"]["vega"] == pytest.approx(1.242, abs=1e-3)
    assert q["greeks"]["theta"] == pytest.approx(-0.344, abs=1e-3)
    assert len(q["breakevens"]) == 2
    assert q["warnings"] == []                      # aucune alerte en régime normal
    st = api.option_lab("SPY", "straddle", days=30, width=0.03)
    assert st["net_premium"] == pytest.approx(24.40, abs=0.01)


def test_lab_choc_irrealiste_est_signalé():
    """+1000 pts d'IV : le lab doit le dire, pas l'écrêter en silence."""
    q = api.option_lab("SPY", "strangle", days=30, width=0.03, iv_shift=10.0)
    assert any("plafonnée" in w for w in q["warnings"])
    assert all(l["iv"] == 4.0 for l in q["legs"])   # surface bornée à 400 %
    # Les points morts existent bel et bien — la grille doit les suivre.
    be = q["breakevens"]
    assert len(be) == 2 and be[0] < 642 < be[1]


def test_lab_bornes_de_payoff_declarees():
    """Un strangle acheté a un gain illimité ; un short strangle une perte
    non bornée. Les bornes sont déclarées par structure, pas déduites d'une
    grille d'évaluation."""
    long_ = api.option_lab("SPY", "strangle", days=30)
    assert long_["max_loss_bounded"] and not long_["max_gain_bounded"]
    short = api.option_lab("SPY", "short_strangle", days=30)
    assert short["max_gain_bounded"] and not short["max_loss_bounded"]
    butterfly = api.option_lab("SPY", "butterfly", days=30)
    assert butterfly["max_loss_bounded"] and butterfly["max_gain_bounded"]


def test_surface_iv_est_bornée():
    spec = config.get_asset("SPY")
    assert opt.iv_surface(spec, 1.0, 30 / 365, iv_shift=100.0) == pytest.approx(4.0)
    assert opt.iv_surface(spec, 1.0, 30 / 365, iv_shift=-100.0) == pytest.approx(0.02)


# --------------------------------------------------------------------------- #
# Moteur
# --------------------------------------------------------------------------- #
BUY_HOLD = """
def initialize(context):
    context.a = symbol('BZ=F')
    schedule_function(buy, date_rules.every_day())

def buy(context, data):
    if not context.portfolio.positions:
        order_target_percent(context.a, 0.50)
"""


def test_moteur_achat_conservation_sans_frais():
    panel = load_panel("global-macro", "2026-07-01", "2026-08-28")
    st = EngineSettings(commission_per_share=0.0, commission_min=0.0, slippage_bps=0.0)
    eng = BacktestEngine(panel, "global-macro", 100000, settings=st)
    res = eng.run(BUY_HOLD)
    assert res["error"] is None
    first = panel.close["BZ=F"].iloc[0]
    last = panel.close["BZ=F"].iloc[-1]
    attendu = 100000 + 0.5 * 100000 * (last / first - 1)
    assert res["equity"].iloc[-1] == pytest.approx(attendu, rel=1e-6)
    # L'attribution se réconcilie avec l'équité (au centime près : le rapport
    # arrondit chaque ligne à 2 décimales).
    assert sum(res["attribution"].values()) == pytest.approx(
        res["equity"].iloc[-1] - 100000, abs=0.05)


def test_les_frais_coutent():
    panel = load_panel("global-macro", "2026-07-01", "2026-08-28")
    zero = EngineSettings(commission_per_share=0.0, commission_min=0.0, slippage_bps=0.0)
    paid = EngineSettings(commission_per_share=0.01, commission_min=2.0, slippage_bps=20.0)
    a = BacktestEngine(panel, "global-macro", 100000, settings=zero).run(BUY_HOLD)
    b = BacktestEngine(panel, "global-macro", 100000, settings=paid).run(BUY_HOLD)
    assert b["equity"].iloc[-1] < a["equity"].iloc[-1]
    assert len(b["trades"]) == 1


OPTION_FEE_CODE = """
def initialize(context):
    schedule_function(buy, date_rules.every_day())

def buy(context, data):
    if not context.portfolio.positions:
        c = option_contract('{sym}', 'call', moneyness=1.0, days=21)
        order(c, 1000)
"""


def test_les_frais_option_sont_comptes_par_contrat():
    """1 000 parts d'option = 10 contrats sur un ETF, 1 contrat sur le Brent.

    Le piège corrigé le 30 août 2026 : le moteur divisait la quantité par la
    taille du contrat AU COMPTANT (1 part pour un ETF), donc il facturait
    1 000 contrats au lieu de 10 — 100× trop de frais. Sur l'atelier « iron
    condor de range », les frais passaient de 30 870 $ à 313 $ pour 138 773 $
    de volume échangé, et le P&L de −29 157 $ à +1 434 $.
    """
    st = EngineSettings(commission_per_share=0.0, commission_min=0.0,
                        slippage_bps=0.0, commission_per_contract=0.65)
    for sym, uni, parts_par_contrat in (("SPY", "us-equities", 100.0),
                                        ("BZ=F", "options-lab", 1000.0)):
        panel = load_panel(uni, "2026-06-01", "2026-07-15", source="synthetic")
        eng = BacktestEngine(panel, uni, 100000, settings=st)
        res = eng.run(OPTION_FEE_CODE.format(sym=sym))
        assert res["error"] is None, res["error"]
        assert res["trades"], "aucun ordre exécuté"
        attendu = 1000.0 / parts_par_contrat * 0.65
        for t in res["trades"]:
            assert t["commission"] == pytest.approx(attendu, abs=0.01)


def test_taille_des_contrats_d_option_par_type_d_actif():
    """Une option US sur action/ETF/indice porte 100 parts ; sur future, la
    taille du contrat à terme."""
    assert config.get_asset("SPY").effective_option_contract_size == 100.0
    assert config.get_asset("QQQ").effective_option_contract_size == 100.0
    assert config.get_asset("AAPL").effective_option_contract_size == 100.0
    assert config.get_asset("^GSPC").effective_option_contract_size == 100.0
    assert config.get_asset("BZ=F").effective_option_contract_size == 1000.0
    assert config.get_asset("GC=F").effective_option_contract_size == 100.0
    assert config.get_asset("SI=F").effective_option_contract_size == 5000.0


SHORT_CODE = """
def initialize(context):
    context.a = symbol('^GSPC')
    schedule_function(short, date_rules.every_day())

def short(context, data):
    if not context.portfolio.positions:
        order_target_percent(context.a, -0.40)
"""


def test_vente_a_decouvert():
    panel = load_panel("global-macro", "2026-07-01", "2026-08-05")
    st = EngineSettings(commission_per_share=0.0, commission_min=0.0, slippage_bps=0.0)
    res = BacktestEngine(panel, "global-macro", 100000, settings=st).run(SHORT_CODE)
    pos = res["portfolio"]["positions"][0]
    assert pos["amount"] < 0
    # Les actions baissent sur la fenêtre : la vente à découvert gagne.
    assert res["equity"].iloc[-1] > 100000


OPTION_CODE = """
def initialize(context):
    context.a = symbol('SPY')
    schedule_function(buy, date_rules.every_day())

def buy(context, data):
    if not context.portfolio.positions:
        c = option_contract('SPY', 'call', moneyness=1.0, days=21)
        order(c, 5)
"""


def test_option_se_regle_a_echeance():
    panel = load_panel("us-equities", "2026-06-01", "2026-08-28")
    st = EngineSettings(commission_per_share=0.0, commission_min=0.0,
                        slippage_bps=0.0, commission_per_contract=0.0)
    eng = BacktestEngine(panel, "us-equities", 100000, settings=st)
    res = eng.run(OPTION_CODE)
    assert res["error"] is None
    # Aucune option échue ne subsiste dans le book : tout est réglé à
    # l'intrinsèque. (La stratégie rachète un contrat neuf après chaque
    # échéance, ce qui est le comportement attendu.)
    fin = panel.dates[-1]
    for k, pos in eng.portfolio.positions.items():
        if isinstance(k, opt.OptionContract) and abs(pos.amount) > 1e-9:
            assert pd.Timestamp(k.expiry) > fin
    assert any("Échéance" in l["message"] for l in res["logs"])


def test_plafond_de_levier():
    code = """
def initialize(context):
    context.a = symbol('BZ=F')
    schedule_function(go, date_rules.every_day())

def go(context, data):
    if not context.portfolio.positions:
        order_target_percent(context.a, 50.0)
"""
    panel = load_panel("global-macro", "2026-07-01", "2026-08-28")
    st = EngineSettings(commission_per_share=0.0, commission_min=0.0,
                        slippage_bps=0.0, max_leverage=2.0)
    eng = BacktestEngine(panel, "global-macro", 100000, settings=st)
    res = eng.run(code)
    brute = sum(abs(p["market_value"]) for p in res["portfolio"]["positions"])
    assert brute <= 2.0 * 100000 * 1.001
    assert any(l["level"] == "warning" and "plafond de levier" in l["message"]
               for l in res["logs"])


def test_erreur_de_code_remontee():
    panel = load_panel("global-macro", "2026-07-01", "2026-07-31")
    res = BacktestEngine(panel, "global-macro", 10000).run("def initialize(context:\n")
    assert res["error"] and "SyntaxError" in res["error"]


# --------------------------------------------------------------------------- #
# Anticipation
# --------------------------------------------------------------------------- #
def test_previsions_point_in_time():
    led = ForecastLedger()
    f1 = led.active(pd.Timestamp("2026-07-20"), "BZ=F")
    f2 = led.active(pd.Timestamp("2026-08-28"), "BZ=F")
    assert f1 is not None and f2 is not None
    assert f1.rev == 1 and f2.rev == 2
    # Avant la publication : rien.
    assert led.active(pd.Timestamp("2026-07-01"), "BZ=F") is None


def test_scoring_net_du_drift():
    panel = load_panel("global-macro", "2026-07-01", "2026-08-28")
    led = ForecastLedger()
    sc = scorecard(led, panel)
    # 7 lignes publiées pour l'exercice, dont le benchmark qui n'est pas un test.
    assert sc["sign_total"] == 6
    assert sc["non_test"] == 1
    assert sc["sign_hits"] == 5
    assert sc["misses"] == ["GC=F"]
    # Le timing du pic est bon à un jour près (médiane), l'amplitude sous-estimée.
    assert sc["median_peak_error_days"] == pytest.approx(1.0)
    oil = [r for r in sc["rows"] if r["asset"] == "BZ=F" and r.get("counted")][0]
    assert oil["amplitude_ratio"] == pytest.approx(3.7, abs=0.15)
    assert oil["peak_error_days"] == 1


def test_scorecard_distingue_le_hors_univers():
    """Une prévision sur un sous-jacent absent du panneau n'est pas un échec :
    elle n'est pas testable dans cet univers.

    Sans cette distinction, un scorecard `us-equities` affichait 9 lignes
    « non évaluable » sur 10 (Brent, or, dollar, crédit, matières premières...)
    et se lisait comme une série de misses.
    """
    led = ForecastLedger()
    panel_ue = load_panel("us-equities", "2026-01-01", "2026-08-28", source="synthetic")
    sc = scorecard(led, panel_ue)
    assert "BZ=F" in sc["out_of_universe"]
    assert sc["out_of_universe_total"] > 0
    assert sc["evaluable_total"] == len(sc["rows"]) - sc["out_of_universe_total"]
    # TLT est chargé dans us-equities : sa ligne est évaluée, pas « hors univers ».
    tlt = [r for r in sc["rows"] if r["asset"] == "TLT"]
    assert tlt and not any(r["out_of_universe"] for r in tlt)
    # Sur l'univers qui charge toutes les lignes publiées : rien hors univers.
    gm = load_panel("global-macro", "2026-07-01", "2026-08-28", source="synthetic")
    assert scorecard(led, gm)["out_of_universe_total"] == 0


def test_validation_exclut_le_drift_du_benchmark():
    panel = load_panel("global-macro", "2026-07-01", "2026-08-28")
    led = ForecastLedger()
    f = led.revisions("shocklab-2026-07-rates")[0]
    v = validate(f, panel)
    # TLT monte moins que le benchmark ne baisse : le rendement actif est positif.
    assert v["end_return_active"] > v["end_return_raw"] or v["benchmark_drift"] < 0
    assert v["beta_to_benchmark"] == pytest.approx(0.15, abs=0.01)


def test_trajectoire_de_prevision():
    led = ForecastLedger()
    f = led.revisions("shocklab-2026-07-oil")[0]
    path = f.path(30)
    assert path[0] == 0.0
    assert path[7] == pytest.approx(0.05, abs=1e-9)     # pic J+7 à +5 %
    assert path[-1] == pytest.approx(-0.03, abs=1e-9)   # reversion à -3 %
    assert max(path) == pytest.approx(0.05, abs=1e-9)


def test_recommandation_de_structures():
    from shockdesk.scenarios import recommend
    led = ForecastLedger()
    f = led.revisions("shocklab-2026-07-oil")[0]
    rec = recommend(f, 84.95, iv_atm=0.36, days=14)
    kinds = [s["kind"] for s in rec["structures"]]
    assert kinds and all(s["legs"] for s in rec["structures"])
    for s in rec["structures"]:
        assert s["pnl_scenarios"]
        assert s["max_loss"] <= 0


# --------------------------------------------------------------------------- #
# Métriques
# --------------------------------------------------------------------------- #
def test_metriques_sur_courbe_connue():
    idx = pd.bdate_range("2024-01-01", periods=253)
    eq = pd.Series(100.0 * (1.001 ** np.arange(253)), index=idx)   # +0,1 %/jour
    m = metrics.compute(eq, risk_free=0.0)
    assert m["total_return"] == pytest.approx(1.001 ** 252 - 1, rel=1e-6)
    assert m["max_drawdown"] == pytest.approx(0.0, abs=1e-9)
    assert m["win_rate"] == pytest.approx(1.0)
    assert m["sharpe"] > 10                                       # trajectoire lisse


def test_metriques_drawdown():
    idx = pd.bdate_range("2024-01-01", periods=5)
    eq = pd.Series([100, 120, 60, 90, 90], index=idx, dtype=float)
    m = metrics.compute(eq)
    assert m["max_drawdown"] == pytest.approx(60 / 120 - 1)
    dd = metrics.drawdown(eq)
    assert dd.min() == pytest.approx(-0.5)


# --------------------------------------------------------------------------- #
# Stratégies livrées
# --------------------------------------------------------------------------- #
CASES = [
    ("shock-lab-oil.py", "global-macro", 25500000, "2026-07-01", "2026-08-28"),
    ("long-strangle-shock.py", "global-macro", 1000000, "2026-07-01", "2026-08-28"),
    ("butterfly-peak.py", "global-macro", 1000000, "2026-07-01", "2026-08-28"),
    ("short-strangle-carry.py", "us-equities", 100000, "2026-01-01", "2026-08-28"),
    ("iron-condor-range.py", "us-equities", 100000, "2026-01-01", "2026-08-28"),
    ("us-equities-momentum.py", "us-equities", 10000, "2024-01-01", "2026-08-28"),
]


@pytest.mark.parametrize("fname,uni,capital,start,end", CASES)
def test_strategies_livrees_s_executent(fname, uni, capital, start, end):
    with open(os.path.join(STRAT_DIR, fname), "r", encoding="utf-8") as fh:
        code = fh.read()
    p = api.run_backtest(code, name=uni, startCapital=capital,
                         startDate=start, endDate=end)
    assert p["error"] is None, p["error"]
    assert p["ok"]
    assert not [l for l in p["logs"] if l["level"] == "error"], p["logs"]
    assert len(p["equity"]["values"]) == p["data"]["bars"]
    # L'équité reste positive : pas de ruine numérique.
    assert min(p["equity"]["values"]) > 0


def test_book_shocklab_sortie_au_pic_bat_le_stop_calendar():
    """Le signal de pic vaut de l'argent : c'est la leçon de l'exercice."""
    with open(os.path.join(STRAT_DIR, "shock-lab-oil.py"), "r", encoding="utf-8") as fh:
        code = fh.read()
    common = dict(name="global-macro", startCapital=25500000,
                  startDate="2026-07-01", endDate="2026-08-28")
    v2 = api.run_backtest(code.replace("TAKE_PROFIT_AT_PEAK = True",
                                       "TAKE_PROFIT_AT_PEAK = True"), **common)
    v1 = api.run_backtest(code.replace("TAKE_PROFIT_AT_PEAK = True",
                                       "TAKE_PROFIT_AT_PEAK = False"), **common)
    # Ce que chaque règle de sortie FIGE : la valeur au jour de sortie, pas le
    # maximum de la courbe (le book est long pétrole, la courbe passe par le pic
    # dans les deux cas).
    peak_pnl = max(v2["equity"]["values"]) - 25500000
    stop_idx = v1["equity"]["dates"].index("2026-08-05")
    stop_pnl = v1["equity"]["values"][stop_idx] - 25500000
    assert peak_pnl > 200000                       # le pic J+7 fige plusieurs centaines de k$
    assert peak_pnl > stop_pnl * 5                 # le stop calendar rend l'essentiel
    # La ligne directionnelle pétrole finit négative au stop, l'or aussi (le miss).
    assert v1["attribution"]["BZ=F"] < 0
    assert v1["attribution"]["GC=F"] < 0
    # Et ce sont les actions (short) qui portent le P&L.
    assert v1["attribution"]["^GSPC"] > 0


# --------------------------------------------------------------------------- #
# Registre & API
# --------------------------------------------------------------------------- #
def test_registre_strategies():
    strats = registry.list_strategies()
    assert len(strats) >= 6
    for s in strats:
        assert registry.get(s["id"])
        assert registry.read_code(s["id"])


def test_registre_aller_retour(tmp_path):
    code = '"""test"""\n\ndef initialize(context):\n    pass\n'
    meta = registry.create("strategie de test", code)
    try:
        assert registry.read_code(meta["id"]) == code
        registry.write_code(meta["id"], code + "\n# modifié\n")
        assert "# modifié" in registry.read_code(meta["id"])
    finally:
        idx = registry._load_index()
        idx.pop(meta["id"], None)
        registry._save_index(idx)
        os.remove(os.path.join(STRAT_DIR, meta["file"]))


def test_registre_previsions_revision(tmp_path):
    path = str(tmp_path / "forecasts.json")
    led = ForecastLedger(path=path)
    led.add_forecast("t1", "test", "BZ=F", sign=1, amplitude=0.05, peak_day=7,
                     reversion=-0.02, reversion_days=10, date="2026-01-01")
    assert led.latest("t1").rev == 1
    led2 = ForecastLedger(path=path)
    led2.add_revision("t1", sign=-1, amplitude=0.09, peak_day=9, reversion=-0.04,
                      reversion_days=12, date="2026-02-01", note="correction")
    led3 = ForecastLedger(path=path)
    assert led3.latest("t1").rev == 2
    assert led3.latest("t1").sign == -1
    # La révision précédente est toujours là : l'historique n'est pas réécrit.
    assert [f.rev for f in led3.revisions("t1")] == [1, 2]


def test_api_endpoints():
    from shockdesk.webapp import create_app
    app = create_app()
    client = app.test_client()

    assert client.get("/health").get_json()["ok"] is True
    unis = client.get("/api/universes").get_json()
    assert unis["ok"] and len(unis["universes"]) == len(config.UNIVERSES)

    strats = client.get("/api/strategies").get_json()["strategies"]
    sid = strats[0]["id"]

    # La forme Blueshift, en POST comme en GET.
    url = (f"/api/backtest?strategy_id={sid}&name=global-macro&startCapital=100000"
           f"&startDate=2026-07-01&endDate=2026-08-28&action=backtest")
    j = client.get(url).get_json()
    assert j["ok"] and j["params"]["name"] == "global-macro"
    assert j["params"]["startCapital"] == 100000

    j = client.post("/api/backtest", json={"strategy_id": sid, "name": "global-macro",
                                           "startCapital": 50000,
                                           "startDate": "2026-07-01",
                                           "endDate": "2026-08-05"}).get_json()
    assert j["ok"] and j["metrics"]["trades"] >= 0

    q = client.post("/api/options/quote", json={"underlying": "SPY",
                                                "structure": "strangle",
                                                "days": 30}).get_json()
    assert q["ok"] and len(q["legs"]) == 2 and q["payoff_curve"]

    b = client.get("/api/scenarios?name=global-macro&asof=2026-08-05").get_json()
    assert b["ok"] and b["rows"]
    assert any(r["forecast"] for r in b["rows"])

    # Une URL de recherche inconnue renvoie une 404 propre.
    assert client.get("/research/strategies/pas-une-uuid/code").status_code == 404


def test_page_recherche_porte_les_parametres_d_url():
    from shockdesk.webapp import create_app
    app = create_app()
    client = app.test_client()
    sid = registry.list_strategies()[0]["id"]
    r = client.get(f"/research/strategies/{sid}/code?name=global-macro"
                   f"&startCapital=25500000&startDate=2026-07-01"
                   f"&endDate=2026-08-28&action=backtest")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "25500000" in html and "2026-07-01" in html and "backtest" in html
    assert "ShockDesk" in html


# --------------------------------------------------------------------------- #
# Revue mensuelle (CLI)
# --------------------------------------------------------------------------- #

def test_revue_mensuelle_produit_les_lignes_attendues(capsys):
    rc = cli.main(["revue", "--name", "global-macro", "--asof", "2026-08-28",
                   "--window", "45"])
    out = capsys.readouterr().out
    assert rc == 0
    for attendu in ("SCORE DES PRÉVISIONS", "RÉVISIONS À ÉCRIRE",
                    "CALIBRATION À REPRENDRE", "STRATÉGIES SUR LA FENÊTRE",
                    "médiane 1.0 j", "GC=F"):
        assert attendu in out, attendu
    # la révision proposée doit être un JSON collable
    import json as _json
    payload = out.split("-d '")[1].split("'")[0]
    sugg = _json.loads(payload)
    assert set(sugg) == {"sign", "amplitude", "peak_day", "reversion", "note"}
    assert sugg["amplitude"] and sugg["peak_day"][0] >= 1
