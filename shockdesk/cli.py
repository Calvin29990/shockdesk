"""
Ligne de commande ShockDesk.

Mêmes paramètres que l'URL de recherche, pour pouvoir scripter / croniser les
revues mensuelles :

    python -m shockdesk.cli backtest --strategy shock-lab-oil \\
        --name global-macro --start-capital 25500000 \\
        --start-date 2026-07-15 --end-date 2026-08-05

    python -m shockdesk.cli strategies
    python -m shockdesk.cli scenarios --name global-macro
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import pandas as pd

from . import api, config, registry
from .marketdata import load_panel


def _find_strategy(ref: str) -> str:
    """Accepte un UUID, un slug ou un chemin de fichier."""
    if registry.get(ref):
        return ref
    for s in registry.list_strategies():
        if s["file"][:-3] == ref or s["name"] == ref:
            return s["id"]
    if os.path.exists(ref):
        meta = registry.create(os.path.basename(ref)[:-3].replace("-", " ").title(),
                               open(ref, "r", encoding="utf-8").read())
        return meta["id"]
    raise SystemExit(f"Stratégie introuvable : {ref}")


def _print_metrics(p: dict):
    m = p["metrics"]
    print(f"\n=== {p['universe']['label']} — {p['params']['startDate']} → "
          f"{p['params']['endDate']} ({p['data']['bars']} barres, {p['data']['source']}) ===")
    if p.get("error"):
        print("ERREUR :", p["error"])
        return
    rows = [
        ("Capital initial", f"{p['params']['startCapital']:,.0f}"),
        ("Capital final", f"{m['final_equity']:,.2f}"),
        ("P&L", f"{m['final_equity'] - p['params']['startCapital']:,.2f} "
                f"({m['total_return']:+.2%})"),
        ("CAGR", f"{(m['cagr'] or 0):+.2%}"),
        ("Vol annualisée", f"{(m['ann_volatility'] or 0):.2%}"),
        ("Sharpe", "n.d." if m["sharpe"] is None else f"{m['sharpe']}"),
        ("Sortino", "n.d." if m["sortino"] is None else f"{m['sortino']}"),
        ("Drawdown max", "n.d." if m["max_drawdown"] is None
         else f"{m['max_drawdown']:.2%}"),
        ("Win rate", f"{(m['win_rate'] or 0):.1%}"),
        ("Trades", f"{m['trades']}"),
        ("Benchmark", f"{m.get('benchmark_symbol')} "
                      f"{(m.get('benchmark_return') or 0):+.2%}"),
    ]
    for k, v in rows:
        print(f"  {k:<20} {v}")
    if p["attribution"]:
        print("\n  Attribution du P&L :")
        for sym, v in p["attribution"].items():
            print(f"    {sym:<12} {v:>12,.2f}")
    sc = p.get("scorecard") or {}
    if sc.get("sign_total"):
        print(f"\n  Score prévisions : signe {sc['sign_hits']}/{sc['sign_total']} · "
              f"erreur de pic {sc['avg_peak_error_days']} j · "
              f"ratio d'amplitude médian {sc['median_amplitude_ratio']}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="shockdesk", description="ShockDesk — desk de backtest et d'anticipation")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("backtest", help="exécute un backtest")
    b.add_argument("--strategy", required=True, help="UUID, slug ou fichier .py")
    b.add_argument("--name", default="us-equities", help="univers (bundle)")
    b.add_argument("--start-capital", type=float, default=10000)
    b.add_argument("--start-date", default="2020-01-01")
    b.add_argument("--end-date", default="2021-09-01")
    b.add_argument("--source", default="auto", choices=["auto", "yfinance", "csv", "synthetic"])
    b.add_argument("--json", action="store_true", help="sortie JSON complète")

    sub.add_parser("strategies", help="liste les stratégies")

    s = sub.add_parser("scenarios", help="tableau d'anticipation")
    s.add_argument("--name", default="global-macro")
    s.add_argument("--asof", default=None)
    s.add_argument("--json", action="store_true")

    lab = sub.add_parser("option-lab", help="price une structure d'options")
    lab.add_argument("--underlying", default="SPY")
    lab.add_argument("--structure", default="strangle")
    lab.add_argument("--days", type=int, default=30)
    lab.add_argument("--width", type=float, default=0.03)
    lab.add_argument("--iv-shift", type=float, default=0.0)

    rv = sub.add_parser("revue", help="revue mensuelle : quoi corriger, quoi recalibrer")
    rv.add_argument("--name", default="global-macro")
    rv.add_argument("--asof", default=None, help="date de fin de la revue (défaut : aujourd'hui)")
    rv.add_argument("--window", type=int, default=120, help="fenêtre en jours")
    rv.add_argument("--port", type=int, default=8050, help="port affiché dans les exemples curl")

    srv = sub.add_parser("serve", help="lance l'interface web")
    srv.add_argument("--host", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=8050)

    args = ap.parse_args(argv)

    if args.cmd == "strategies":
        for s in registry.list_strategies():
            print(f"{s['id']}  {s['file']:<32} {s['description']}")
        return 0

    if args.cmd == "backtest":
        sid = _find_strategy(args.strategy)
        p = api.strategy_payload(sid, name=args.name, startCapital=args.start_capital,
                                 startDate=args.start_date, endDate=args.end_date,
                                 source=args.source) if args.source == "auto" else \
            api.run_backtest(registry.read_code(sid), strategy_id=sid, name=args.name,
                             startCapital=args.start_capital, startDate=args.start_date,
                             endDate=args.end_date, source=args.source)
        if args.json:
            print(json.dumps(p, ensure_ascii=False, indent=2, default=str))
        else:
            _print_metrics(p)
        return 0

    if args.cmd == "scenarios":
        board = api.scenario_board(args.name, asof=args.asof)
        if args.json:
            print(json.dumps(board, ensure_ascii=False, indent=2, default=str))
            return 0
        print(f"\n=== Anticipation — {board['universe']['label']} "
              f"(au {board['asof']}, données {board['data_source']}) ===")
        for r in board["rows"]:
            f = r["forecast"]
            print(f"\n  {r['symbol']:<10} spot {r['spot']:>10,.2f}  "
                  f"IV30 {r['iv_atm_30d']:.1%}  vol réalisée {r['realized_vol']:.1%}")
            if not f:
                print("    aucune prévision active")
                continue
            print(f"    prévision r{f['rev']} ({f['published']}) : sens {f['sign']:+d} · "
                  f"amplitude {f['amp_base']:+.1%} · pic J+{f['peak_base']:.0f} · "
                  f"reversion {f['reversion']:+.1%} · IV {f['iv_shift']:+.0%} pts")
            v = r.get("validation") or {}
            if "sign_ok_peak" in v:
                print(f"    validation : signe {'✔' if v['sign_ok_peak'] else '✘'} · "
                      f"amplitude réelle {v['amplitude_realized']:+.1%} "
                      f"(x{v['amplitude_ratio']}) · pic {v['peak_realized_days']} j "
                      f"(erreur {v['peak_error_days']:+.0f} j)")
            for st in (r.get("structures") or [])[:3]:
                print(f"    → {st['name']:<20} coût {st['cost']:>8.2f}  "
                      f"BE {', '.join(f'{x:.1f}' for x in st['breakevens'])}")
        return 0

    if args.cmd == "option-lab":
        out = api.option_lab(args.underlying, args.structure, days=args.days,
                             width=args.width, iv_shift=args.iv_shift)
        print(f"\n{out['name']} sur {args.underlying} "
              f"({out['underlying_name']}) — {out['days']} j")
        print(f"  spot {out['spot']:.2f} · prime nette {out['net_premium']:.2f}")
        for w in out.get("warnings", []):
            print(f"  ⚠ {w}")
        print(f"  perte max " + (f"{out['max_loss']:.2f}" if out["max_loss_bounded"]
                                else "non bornée (structure vendeuse)"))
        print(f"  gain max " + (f"{out['max_profit']:.2f}" if out["max_gain_bounded"]
                                else "illimité (structure acheteuse)"))
        print(f"  points morts : {', '.join(f'{b:.2f}' for b in out['breakevens'])}")
        g = out["greeks"]
        print(f"  delta {g['delta']:+.2f} · gamma {g['gamma']:+.4f} · "
              f"vega {g['vega']:+.2f}/pt · theta {g['theta']:+.3f}/j")
        for l in out["legs"]:
            print(f"    {l['qty']:+.0f} {l['kind']:<4} {l['strike']:>10.2f} "
                  f"@ {l['premium']:.2f} (IV {l['iv']:.1%})")
        return 0

    if args.cmd == "revue":
        return _cmd_revue(args)

    if args.cmd == "serve":
        from .webapp import create_app
        create_app().run(host=args.host, port=args.port, debug=False)
        return 0

    return 1


def _cmd_revue(args):
    """Revue mensuelle : ce qu'il faut corriger, et quoi recalibrer.

    C'est l'outil de la boucle de phase 1. Il ne décide rien : il met sous les
    yeux l'écart entre ce qui a été publié et ce qui s'est passé, et propose la
    révision suivante au format prêt à coller.
    """
    import json as _json

    import numpy as _np

    from .scenarios import ForecastLedger, scorecard

    end = pd.Timestamp(args.asof) if args.asof else pd.Timestamp.today()
    start = end - pd.Timedelta(days=args.window)
    panel = load_panel(args.name, start, end)
    ledger = ForecastLedger()
    sc = scorecard(ledger, panel)

    print(f"\n=== Revue mensuelle — {args.name} au {end.date()} "
          f"({panel.source}, {len(panel.close)} barres) ===")
    print(f"\n1. SCORE DES PRÉVISIONS PUBLIÉES (révisions originales)")
    print(f"   accord de signe net du drift : {sc['sign_hits']}/{sc['sign_total']}"
          f" ({sc['lines_total']} lignes publiées, {sc['non_test']} non-test)")
    print(f"   erreur de timing du pic      : médiane {sc['median_peak_error_days']} j"
          f" · moyenne {sc['avg_peak_error_days']} j")
    print(f"   ratio d'amplitude            : médian x{sc['median_amplitude_ratio']}")
    print(f"   misses                       : {', '.join(sc['misses']) or 'aucun'}")

    print(f"\n2. RÉVISIONS À ÉCRIRE")
    for row in sc["rows"]:
        if not row.get("counted") or "sign_ok_peak" not in row:
            continue
        ratio = row["amplitude_ratio"] or 1.0
        err = row["peak_error_days"] or 0
        base = row["amplitude_forecast"] or 0.05
        grille = sorted({round(base * m, 4) for m in (0.5, 1.0, max(ratio, 1.0))})
        sugg = {
            "sign": row["sign_forecast"],
            "amplitude": grille,
            "peak_day": [max(int(row["peak_forecast_days"] + err - 1), 1),
                         int(row["peak_forecast_days"] + err + 1)],
            "reversion": row["end_return_active"],
            "note": (f"revue du {end.date()} : amplitude réelle x{ratio:.2f}, "
                     f"pic à {err:+.0f} j, signe "
                     f"{'confirmé' if row['sign_ok_peak'] else 'infirmé'}"),
        }
        print(f"\n   {row['asset']} — {row['name']} (r{row['rev']})")
        print(f"     prévu {row['amplitude_forecast']:+.1%} à J+{row['peak_forecast_days']:.0f}"
              f" · réalisé {row['amplitude_realized']:+.1%} à J+{row['peak_realized_days']}"
              f" · signe {'✔' if row['sign_ok_peak'] else '✘'}")
        print(f"     curl -X POST localhost:{args.port}/api/ledger/{row['id']}/revision \\")
        print(f"       -H 'Content-Type: application/json' -d '{_json.dumps(sugg, ensure_ascii=False)}'")

    # La calibration se mesure sur un an, pas sur la fenêtre de revue : une
    # fenêtre courte n'a aucune raison de reproduire la vol annuelle.
    print(f"\n3. CALIBRATION À REPRENDRE (config/calibration.json)")
    long_panel = load_panel(args.name, end - pd.Timedelta(days=365), end)
    print(f"   (volatilité réalisée sur {len(long_panel.close)} séances, "
          f"du {long_panel.close.index[0].date()} au {long_panel.close.index[-1].date()})")
    for sym in long_panel.close.columns:
        spec = config.get_asset(sym)
        r = _np.diff(_np.log(long_panel.close[sym].to_numpy()))
        rv = float(r.std(ddof=0) * _np.sqrt(config.TRADING_DAYS))
        ecart = rv / spec.ann_vol - 1 if spec.ann_vol else 0
        flag = "  ← à corriger" if abs(ecart) > 0.15 else ""
        print(f"   {sym:<10} vol réalisée {rv:6.1%} · calibrée {spec.ann_vol:6.1%} "
              f"({ecart:+.0%}){flag}")

    print(f"\n4. STRATÉGIES SUR LA FENÊTRE")
    rows = []
    for meta in registry.list_strategies():
        code = registry.read_code(meta["id"])
        defaults = meta.get("defaults") or {}
        uni = args.name
        p = api.run_backtest(code, name=uni, startCapital=100000,
                             startDate=str(start.date()), endDate=str(end.date()))
        note = ""
        if p.get("error") and "n'est pas dans l'univers" in str(p["error"]):
            # La stratégie vise un autre univers : on la joue sur le sien,
            # mais elle sort alors de la comparaison.
            uni = defaults.get("name", args.name)
            p = api.run_backtest(code, name=uni,
                                 startCapital=float(defaults.get("startCapital", 100000)),
                                 startDate=defaults.get("startDate", str(start.date())),
                                 endDate=defaults.get("endDate", str(end.date())))
            note = f"(hors revue : univers {uni})"
        m = p["metrics"]
        rows.append((meta["name"] + (" " + note if note else ""), m.get("total_return"),
                     m.get("sharpe"), m.get("max_drawdown"), m.get("alpha"),
                     p.get("error"), bool(note), m.get("trades")))
    ref = [r for r in rows if "référence" in r[0].lower() or "momentum" in r[0].lower()]
    ref_ret = ref[0][1] if ref and ref[0][1] is not None and ref[0][7] else None
    if ref and not ref[0][7]:
        print("   (référence inactive : son pool ne recoupe pas cet univers — "
              "la comparaison ne veut rien dire ici)")
    # Un ratio non defini arrive en None depuis metrics.compute() : on
    # l'affiche « n.d. » plutot que de le formater (et plutot que 0,0).
    def _fmt(v, spec):
        return ("n.d." if v is None else format(v, spec)).rjust(7)

    for name, ret, sharpe, dd, alpha, err, hors, trades in rows:
        if err:
            print(f"   {name:<44} ERREUR {err.splitlines()[0][:56]}")
            continue
        verdict = ""
        if (ref_ret is not None and ret is not None and not hors
                and "momentum" not in name.lower()):
            verdict = "bat la référence" if ret > ref_ret else "sous la référence"
        print(f"   {name:<44} {ret:+7.2%}  Sharpe {_fmt(sharpe, '.2f')}  "
              f"DD {_fmt(dd, '.2%')}  alpha {_fmt(alpha, '+.2%')}  {verdict}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

