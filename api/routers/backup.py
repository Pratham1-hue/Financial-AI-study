"""Backup / restore for the ephemeral Render free tier.

GET  /api/backup/export   -> JSON snapshot of progress + profile + focus
POST /api/backup/import   -> { backup: <JSON object or string> } restores state
"""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lib import backup
from api import deps

router = APIRouter()


class ImportBody(BaseModel):
    backup: str | dict


@router.get("/backup/export")
def export_backup():
    return {"backup": backup.snapshot(), "as_json": backup.dumps()}


@router.post("/backup/import")
def import_backup(body: ImportBody):
    payload = body.backup
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid backup JSON: {e}")
    try:
        written = backup.restore(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "written": written, "inspect": backup.inspect(payload)}


@router.get("/backup/inspect")
def inspect_backup():
    """Preview what a restore would contain, without writing."""
    p = deps.progress()
    prof = deps.profile()
    return {
        "xp": p.get("xp", 0),
        "tasks": len(p.get("completed_tasks", [])),
        "modules_done": len(p.get("quiz_scores", {})),
        "watched": len(p.get("watched", {})),
        "has_profile": isinstance(prof, dict) and bool(prof),
        "desk_rounds": len(p.get("desk_rounds", [])),
        "lab_runs": len(p.get("lab_runs", [])),
    }
