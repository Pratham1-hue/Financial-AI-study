"""Focus / Pomodoro engine endpoints. The server owns the clock."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib import focus
from lib.nyc import RANKS, rank_for

router = APIRouter()


def _state_payload(s):
    cfg = focus.mode_cfg(s)
    return {
        "status": s["status"],
        "phase": s["phase"],
        "phase_label": focus.PHASE_LABEL[s["phase"]],
        "phase_color": focus.PHASE_COLOR[s["phase"]],
        "mode": s["mode"],
        "modes": {k: {"focus": v["focus"], "short": v["short"], "long": v["long"],
                      "every": v["every"], "desc": v["desc"]} for k, v in focus.MODES.items()},
        "subjects": focus.SUBJECTS,
        "subject": s["subject"],
        "label": s["label"],
        "cycles": s.get("cycles", 0),
        "every": cfg["every"],
        "auto_break": s.get("auto_break", True),
        "sound": s.get("sound", True),
        "ends_at": s.get("ends_at"),
        "remaining": round(focus.remaining(s)),
        "total": round(focus.total(s)),
        "custom": s.get("custom", {}),
    }


class StartBody(BaseModel):
    mode: str | None = None
    subject: str | None = None
    label: str | None = None
    custom: dict | None = None
    auto_break: bool | None = None
    sound: bool | None = None


class ConfigBody(BaseModel):
    mode: str | None = None
    subject: str | None = None
    label: str | None = None
    custom: dict | None = None
    auto_break: bool | None = None
    sound: bool | None = None


@router.post("/focus/config")
def config(body: ConfigBody):
    """Change session settings without starting the clock."""
    s = focus.load_state()
    if s["status"] != "idle":
        raise HTTPException(status_code=409, detail="Pause, stop or reset before changing settings.")
    if body.mode in focus.MODES:
        s["mode"] = body.mode
    if body.subject in focus.SUBJECTS:
        s["subject"] = body.subject
    if body.label is not None:
        s["label"] = body.label
    if body.custom:
        s["custom"] = {**s.get("custom", {}), **body.custom}
    if body.auto_break is not None:
        s["auto_break"] = body.auto_break
    if body.sound is not None:
        s["sound"] = body.sound
    focus.save_state(s)
    return {"state": _state_payload(s)}


@router.get("/focus")
def get_focus():
    s = focus.load_state()
    p = deps.progress()
    hours = focus.total_hours(p)
    rank, nxt, pct = rank_for(hours)
    return {
        "state": _state_payload(s),
        "stats": deps.focus_summary(p),
        "goal_min": deps.goal_minutes(),
        "rank": {"current": rank, "next": nxt, "pct": round(pct, 4), "ladder": RANKS},
        "log": p.get("focus_log", [])[-25:][::-1],
    }


@router.post("/focus/start")
def start(body: StartBody):
    s = focus.load_state()
    if s["status"] in ("running", "paused"):
        return {"state": _state_payload(s), "event": None, "already_active": True}
    if body.mode in focus.MODES:
        s["mode"] = body.mode
    if body.custom:
        s["custom"] = {**s.get("custom", {}), **body.custom}
    if body.subject:
        s["subject"] = body.subject
    if body.label is not None:
        s["label"] = body.label
    if body.auto_break is not None:
        s["auto_break"] = body.auto_break
    if body.sound is not None:
        s["sound"] = body.sound
    if s["phase"] != "focus":
        s["phase"] = "focus"
    focus.start(s)
    return {"state": _state_payload(s), "event": None, "already_active": False}


@router.post("/focus/pause")
def pause():
    s = focus.load_state()
    if s["status"] == "running":
        focus.pause(s)
    return {"state": _state_payload(s)}


@router.post("/focus/skip")
def skip():
    s = focus.load_state()
    focus.skip(s)
    return {"state": _state_payload(s)}


@router.post("/focus/reset")
def reset():
    s = focus.load_state()
    focus.reset(s)
    return {"state": _state_payload(s)}


@router.post("/focus/stop")
def stop():
    s = focus.load_state()
    minutes = focus.stop_and_log(s)
    return {"state": _state_payload(s), "minutes": minutes}


@router.post("/focus/tick")
def tick():
    """Advance the state machine when a phase has ended. Idempotent."""
    s = focus.load_state()
    event = focus.tick(s)
    return {"state": _state_payload(s), "event": event}
