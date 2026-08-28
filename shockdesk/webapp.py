"""
Application web ShockDesk — la forme « research » de Blueshift.

L'URL de travail a exactement la même silhouette::

    /research/strategies/<uuid>/code?name=global-macro&startCapital=25500000
        &startDate=2026-07-01&endDate=2026-08-28&action=backtest

Les mêmes paramètres existent côté API (``POST /api/backtest``) et côté CLI
(``python -m shockdesk.cli backtest``) : une seule grammaire, trois portes
d'entrée.
"""

from __future__ import annotations

import os
import traceback

from flask import Flask, jsonify, redirect, render_template, request, url_for

from . import api, config, registry
from .scenarios import ForecastLedger

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

DEFAULT_PARAMS = {
    "name": "us-equities",
    "startCapital": 10000,
    "startDate": "2020-01-01",
    "endDate": "2021-09-01",
    "action": "backtest",
}


def _err(exc, status=400):
    return jsonify({"ok": False, "error": str(exc),
                    "detail": traceback.format_exc(limit=6)}), status


def create_app() -> Flask:
    app = Flask(__name__, template_folder=os.path.join(WEB_DIR, "templates"),
                static_folder=os.path.join(WEB_DIR, "static"))
    app.config["JSON_AS_ASCII"] = False
    app.json.ensure_ascii = False

    # ------------------------------------------------------------------ #
    # Pages
    # ------------------------------------------------------------------ #
    @app.route("/")
    def home():
        strategies = registry.list_strategies()
        if not strategies:
            return jsonify({"ok": False, "error": "aucune stratégie dans strategies/"}), 500
        first = strategies[0]
        d = dict(first.get("defaults") or {})
        return redirect(url_for("research", sid=first["id"],
                                name=d.get("name", DEFAULT_PARAMS["name"]),
                                startCapital=d.get("startCapital", DEFAULT_PARAMS["startCapital"]),
                                startDate=d.get("startDate", DEFAULT_PARAMS["startDate"]),
                                endDate=d.get("endDate", DEFAULT_PARAMS["endDate"]),
                                action="backtest"))

    @app.route("/research/strategies/<sid>/code")
    def research(sid):
        """La page de recherche. Les paramètres d'URL pilotent le backtest."""
        meta = registry.get(sid)
        if meta is None:
            return jsonify({"ok": False, "error": f"stratégie inconnue : {sid}"}), 404
        params = {
            "name": request.args.get("name", (meta.get("defaults") or {}).get(
                "name", DEFAULT_PARAMS["name"])),
            "startCapital": request.args.get(
                "startCapital", (meta.get("defaults") or {}).get(
                    "startCapital", DEFAULT_PARAMS["startCapital"])),
            "startDate": request.args.get("startDate", (meta.get("defaults") or {}).get(
                "startDate", DEFAULT_PARAMS["startDate"])),
            "endDate": request.args.get("endDate", (meta.get("defaults") or {}).get(
                "endDate", DEFAULT_PARAMS["endDate"])),
            "action": request.args.get("action", DEFAULT_PARAMS["action"]),
        }
        return render_template("index.html", sid=sid, params=params,
                               strategy=meta, universes=config.list_universes(),
                               calibration=config.CALIBRATION_NOTE)

    @app.route("/health")
    def health():
        return jsonify({"ok": True, "service": "shockdesk",
                        "universes": list(config.UNIVERSES),
                        "calibration": config.CALIBRATION_NOTE})

    # ------------------------------------------------------------------ #
    # API — référentiels
    # ------------------------------------------------------------------ #
    @app.route("/api/universes")
    def api_universes():
        return jsonify({"ok": True, "universes": config.list_universes()})

    @app.route("/api/strategies")
    def api_strategies():
        return jsonify({"ok": True, "strategies": registry.list_strategies()})

    @app.route("/api/strategies", methods=["POST"])
    def api_create_strategy():
        body = request.get_json(force=True, silent=True) or {}
        if not body.get("name") or not body.get("code"):
            return _err(ValueError("champs requis : name, code"))
        meta = registry.create(body["name"], body["code"], body.get("defaults") or {})
        return jsonify({"ok": True, "strategy": meta})

    @app.route("/api/strategies/<sid>")
    def api_strategy(sid):
        try:
            meta = registry.get(sid)
            if not meta:
                return _err(KeyError(f"stratégie inconnue : {sid}"), 404)
            return jsonify({"ok": True, "strategy": meta,
                            "code": registry.read_code(sid)})
        except Exception as exc:
            return _err(exc)

    @app.route("/api/strategies/<sid>/code", methods=["PUT", "POST"])
    def api_save_code(sid):
        try:
            body = request.get_json(force=True, silent=True) or {}
            code = body.get("code")
            if code is None:
                return _err(ValueError("champ requis : code"))
            registry.write_code(sid, code)
            if "defaults" in body:
                registry.set_defaults(sid, body["defaults"])
            if "name" in body:
                registry.rename(sid, body["name"])
            return jsonify({"ok": True, "strategy": registry.get(sid)})
        except Exception as exc:
            return _err(exc)

    # ------------------------------------------------------------------ #
    # API — backtest
    # ------------------------------------------------------------------ #
    @app.route("/api/backtest", methods=["POST", "GET"])
    def api_backtest():
        """Mêmes paramètres que l'URL de recherche."""
        body = request.get_json(force=True, silent=True) or {}
        src = body if request.method == "POST" else request.args
        try:
            params = {
                "name": src.get("name", DEFAULT_PARAMS["name"]),
                "startCapital": float(src.get("startCapital", DEFAULT_PARAMS["startCapital"])),
                "startDate": src.get("startDate", DEFAULT_PARAMS["startDate"]),
                "endDate": src.get("endDate", DEFAULT_PARAMS["endDate"]),
                "action": src.get("action", "backtest"),
            }
            sid = src.get("strategy_id") or src.get("strategyId")
            code = src.get("code")
            if sid:
                payload = api.strategy_payload(sid, **params,
                                               source=src.get("source", "auto"))
            elif code:
                payload = api.run_backtest(code, **params,
                                           source=src.get("source", "auto"))
            else:
                return _err(ValueError("strategy_id ou code requis"))
            return jsonify(payload)
        except Exception as exc:
            return _err(exc, 500)

    # ------------------------------------------------------------------ #
    # API — anticipation & options
    # ------------------------------------------------------------------ #
    @app.route("/api/scenarios")
    def api_scenarios():
        try:
            board = api.scenario_board(request.args.get("name", "global-macro"),
                                       asof=request.args.get("asof"),
                                       horizon_days=int(request.args.get("horizon", 45)),
                                       width=float(request.args.get("width", 0.03)))
            return jsonify({"ok": True, **board})
        except Exception as exc:
            return _err(exc, 500)

    @app.route("/api/options/quote", methods=["POST", "GET"])
    def api_options_quote():
        src = request.get_json(force=True, silent=True) or request.args
        try:
            out = api.option_lab(
                underlying=src.get("underlying", "SPY"),
                structure=src.get("structure", "strangle"),
                days=int(src.get("days", 30)),
                width=float(src.get("width", 0.03)),
                iv_shift=float(src.get("iv_shift", 0.0)),
                vol_regime=float(src.get("vol_regime", 1.0)),
                spot_override=src.get("spot"))
            return jsonify({"ok": True, **out})
        except Exception as exc:
            return _err(exc)

    # ------------------------------------------------------------------ #
    # API — registre des prévisions (la boucle de correction mensuelle)
    # ------------------------------------------------------------------ #
    @app.route("/api/ledger")
    def api_ledger():
        led = ForecastLedger()
        return jsonify({"ok": True, "path": led.path,
                        "note": led.raw.get("note", ""),
                        "forecasts": [f.as_dict() for f in led.all()],
                        "revisions": {fid: [f.as_dict() for f in led.revisions(fid)]
                                      for fid in led.revs}})

    @app.route("/api/ledger/<fid>/revision", methods=["POST"])
    def api_ledger_revision(fid):
        """Ajoute une révision datée. On ne réécrit jamais l'historique."""
        try:
            body = request.get_json(force=True, silent=True) or {}
            required = ("sign", "amplitude", "peak_day")
            missing = [k for k in required if k not in body]
            if missing:
                return _err(ValueError(f"champs requis : {', '.join(missing)}"))
            led = ForecastLedger()
            f = led.add_revision(fid, **body)
            return jsonify({"ok": True, "forecast": f.as_dict()})
        except Exception as exc:
            return _err(exc)

    @app.route("/api/ledger", methods=["POST"])
    def api_ledger_new():
        try:
            body = request.get_json(force=True, silent=True) or {}
            for k in ("id", "name", "asset", "sign", "amplitude", "peak_day"):
                if k not in body:
                    return _err(ValueError(f"champ requis : {k}"))
            led = ForecastLedger()
            rev = {k: body[k] for k in ("sign", "amplitude", "peak_day", "reversion",
                                        "reversion_days", "iv_shift", "confidence",
                                        "note", "date") if k in body}
            f = led.add_forecast(body["id"], body["name"], body["asset"],
                                 benchmark=body.get("benchmark", "^GSPC"),
                                 stop_date=body.get("stop_date"),
                                 tags=body.get("tags", []), **rev)
            return jsonify({"ok": True, "forecast": f.as_dict()})
        except Exception as exc:
            return _err(exc)

    return app


def main():
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)),
                     debug=False, threaded=True)


if __name__ == "__main__":
    main()
