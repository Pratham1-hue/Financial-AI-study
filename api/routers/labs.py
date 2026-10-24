"""Hands-on labs: SQL, credit risk, valuation. All auto-graded."""
from __future__ import annotations

import random
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib import labs as engine
from lib.storage import log_activity

router = APIRouter()


def _record(p, lab, ok, detail=""):
    p.setdefault("lab_runs", []).append({
        "date": date.today().isoformat(), "lab": lab, "ok": bool(ok), "detail": detail,
    })
    if ok:
        p["xp"] = p.get("xp", 0) + 15
        log_activity(p, "lab")
    deps.commit(p)


def _already_solved(p, lab, detail):
    return any(r.get("lab") == lab and r.get("detail") == detail and r.get("ok")
               for r in p.get("lab_runs", []))


@router.get("/labs")
def meta():
    return {
        "schema": engine.SCHEMA,
        "sql": [{"id": t["id"], "level": t["level"], "prompt": t["prompt"],
                 "cols": t["cols"], "hint": t["hint"]} for t in engine.SQL_TASKS],
        "credit": {"features": engine.CREDIT_FEATURES, "models": engine.CREDIT_MODELS,
                   "n_borrowers": 4000, "usable_auc": 0.72},
        "valuation": {"time_limit_secs": 300},
    }


class SqlBody(BaseModel):
    sql: str
    task_id: str | None = None
    attempt: int = 1


@router.post("/labs/sql/run")
def sql_run(body: SqlBody):
    preview, error = engine.run_sql(body.sql)
    if error:
        return {"ok": False, "error": error}
    return {"ok": True, "preview": preview}


@router.post("/labs/sql/check")
def sql_check(body: SqlBody):
    if not body.task_id:
        raise HTTPException(status_code=400, detail="task_id is required to check.")
    result = engine.check_sql(body.task_id, body.sql, body.attempt)
    p = deps.progress()
    if result.get("ok"):
        if not _already_solved(p, "SQL", body.task_id):
            _record(p, "SQL", True, body.task_id)
            result["recorded"] = True
        else:
            result["recorded"] = False
    elif result.get("error"):
        _record(p, "SQL", False, body.task_id)
    return result


class CreditBody(BaseModel):
    features: list[str]
    model: str = "Logistic regression"
    threshold: float = 0.30


@router.post("/labs/credit")
def credit(body: CreditBody):
    return engine.run_credit(body.features, body.model, body.threshold)


@router.post("/labs/credit/bank")
def credit_bank(body: CreditBody):
    result = engine.run_credit(body.features, body.model, body.threshold)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    p = deps.progress()
    _record(p, "Credit ML", result["usable"], f"{body.model} auc={result['auc']:.3f}")
    return result


class ValuationBody(BaseModel):
    seed: int | None = None
    ev: float | None = None
    equity: float | None = None
    per_share: float | None = None


@router.post("/labs/valuation")
def valuation(body: ValuationBody):
    seed = body.seed or random.randint(1, 10**6)
    if body.ev is None:
        return {"case": engine.public_case(seed)}
    result = engine.grade_valuation(seed, body.ev, body.equity, body.per_share)
    p = deps.progress()
    _record(p, "Valuation", result["correct"], f"seed={seed}" if result["correct"] else f"{result['passed']}/3")
    result["case"] = engine.public_case(seed)
    return result


@router.get("/labs/log")
def lab_log():
    p = deps.progress()
    runs = p.get("lab_runs", [])
    today = date.today().isoformat()
    todays = [r for r in runs if r.get("date") == today]
    return {
        "today_attempts": len(todays),
        "today_correct": sum(1 for r in todays if r.get("ok")),
        "all_time_correct": sum(1 for r in runs if r.get("ok")),
        "recent": runs[-12:][::-1],
        "sql_solved": sorted({r["detail"] for r in runs
                              if r.get("lab") == "SQL" and r.get("ok")}),
    }
