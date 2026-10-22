"""One-file snapshot of user state, for deployments without a persistent disk.

Render's free tier wipes the container filesystem on every restart, deploy and
spin-down. Local JSON is not durable there, so the app offers an explicit
export/restore path instead of pretending otherwise.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from lib.focus import DEFAULT_STATE, FOCUS_FILE
from lib.paths import DATA_DIR
from lib.storage import DEFAULT_PROFILE, DEFAULT_PROGRESS, PROFILE_FILE, PROGRESS_FILE

VERSION = 1


def _read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def snapshot():
    """Everything worth keeping: progress, profile, focus session."""
    return {
        "app": "project-devi",
        "version": VERSION,
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "progress": _read(PROGRESS_FILE, DEFAULT_PROGRESS),
        "profile": _read(PROFILE_FILE, DEFAULT_PROFILE),
        "focus": _read(FOCUS_FILE, DEFAULT_STATE),
    }


def dumps():
    return json.dumps(snapshot(), indent=2, ensure_ascii=False)


def _normalise(payload):
    if not isinstance(payload, dict):
        raise ValueError("Backup is not a JSON object.")

    if "progress" not in payload:
        # Older export: a bare progress.json.
        if "xp" in payload or "activity" in payload or "completed_tasks" in payload:
            return {"progress": payload}
        raise ValueError("This file has no 'progress' section.")

    if not isinstance(payload["progress"], dict):
        raise ValueError("'progress' must be a JSON object.")
    return payload


def inspect(payload):
    """Summary for the confirmation step, without writing anything."""
    data = _normalise(payload)
    p = data["progress"]
    return {
        "exported_at": data.get("exported_at"),
        "xp": p.get("xp", 0),
        "tasks": len(p.get("completed_tasks", []) or []),
        "modules_done": len(p.get("quiz_scores", {}) or {}),
        "watched": len(p.get("watched", {}) or {}),
        "has_profile": isinstance(data.get("profile"), dict),
        "has_focus": isinstance(data.get("focus"), dict),
    }


def restore(payload):
    """Atomically replace local state with the backup. Returns what was written."""
    data = _normalise(payload)
    targets = [
        ("progress", PROGRESS_FILE, DEFAULT_PROGRESS),
        ("profile", PROFILE_FILE, DEFAULT_PROFILE),
        ("focus", FOCUS_FILE, DEFAULT_STATE),
    ]
    written = []
    os.makedirs(DATA_DIR, exist_ok=True)
    for key, path, defaults in targets:
        value = data.get(key)
        if not isinstance(value, dict):
            continue
        merged = dict(defaults)
        merged.update(value)
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
        written.append(key)

    if "progress" not in written:
        raise ValueError("Nothing to restore: the backup has no progress data.")
    return written
