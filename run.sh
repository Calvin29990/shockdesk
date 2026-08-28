#!/usr/bin/env bash
# Lance ShockDesk : venv, dépendances, serveur sur http://0.0.0.0:8050
set -euo pipefail
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
PORT=${PORT:-8050}
HOST=${HOST:-0.0.0.0}

if [ ! -d .venv ]; then
  echo "→ création du venv (.venv)"
  "$PY" -m venv .venv
fi

echo "→ dépendances"
./.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt

if ! ./.venv/bin/python -c "import yfinance" 2>/dev/null; then
  echo "ℹ yfinance absent : les prix viendront du cache CSV ou du générateur"
  echo "  synthétique (badge orange dans l'interface). Installez-le pour les"
  echo "  données réelles :  ./.venv/bin/pip install yfinance"
fi

echo "→ tests rapides"
./.venv/bin/pytest tests/ -q || echo "⚠ des tests échouent : le serveur démarre quand même"

echo "→ ShockDesk sur http://${HOST}:${PORT}"
exec ./.venv/bin/python -m shockdesk.cli serve --host "$HOST" --port "$PORT"
