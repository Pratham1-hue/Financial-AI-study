"""Read-side access to the synced YouTube data (catalog + per-module curriculum).

Nothing here touches the network. The sync script writes the JSON; the app only reads it,
so browsing costs zero quota and never blocks on an API call.
"""
import json
import os

import streamlit as st

from lib.paths import DATA_DIR

CATALOG = os.path.join(DATA_DIR, "yt_catalog.json")
CURRICULUM = os.path.join(DATA_DIR, "yt_curriculum.json")

_EMPTY_CATALOG = {"synced_at": None, "channels": {}, "videos": {}, "broken_handles": []}
_EMPTY_CURRICULUM = {"generated_at": None, "modules": {}}


def _read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0


def fmt_views(n):
    n = int(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K views"
    return f"{n} views"


@st.cache_data(show_spinner=False)
def _catalog_cached(mtime):
    d = _read(CATALOG, _EMPTY_CATALOG)
    d.setdefault("videos", {})
    d.setdefault("channels", {})
    return d


@st.cache_data(show_spinner=False)
def _curriculum_cached(mtime):
    d = _read(CURRICULUM, _EMPTY_CURRICULUM)
    d.setdefault("modules", {})
    return d


def catalog():
    return _catalog_cached(_mtime(CATALOG))


def curriculum():
    return _curriculum_cached(_mtime(CURRICULUM))


def ready():
    return bool(curriculum().get("modules"))


def synced_at():
    return curriculum().get("generated_at") or catalog().get("synced_at")


def module_videos(mid):
    """Curated queue for a module: 10 videos, lessons first."""
    return curriculum().get("modules", {}).get(mid, {}).get("picked", [])


def video(vid):
    return catalog().get("videos", {}).get(vid)


def channels():
    return catalog().get("channels", {})


def all_videos():
    return catalog().get("videos", {}).values()


def search(q, track=None, limit=30):
    """Local search over the whole synced catalog. Free - no API call."""
    q = (q or "").lower().strip()
    if not q:
        return []
    terms = q.split()
    out = []
    for v in all_videos():
        if track and v.get("track") not in (track, "mixed"):
            continue
        hay = (v.get("title", "") + " " + v.get("channel", "") + " " +
               v.get("desc", "")[:400]).lower()
        hits = sum(1 for t in terms if t in hay)
        if hits == len(terms):
            out.append((hits, v.get("views", 0), v))
    out.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [v for _, _, v in out[:limit]]


def channel_catalog(track=None):
    """Trusted channels for a track, richest first."""
    ch = list(channels().values())
    if track:
        ch = [c for c in ch if c.get("track") == track]
    return sorted(ch, key=lambda c: c.get("subs", 0), reverse=True)
