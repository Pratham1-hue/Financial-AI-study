"""Spaced repetition (Leitner) over the question bank + Khan-style mastery levels."""
from datetime import date, timedelta

from lib.content import MODULE_BY_ID, MODULES
from lib.quiz_bank import QUESTIONS, Q_BY_ID
from lib.storage import log_activity

INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}   # days until next review per box
NEW_PER_DAY = 10
BOX_POINTS = {0: 0.0, 1: 1.0, 2: 1.5, 3: 2.5, 4: 3.5, 5: 4.0}
LEVELS = [(0.0, "Not started"), (0.01, "Familiar"), (0.40, "Proficient"), (0.75, "Mastered")]
LEVEL_ICON = {"Not started": ":material/radio_button_unchecked:", "Familiar": ":material/counter_1:",
              "Proficient": ":material/counter_2:", "Mastered": ":material/workspace_premium:"}


def _week_of(q):
    mod = MODULE_BY_ID.get(q["module"])
    return min(mod["weeks"]) if mod else 99


CURRICULUM_ORDER = [q["id"] for q in sorted(QUESTIONS, key=lambda q: (_week_of(q), q["module"], q["id"]))]


def due_cards(progress):
    today = date.today().isoformat()
    srs = progress.get("srs", {})
    due = sorted((qid for qid, c in srs.items() if c["due"] <= today and qid in Q_BY_ID),
                 key=lambda qid: (srs[qid]["due"], srs[qid]["box"]))
    new_left = max(0, NEW_PER_DAY - progress.get("srs_new", {}).get(today, 0))
    new = [qid for qid in CURRICULUM_ORDER if qid not in srs][:new_left]
    return due, new


def grade(progress, qid, correct):
    today = date.today()
    srs = progress.setdefault("srs", {})
    card = srs.get(qid)
    if card is None:
        card = {"box": 0, "due": today.isoformat(), "seen": 0, "correct": 0}
        news = progress.setdefault("srs_new", {})
        news[today.isoformat()] = news.get(today.isoformat(), 0) + 1
    card["box"] = min(5, card["box"] + 1) if correct else 1
    card["due"] = (today + timedelta(days=INTERVALS[card["box"]])).isoformat()
    card["seen"] += 1
    card["correct"] += int(bool(correct))
    srs[qid] = card
    log_activity(progress, "review")
    return card


def _level(pct):
    name = LEVELS[0][1]
    for threshold, label in LEVELS:
        if pct >= threshold:
            name = label
    return name


def module_mastery(progress, module_id):
    qs = [q["id"] for q in QUESTIONS if q["module"] == module_id]
    if not qs:
        return None, "No questions yet"
    srs = progress.get("srs", {})
    pts = sum(BOX_POINTS[srs[q]["box"]] if q in srs else 0.0 for q in qs)
    pct = pts / (4.0 * len(qs))
    return pct, _level(pct)


def overall_retention(progress):
    srs = progress.get("srs", {})
    pts = sum(BOX_POINTS[srs[q]["box"]] if q in srs else 0.0 for q in Q_BY_ID)
    return pts / (4.0 * len(Q_BY_ID))


def mastery_table(progress):
    rows = []
    for m in MODULES:
        pct, level = module_mastery(progress, m["id"])
        if pct is None:
            continue
        rows.append({"module": m["id"], "title": m["title"], "track": m["track"],
                     "mastery": round(pct * 100), "level": level})
    return rows