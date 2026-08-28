"""
Registre des stratégies.

Reprend la forme de l'URL Blueshift : chaque stratégie a un identifiant UUID
stable, le code vit dans ``strategies/<slug>.py``, l'index dans
``strategies/_index.json``. Le code est du vrai Python : on peut l'éditer dans
l'interface ou dans son éditeur, les deux voient le même fichier.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from . import config

INDEX_PATH = os.path.join(config.STRATEGY_DIR, "_index.json")


def _load_index() -> Dict[str, dict]:
    if not os.path.exists(INDEX_PATH):
        return {}
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _save_index(index: Dict[str, dict]):
    os.makedirs(config.STRATEGY_DIR, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "strategie").lower()).strip("-")
    return s or "strategie"


def _path(slug: str) -> str:
    return os.path.join(config.STRATEGY_DIR, slug + ".py")


def _reindex():
    """Réconcilie l'index avec les fichiers présents sur le disque."""
    index = _load_index()
    known = {v["file"] for v in index.values()}
    for fname in sorted(os.listdir(config.STRATEGY_DIR)) if os.path.isdir(config.STRATEGY_DIR) else []:
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        if fname in known:
            continue
        slug = fname[:-3]
        sid = str(uuid.uuid4())
        index[sid] = {
            "id": sid,
            "file": fname,
            "name": slug.replace("-", " ").title(),
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "defaults": {},
        }
    for sid, meta in list(index.items()):
        if not os.path.exists(_path(meta["file"][:-3])):
            index.pop(sid)
    _save_index(index)
    return index


def list_strategies() -> List[dict]:
    index = _reindex()
    out = []
    for sid, meta in index.items():
        out.append({
            "id": sid,
            "name": meta.get("name", meta["file"]),
            "file": meta["file"],
            "updated": meta.get("updated"),
            "defaults": meta.get("defaults", {}),
            "description": read_description(meta["file"]),
        })
    return sorted(out, key=lambda s: (s["name"] or "").lower())


def read_description(fname: str) -> str:
    """Première ligne de docstring du fichier, si elle existe."""
    try:
        with open(_path(fname[:-3]), "r", encoding="utf-8") as fh:
            src = fh.read()
    except OSError:
        return ""
    m = re.search(r'"""(.*?)"""', src, re.S)
    if not m:
        return ""
    first = m.group(1).strip().splitlines()[0] if m.group(1).strip() else ""
    return first.strip()


def get(sid: str) -> Optional[dict]:
    index = _reindex()
    return index.get(sid)


def read_code(sid: str) -> str:
    meta = get(sid)
    if not meta:
        raise KeyError(f"Stratégie inconnue : {sid}")
    with open(_path(meta["file"][:-3]), "r", encoding="utf-8") as fh:
        return fh.read()


def write_code(sid: str, code: str) -> dict:
    index = _reindex()
    meta = index.get(sid)
    if not meta:
        raise KeyError(f"Stratégie inconnue : {sid}")
    with open(_path(meta["file"][:-3]), "w", encoding="utf-8") as fh:
        fh.write(code)
    meta["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _save_index(index)
    return meta


def create(name: str, code: str, defaults: Optional[dict] = None) -> dict:
    index = _reindex()
    slug = _slug(name)
    n = 2
    while os.path.exists(_path(slug)):
        slug = f"{_slug(name)}-{n}"
        n += 1
    sid = str(uuid.uuid4())
    with open(_path(slug), "w", encoding="utf-8") as fh:
        fh.write(code)
    index[sid] = {
        "id": sid, "file": slug + ".py", "name": name,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "defaults": defaults or {},
    }
    _save_index(index)
    return index[sid]


def rename(sid: str, name: str) -> dict:
    index = _reindex()
    meta = index.get(sid)
    if not meta:
        raise KeyError(sid)
    meta["name"] = name
    meta["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _save_index(index)
    return meta


def set_defaults(sid: str, defaults: dict) -> dict:
    index = _reindex()
    meta = index.get(sid)
    if not meta:
        raise KeyError(sid)
    meta["defaults"] = defaults
    _save_index(index)
    return meta
