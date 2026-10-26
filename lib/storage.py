"""JSON-backed persistence for user progress and settings."""
import copy
import json
import os
from datetime import datetime

from lib.paths import DATA_DIR

PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")


def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(path, default):
    _ensure()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    _ensure()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


DEFAULT_PROGRESS = {
    "started_at": None,
    "study_days": {},
    "completed_tasks": [],
    "quiz_scores": {},
    "exam_scores": {},
    "practice_runs": 0,
    "xp": 0,
    "badges": [],
    "weak_topics": [],
    "focus_log": [],
    "activity": {},      # {date: {kind: count}}
    "srs": {},           # {question_id: {box, due, seen, correct}}
    "srs_new": {},       # {date: new cards introduced}
    "debriefs": {},      # {date: {...}}
    "interviews": [],    # [{date, id, category, score, overtime}]
    "contract": None,    # signed oath
    "incidents": {},     # {date: incident report}
    "gates": {},         # {module_id: mastery gate state}
    "challenges": {},    # {challenge_id: {first_seen, attempts, solved}}
    "speed_drills": [],  # [{date, score, wrong, minutes, ops}]
    "watched": {},       # {video_id: {date, module, mins, title, channel}}
    "desk_rounds": [],   # [{date, score, ret, dd, trades, ...}] live market sim
    "lab_runs": [],      # [{date, lab, ok, detail}] SQL / ML / valuation labs
    "last_visit": None,
}

DEFAULT_PROFILE = {
    "name": "Learner",
    "target_role": "Quantitative ML Engineer (NYC)",
    "target_date": "",
    "daily_hours": 6,
    "level": "Beginner",
    "why": "A corner desk overlooking Manhattan, a role at the intersection of markets and AI, and the freedom that comes with being world-class.",
    "dream_companies": "Jane Street, Two Sigma, Citadel, Goldman Sachs, JPMorgan, Bloomberg, Renaissance",
    "day_start": 9,
}


def fresh_progress():
    return copy.deepcopy(DEFAULT_PROGRESS)


def load_progress():
    p = _load(PROGRESS_FILE, fresh_progress())
    for k, v in DEFAULT_PROGRESS.items():
        p.setdefault(k, copy.deepcopy(v))
    return p


def save_progress(p):
    p["last_visit"] = datetime.now().isoformat()
    _save(PROGRESS_FILE, p)


def load_profile():
    prof = _load(PROFILE_FILE, dict(DEFAULT_PROFILE))
    for k, v in DEFAULT_PROFILE.items():
        prof.setdefault(k, v)
    return prof


def save_profile(prof):
    _save(PROFILE_FILE, prof)


def mark_task(progress, task_id):
    if task_id not in progress["completed_tasks"]:
        progress["completed_tasks"].append(task_id)
        progress["xp"] += 10
        _bump(progress, "task")
    save_progress(progress)


def is_task_done(progress, task_id):
    return task_id in progress["completed_tasks"]


def record_quiz(progress, quiz_id, score, total):
    total = max(total, 1)
    pct = round(100 * score / total)
    rec = progress["quiz_scores"].get(quiz_id, {})
    best_pct = rec.get("best", 0)
    # Best raw score, not just the rounded percentage: paying the full current
    # score on every small improvement let retakers out-earn one clean run.
    prev_best = rec.get("best_score")
    if prev_best is None:
        prev_best = round(best_pct / 100 * total)  # legacy records
    improvement = max(0, score - prev_best)
    progress["quiz_scores"][quiz_id] = {
        "last": pct,
        "best": max(best_pct, pct),
        "best_score": max(prev_best, score),
        "attempts": rec.get("attempts", 0) + 1,
    }
    # XP rewards progress, not repetition: each newly correct answer pays once.
    if improvement:
        progress["xp"] += improvement * 5
    _bump(progress, "quiz")
    if pct >= 80:
        _bump(progress, "quiz80")
    save_progress(progress)
    return pct


def record_exam(progress, exam_id, score, total):
    total = max(total, 1)
    pct = round(100 * score / total)
    rec = progress["exam_scores"].get(exam_id, {})
    prev_pct = rec.get("score", 0)
    prev_best = rec.get("best_score")
    if prev_best is None:
        prev_best = round(prev_pct / 100 * total)  # legacy records
    improvement = max(0, score - prev_best)
    # Keep the personal best: a retake must never lower a mastered score.
    progress["exam_scores"][exam_id] = {
        "score": max(prev_pct, pct),
        "last": pct,
        "best_score": max(prev_best, score),
        "at": datetime.now().isoformat(),
    }
    # Retakes are for mastery, not farming: only newly correct answers pay.
    if improvement:
        progress["xp"] += improvement * 10
    _bump(progress, "exam")
    save_progress(progress)
    return pct


def _bump(progress, kind, n=1):
    today = datetime.now().date().isoformat()
    day = progress.setdefault("activity", {}).setdefault(today, {})
    day[kind] = day.get(kind, 0) + n


def log_activity(progress, kind, n=1):
    """Record a countable action for today (code, review, debrief, interview, task...)."""
    _bump(progress, kind, n)
    save_progress(progress)


def log_study_day(progress):
    today = datetime.now().date().isoformat()
    progress["study_days"][today] = progress["study_days"].get(today, 0) + 1
    if progress["started_at"] is None:
        progress["started_at"] = today
    save_progress(progress)


def streak_days(progress):
    days = sorted(progress["study_days"].keys(), reverse=True)
    if not days:
        return 0
    from datetime import date, timedelta
    today = date.today()
    streak = 0
    cursor = today
    dayset = set(days)
    while cursor.isoformat() in dayset:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak