"""Evening Feynman debrief: the fifth step of the daily loop.

The old Streamlit page stored one entry per day in ``progress["debriefs"]``.
This router exposes the same data so the React app can complete the loop.
"""
from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib.storage import log_activity

router = APIRouter()

MIN_CHARS = 200
XP_REWARD = 50


class DebriefBody(BaseModel):
    concept: str = ""
    explain: str = ""
    gaps: str = ""
    win: str = ""
    first: str = ""
    energy: int = 3


@router.get("/debrief")
def get_debrief():
    p = deps.progress()
    today = date.today().isoformat()
    entries = p.get("debriefs", {})
    history = [{"date": d, **e} for d, e in sorted(entries.items(), reverse=True)[:30]]
    return {
        "today": today,
        "entry": entries.get(today),
        "history": history,
        "min_chars": MIN_CHARS,
        "xp_reward": XP_REWARD,
    }


@router.post("/debrief")
def save_debrief(body: DebriefBody):
    explain = (body.explain or "").strip()
    concept = (body.concept or "").strip()
    first = (body.first or "").strip()
    if len(explain) < MIN_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"That is {len(explain)} characters. A tweet is not an explanation - write {MIN_CHARS}+.",
        )
    if not concept or not first:
        raise HTTPException(
            status_code=400,
            detail="Name the concept and commit to tomorrow's first focus block.",
        )

    p = deps.progress()
    today = date.today().isoformat()
    entries = p.setdefault("debriefs", {})
    is_new = today not in entries
    entries[today] = {
        "concept": concept,
        "explain": explain,
        "gaps": (body.gaps or "").strip(),
        "win": (body.win or "").strip(),
        "first": first,
        "energy": max(1, min(5, int(body.energy))),
        "at": datetime.now().isoformat(timespec="minutes"),
    }
    if is_new:
        p["xp"] = p.get("xp", 0) + XP_REWARD
        log_activity(p, "debrief")
    deps.commit(p)
    return {
        "ok": True,
        "is_new": is_new,
        "xp_gain": XP_REWARD if is_new else 0,
        "xp": p.get("xp", 0),
        "entry": entries[today],
    }
