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

from . import api, config, registry


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
        ("Sharpe", f"{m['sharpe']}"),
        ("Sortino", f"{m['sortino']}"),
        ("Drawdown max", f"{(m['max_drawdown'] or 0):.2%}"),
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
        print(f"  spot {out['spot']:.2f} · prime nette {out['net_premium']:.2f} · "
              f"perte max {out['max_loss']:.2f} · gain max {out['max_profit']:.2f}")
        print(f"  points morts : {', '.join(f'{b:.2f}' for b in out['breakevens'])}")
        g = out["greeks"]
        print(f"  delta {g['delta']:+.2f} · gamma {g['gamma']:+.4f} · "
              f"vega {g['vega']:+.2f}/pt · theta {g['theta']:+.3f}/j")
        for l in out["legs"]:
            print(f"    {l['qty']:+.0f} {l['kind']:<4} {l['strike']:>10.2f} "
                  f"@ {l['premium']:.2f} (IV {l['iv']:.1%})")
        return 0

    if args.cmd == "serve":
        from .webapp import create_app
        create_app().run(host=args.host, port=args.port, debug=False)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
