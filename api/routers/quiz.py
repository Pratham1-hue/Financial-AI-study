"""Quiz, spaced-repetition drill and mastery-gate endpoints."""
from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib import gates, srs
from lib.quiz_bank import Q_BY_ID, QUESTIONS
from lib.storage import log_activity, record_quiz

router = APIRouter()


def _public(q):
    return {"id": q["id"], "track": q["track"], "module": q["module"], "diff": q["diff"],
            "q": q["q"], "opts": q["opts"]}


@router.get("/quiz/bank")
def bank():
    counts = {
        "tracks": sorted({q["track"] for q in QUESTIONS}),
        "modules": sorted({q["module"] for q in QUESTIONS}),
        "diffs": ["easy", "medium", "hard"],
    }
    return {"questions": [_public(q) for q in QUESTIONS], "counts": counts}


class QuizSubmit(BaseModel):
    quiz_id: str = "quiz"
    answers: dict[str, int] = {}
    qids: list[str] = []


@router.post("/quiz/submit")
def submit(body: QuizSubmit):
    p = deps.progress()
    # Grade every question in the set the learner was shown. Sending only the
    # answered ids used to grade 1/1 = 100%; unanswered questions are wrong.
    requested = body.qids or list(body.answers.keys())
    ids = list(dict.fromkeys(qid for qid in requested if qid in Q_BY_ID))
    if not ids:
        raise HTTPException(status_code=400, detail="No questions to grade.")

    score, review, wrong = 0, [], []
    for qid in ids:
        q = Q_BY_ID[qid]
        chosen = body.answers.get(qid)
        ok = isinstance(chosen, int) and chosen == q["ans"]
        score += int(ok)
        if not ok:
            wrong.append(q["module"])
        review.append({"id": qid, "q": q["q"], "module": q["module"], "diff": q["diff"],
                       "you": q["opts"][chosen] if isinstance(chosen, int) and 0 <= chosen < len(q["opts"]) else None,
                       "correct": q["opts"][q["ans"]], "ok": ok, "exp": q["exp"]})

    quiz_id = (body.quiz_id or "quiz")[:80]
    pct = record_quiz(p, quiz_id, score, len(ids))
    weak = [m for m, _ in Counter(wrong).most_common(3)]
    p["weak_topics"] = list(dict.fromkeys(p.get("weak_topics", []) + weak))
    deps.commit(p)
    return {"score": score, "total": len(ids), "pct": pct, "review": review,
            "weak_topics": p["weak_topics"], "xp": p.get("xp", 0)}


@router.get("/drill")
def drill():
    p = deps.progress()
    due, new = srs.due_cards(p)
    cards = [{"id": qid, "box": p.get("srs", {}).get(qid, {}).get("box", 0), **_public(Q_BY_ID[qid])}
             for qid in due]
    fresh = [{"id": qid, "box": 0, **_public(Q_BY_ID[qid])} for qid in new]
    return {
        "due": cards,
        "new": fresh,
        "due_count": len(cards),
        "new_count": len(fresh),
        "retention": round(srs.overall_retention(p), 4),
        "mastery": srs.mastery_table(p),
    }


class DrillGrade(BaseModel):
    qid: str
    correct: bool


@router.post("/drill/grade")
def drill_grade(body: DrillGrade):
    if body.qid not in Q_BY_ID:
        raise HTTPException(status_code=404, detail="Unknown question.")
    p = deps.progress()
    card = srs.grade(p, body.qid, body.correct)
    deps.commit(p)
    return {"card": card, "retention": round(srs.overall_retention(p), 4)}


# ------------------------------------------------------------------ gates
@router.get("/gates")
def gate_overview():
    p = deps.progress()
    from lib.content import MODULES
    return [{"id": m["id"], "title": m["title"], "track": m["track"],
             "status": gates.status(p, m["id"]),
             "missing_prereqs": gates.missing_prereqs(p, m["id"]),
             "mcq": len(gates.mcq_for(m["id"])),
             "attempts": (gates.gate(p, m["id"]) or {}).get("attempts", 0)}
            for m in MODULES]


@router.get("/gates/{mid}")
def gate_detail(mid: str):
    if mid not in gates.ORAL:
        raise HTTPException(status_code=404, detail="Unknown gate.")
    p = deps.progress()
    cd = gates.cooldown_left(p, mid)
    return {
        "module": mid,
        "title": gates.title(mid),
        "status": gates.status(p, mid),
        "missing_prereqs": gates.missing_prereqs(p, mid),
        "cooldown_hours": round(cd.total_seconds() / 3600, 1) if cd else None,
        "pass_marks": {"mcq": gates.MCQ_PASS, "oral": gates.ORAL_PASS, "min_chars": gates.ORAL_MIN_CHARS},
        "mcq": [_public(q) for q in gates.mcq_for(mid)],
        "oral": [{"prompt": prompt, "points": points} for prompt, points in gates.ORAL[mid]],
    }


class McqBody(BaseModel):
    answers: dict[str, int] = {}


def _score_mcq(mid, answers):
    mcq = gates.mcq_for(mid)
    if not mcq:
        return 0, []
    correct, review = 0, []
    for q in mcq:
        chosen = answers.get(q["id"])
        ok = chosen == q["ans"]
        correct += int(ok)
        review.append({"id": q["id"], "q": q["q"], "ok": ok,
                       "you": q["opts"][chosen] if isinstance(chosen, int) and 0 <= chosen < len(q["opts"]) else None,
                       "correct": q["opts"][q["ans"]], "exp": q["exp"]})
    return round(100 * correct / len(mcq)), review


@router.post("/gates/{mid}/mcq")
def gate_mcq(mid: str, body: McqBody):
    if mid not in gates.ORAL:
        raise HTTPException(status_code=404, detail="Unknown gate.")
    pct, review = _score_mcq(mid, body.answers)
    return {"mcq_pct": pct, "review": review}


class GateSubmit(BaseModel):
    answers: dict[str, int] = {}
    oral_hits: list[int] = []
    texts: list[str] = []


@router.post("/gates/{mid}/submit")
def gate_submit(mid: str, body: GateSubmit):
    if mid not in gates.ORAL:
        raise HTTPException(status_code=404, detail="Unknown gate.")
    oral = gates.ORAL[mid]
    if len(body.texts) != len(oral):
        raise HTTPException(status_code=400, detail="Answer every teach-back.")
    if any(len((t or "").strip()) < gates.ORAL_MIN_CHARS for t in body.texts):
        raise HTTPException(status_code=400,
                            detail=f"Each teach-back needs {gates.ORAL_MIN_CHARS}+ characters.")

    mcq_pct, review = _score_mcq(mid, body.answers)
    total_points = sum(len(points) for _, points in oral)
    hits = sum(max(0, min(int(h), len(oral[i][1]))) for i, h in enumerate(body.oral_hits or [0] * len(oral)))
    oral_pct = round(100 * hits / total_points) if total_points else 0

    p = deps.progress()
    passed, reset = gates.record_attempt(p, mid, mcq_pct, oral_pct, {"teach_back": body.texts})
    if passed:
        p["xp"] = p.get("xp", 0) + 150
    deps.commit(p)
    log_activity(p, "gate")
    if passed:
        log_activity(p, "gate_pass")
    return {"passed": passed, "reset": reset, "mcq_pct": mcq_pct, "oral_pct": oral_pct,
            "review": review, "status": gates.status(deps.progress(), mid)}
