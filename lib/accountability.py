"""Accountability engine: daily score, career stock, Mastery Index, contract breaches."""
import re
from datetime import date, timedelta

from lib import focus, srs
from lib.study_plan import WEEKS

ZERO_DAY = 10           # a day scoring below this is a zero day
PLAN_DAYS = 112

# Points each component can contribute. Must sum to 100.
PART_MAX = {
    "Deep work": 30,
    "Lesson watched": 10,
    "Retention drill": 15,
    "Proof (quiz 80%+)": 15,
    "Hands-on practice": 10,
    "Feynman debrief": 20,
}


# ---------- daily score ----------
def day_parts(progress, d, goal_min):
    key = d.isoformat()
    a = progress.get("activity", {}).get(key, {})
    fm = focus.minutes_by_day(progress).get(key, 0)
    reviews = a.get("review", 0)
    lesson_secs = sum(v.get("secs", 0) for v in progress.get("watched", {}).values()
                      if v.get("date") == key and v.get("secs", 0) >= 6 * 60)
    parts = {
        "Deep work": min(1.0, fm / max(goal_min, 1)) * 30,
        "Lesson watched": min(1.0, lesson_secs / (20 * 60)) * 10,
        "Retention drill": 15.0 if a.get("drill_clear") else min(1.0, reviews / 10) * 15,
        "Proof (quiz 80%+)": 15.0 if (a.get("quiz80") or a.get("gate_pass")) else (7.0 if a.get("quiz") or a.get("exam") or a.get("gate") else 0.0),
        "Hands-on practice": 10.0 if any(a.get(k) for k in ("code", "interview", "task", "challenge", "speed", "desk", "lab")) else 0.0,
        "Feynman debrief": 20.0 if key in progress.get("debriefs", {}) else 0.0,
    }
    return parts, fm


def day_score(progress, d, goal_min):
    parts, _ = day_parts(progress, d, goal_min)
    return round(sum(parts.values()))


def start_date(progress):
    try:
        return date.fromisoformat(progress.get("started_at") or date.today().isoformat())
    except ValueError:
        return date.today()


def plan_day(progress):
    return (date.today() - start_date(progress)).days + 1


def todays_assignment(progress):
    n = plan_day(progress)
    if n > PLAN_DAYS:
        return n, None, "Plan complete. Every day now: one mock interview, one paper, one application."
    week = WEEKS[(n - 1) // 7]
    return n, week, week["days"][(n - 1) % 7]


# ---------- career stock ----------
def day_return(score):
    if score < ZERO_DAY:
        return -0.08
    return (score - 50) / 50 * 0.06


def stock_series(progress, goal_min):
    rows, price = [], 100.0
    d, today = start_date(progress), date.today()
    while d <= today:
        score = day_score(progress, d, goal_min)
        _, fm = day_parts(progress, d, goal_min)
        o = price
        c = o * (1 + day_return(score))
        rows.append({
            "date": d.isoformat(), "open": round(o, 2), "close": round(c, 2),
            "high": round(max(o, c) * (1.004 + score / 12000), 2),
            "low": round(min(o, c) * (0.996 - (100 - score) / 25000), 2),
            "volume": fm, "score": score, "live": d == today,
        })
        price = c
        d += timedelta(days=1)
    return rows


def analyst_rating(rows):
    recent = [r["score"] for r in rows[-5:]] or [0]
    avg = sum(recent) / len(recent)
    for threshold, label in [(80, "Strong buy"), (60, "Buy"), (40, "Hold"), (20, "Sell")]:
        if avg >= threshold:
            return label, avg
    return "Strong sell", avg


def ticker_symbol(profile):
    if profile.get("ticker"):
        return profile["ticker"].upper()[:5]
    letters = re.sub(r"[^A-Za-z]", "", profile.get("name", "")).upper()
    return "LAKSH" if letters == "LEARNER" else (letters[:4] or "LAKSH")


# ---------- Mastery Index ----------
MI_MAX = {"Mastery gates passed": 20, "Proven retention": 20, "Exam performance": 15, "Deep-work hours": 15,
          "Interview reps": 15, "Challenges solved": 10, "Feynman debriefs": 5}


def mastery_index(progress):
    from lib.challenges import CHALLENGES
    from lib.content import MODULES
    from lib.gates import mastered_count
    exams = progress.get("exam_scores", {})
    exam_avg = sum(e.get("score", 0) for e in exams.values()) / 5 / 100 if exams else 0.0
    iv = progress.get("interviews", [])
    iv_avg = (sum(x["score"] for x in iv) / len(iv) / 5) if iv else 0.0
    solved = sum(1 for c in progress.get("challenges", {}).values() if c.get("solved"))
    parts = {
        "Mastery gates passed": mastered_count(progress) / len(MODULES) * MI_MAX["Mastery gates passed"],
        "Proven retention": srs.overall_retention(progress) * MI_MAX["Proven retention"],
        "Exam performance": min(1.0, exam_avg) * MI_MAX["Exam performance"],
        "Deep-work hours": min(1.0, focus.total_hours(progress) / 400) * MI_MAX["Deep-work hours"],
        "Interview reps": min(1.0, len(iv) / 60) * iv_avg * MI_MAX["Interview reps"],
        "Challenges solved": solved / len(CHALLENGES) * MI_MAX["Challenges solved"],
        "Feynman debriefs": min(1.0, len(progress.get("debriefs", {})) / 60) * MI_MAX["Feynman debriefs"],
    }
    return round(sum(parts.values()), 1), parts


# ---------- bootcamp day (Le Wagon rhythm + Hack Reactor warm-up, adapted for solo study) ----------
DAY_BLOCKS = [
    ("Toy problem warm-up", 0.08, "Solve today's toy problem before anything else. Wakes up the problem-solving brain.", "app_pages/19_challenge_lab.py"),
    ("Lecture block", 0.25, "Watch the module's next ranked lesson and take active notes: questions, not transcripts.", "app_pages/22_watch.py"),
    ("Challenge block", 0.40, "Deliberate practice: challenges, console, models. The 20-minute rule applies before hints.", "app_pages/19_challenge_lab.py"),
    ("Retrieval block", 0.10, "Daily drill: active recall on everything due.", "app_pages/16_drill.py"),
    ("Review block", 0.09, "Compare your solutions with the reference. Fix one mistake for real.", "app_pages/19_challenge_lab.py"),
    ("Debrief", 0.08, "Feynman debrief: explain the hardest idea simply. Commit to tomorrow's first block.", "app_pages/15_mission.py"),
]


def bootcamp_day(goal_min, start_hour):
    from datetime import datetime as _dt
    t = _dt.combine(date.today(), _dt.min.time()) + timedelta(hours=start_hour)
    out = []
    for name, frac, desc, page in DAY_BLOCKS:
        mins = max(10, int(round(goal_min * frac / 5) * 5))
        out.append({"name": name, "start": t, "end": t + timedelta(minutes=mins), "desc": desc, "page": page, "mins": mins})
        t += timedelta(minutes=mins)
    return out


# ---------- the contract ----------
def unresolved_breaches(progress, goal_min):
    c = progress.get("contract")
    if not c or not c.get("signed_on"):
        return []
    try:
        d = date.fromisoformat(c["signed_on"]) + timedelta(days=1)
    except ValueError:
        return []
    out, incidents = [], progress.get("incidents", {})
    while d < date.today():
        if d.isoformat() not in incidents and day_score(progress, d, goal_min) < ZERO_DAY:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out