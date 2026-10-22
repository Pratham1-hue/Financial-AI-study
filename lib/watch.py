"""Watch tracking: which lesson videos have been watched, for how long, and on what day.

Watching counts as the lecture block of the bootcamp day, so it feeds the daily score -
but only for a real lesson (>= 6 minutes) tied to a module, never for a clip.
"""
from datetime import date

MIN_CREDIT_SECS = 6 * 60      # a "watched" video must be at least this long to earn credit

def _today():
    return date.today().isoformat()


def is_watched(progress, vid):
    return vid in progress.get("watched", {})


def mark(progress, vid, module, title, channel, secs, xp=25):
    """Record a video as watched. Returns True if this is the first time."""
    w = progress.setdefault("watched", {})
    first = vid not in w
    if first:
        w[vid] = {"date": _today(), "module": module, "title": title,
                  "channel": channel, "secs": int(secs or 0)}
        progress["xp"] = progress.get("xp", 0) + xp
    return first


def today_secs(progress):
    t = _today()
    return sum(v.get("secs", 0) for v in progress.get("watched", {}).values() if v.get("date") == t)


def today_count(progress):
    t = _today()
    return sum(1 for v in progress.get("watched", {}).values() if v.get("date") == t)


def for_module(progress, mid):
    return {k: v for k, v in progress.get("watched", {}).items() if v.get("module") == mid}


def queue_progress(progress, queue):
    """(watched, total, minutes_left) for a module's curated queue."""
    done = sum(1 for v in queue if is_watched(progress, v["id"]))
    left = sum(v["secs"] for v in queue if not is_watched(progress, v["id"]))
    return done, len(queue), left


def next_up(progress, queue):
    for v in queue:
        if not is_watched(progress, v["id"]):
            return v
    return None


def total_hours(progress):
    return sum(v.get("secs", 0) for v in progress.get("watched", {}).values()) / 3600
