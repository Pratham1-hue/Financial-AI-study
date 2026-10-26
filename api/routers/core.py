"""Core endpoints: health, session, dashboard bootstrap, profile."""
from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

from api import deps
from api.security import (COOKIE, TTL_SECONDS, auth_required, check_password,
                          cookie_secure, issue_token, verify_token)
from lib import accountability as acc
from lib import focus, gates
from lib.content import MODULES
from lib.nyc import NYC_COMP, rank_for
from lib.quotes import quote_of_the_day
from lib.storage import save_profile, streak_days
from lib.study_plan import PHASES, WEEKS

router = APIRouter()


class LoginBody(BaseModel):
    password: str = ""


class ProfileBody(BaseModel):
    name: str | None = None
    target_role: str | None = None
    target_date: str | None = None
    daily_hours: int | None = None
    level: str | None = None
    why: str | None = None
    dream_companies: str | None = None
    day_start: int | None = None


@router.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat(timespec="seconds")}


@router.get("/session")
def session(laksh_session: str | None = Cookie(default=None)):
    return {"auth_required": auth_required(), "authenticated": verify_token(laksh_session)}


@router.post("/login")
def login(body: LoginBody, response: Response):
    if not check_password(body.password):
        raise HTTPException(status_code=401, detail="Wrong password.")
    response.set_cookie(COOKIE, issue_token(), max_age=TTL_SECONDS, httponly=True,
                        samesite="lax", secure=cookie_secure(), path="/")
    return {"ok": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


def _loop_state(p):
    today = date.today().isoformat()
    a = p.get("activity", {}).get(today, {})
    learn_secs = sum(v.get("secs", 0) for v in p.get("watched", {}).values() if v.get("date") == today)
    blocks = [
        {"name": "Learn", "done": learn_secs >= 600 or bool(a.get("watch")), "to": "/learn"},
        {"name": "Drill", "done": bool(a.get("drill_clear")) or a.get("review", 0) >= 5, "to": "/quizzes?tab=drill"},
        {"name": "Build", "done": any(a.get(k) for k in ("code", "desk", "lab", "challenge", "speed", "task")),
         "to": "/labs"},
        {"name": "Prove", "done": any(a.get(k) for k in ("quiz", "quiz80", "gate", "gate_pass", "exam")),
         "to": "/quizzes"},
        {"name": "Debrief", "done": today in p.get("debriefs", {}), "to": "/debrief"},
    ]
    return blocks


def _phase_progress(p):
    out = []
    for ph in PHASES:
        wks = [w for w in WEEKS if w["phase"] == ph]
        done = sum(1 for w in wks if f"w{w['w']}" in p.get("completed_tasks", []))
        out.append({"phase": ph, "done": done, "total": len(wks)})
    return out


@router.get("/bootstrap")
def bootstrap():
    p = deps.progress()
    prof = deps.profile()
    gm = deps.goal_minutes(prof)
    today = date.today()

    n, week, assignment = acc.todays_assignment(p)
    parts, fm = acc.day_parts(p, today, gm)
    score = round(sum(parts.values()))
    rows = acc.stock_series(p, gm)
    rating, avg = acc.analyst_rating(rows)
    mi, mi_parts = acc.mastery_index(p)
    hours = focus.total_hours(p)
    rank, nxt, pct = rank_for(hours)
    level, level_title = deps.xp_level(p.get("xp", 0))

    loop = _loop_state(p)
    current_week = next((w for w in WEEKS if f"w{w['w']}" not in p.get("completed_tasks", [])), None)
    last = rows[-1] if rows else {"close": 100.0, "score": 0}
    prev = rows[-2]["close"] if len(rows) > 1 else 100.0

    module_states = [
        {"id": m["id"], "title": m["title"], "track": m["track"],
         "status": gates.status(p, m["id"]), "weeks": m["weeks"]}
        for m in MODULES
    ]

    return {
        "profile": prof,
        "plan": {
            "day": n,
            "days_total": acc.PLAN_DAYS,
            "week": week,
            "assignment": assignment,
            "phase_progress": _phase_progress(p),
            "current_week": current_week,
        },
        "metrics": {
            "day_score": score,
            "day_parts": [{"name": k, "value": round(v, 1), "max": acc.PART_MAX[k]} for k, v in parts.items()],
            "focus_min_today": fm,
            "goal_min": gm,
            "all_time_hours": round(hours, 1),
            "mastery_index": mi,
            "mastery_parts": mi_parts,
            "streak": streak_days(p),
            "xp": p.get("xp", 0),
            "level": level,
            "level_title": level_title,
            "locked_today_min": focus.today_minutes(p),
        },
        "stock": {
            "symbol": acc.ticker_symbol(prof),
            "price": last["close"],
            "change_pct": round((last["close"] / prev - 1) * 100, 2) if prev else 0.0,
            "rating": rating,
            "rating_avg": round(avg, 1),
            "series": rows[-60:],
        },
        "loop": loop,
        "focus": deps.focus_summary(p),
        "rank": {"current": rank, "next": nxt, "pct": round(pct, 4)},
        "quote": quote_of_the_day(),
        "modules": module_states,
        "breaches": acc.unresolved_breaches(p, gm),
        "comp": [{"role": role, "comp": comp} for role, comp in NYC_COMP],
        "bootcamp": [
            {"name": b["name"], "mins": b["mins"], "desc": b["desc"],
             "start": b["start"].strftime("%H:%M"), "end": b["end"].strftime("%H:%M")}
            for b in acc.bootcamp_day(gm, int(prof.get("day_start", 9)))
        ],
    }


@router.get("/profile")
def get_profile():
    return deps.profile()


@router.put("/profile")
def update_profile(body: ProfileBody):
    prof = deps.profile()
    for k, v in body.model_dump(exclude_none=True).items():
        prof[k] = v
    save_profile(prof)
    return prof


@router.get("/modules/{mid}/gate")
def gate_state(mid: str):
    p = deps.progress()
    g = gates.gate(p, mid)
    cd = gates.cooldown_left(p, mid)
    return {
        "module": mid,
        "title": gates.title(mid),
        "status": gates.status(p, mid),
        "missing_prereqs": gates.missing_prereqs(p, mid),
        "cooldown_hours": round(cd.total_seconds() / 3600, 1) if cd else None,
        "attempts": (g or {}).get("attempts", 0),
        "not_yet": (g or {}).get("not_yet", 0),
        "passed_on": (g or {}).get("passed_on"),
    }
