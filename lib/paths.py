"""Filesystem locations for the app.

Locally, everything lives in ``<repo>/data``. In a container (Render, Fly, Railway)
set ``LAKSH_DATA_DIR`` to a mounted volume so progress, focus sessions and caches
survive restarts. The legacy ``DEVI_DATA_DIR`` name is still honoured.

Only the read-only assets (YouTube catalog/curriculum, link verification) are
seeded into a fresh volume. Writable state (progress, focus, profile) is created
with defaults instead of leaking whatever was on the machine that built the image.
"""
from __future__ import annotations

import os
import shutil

from lib.env import get

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_DATA = os.path.join(ROOT, "data")
DATA_DIR = os.path.abspath(get("DATA_DIR") or BUNDLED_DATA)

# Generated offline by scripts/sync_youtube.py and scripts/check_links.py.
SEED_FILES = ("yt_catalog.json", "yt_curriculum.json", "link_check.json")


def _seed():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.normcase(DATA_DIR) == os.path.normcase(BUNDLED_DATA):
        return
    for name in SEED_FILES:
        src = os.path.join(BUNDLED_DATA, name)
        dst = os.path.join(DATA_DIR, name)
        if os.path.exists(dst) or not os.path.isfile(src):
            continue
        try:
            shutil.copy2(src, dst)
        except OSError:
            # A read-only or misconfigured volume should not stop the app from
            # booting; the pages that need the file handle a missing catalog.
            pass


_seed()
