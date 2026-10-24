"""Verified-link data produced by scripts/check_links.py."""
import json
import os

from lib.cache import cache_data
from lib.paths import DATA_DIR

CHECKS = os.path.join(DATA_DIR, "link_check.json")


@cache_data(show_spinner=False)
def _load(mtime):
    try:
        with open(CHECKS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"checked_at": None, "links": {}}


def all_checks():
    try:
        m = os.path.getmtime(CHECKS)
    except OSError:
        m = 0
    return _load(m)


def for_key(key):
    return all_checks().get("links", {}).get(key)


def checked_at():
    return all_checks().get("checked_at")


def counts():
    links = all_checks().get("links", {})
    ok = sum(1 for v in links.values() if v.get("ok") is True)
    unknown = sum(1 for v in links.values() if v.get("ok") is None)
    dead = sum(1 for v in links.values() if v.get("ok") is False)
    return ok, unknown, dead, len(links)
