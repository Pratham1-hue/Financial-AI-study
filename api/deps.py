"""Shared helpers for the API: progress/profile access, formatting, in-memory desk rounds."""
from __future__ import annotations

import threading

from lib import focus
from lib.market_sim import new_round
from lib.storage import load_profile, load_progress, save_progress

XP_TITLES = {1: "Novice", 2: "Apprentice", 3: "Practitioner", 4: "Specialist",
             5: "Expert", 6: "Master", 7: "Grandmaster"}


def xp_level(xp: int):
    level = int(xp) // 500 + 1
    return level, XP_TITLES.get(min(level, 7), "Legend")


def progress():
    return load_progress()


def profile():
    return load_profile()


def commit(p):
    save_progress(p)
    return p


def goal_minutes(prof=None):
    return int((prof or load_profile()).get("daily_hours", 6)) * 60


# --------------------------------------------------------------- desk rounds
# A round is a live 3-minute tape; the server owns the clock. One instance on
# Render's free tier means an in-process store is enough. A restart drops the
# round - acceptable for a practice drill.
_ROUNDS: dict[str, dict] = {}
_LOCK = threading.Lock()


def create_round(seed=None):
    state = new_round(seed)
    rid = f"{state['seed']}-{int(state['start'])}"
    with _LOCK:
        _ROUNDS[rid] = state
        # keep the store small
        if len(_ROUNDS) > 12:
            for k in list(_ROUNDS)[:-8]:
                _ROUNDS.pop(k, None)
    return rid, state


def get_round(rid):
    return _ROUNDS.get(rid)


def drop_round(rid):
    with _LOCK:
        _ROUNDS.pop(rid, None)


def focus_summary(p):
    today = focus.today_minutes(p)
    return {
        "today_min": today,
        "sessions_today": focus.sessions_today(p),
        "week_min": focus.week_minutes(p),
        "total_hours": round(focus.total_hours(p), 2),
        "streak": focus.focus_streak(p),
    }
