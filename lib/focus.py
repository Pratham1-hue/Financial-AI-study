"""Lock-in mode: a persistent Pomodoro engine that logs real focus hours."""
import base64
import io
import os
import time
import wave
from datetime import date, datetime, timedelta
from functools import lru_cache

import numpy as np

from lib.storage import DATA_DIR, _load, _save, load_progress, save_progress

FOCUS_FILE = os.path.join(DATA_DIR, "focus.json")

MODES = {
    "Pomodoro": {"focus": 25, "short": 5, "long": 15, "every": 4,
                 "desc": "Classic 25/5. Drills, quizzes, LeetCode, flashcards."},
    "Deep Work": {"focus": 50, "short": 10, "long": 20, "every": 3,
                  "desc": "50/10. Reading papers, building models, financial modeling."},
    "Monk Mode": {"focus": 90, "short": 15, "long": 30, "every": 2,
                  "desc": "90-minute ultradian block. Capstones and the hardest problems."},
    "Sprint": {"focus": 15, "short": 3, "long": 10, "every": 4,
               "desc": "15/3. For low-motivation days. Just start; momentum does the rest."},
    "Custom": {"focus": 40, "short": 8, "long": 20, "every": 3,
               "desc": "Your own rhythm."},
}

SUBJECTS = ["AI & ML", "Finance", "Quant", "Python & SQL", "Interview prep", "Projects", "Reading papers"]

PHASE_LABEL = {"focus": "Locked in", "short_break": "Short break", "long_break": "Long break"}
PHASE_COLOR = {"focus": "#F5B942", "short_break": "#2DD4BF", "long_break": "#A78BFA"}

DEFAULT_STATE = {
    "status": "idle",          # idle | running | paused
    "phase": "focus",          # focus | short_break | long_break
    "mode": "Pomodoro",
    "custom": {"focus": 40, "short": 8, "long": 20, "every": 3},
    "ends_at": None,
    "remaining": None,
    "phase_total": None,
    "phase_started": None,
    "label": "",
    "subject": "AI & ML",
    "cycles": 0,
    "auto_break": True,
    "sound": True,
}


def load_state():
    s = _load(FOCUS_FILE, dict(DEFAULT_STATE))
    for k, v in DEFAULT_STATE.items():
        s.setdefault(k, v)
    return s


def save_state(s):
    _save(FOCUS_FILE, s)


def mode_cfg(s):
    if s["mode"] == "Custom":
        return {**MODES["Custom"], **s.get("custom", {})}
    return MODES.get(s["mode"], MODES["Pomodoro"])


def phase_seconds(s, phase=None):
    cfg = mode_cfg(s)
    phase = phase or s["phase"]
    mins = {"focus": cfg["focus"], "short_break": cfg["short"], "long_break": cfg["long"]}[phase]
    return int(mins * 60)


def remaining(s):
    if s["status"] == "running" and s["ends_at"]:
        return max(0.0, s["ends_at"] - time.time())
    if s["status"] == "paused" and s["remaining"] is not None:
        return float(s["remaining"])
    return float(phase_seconds(s))


def total(s):
    return float(s["phase_total"] or phase_seconds(s))


def start(s):
    now = time.time()
    if s["status"] == "paused" and s["remaining"] is not None:
        s["ends_at"] = now + s["remaining"]
    else:
        t = phase_seconds(s)
        s["phase_total"] = t
        s["phase_started"] = now
        s["ends_at"] = now + t
    s["remaining"] = None
    s["status"] = "running"
    save_state(s)


def pause(s):
    s["remaining"] = remaining(s)
    s["ends_at"] = None
    s["status"] = "paused"
    save_state(s)


def reset(s):
    s.update(status="idle", phase="focus", ends_at=None, remaining=None,
             phase_total=None, phase_started=None)
    save_state(s)


def _go_idle(s, phase):
    s.update(status="idle", phase=phase, ends_at=None, remaining=None,
             phase_total=None, phase_started=None)


def stop_and_log(s):
    """End the current focus block early and log the minutes actually worked."""
    minutes = 0
    if s["phase"] == "focus" and s["status"] in ("running", "paused"):
        elapsed = total(s) - remaining(s)
        minutes = int(elapsed // 60)
        if minutes >= 1:
            log_focus(minutes, s["subject"], s["label"], s["mode"], s["phase_started"])
    _go_idle(s, "focus")
    save_state(s)
    return minutes


def skip(s):
    if s["phase"] == "focus":
        _go_idle(s, _next_break(s))
    else:
        _go_idle(s, "focus")
    save_state(s)


def _next_break(s):
    every = mode_cfg(s)["every"]
    return "long_break" if s["cycles"] and s["cycles"] % every == 0 else "short_break"


def log_focus(minutes, subject, label, mode, session_id):
    p = load_progress()
    log = p.setdefault("focus_log", [])
    sid = str(session_id)
    if any(e.get("id") == sid for e in log):
        return False
    log.append({
        "id": sid,
        "date": date.today().isoformat(),
        "ended_at": datetime.now().isoformat(timespec="minutes"),
        "minutes": int(minutes),
        "subject": subject,
        "label": label,
        "mode": mode,
    })
    p["xp"] = p.get("xp", 0) + int(minutes) * 2
    save_progress(p)
    return True


def tick(s):
    """Advance the state machine if the running phase has ended.

    Returns an event dict or None.
    """
    if s["status"] != "running" or not s["ends_at"]:
        return None
    now = time.time()
    if now < s["ends_at"]:
        return None
    overdue = now - s["ends_at"]
    if s["phase"] == "focus":
        minutes = int(round(total(s) / 60))
        log_focus(minutes, s["subject"], s["label"], s["mode"], s["phase_started"])
        s["cycles"] = s.get("cycles", 0) + 1
        nxt = _next_break(s)
        _go_idle(s, nxt)
        if s.get("auto_break", True) and overdue < phase_seconds(s, nxt):
            t = phase_seconds(s, nxt)
            s.update(status="running", phase_total=t, phase_started=now - overdue,
                     ends_at=now - overdue + t)
        save_state(s)
        return {"type": "focus_done", "minutes": minutes, "subject": s["subject"]}
    _go_idle(s, "focus")
    save_state(s)
    return {"type": "break_done"}


# ---------- stats ----------
def minutes_by_day(progress):
    out = {}
    for e in progress.get("focus_log", []):
        out[e["date"]] = out.get(e["date"], 0) + e["minutes"]
    return out


def today_minutes(progress):
    return minutes_by_day(progress).get(date.today().isoformat(), 0)


def week_minutes(progress):
    by = minutes_by_day(progress)
    start = date.today() - timedelta(days=6)
    return sum(m for d, m in by.items() if d >= start.isoformat())


def total_hours(progress):
    return sum(e["minutes"] for e in progress.get("focus_log", [])) / 60


def sessions_today(progress):
    t = date.today().isoformat()
    return sum(1 for e in progress.get("focus_log", []) if e["date"] == t)


def focus_streak(progress, min_minutes=25):
    by = minutes_by_day(progress)
    d = date.today()
    if by.get(d.isoformat(), 0) < min_minutes:
        d -= timedelta(days=1)
    streak = 0
    while by.get(d.isoformat(), 0) >= min_minutes:
        streak += 1
        d -= timedelta(days=1)
    return streak


def fmt_clock(seconds):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def fmt_hm(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m"


@lru_cache(maxsize=1)
def chime_b64():
    """A soft three-note chime (C6-E6-G6) as a base64 WAV."""
    sr = 22050
    notes = [1046.5, 1318.5, 1568.0]
    chunks = []
    for f in notes:
        t = np.linspace(0, 0.32, int(sr * 0.32), endpoint=False)
        env = np.exp(-5 * t)
        chunks.append(0.35 * env * np.sin(2 * np.pi * f * t))
    audio = np.concatenate(chunks)
    pcm = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return base64.b64encode(buf.getvalue()).decode()