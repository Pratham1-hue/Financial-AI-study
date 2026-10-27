"""Learning endpoints: modules, lessons, resources, watch tracking."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib import gates, watch, yt_data
from lib.content import MODULE_BY_ID, MODULES, modules_for_track
from lib.quiz_bank import QUESTIONS
from lib.resources import ALIASES, RESOURCES
from lib.storage import log_activity

router = APIRouter()


def _resource(key):
    real = ALIASES.get(key, key)
    r = RESOURCES.get(real)
    if not r:
        return None
    return {"id": real, **r}


def _resource_list(keys):
    out = []
    for k in keys or []:
        r = _resource(k)
        if r:
            out.append(r)
    return out


@router.get("/modules")
def modules(track: str | None = None):
    p = deps.progress()
    mods = modules_for_track(track) if track else MODULES
    return [
        {
            "id": m["id"], "title": m["title"], "track": m["track"], "level": m["level"],
            "weeks": m["weeks"], "summary": m["summary"],
            "specialties": m.get("specialties", []),
            "status": gates.status(p, m["id"]),
            "lessons": len(m["lessons"]),
            "videos": len(yt_data.module_videos(m["id"])),
            "quiz_questions": sum(1 for q in QUESTIONS if q["module"] == m["id"]),
        }
        for m in mods
    ]


@router.get("/modules/{mid}")
def module(mid: str):
    m = MODULE_BY_ID.get(mid)
    if not m:
        raise HTTPException(status_code=404, detail="Unknown module.")
    p = deps.progress()
    videos = yt_data.module_videos(mid)
    watched_ids = p.get("watched", {})
    done, total, left = watch.queue_progress(p, videos)
    return {
        "id": m["id"], "title": m["title"], "track": m["track"], "level": m["level"],
        "weeks": m["weeks"], "summary": m["summary"], "lessons": m["lessons"],
        "specialties": m.get("specialties", []),
        "outcomes": m["outcomes"],
        "status": gates.status(p, mid),
        "missing_prereqs": gates.missing_prereqs(p, mid),
        "resources": _resource_list(m["resources"]),
        "videos": [
            {**v, "watched": v["id"] in watched_ids} for v in videos
        ],
        "watch": {"done": done, "total": total, "minutes_left": left // 60},
        "quiz_questions": sum(1 for q in QUESTIONS if q["module"] == mid),
    }


class WatchBody(BaseModel):
    video_id: str


@router.post("/modules/{mid}/watch")
def mark_watched(mid: str, body: WatchBody):
    p = deps.progress()
    v = yt_data.video(body.video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Unknown video.")
    first = watch.mark(p, v["id"], mid, v.get("title", ""), v.get("channel", ""), v.get("secs", 0))
    if first:
        log_activity(p, "watch")
    deps.commit(p)
    return {"first_time": first, "xp": p.get("xp", 0)}


@router.get("/resources")
def resources(track: str | None = None, cat: str | None = None, q: str | None = None, limit: int = 500):
    limit = max(1, min(limit, 1000))
    out = []
    needle = (q or "").lower().strip()
    for key, r in RESOURCES.items():
        if track and r.get("track") != track:
            continue
        if cat and r.get("cat") != cat:
            continue
        if needle:
            hay = f"{r.get('title','')} {r.get('desc','')} {r.get('type','')}".lower()
            if needle not in hay:
                continue
        out.append({"id": key, **r})
    out.sort(key=lambda r: (r.get("track", ""), r.get("cat", ""), r.get("title", "")))
    return {"total": len(out), "items": out[:limit]}


@router.get("/videos/search")
def video_search(q: str, track: str | None = None, limit: int = 24):
    if not q.strip():
        return {"items": []}
    return {"items": yt_data.search(q, track=track, limit=limit)}


@router.get("/videos")
def video_info(vid: str):
    v = yt_data.video(vid)
    if not v:
        raise HTTPException(status_code=404, detail="Unknown video.")
    return v


@router.get("/channels")
def channels(track: str | None = None):
    return {"synced_at": yt_data.synced_at(), "items": yt_data.channel_catalog(track)}
