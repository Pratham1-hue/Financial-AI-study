"""Environment helpers.

Configuration reads the new ``LAKSH_*`` names first and falls back to the
pre-rename ``DEVI_*`` names, so an existing Render service keeps working while
the rebrand rolls out.
"""
from __future__ import annotations

import os

PREFIXES = ("LAKSH", "DEVI")


def get(name: str, default: str = "") -> str:
    """Return ``LAKSH_<name>`` if set, else ``DEVI_<name>``, else ``default``."""
    for prefix in PREFIXES:
        value = os.environ.get(f"{prefix}_{name}")
        if value is not None:
            return value
    return default
