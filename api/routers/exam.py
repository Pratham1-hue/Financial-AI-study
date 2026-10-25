"""Formal mastery exams and backup/export endpoints.

Exams are proctored-feeling multi-module assessments (E1..E5) drawn from
quiz_bank.EXAM_QUESTION_IDS. Answers are stripped client-side; grading happens
server-side. Passing an exam records exam_scores and XP via lib.storage.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib.quiz_bank import EXAM_QUESTION_IDS, Q_BY_ID, QUESTIONS
from lib.storage import record_exam

router = APIRouter()

EXAMS = {
    "E1": {"title": "Foundations I", "modules": ["F1", "F2", "A1", "A2", "F7"], "time_limit": 900},
    "E2": {"title": "Foundations II", "modules": ["F3", "F4", "A3", "A4", "ML"], "time_limit": 1200},
    "E3": {"title": "Quant & Derivatives", "modules": ["F5", "F6", "A8"], "time_limit": 1200},
    "E4": {"title": "AI & MLOps", "modules": ["A5", "A6", "A7"], "time_limit": 1200},
    "E5": {"title": "Capstone Review", "modules": ["C1", "C2", "F8"], "time_limit": 900},
}

PASS_MARK = 80


def _public(q):
    return {"id": q["id"], "track": q["track"], "module": q["module"], "diff": q["diff"],
            "q": q["q"], "opts": q["opts"]}


class ExamSubmit(BaseModel):
    answers: dict[str, int] = {}


@router.get("/exams")
def list_exams():
    p = deps.progress()
    scores = p.get("exam_scores", {})
    out = []
    for eid, cfg in EXAMS.items():
        qids = EXAM_QUESTION_IDS.get(eid, [])
        s = scores.get(eid)
        out.append({
            "id": eid,
            "title": cfg["title"],
            "modules": cfg["modules"],
            "questions": len(qids),
            "time_limit": cfg["time_limit"],
            "pass_mark": PASS_MARK,
            "status": "mastered" if (s and s["score"] >= PASS_MARK) else ("attempted" if s else "open"),
            "score": s["score"] if s else None,
            "at": s["at"] if s else None,
        })
    return {"exams": out}


@router.get("/exams/{eid}")
def exam_questions(eid: str):
    if eid not in EXAMS:
        raise HTTPException(status_code=404, detail="Unknown exam.")
    qids = EXAM_QUESTION_IDS.get(eid, [])
    questions = [_public(Q_BY_ID[qid]) for qid in qids if qid in Q_BY_ID]
    if not questions:
        raise HTTPException(status_code=404, detail="Exam has no questions.")
    return {"id": eid, "title": EXAMS[eid]["title"], "time_limit": EXAMS[eid]["time_limit"],
            "questions": questions}


@router.post("/exams/{eid}/submit")
def submit_exam(eid: str, body: ExamSubmit):
    if eid not in EXAMS:
        raise HTTPException(status_code=404, detail="Unknown exam.")
    qids = EXAM_QUESTION_IDS.get(eid, [])
    ids = [qid for qid in body.answers if qid in Q_BY_ID]
    if not ids:
        raise HTTPException(status_code=400, detail="No answers submitted.")

    score = 0
    review = []
    wrong_modules = []
    for qid in ids:
        q = Q_BY_ID[qid]
        chosen = body.answers[qid]
        ok = chosen == q["ans"]
        score += int(ok)
        if not ok:
            wrong_modules.append(q["module"])
        review.append({
            "id": qid, "q": q["q"], "module": q["module"], "diff": q["diff"],
            "you": q["opts"][chosen] if isinstance(chosen, int) and 0 <= chosen < len(q["opts"]) else None,
            "correct": q["opts"][q["ans"]], "ok": ok, "exp": q["exp"],
        })

    total = len(ids)
    pct = record_exam(deps.progress(), eid, score, total)

    return {
        "score": score, "total": total, "pct": pct, "passed": pct >= PASS_MARK,
        "review": review, "weak_topics": wrong_modules, "xp": deps.progress().get("xp", 0),
    }


@router.get("/exams/{eid}/result")
def exam_result(eid: str):
    if eid not in EXAMS:
        raise HTTPException(status_code=404, detail="Unknown exam.")
    p = deps.progress()
    s = p.get("exam_scores", {}).get(eid)
    if not s:
        raise HTTPException(status_code=404, detail="No attempt yet.")
    return {"id": eid, "score": s["score"], "at": s["at"], "passed": s["score"] >= PASS_MARK}
