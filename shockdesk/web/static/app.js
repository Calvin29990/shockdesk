/* ShockDesk — poste de recherche. Vanilla JS, zéro dépendance externe. */
(function () {
  "use strict";
  const BOOT = window.SHOCKDESK;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const state = {
    code: "", result: null, board: null, quote: null,
    universes: {}, strategy: null, running: false, dirty: false
  };

  /* ------------------------------------------------------------------ */
  /* formatage                                                           */
  /* ------------------------------------------------------------------ */
  const nf = (n, d) => (n === null || n === undefined || isNaN(n)) ? "—"
    : Number(n).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });
  const money = n => (n === null || n === undefined || isNaN(n)) ? "—"
    : (n < 0 ? "-" : "") + Math.abs(n).toLocaleString("fr-FR", { maximumFractionDigits: 0 }) + " $";
  const compact = n => {
    if (n === null || n === undefined || isNaN(n)) return "—";
    const a = Math.abs(n);
    if (a >= 1e9) return (n / 1e9).toFixed(2) + " Md";
    if (a >= 1e6) return (n / 1e6).toFixed(2) + " M";
    if (a >= 1e3) return (n / 1e3).toFixed(1) + " k";
    return n.toFixed(0);
  };
  const pct = (x, d) => (x === null || x === undefined || isNaN(x)) ? "—"
    : (x * 100).toFixed(d === undefined ? 2 : d) + " %";
  const sgn = x => (x > 0 ? "pos" : x < 0 ? "neg" : "");
  // Un ratio non defini (volatilite nulle, drawdown nul, moins de deux jours
  // negatifs) s'affiche "n.d." : un 0,00 se lit comme une mesure et fausse
  // le jugement. Cf. journal de bord, correctif du 30/08/2026.
  const ratio = (n, d) => (n === null || n === undefined || isNaN(n))
    ? "n.d." : nf(n, d);
  const esc = s => String(s === null || s === undefined ? "" : s)
    .replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function el(tag, attrs, kids) {
    const n = document.createElement(tag);
    for (const k in (attrs || {})) {
      if (k === "class") n.className = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k];
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]);
    }
    (Array.isArray(kids) ? kids : kids ? [kids] : []).forEach(c => {
      if (c === null || c === undefined) return;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return n;
  }

  function toast(msg, err) {
    const t = $("#toast");
    t.textContent = msg;
    t.className = "toast show" + (err ? " err" : "");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { t.className = "toast"; }, 3200);
  }
  function status(msg, cls) {
    const s = $("#status");
    s.textContent = msg || "";
    s.className = "status" + (cls ? " " + cls : "");
  }

  /* ------------------------------------------------------------------ */
  /* URL — la forme Blueshift                                            */
  /* ------------------------------------------------------------------ */
  function currentParams() {
    return {
      name: $("#p-name").value,
      startCapital: $("#p-capital").value.replace(/\s/g, ""),
      startDate: $("#p-start").value,
      endDate: $("#p-end").value,
      action: "backtest"
    };
  }
  function buildUrl(p, sid) {
    const base = "/research/strategies/" + (sid || BOOT.sid) + "/code";
    const q = new URLSearchParams();
    q.set("name", p.name);
    q.set("startCapital", p.startCapital);
    q.set("startDate", p.startDate);
    q.set("endDate", p.endDate);
    q.set("action", p.action || "backtest");
    return base + "?" + q.toString();
  }
  function syncUrl() {
    const url = buildUrl(currentParams());
    $("#url-display").textContent = url;
    history.replaceState(null, "", url);
  }

  /* ------------------------------------------------------------------ */
  /* éditeur de code                                                     */
  /* ------------------------------------------------------------------ */
  const PY_KW = ["def", "return", "if", "elif", "else", "for", "while", "in", "not", "and",
    "or", "import", "from", "as", "class", "try", "except", "finally", "with", "lambda",
    "pass", "break", "continue", "global", "None", "True", "False", "raise", "yield",
    "assert", "del", "is", "nonlocal", "async", "await"];
  const API_FN = ["symbol", "symbols", "order", "order_value", "order_target",
    "order_target_value", "order_target_percent", "schedule_function", "date_rules",
    "time_rules", "record", "get_datetime", "option_contract", "get_iv", "vol_regime",
    "get_forecast", "get_scenario", "set_commission", "set_slippage", "log",
    "initialize", "handle_data", "before_trading_start", "context", "data", "structures"];

  function highlight(src) {
    const rx = /("""[\s\S]*?"""|'''[\s\S]*?'''|#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+\.?\d*(?:e[+-]?\d+)?\b|\b[A-Za-z_][A-Za-z0-9_]*\b|\s+|.)/g;
    let out = "", m;
    while ((m = rx.exec(src))) {
      const t = m[0];
      if (t.startsWith('"""') || t.startsWith("'''")) out += '<span class="tk-str">' + esc(t) + "</span>";
      else if (t.startsWith("#")) out += '<span class="tk-com">' + esc(t) + "</span>";
      else if (t.startsWith('"') || t.startsWith("'")) out += '<span class="tk-str">' + esc(t) + "</span>";
      else if (/^\d/.test(t)) out += '<span class="tk-num">' + esc(t) + "</span>";
      else if (/^[A-Za-z_]/.test(t)) {
        if (PY_KW.indexOf(t) >= 0) out += '<span class="tk-kw">' + t + "</span>";
        else if (t === "self") out += '<span class="tk-self">' + t + "</span>";
        else if (API_FN.indexOf(t) >= 0) out += '<span class="tk-api">' + t + "</span>";
        else out += esc(t);
      } else out += esc(t);
    }
    return out;
  }

  function refreshEditor() {
    const ta = $("#code"), pre = $("#highlight"), gut = $("#gutter");
    const src = ta.value;
    pre.innerHTML = highlight(src) + "\n";
    const lines = src.split("\n").length;
    let g = "";
    for (let i = 1; i <= lines; i++) g += i + "\n";
    gut.textContent = g;
    gut.scrollTop = ta.scrollTop;
    pre.scrollTop = ta.scrollTop;
    pre.scrollLeft = ta.scrollLeft;
  }

  function initEditor() {
    const ta = $("#code");
    ta.addEventListener("input", () => { state.dirty = true; refreshEditor(); });
    ta.addEventListener("scroll", () => {
      $("#highlight").scrollTop = ta.scrollTop;
      $("#highlight").scrollLeft = ta.scrollLeft;
      $("#gutter").scrollTop = ta.scrollTop;
    });
    ta.addEventListener("keydown", e => {
      if (e.key === "Tab") {
        e.preventDefault();
        const s = ta.selectionStart, epos = ta.selectionEnd;
        ta.value = ta.value.slice(0, s) + "    " + ta.value.slice(epos);
        ta.selectionStart = ta.selectionEnd = s + 4;
        refreshEditor();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); saveCode(); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runBacktest(); }
    });
  }

  async function loadCode() {
    const r = await fetch("/api/strategies/" + BOOT.sid);
    const j = await r.json();
    if (!j.ok) throw new Error(j.error);
    state.code = j.code;
    state.strategy = j.strategy;
    $("#code").value = j.code;
    $("#code-title").textContent = j.strategy.name || "";
    $("#code-file").textContent = j.strategy.file || "";
    refreshEditor();
    renderCheatsheet(j.code);
  }

  async function saveCode() {
    const code = $("#code").value;
    status("enregistrement…", "busy");
    const r = await fetch("/api/strategies/" + BOOT.sid + "/code", {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code })
    });
    const j = await r.json();
    status("");
    if (!j.ok) return toast("échec : " + j.error, true);
    state.dirty = false;
    toast("code enregistré dans strategies/" + (j.strategy.file || ""));
  }

  function renderCheatsheet(code) {
    const m = code.match(/"""([\s\S]*?)"""/);
    $("#side-forecasts").innerHTML = "";
    $("#api-cheatsheet").innerHTML = [
      "<b>initialize(context)</b> — appelé une fois",
      "<b>handle_data(context, data)</b> — chaque bar",
      "<b>schedule_function(f, date_rules.month_start())</b>",
      "<b>symbol('BZ=F')</b> · <b>symbols(...)</b>",
      "<b>order / order_target_percent(asset, w)</b>",
      "<b>data.current(a,'close')</b> · <b>data.history(a,'close',63)</b>",
      "<b>get_forecast('BZ=F')</b> — prévision active, point-in-time",
      "<b>option_contract(u,'call',moneyness=1.03,days=30)</b>",
      "<b>get_iv(u, 1.0, 30)</b> · <b>vol_regime(u)</b>",
      "<b>record(pnl=..., signal=...)</b>",
      "<b>context.portfolio.portfolio_value / .positions / .cash</b>"
    ].map(x => "<div>" + x + "</div>").join("");
    if (m) {
      const first = m[1].trim().split("\n")[0];
      $("#code-title").setAttribute("title", first);
    }
  }

  /* ------------------------------------------------------------------ */
  /* graphiques SVG maison                                               */
  /* ------------------------------------------------------------------ */
  const PALETTE = ["#28c2a0", "#4aa3ff", "#f2b134", "#ff5d6c", "#a78bfa", "#7dd3fc", "#f472b6"];

  function svgEl(tag, attrs) {
    const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  function niceTicks(min, max, n) {
    if (min === max) { min -= 1; max += 1; }
    const span = max - min;
    const step0 = span / Math.max(n - 1, 1);
    const mag = Math.pow(10, Math.floor(Math.log10(step0)));
    const norm = step0 / mag;
    const step = (norm >= 7.5 ? 10 : norm >= 3.5 ? 5 : norm >= 1.5 ? 2 : 1) * mag;
    const lo = Math.floor(min / step) * step;
    const hi = Math.ceil(max / step) * step;
    const out = [];
    for (let v = lo; v <= hi + step * 1e-6; v += step) out.push(v);
    return out;
  }

  /**
   * lineChart(box, series, opts)
   * series: [{name, values:[{x:label,y:number}], color, fill, axis:'l'|'r'}]
   */
  function lineChart(box, series, opts) {
    opts = opts || {};
    box.innerHTML = "";
    const W = box.clientWidth || 600, H = box.clientHeight || 220;
    const pad = { l: opts.padL || 58, r: opts.padR || 16, t: 12, b: 22 };
    const svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, preserveAspectRatio: "none" });

    const all = series.filter(s => s.values && s.values.length);
    if (!all.length) { box.appendChild(el("div", { class: "muted" }, "pas de données")); return; }
    let ys = [];
    all.forEach(s => s.values.forEach(p => { if (p.y !== null && !isNaN(p.y)) ys.push(p.y); }));
    let lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
    if (opts.zero) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
    if (lo === hi) { lo -= 1; hi += 1; }
    const padY = (hi - lo) * 0.08;
    lo -= padY; hi += padY;
    const n = all[0].values.length;
    const X = i => pad.l + (n <= 1 ? 0 : i * (W - pad.l - pad.r) / (n - 1));
    const Y = v => pad.t + (hi - v) * (H - pad.t - pad.b) / (hi - lo);

    const ticks = niceTicks(lo, hi, 5);
    ticks.forEach(t => {
      if (t < lo || t > hi) return;
      svg.appendChild(svgEl("line", { x1: pad.l, x2: W - pad.r, y1: Y(t), y2: Y(t), stroke: "#1b2836", "stroke-width": 1 }));
      const txt = svgEl("text", { x: pad.l - 6, y: Y(t) + 3.5, "text-anchor": "end", fill: "#61748a", "font-size": 10, "font-family": "var(--mono)" });
      txt.textContent = opts.fmtY ? opts.fmtY(t) : compact(t);
      svg.appendChild(txt);
    });
    if (opts.zero || (lo < 0 && hi > 0)) {
      svg.appendChild(svgEl("line", { x1: pad.l, x2: W - pad.r, y1: Y(0), y2: Y(0), stroke: "#33475b", "stroke-width": 1 }));
    }

    // axe des abscisses
    const labels = all[0].values.map(p => p.x);
    const every = Math.max(1, Math.floor(labels.length / 6));
    labels.forEach((l, i) => {
      if (i % every !== 0 && i !== labels.length - 1) return;
      const txt = svgEl("text", { x: X(i), y: H - 6, "text-anchor": i === 0 ? "start" : "middle", fill: "#61748a", "font-size": 9.5, "font-family": "var(--mono)" });
      txt.textContent = String(l).slice(0, 10);
      svg.appendChild(txt);
    });

    all.forEach((s, si) => {
      const col = s.color || PALETTE[si % PALETTE.length];
      const pts = s.values.map((p, i) => X(i) + "," + Y(p.y === null || isNaN(p.y) ? lo : p.y)).join(" ");
      if (s.fill) {
        const area = svgEl("polygon", {
          points: pad.l + "," + Y(Math.max(lo, 0)) + " " + pts + " " + X(s.values.length - 1) + "," + Y(Math.max(lo, 0)),
          fill: col, opacity: 0.14
        });
        svg.appendChild(area);
      }
      svg.appendChild(svgEl("polyline", {
        points: pts, fill: "none", stroke: col, "stroke-width": s.width || 1.6,
        "stroke-dasharray": s.dash || "none", "vector-effect": "non-scaling-stroke"
      }));
    });

    // curseur
    const cross = svgEl("line", { y1: pad.t, y2: H - pad.b, stroke: "#4a6480", "stroke-width": 1, opacity: 0 });
    svg.appendChild(cross);
    const tip = el("div", { class: "tooltip" });
    tip.style.opacity = 0;
    box.appendChild(svg); box.appendChild(tip);

    svg.addEventListener("mousemove", ev => {
      const r = svg.getBoundingClientRect();
      const px = (ev.clientX - r.left) * (W / r.width);
      const i = Math.round((px - pad.l) / ((W - pad.l - pad.r) / Math.max(n - 1, 1)));
      const idx = Math.max(0, Math.min(n - 1, i));
      cross.setAttribute("x1", X(idx)); cross.setAttribute("x2", X(idx)); cross.setAttribute("opacity", 1);
      let html = "<div style='color:#8fa3b8'>" + esc(labels[idx]) + "</div>";
      all.forEach((s, si) => {
        const v = s.values[idx] ? s.values[idx].y : null;
        const txt = opts.fmtY ? opts.fmtY(v) : compact(v);
        html += "<div><span style='color:" + (s.color || PALETTE[si % PALETTE.length]) + "'>■</span> "
          + esc(s.name) + " <b>" + txt + "</b></div>";
      });
      tip.innerHTML = html;
      tip.style.opacity = 1;
      const left = Math.min(Math.max(ev.clientX - r.left + 12, 4), r.width - 170);
      tip.style.left = left + "px";
      tip.style.top = Math.max(ev.clientY - r.top - 10, 4) + "px";
    });
    svg.addEventListener("mouseleave", () => { tip.style.opacity = 0; cross.setAttribute("opacity", 0); });
  }

  function barChart(box, items, opts) {
    opts = opts || {};
    box.innerHTML = "";
    if (!items.length) { box.appendChild(el("div", { class: "muted" }, "pas de données")); return; }
    const W = box.clientWidth || 600, H = box.clientHeight || 260;
    const pad = { l: 84, r: 62, t: 8, b: 18 };
    const svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H });
    const vals = items.map(i => i.value);
    let lo = Math.min(0, Math.min.apply(null, vals));
    let hi = Math.max(0, Math.max.apply(null, vals));
    if (lo === hi) { lo -= 1; hi += 1; }
    const rowH = (H - pad.t - pad.b) / items.length;
    const barH = Math.max(4, Math.min(20, rowH * 0.62));
    const X = v => pad.l + (v - lo) * (W - pad.l - pad.r) / (hi - lo);

    svg.appendChild(svgEl("line", { x1: X(0), x2: X(0), y1: pad.t, y2: H - pad.b, stroke: "#33475b" }));
    items.forEach((it, i) => {
      const y = pad.t + i * rowH + (rowH - barH) / 2;
      const x0 = X(Math.min(0, it.value)), x1 = X(Math.max(0, it.value));
      svg.appendChild(svgEl("rect", {
        x: Math.min(x0, x1), y: y, width: Math.max(1, Math.abs(x1 - x0)), height: barH,
        fill: it.value >= 0 ? "#28c2a0" : "#ff5d6c", opacity: 0.85, rx: 2
      }));
      const lab = svgEl("text", { x: pad.l - 8, y: y + barH / 2 + 3.5, "text-anchor": "end", fill: "#8fa3b8", "font-size": 10.5, "font-family": "var(--mono)" });
      lab.textContent = it.label.length > 12 ? it.label.slice(0, 12) : it.label;
      svg.appendChild(lab);
      const val = svgEl("text", { x: W - pad.r + 8, y: y + barH / 2 + 3.5, fill: it.value >= 0 ? "#28c2a0" : "#ff5d6c", "font-size": 10.5, "font-family": "var(--mono)" });
      val.textContent = opts.fmt ? opts.fmt(it.value) : compact(it.value);
      svg.appendChild(val);
    });
    box.appendChild(svg);
  }

  function pair(dates, values) {
    return (values || []).map((v, i) => ({ x: dates[i], y: v }));
  }

  /* ------------------------------------------------------------------ */
  /* backtest                                                            */
  /* ------------------------------------------------------------------ */
  function card(k, v, sub, cls, title) {
    return el("div", { class: "card", title: title || "" }, [
      el("div", { class: "k" }, k),
      el("div", { class: "v " + (cls || "") }, v),
      sub ? el("div", { class: "s" }, sub) : null
    ]);
  }

  function renderBacktest(p) {
    $("#bt-empty").classList.toggle("hidden", !!p.ok);
    $("#bt-content").classList.toggle("hidden", !p.ok);
    const src = $("#source-badge");
    src.textContent = p.data.source + " · " + p.data.detail;
    src.className = "badge " + (p.data.source === "yfinance" ? "live" : "synth");

    if (!p.ok) {
      $("#bt-empty").innerHTML = "<h3 style='color:var(--red)'>Erreur d'exécution</h3><pre class='code-block'>"
        + esc(p.error) + "</pre>";
      return;
    }
    const m = p.metrics;
    const pnl = m.final_equity - p.params.startCapital;
    $("#metric-cards").innerHTML = "";
    [
      card("P&L", money(pnl), pct(m.total_return), sgn(pnl)),
      card("Capital final", money(m.final_equity), "départ " + money(p.params.startCapital)),
      card("CAGR", pct(m.cagr), "sur " + m.years + " an(s)", sgn(m.cagr)),
      card("Vol annualisée", pct(m.ann_volatility)),
      card("Sharpe", ratio(m.sharpe, 2), "Sortino " + ratio(m.sortino, 2), sgn(m.sharpe),
           (m.risk_free ? "Sharpe net du taux sans risque de " + pct(m.risk_free, 1)
             + " par an, retire a chaque barre — y compris celles ou le book dort en\n"
             + "liquidites (le moteur ne remunere pas le cash)."
             : "Volatilite nulle : ratio non defini.")),
      card("Drawdown max", pct(m.max_drawdown), "Calmar " + ratio(m.calmar, 2), sgn(m.max_drawdown),
           "Calmar = CAGR / drawdown max. Non defini si le drawdown est nul."),
      card("Win rate", pct(m.win_rate, 1), m.trades + " trades · " + money(m.turnover) + " échangés"),
      card("Benchmark", pct(m.benchmark_return), m.benchmark_symbol + " · alpha " + pct(m.alpha) + " · β " + nf(m.beta, 2),
        sgn((m.alpha || 0)))
    ].forEach(c => $("#metric-cards").appendChild(c));

    // courbe d'équité
    const series = [{
      name: "stratégie", values: pair(p.equity.dates, p.equity.values),
      color: "#28c2a0", width: 2, fill: true
    }];
    if (p.benchmark) series.push({
      name: p.benchmark.symbol, values: pair(p.benchmark.dates, p.benchmark.values),
      color: "#4aa3ff", width: 1.3, dash: "4 3"
    });
    $("#eq-legend").textContent = "· " + p.universe.label + " · " + p.data.bars + " barres";
    lineChart($("#chart-equity"), series, { fmtY: v => compact(v) });
    lineChart($("#chart-dd"), [{
      name: "drawdown", values: pair(p.drawdown.dates, p.drawdown.values.map(v => v * 100)),
      color: "#ff5d6c", fill: true
    }], { zero: true, fmtY: v => v.toFixed(1) + "%" });

    const attr = Object.keys(p.attribution || {}).map(k => ({ label: k, value: p.attribution[k] }));
    barChart($("#chart-attribution"), attr, { fmt: v => compact(v) + " $" });

    // grecs
    if ((p.greeks || []).length) {
      const gd = p.greeks.map(g => g.date);
      lineChart($("#chart-greeks"), [
        { name: "delta (nb de titres)", values: pair(gd, p.greeks.map(g => g.delta)), color: "#4aa3ff" },
        { name: "vega (par point)", values: pair(gd, p.greeks.map(g => g.vega)), color: "#f2b134" },
        { name: "theta (par jour)", values: pair(gd, p.greeks.map(g => g.theta)), color: "#ff5d6c" },
        { name: "gamma", values: pair(gd, p.greeks.map(g => g.gamma)), color: "#a78bfa" }
      ], {});
    }

    // records
    const recKeys = Object.keys(p.records || {});
    if (recKeys.length) {
      $("#records-box").classList.remove("hidden");
      lineChart($("#chart-records"), recKeys.map((k, i) => ({
        name: k, values: pair(p.records[k].dates, p.records[k].values),
        color: PALETTE[i % PALETTE.length]
      })), {});
    } else {
      $("#records-box").classList.add("hidden");
    }

    // tables
    const pos = p.positions || [];
    $("#tbl-positions").innerHTML = pos.length ? table(
      ["ligne", "type", "quantité", "PRU", "dernier", "valeur", "P&L latent", "P&L réalisé"],
      pos.map(r => [r.label, r.type, nf(r.amount, 2), nf(r.cost_basis, 3), nf(r.last_sale_price, 3),
      { v: money(r.market_value), c: "num" }, { v: money(r.unrealized_pnl), c: "num " + sgn(r.unrealized_pnl) },
      { v: money(r.realized_pnl), c: "num " + sgn(r.realized_pnl) }]))
      : "<tr><td class='muted'>aucune position en fin de période</td></tr>";

    const sc = p.scorecard || {};
    const rows = sc.rows || [];
    const tagOf = r => r.error ? ["non évaluable", "na"]
      : r.is_benchmark ? ["non-test", "na"]
      : r.counted ? ["compté", "ok"] : ["correction", "na"];
    $("#tbl-scorecard").innerHTML = rows.length ? table(
      ["ligne", "rév.", "statut", "sens prévu", "réel", "amplitude", "pic prévu", "pic réel", "écart"],
      rows.map(r => {
        const t = tagOf(r);
        if (r.error) return [r.asset, "r" + r.rev, { v: t[0], c: "muted" },
          { v: "—", c: "muted" }, { v: "—", c: "muted" },
          { v: r.error, c: "muted" }, "", "", ""];
        return [
          r.asset, "r" + r.rev, { v: t[0], c: "" },
          { v: (r.sign_forecast > 0 ? "↑" : "↓"), c: r.sign_forecast > 0 ? "pos" : "neg" },
          { v: (r.sign_ok_peak ? "✔ " : "✘ ") + pct(r.amplitude_realized, 1), c: r.sign_ok_peak ? "pos" : "neg" },
          { v: pct(r.amplitude_forecast, 1) + " → x" + nf(r.amplitude_ratio, 2), c: "num" },
          { v: "J+" + r.peak_forecast_days, c: "num" },
          { v: "J+" + r.peak_realized_days, c: "num" },
          { v: (r.peak_error_days > 0 ? "+" : "") + r.peak_error_days + " j", c: "num " + (r.peak_error_days ? "neg" : "pos") }
        ];
      })) + "<tfoot><tr><td colspan='9' class='muted'>accord de signe net du drift : <b>"
      + (sc.sign_hits || 0) + "/" + (sc.sign_total || 0) + "</b> sur les révisions originales ("
      + (sc.lines_total || 0) + " lignes publiées, " + (sc.non_test || 0) + " non-test) · "
      + "erreur de pic médiane <b>" + nf(sc.median_peak_error_days, 1) + " j</b> · "
      + "ratio d'amplitude médian <b>" + nf(sc.median_amplitude_ratio, 2) + "</b>"
      + ((sc.misses || []).length ? " · misses : <b>" + esc((sc.misses || []).join(", ")) + "</b>" : "")
      + "</td></tr></tfoot>"
      : "<tr><td class='muted'>aucune prévision publiée</td></tr>";

    $("#trades-count").textContent = "(" + (p.trades || []).length + ")";
    $("#tbl-trades").innerHTML = (p.trades || []).length ? table(
      ["date", "ligne", "sens", "quantité", "prix", "brut", "commission", "motif"],
      p.trades.slice(-400).reverse().map(t => [t.date, t.sid,
      { v: t.side === "buy" ? "achat" : "vente", c: t.side === "buy" ? "pos" : "neg" },
      { v: nf(t.amount, 2), c: "num" }, { v: nf(t.price, 3), c: "num" },
      { v: money(t.gross), c: "num" }, { v: nf(t.commission, 2), c: "num" }, t.reason]))
      : "<tr><td class='muted'>aucune transaction</td></tr>";

    $("#log-box").innerHTML = (p.logs || []).map(l =>
      "<div class='log-line " + esc(l.level) + "'><span class='d'>" + esc(l.date)
      + "</span><span class='m'>" + esc(l.message) + "</span></div>").join("")
      || "<div class='muted'>journal vide</div>";
  }

  function table(head, rows) {
    let h = "<thead><tr>" + head.map(x => "<th>" + esc(x) + "</th>").join("") + "</tr></thead><tbody>";
    rows.forEach(r => {
      h += "<tr>" + r.map(c => {
        if (c && typeof c === "object" && !Array.isArray(c))
          return "<td class='" + (c.c || "") + "'>" + esc(c.v) + "</td>";
        return "<td>" + esc(c) + "</td>";
      }).join("") + "</tr>";
    });
    return h + "</tbody>";
  }

  /* ------------------------------------------------------------------ */
  /* exécution                                                           */
  /* ------------------------------------------------------------------ */
  async function runBacktest(opts) {
    if (state.running) return;
    // Le moteur relit le fichier enregistre, pas l'editeur : lancer avec des
    // modifications non enregistrees_execute silencieusement l'ancienne version.
    if (state.dirty) {
      toast("Attention : le code affiche n'est pas enregistre. Le backtest part sur "
            + "la derniere version sauvegardee — cliquez sur Enregistrer d'abord.", true);
    }
    state.running = true;
    $("#btn-run").disabled = true;
    status("backtest en cours…", "busy");
    syncUrl();
    const params = currentParams();
    const body = Object.assign({ strategy_id: BOOT.sid }, params, opts || {});
    const t0 = performance.now();
    try {
      const r = await fetch("/api/backtest", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const j = await r.json();
      state.result = j;
      renderBacktest(j);
      switchTab("backtest");
      const ms = Math.round(performance.now() - t0);
      status((j.ok ? "ok · " : "erreur · ") + ms + " ms · " + (j.data ? j.data.bars : 0) + " barres · "
        + (j.data ? j.data.source : ""), j.ok ? "" : "err");
      if (j.ok) toast("Backtest exécuté : " + pct(j.metrics.total_return) + " sur " + j.data.bars + " barres");
    } catch (e) {
      status("échec réseau", "err");
      toast("échec : " + e.message, true);
    } finally {
      state.running = false;
      $("#btn-run").disabled = false;
    }
  }

  /* ------------------------------------------------------------------ */
  /* anticipation                                                        */
  /* ------------------------------------------------------------------ */
  async function loadScenarios() {
    status("chargement des prévisions…", "busy");
    const q = new URLSearchParams({
      name: $("#sc-universe").value,
      horizon: $("#sc-horizon").value
    });
    if ($("#sc-asof").value) q.set("asof", $("#sc-asof").value);
    const r = await fetch("/api/scenarios?" + q.toString());
    const j = await r.json();
    status("");
    if (!j.ok) return toast("échec : " + j.error, true);
    state.board = j;
    renderScenarios(j);
  }

  function renderScenarios(b) {
    const sc = b.scorecard || {};
    $("#scorecard-banner").innerHTML =
      "<div class='score-banner'>"
      + "<div><div class='lbl'>accord de signe (net du drift)</div><div class='big'>"
      + (sc.sign_hits || 0) + " / " + (sc.sign_total || 0) + "</div>"
      + "<div class='lbl'>" + ((sc.misses || []).length ? "misses : " + esc((sc.misses || []).join(", ")) : "aucun miss") + "</div></div>"
      + "<div><div class='lbl'>erreur de timing du pic (médiane)</div><div class='big'>"
      + nf(sc.median_peak_error_days, 1) + " j</div></div>"
      + "<div><div class='lbl'>ratio d'amplitude médian</div><div class='big'>"
      + nf(sc.median_amplitude_ratio, 2) + "x</div></div>"
      + "<div><div class='lbl'>au</div><div class='big'>" + esc(b.asof || "—") + "</div></div>"
      + "<div class='muted'>Données : " + esc(b.data_source)
      + ". Le sens est mesuré net du benchmark, pondéré par le beta de la ligne. "
      + "Les misses sont affichés avec les réussites.</div></div>";

    const box = $("#scenario-rows");
    box.innerHTML = "";
    (b.rows || []).forEach(row => {
      const f = row.forecast;
      const head = el("div", { class: "scen-card-head" }, [
        el("span", { class: "scen-sym" }, row.symbol),
        el("span", { class: "scen-name" }, row.name + " · " + row.asset_class),
        el("div", { class: "scen-nums" }, [
          num("spot", nf(row.spot, 2) + (row.unit !== "USD" ? " " + row.unit : "")),
          num("vol réalisée", pct(row.realized_vol, 1)),
          num("régime", nf(row.vol_regime, 2) + "x"),
          num("IV 30 j", pct(row.iv_atm_30d, 1)),
          num("IV de base", pct(row.iv_base, 1))
        ])
      ]);
      const body = el("div", { class: "scen-body" + (f ? "" : " wide") });

      if (!f) {
        body.appendChild(el("div", { class: "muted" },
          "Aucune prévision active sur cette ligne au " + b.asof + ". "
          + "Ajoutez-en une dans config/forecasts.json ou via l'API /api/ledger."));
      } else {
        const v = row.validation || {};
        const left = el("div", {}, [
          el("div", { class: "kv", html:
            "<div><span>prévision</span><span>" + esc(f.name) + "</span></div>"
            + "<div><span>révision</span><span>r" + f.rev + " · publiée le " + esc(f.published) + "</span></div>"
            + "<div><span>sens</span><span class='" + (f.sign > 0 ? "pos" : "neg") + "'>"
            + (f.sign > 0 ? "hausse ↑" : "baisse ↓") + "</span></div>"
            + "<div><span>amplitude</span><span>" + pct(f.amp_base, 1)
            + " <span class='muted'>grille " + f.grid.map(g => pct(g, 1)).join(" / ") + "</span></span></div>"
            + "<div><span>pic</span><span>J+" + nf(f.peak_base, 0) + "</span></div>"
            + "<div><span>reversion</span><span>" + pct(f.reversion, 1) + " sur " + f.reversion_days + " j</span></div>"
            + "<div><span>choc d'IV</span><span>" + (f.iv_shift >= 0 ? "+" : "") + (f.iv_shift * 100).toFixed(0) + " pts</span></div>"
            + "<div><span>confiance</span><span>" + pct(f.confidence, 0) + "</span></div>"
            + "<div><span>stop ex-ante</span><span>" + esc(f.stop_date || "—") + "</span></div>"
            + "<div><span>note</span><span style='text-align:right;max-width:60%'>" + esc(f.note || "") + "</span></div>"
          }),
          validationBlock(v),
          revisionForm(f)
        ]);
        body.appendChild(left);

        const right = el("div", {}, [
          el("h3", { style: "margin:0 0 8px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--fg-mute)" },
            "Structures cohérentes avec cette prévision")
        ]);
        const st = row.structures || [];
        if (!st.length) {
          right.appendChild(el("div", { class: "muted" },
            "Pas d'options modélisées sur ce sous-jacent (ou univers sans options)."));
        } else {
          const rec = row.recommendation || {};
          right.appendChild(el("div", { class: "muted", style: "margin-bottom:8px" },
            "Mouvement attendu " + pct(rec.expected_move / row.spot, 1)
            + " · mouvement payé par l'IV " + pct(rec.implied_move / row.spot, 1)
            + " · ratio " + nf(rec.ratio, 2)));
          const list = el("div", { class: "struct-list" });
          st.forEach(s => list.appendChild(structureCard(s, row)));
          right.appendChild(list);
        }
        body.appendChild(right);
      }

      box.appendChild(el("div", { class: "scen-card" }, [head, body]));
    });

    // mini-courbes de trajectoire prévue
    (b.rows || []).forEach((row, i) => {
      if (!row.path) return;
      const host = $$(".scen-card")[i];
      if (!host) return;
      const box2 = el("div", { class: "chart", style: "height:130px;margin-top:10px" });
      host.querySelector(".scen-body").appendChild(box2);
      lineChart(box2, [{
        name: "trajectoire prévue", color: "#f2b134", width: 1.6,
        values: row.path.map(p => ({ x: "J+" + p.day, y: p.value * 100 }))
      }], { zero: true, fmtY: v => v.toFixed(1) + "%" });
    });
  }

  function num(k, v) {
    return el("div", {}, [el("span", {}, k), el("span", {}, v)]);
  }

  function validationBlock(v) {
    if (!v || v.sign_ok_peak === undefined)
      return el("div", { class: "muted", style: "margin-top:8px" },
        "Pas encore évaluable : " + esc((v && v.error) || "fenêtre non couverte par les données"));
    return el("div", { class: "kv", style: "margin-top:10px", html:
      "<div><span>validation</span><span>"
      + (v.sign_ok_peak ? "<span class='chip ok'>sens ✔</span>" : "<span class='chip ko'>sens ✘</span>")
      + " <span class='muted'>fenêtre " + esc((v.window || []).join(" → ")) + "</span></span></div>"
      + "<div><span>amplitude réelle</span><span>" + pct(v.amplitude_realized, 1)
      + " vs " + pct(v.amplitude_forecast, 1) + " → <b>x" + nf(v.amplitude_ratio, 2) + "</b></span></div>"
      + "<div><span>pic réel</span><span>" + esc(v.peak_date) + " (J+" + v.peak_realized_days
      + ") · écart <b>" + (v.peak_error_days > 0 ? "+" : "") + v.peak_error_days + " j</b></span></div>"
      + "<div><span>net du drift</span><span>" + pct(v.end_return_active, 2)
      + " <span class='muted'>(brut " + pct(v.end_return_raw, 2) + ", benchmark "
      + pct(v.benchmark_drift, 2) + ", β " + nf(v.beta_to_benchmark, 2) + ")</span></span></div>"
      + "<div><span>MFE / MAE</span><span>" + pct(v.mfe, 2) + " / " + pct(v.mae, 2) + "</span></div>"
      + "<div><span>corrélation de trajectoire</span><span>" + nf(v.path_correlation, 2) + "</span></div>"
    });
  }

  function structureCard(s, row) {
    const g = s.greeks || {};
    const cells = (s.pnl_scenarios || []).map(p =>
      "<span class='pnl-cell' style='color:" + (p.pnl >= 0 ? "#28c2a0" : "#ff5d6c") + "'>"
      + esc(p.label) + " <b>" + compact(p.pnl) + "</b></span>").join("");
    const node = el("div", { class: "struct" }, [
      el("h4", {}, [s.name, el("span", { class: "chip na" }, s.days + " j"),
        el("button", { class: "btn tiny", style: "margin-left:auto",
          onclick: () => openInLab(row.symbol, s.kind || "strangle", s.days) }, "ouvrir dans l'atelier")]),
      el("p", { class: "why" }, s.rationale || ""),
      el("div", { class: "figs", html:
        "<span>prime nette <b>" + nf(s.cost, 2) + "</b> (" + (s.cost >= 0 ? "débit" : "crédit") + ")</span>"
        + "<span>perte max <b class='neg'>" + (s.max_loss_bounded ? nf(s.max_loss, 2) : "non bornée") + "</b></span>"
        + "<span>gain max <b class='pos'>" + (s.max_gain_bounded ? nf(s.max_profit, 2) : "illimité") + "</b></span>"
        + "<span>points morts <b>" + ((s.breakevens || []).map(b => nf(b, 1)).join(" / ") || "hors plage") + "</b></span>"
        + "<span>Δ " + nf(g.delta, 2) + " · Γ " + nf(g.gamma, 4) + " · V " + nf(g.vega, 2)
        + " · Θ " + nf(g.theta, 3) + "</span>" }),
      el("div", { class: "pnl-grid", html: cells })
    ]);
    return node;
  }

  function revisionForm(f) {
    const wrap = el("div", { class: "rev-form" });
    const fields = [
      ["sens", "select", ["+1 hausse", "-1 baisse"]],
      ["amplitude", "number", "0.05"], ["pic (j)", "number", "7"],
      ["reversion", "number", "-0.03"], ["IV (pts)", "number", "0.00"],
      ["confiance", "number", "0.5"]
    ];
    const inputs = {};
    fields.forEach(([lab, type, val]) => {
      const key = lab.split(" ")[0].toLowerCase();
      const id = "rev-" + f.id + "-" + key;
      let input;
      if (type === "select") {
        input = el("select", { id: id }, [el("option", { value: "1" }, "+1 hausse"),
        el("option", { value: "-1" }, "-1 baisse")]);
        input.value = String(f.sign);
      } else {
        input = el("input", { id: id, type: "number", step: "0.01" });
        const map = { amplitude: f.amp_base, pic: f.peak_base, reversion: f.reversion,
          iv: (f.iv_shift !== undefined ? f.iv_shift * 100 : undefined), confiance: f.confidence };
        input.value = map[key] !== undefined ? map[key] : val;
      }
      inputs[key] = input;
      wrap.appendChild(el("label", { class: "field" }, [el("span", {}, lab), input]));
    });
    const note = el("input", { type: "text", placeholder: "note de révision", style: "width:260px" });
    wrap.appendChild(el("label", { class: "field" }, [el("span", {}, "note"), note]));
    wrap.appendChild(el("button", {
      class: "btn primary", onclick: async () => {
        const body = {
          sign: parseInt(inputs.sens.value, 10),
          amplitude: parseFloat(inputs.amplitude.value),
          peak_day: parseFloat(inputs.pic.value),
          reversion: parseFloat(inputs.reversion.value),
          iv_shift: parseFloat(inputs.iv.value) / 100,
          confidence: parseFloat(inputs.confiance.value),
          note: note.value || "révision mensuelle"
        };
        const r = await fetch("/api/ledger/" + encodeURIComponent(f.id) + "/revision", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        const j = await r.json();
        if (!j.ok) return toast("échec : " + j.error, true);
        toast("révision r" + j.forecast.rev + " enregistrée sur " + f.id);
        loadScenarios();
      }
    }, "ajouter une révision"));
    return wrap;
  }

  /* ------------------------------------------------------------------ */
  /* atelier options                                                     */
  /* ------------------------------------------------------------------ */
  function openInLab(underlying, structure, days) {
    switchTab("options");
    $("#op-underlying").value = underlying;
    if (structure && $$("#op-structure option").some(o => o.value === structure))
      $("#op-structure").value = structure;
    if (days) $("#op-days").value = days;
    quote();
  }

  async function quote() {
    status("pricing…", "busy");
    const body = {
      underlying: $("#op-underlying").value,
      structure: $("#op-structure").value,
      days: parseInt($("#op-days").value, 10),
      width: parseFloat($("#op-width").value),
      // Le champ affiche des points (10 = +10 pts) ; le moteur attend une
      // fraction (0.10 = +10 pts). La conversion est faite ici, à la saisie.
      iv_shift: parseFloat($("#op-ivshift").value) / 100,
      vol_regime: parseFloat($("#op-regime").value)
    };
    const r = await fetch("/api/options/quote", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const j = await r.json();
    status("");
    if (!j.ok) return toast("échec : " + j.error, true);
    state.quote = j;
    renderQuote(j);
  }

  function renderQuote(q) {
    $("#op-title").textContent = q.name + " sur " + q.underlying + " (" + q.underlying_name
      + ") — " + q.days + " jours";
    const g = q.greeks || {};
    const warns = (q.warnings || []).map(w =>
      "<div class='warn'>⚠ " + esc(w) + "</div>").join("");
    $("#op-summary").innerHTML = warns +
      "<div class='kv'>"
      + "<div><span>spot</span><span>" + nf(q.spot, 2) + "</span></div>"
      + "<div><span>prime nette</span><span class='" + sgn(-q.net_premium) + "'>"
      + nf(q.net_premium, 2) + " (" + (q.net_premium >= 0 ? "débit" : "crédit") + ")</span></div>"
      + "<div><span>perte max</span><span class='neg'>" + (q.max_loss_bounded
        ? nf(q.max_loss, 2) : "non bornée (structure vendeuse)") + "</span></div>"
      + "<div><span>gain max</span><span class='pos'>" + (q.max_gain_bounded
        ? nf(q.max_profit, 2) : "illimité (structure acheteuse)") + "</span></div>"
      + "<div><span>points morts</span><span>"
      + (((q.breakevens || []).map(b => nf(b, 2)).join(" / ")) || "hors plage") + "</span></div>"
      + "<div><span>delta</span><span>" + nf(g.delta, 3) + "</span></div>"
      + "<div><span>gamma</span><span>" + nf(g.gamma, 5) + "</span></div>"
      + "<div><span>vega</span><span>" + nf(g.vega, 3) + " / point de vol</span></div>"
      + "<div><span>theta</span><span>" + nf(g.theta, 3) + " / jour</span></div>"
      + "<div><span>IV de la surface</span><span>" + (q.legs || []).map(l => pct(l.iv, 1)).join(" / ") + "</span></div>"
      + "<div><span>hypothèses</span><span>régime de vol " + nf(q.vol_regime, 2)
      + "x · choc d'IV " + (q.iv_shift * 100).toFixed(0) + " pts</span></div>"
      + "</div>";
    $("#tbl-legs").innerHTML = table(["sens", "type", "strike", "prime", "IV", "delta"],
      (q.legs || []).map(l => [
        { v: l.qty > 0 ? "achat " + l.qty : "vente " + Math.abs(l.qty), c: l.qty > 0 ? "pos" : "neg" },
        l.kind, { v: nf(l.strike, 2), c: "num" }, { v: nf(l.premium, 2), c: "num" },
        { v: pct(l.iv, 1), c: "num" }, { v: nf((l.greeks || {}).delta * l.qty, 3), c: "num" }]));

    const curve = q.payoff_curve || [];
    lineChart($("#chart-payoff"), [{
      name: "P&L à l'échéance", color: "#4aa3ff", fill: true,
      values: curve.map(p => ({ x: nf(p.s, 1), y: p.pnl }))
    }], { zero: true, fmtY: v => compact(v) });

    if (!$("#op-catalog").children.length) {
      const cat = q.catalog || {};
      Object.keys(cat).forEach(k => {
        $("#op-catalog").appendChild(el("div", {
          class: "cat-item", onclick: () => { $("#op-structure").value = k; quote(); }
        }, [el("b", {}, cat[k].label), el("p", {}, cat[k].desc)]));
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* divers                                                              */
  /* ------------------------------------------------------------------ */
  function switchTab(name) {
    $$(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === name));
    $$(".panel").forEach(p => p.classList.toggle("active", p.id === "tab-" + name));
    if (name === "scenarios" && !state.board) loadScenarios();
    if (name === "options" && !state.quote) quote();
    if (name === "backtest" && state.result) {
      requestAnimationFrame(() => renderBacktest(state.result));
    }
  }

  function fillUniverses() {
    const opts = BOOT.universes.map(u => el("option", { value: u.name }, u.label));
    $("#p-name").innerHTML = "";
    $("#sc-universe").innerHTML = "";
    BOOT.universes.forEach(u => {
      $("#p-name").appendChild(el("option", { value: u.name }, u.label));
      $("#sc-universe").appendChild(el("option", { value: u.name }, u.label));
      state.universes[u.name] = u;
    });
    $("#p-name").value = BOOT.params.name;
    $("#sc-universe").value = BOOT.params.name;

    const allSymbols = {};
    BOOT.universes.forEach(u => (u.assets || []).forEach(a => { if (a.options) allSymbols[a.symbol] = a; }));
    $("#op-underlying").innerHTML = "";
    const order = Object.keys(allSymbols).sort((a, b) =>
      (a === "SPY" ? -1 : b === "SPY" ? 1 : a.localeCompare(b)));
    order.forEach(s =>
      $("#op-underlying").appendChild(el("option", { value: s }, s + " — " + allSymbols[s].name)));
    if (allSymbols["SPY"]) $("#op-underlying").value = "SPY";
  }

  function renderAssets() {
    const u = state.universes[$("#p-name").value];
    if (!u) return;
    $("#side-universe").textContent = "· " + u.name;
    $("#side-assets").innerHTML = (u.assets || []).map(a =>
      "<div class='asset-row'><span>" + esc(a.symbol) + "</span><span>"
      + esc(a.name.slice(0, 22)) + " · vol " + (a.ann_vol * 100).toFixed(0) + "%"
      + (a.options ? " · opt" : "") + "</span></div>").join("");
  }

  function renderSideForecasts() {
    fetch("/api/ledger").then(r => r.json()).then(j => {
      if (!j.ok) return;
      $("#side-forecasts").innerHTML = (j.forecasts || []).map(f =>
        "<div class='forecast-item'><div class='fid'>" + esc(f.asset) + " · r" + f.rev + "</div>"
        + "<div class='fmeta'>" + esc(f.name) + "</div>"
        + "<div class='fmeta'>publiée " + esc(f.published) + " · sens " + (f.sign > 0 ? "↑" : "↓")
        + " " + (f.amp_base * 100).toFixed(1) + "% · pic J+" + f.peak_base
        + " · stop " + esc(f.stop_date || "—") + "</div></div>").join("")
        || "<div class='muted'>registre vide</div>";
    });
  }

  function renderDoc() {
    const p = currentParams();
    $("#doc-url").textContent = location.origin + buildUrl(p);
    $("#doc-api").textContent =
      "# même backtest via l'API\ncurl -X POST " + location.origin + "/api/backtest \\\n"
      + "  -H 'Content-Type: application/json' \\\n"
      + "  -d '{\"strategy_id\":\"" + BOOT.sid + "\",\"name\":\"" + p.name
      + "\",\"startCapital\":" + p.startCapital + ",\"startDate\":\"" + p.startDate
      + "\",\"endDate\":\"" + p.endDate + "\",\"action\":\"backtest\"}'\n\n"
      + "# et en ligne de commande\npython -m shockdesk.cli backtest --strategy "
      + (state.strategy && state.strategy.file || "ma-strategie") .replace(/\.py$/, "")
      + " --name " + p.name + " --start-capital " + p.startCapital
      + " --start-date " + p.startDate + " --end-date " + p.endDate;
    $("#doc-strategy").textContent =
      '"""Ma stratégie — une phrase qui la résume."""\n\n'
      + "WEIGHT = 0.30\n\n"
      + "def initialize(context):\n"
      + "    context.asset = symbol('BZ=F')\n"
      + "    schedule_function(trade, date_rules.every_day())\n\n"
      + "def trade(context, data):\n"
      + "    f = get_forecast('BZ=F')          # prévision active, sans fuite\n"
      + "    if f is None:\n"
      + "        return\n"
      + "    spot = data.current(context.asset, 'close')\n"
      + "    if f.sign > 0:\n"
      + "        order_target_percent(context.asset, WEIGHT)\n"
      + "        # couverture en options : strangle acheté si l'amplitude le justifie\n"
      + "        c = option_contract('BZ=F', 'call', moneyness=1.05, days=30)\n"
      + "        p = option_contract('BZ=F', 'put',  moneyness=0.95, days=30)\n"
      + "        order(c, 10); order(p, 10)\n"
      + "    record(signal=f.sign, iv=get_iv('BZ=F', 1.0, 30))\n";
    $("#tbl-api").innerHTML = table(["appel", "effet"], [
      ["symbol('BZ=F') / symbols(...)", "résout un sous-jacent de l'univers courant"],
      ["schedule_function(f, date_rules.every_day())", "planifie f à chaque bar"],
      ["date_rules.every_day / every_n_days(n) / week_start / month_start / month_end", "règles de calendrier"],
      ["order(a, q) / order_value(a, v)", "ordre en quantité / en montant"],
      ["order_target(a, q) / order_target_value(a, v) / order_target_percent(a, w)", "ordre vers une cible"],
      ["data.current(a, 'close')", "prix du bar courant"],
      ["data.history(a, 'close', n)", "n derniers bars"],
      ["get_forecast(sym)", "prévision active à la date du bar (révision point-in-time)"],
      ["get_scenario(id)", "prévision par identifiant, quelle que soit la date"],
      ["option_contract(u, 'call'|'put', moneyness=, strike=, days=)", "construit un contrat"],
      ["get_iv(u, moneyness, days)", "IV de la surface pour ce contrat"],
      ["vol_regime(u, window=20)", "vol réalisée / vol calibrée"],
      ["record(k=v)", "série personnalisée, tracée dans l'onglet Backtest"],
      ["set_commission(per_share=, per_contract=, min_trade_cost=)", "frais"],
      ["set_slippage(bps=)", "slippage"],
      ["context.portfolio.portfolio_value / .cash / .positions / .pnl", "état du portefeuille"],
      ["log.info / log.warn / log.error", "journal d'exécution"]
    ]);
    $("#doc-data").innerHTML = "Trois sources, essayées dans cet ordre : <code>yfinance</code> "
      + "(données réelles, si le paquet est installé et que Yahoo répond), "
      + "<code>data/*.csv</code> (export manuel), puis le "
      + "<strong>générateur synthétique</strong> — modèle factoriel calibré sur "
      + Object.keys(state.universes).length + " univers, déterministe, avec la "
      + "reconstruction de l'exercice publié de juillet 2026. La source utilisée est "
      + "toujours affichée dans le bandeau en haut à droite : un chiffre lu ici n'est une "
      + "donnée réelle que si le badge est vert."
      + (BOOT.calibration ? "<br>Calibration active : " + esc(BOOT.calibration) : "");
  }

  /* ------------------------------------------------------------------ */
  /* boot                                                                */
  /* ------------------------------------------------------------------ */
  async function boot() {
    fillUniverses();
    initEditor();

    // liste des stratégies
    const r = await fetch("/api/strategies");
    const j = await r.json();
    if (j.ok) {
      $("#p-strategy").innerHTML = "";
      j.strategies.forEach(s => {
        $("#p-strategy").appendChild(el("option", { value: s.id }, s.name));
      });
      $("#p-strategy").value = BOOT.sid;
    }

    await loadCode();
    renderAssets();
    renderSideForecasts();
    renderDoc();
    syncUrl();

    // sélecteurs d'option
    fetch("/api/options/quote?underlying=SPY&structure=strangle").then(r => r.json()).then(q => {
      if (!q.ok) return;
      $("#op-structure").innerHTML = "";
      Object.keys(q.catalog).forEach(k =>
        $("#op-structure").appendChild(el("option", { value: k }, q.catalog[k].label)));
      $("#op-structure").value = "strangle";
    });

    $$(".tab").forEach(t => t.addEventListener("click", () => switchTab(t.dataset.tab)));
    $("#btn-run").addEventListener("click", () => runBacktest());
    $("#btn-save").addEventListener("click", saveCode);
    $("#btn-scen").addEventListener("click", loadScenarios);
    $("#btn-quote").addEventListener("click", quote);
    $("#btn-format-check").addEventListener("click", async () => {
      const r = await fetch("/api/backtest", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: $("#code").value, name: $("#p-name").value,
          startCapital: 10000, startDate: "2026-07-01", endDate: "2026-08-28" })
      });
      const j = await r.json();
      toast(j.ok ? "syntaxe et exécution OK" : "erreur : " + String(j.error).split("\n")[0], !j.ok);
    });
    $("#btn-new").addEventListener("click", async () => {
      const name = prompt("Nom de la nouvelle stratégie :", "ma-strategie");
      if (!name) return;
      const code = '"""' + name + ' — à compléter."""\n\ndef initialize(context):\n'
        + "    schedule_function(trade, date_rules.every_day())\n\n"
        + "def trade(context, data):\n    pass\n";
      const r = await fetch("/api/strategies", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, code: code })
      });
      const j = await r.json();
      if (!j.ok) return toast("échec : " + j.error, true);
      location.href = buildUrl(currentParams(), j.strategy.id);
    });
    $("#btn-copy-url").addEventListener("click", () => {
      const u = location.origin + $("#url-display").textContent;
      (navigator.clipboard ? navigator.clipboard.writeText(u) : Promise.reject())
        .then(() => toast("URL copiée")).catch(() => toast("copie impossible", true));
    });
    $("#p-strategy").addEventListener("change", e => {
      location.href = buildUrl(currentParams(), e.target.value);
    });
    ["#p-name", "#p-capital", "#p-start", "#p-end"].forEach(sel => {
      $(sel).addEventListener("change", () => {
        syncUrl();
        if (sel === "#p-name") { renderAssets(); renderDoc(); }
      });
    });
    window.addEventListener("resize", () => {
      if (state.result && !$("#tab-backtest").classList.contains("hidden"))
        renderBacktest(state.result);
      if (state.quote && !$("#tab-options").classList.contains("hidden")) renderQuote(state.quote);
    });
    window.addEventListener("beforeunload", e => {
      if (state.dirty) { e.preventDefault(); e.returnValue = ""; }
    });

    $("#boot").classList.add("gone");
    if (BOOT.params.action === "backtest") runBacktest();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
