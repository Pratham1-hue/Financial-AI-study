"""Sync YouTube data into local JSON: channels, catalogs, and a per-module curriculum.

Run:  .venv\\Scripts\\python.exe scripts\\sync_youtube.py [--quota-limit 6000]

Costs roughly 2,000 quota units on a cold run (one `search` per module = 100 units each),
and ~0 on a warm run because every response is cached for a week.
"""
import argparse
import json
import math
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import youtube as yt          # noqa: E402
from lib.paths import DATA_DIR as DATA  # noqa: E402
from lib.yt_sources import CHANNELS, MODULE_KEYWORDS, MODULE_QUERIES, PLAYLISTS  # noqa: E402

CATALOG = os.path.join(DATA, "yt_catalog.json")
CURRICULUM = os.path.join(DATA, "yt_curriculum.json")

PER_MODULE = 10
MIN_SECS, MAX_SECS = 180, 3 * 3600     # no shorts, no 3-hour streams

# Titles that signal market commentary rather than a lesson. This app is a curriculum.
NEWSY = ("breaking", "market analysis", "reacts", "tiktok", "shorts", "this week",
         "just filed", "scandal", "what happened", "live:", "recap", "news roundup",
         "why everyone is leaving", "may have just", "on the verge")
LESSON = ("tutorial", "explained", "course", "intro", "beginner", "from scratch",
          "lecture", "masterclass", "crash course", "walkthrough", "deep dive",
          "fundamentals", "basics", "how to", "step by step", "guide", "full")

# Non-Latin scripts: `relevanceLanguage=en` still leaks other languages through.
NON_LATIN = re.compile(r"[\u0400-\u04FF\u0590-\u05FF\u0600-\u06FF\u0900-\u097F"
                       r"\u0B80-\u0BFF\u0C00-\u0C7F\u0E00-\u0E7F\u3040-\u30FF"
                       r"\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF]")
LANG_MARKERS = ("tamil", "hindi", "telugu", "urdu", "malayalam", "kannada", "bengali",
                "espanol", "español", "portugues", "português", "deutsch", "francais",
                "français", "bahasa", "tiếng việt")

# Mass-retail trading channels: on-topic, but they teach trading, not market structure.
# Down-ranked rather than banned - in a thin module they may still be the best available.
RETAIL = ("pushkar", "zebu", "pandrea", "brad finn", "projectoption", "trading chanakya")


def shouting(title):
    letters = [c for c in title if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) > 0.7


def log(*a):
    print(*a, flush=True)


def score(v, trusted, keywords, rank=None):
    """Higher is better. YouTube's own relevance order dominates; keywords gate entry."""
    title = v["title"].lower()
    desc = v["desc"].lower()[:600]
    if NON_LATIN.search(v["title"]):        # wrong language for this curriculum
        return -999.0
    if any(m in title for m in LANG_MARKERS):
        return -999.0
    hits_t = sum(1 for k in keywords if k in title)
    hits_d = sum(1 for k in keywords if k in desc)
    if hits_t == 0 and hits_d < 2 and rank is None:
        return -999.0

    s = 0.0
    if rank is not None:                 # search results keep YouTube's relevance ranking
        s += max(0.0, 40.0 - rank)
    s += min(45, hits_t * 18) + min(10, hits_d * 2)   # topical match
    if v["channel_id"] in trusted:
        s += 12
    if any(w in title for w in NEWSY):
        s -= 35
    if any(w in title for w in LESSON):
        s += 6
    if shouting(v["title"]):
        s -= 18
    if any(r in v["channel"].lower() for r in RETAIL):
        s -= 12
    if v["views"] < 2000:                # long tail: allowed, but never first
        s -= 6
    secs = v["secs"]
    if 300 <= secs <= 4200:              # 5-70 min: a real lesson, not a clip or a stream
        s += 10
    elif secs < 240:
        s -= 25
    s += min(5, math.log10(v["views"] + 1))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quota-limit", type=int, default=6000, help="stop before exceeding this")
    ap.add_argument("--per-module", type=int, default=PER_MODULE)
    args = ap.parse_args()

    if not yt.available():
        log("No API key. Put YOUTUBE_API_KEY in .streamlit/secrets.toml or the environment.")
        return 1

    st = yt.status()
    log(f"API: ok={st['ok']} quota_used={st['quota']} {st['reason']}")

    # ---------------- 1. channels ----------------
    chans, broken = {}, []
    for handle, (name, track, why) in CHANNELS.items():
        if yt.quota_used_today() > args.quota_limit:
            log(f"! quota guard hit at {yt.quota_used_today()} - stopping channel phase")
            break
        try:
            c = yt.channel(handle)
        except yt.YouTubeError as e:
            broken.append((handle, str(e)))
            continue
        if not c:
            broken.append((handle, "not found"))
            continue
        c.update(handle=handle, track=track, why=why, name=name)
        chans[handle] = c
        log(f"  ok  {handle:<26} {c['subs']:>10,} subs  {c['videos']:>5} videos")

    log(f"\nresolved {len(chans)} channels, {len(broken)} broken")
    for h, why in broken:
        log(f"  BROKEN {h}: {why}")

    # ---------------- 2. catalogs ----------------
    videos = {}
    for handle, c in chans.items():
        if yt.quota_used_today() > args.quota_limit:
            log("! quota guard hit - stopping catalog phase")
            break
        try:
            vs = yt.channel_videos(c["id"], 50)
        except yt.YouTubeError as e:
            log(f"  ! {handle}: {e}")
            continue
        for v in vs:
            v["track"] = c["track"]
            v["source"] = handle
            videos[v["id"]] = v
        log(f"  {handle:<26} {len(vs):>3} videos")

    for pid, (title, mid) in PLAYLISTS.items():
        try:
            vs = yt.playlist_videos(pid, 100)
        except yt.YouTubeError as e:
            log(f"  ! playlist {title}: {e}")
            continue
        for v in vs:
            v.setdefault("track", "ai")
            v["source"] = f"playlist:{title}"
            v.setdefault("module_hint", mid)
            videos.setdefault(v["id"], v)
        log(f"  playlist {title:<26} {len(vs):>3} videos")

    log(f"\ncatalog: {len(videos)} unique videos")

    # ---------------- 3. per-module search ----------------
    trusted = {c["id"] for c in chans.values()}
    searched, searches_failed = {}, []
    for mid, queries in MODULE_QUERIES.items():
        hits = {}
        for q in queries:
            if yt.quota_used_today() + 100 > args.quota_limit:
                log(f"! quota guard hit before search {mid} - using catalog only")
                break
            try:
                res = yt.search_videos(q, 25)
            except yt.YouTubeError as e:
                searches_failed.append((mid, str(e)))
                log(f"  ! search {mid}: {e}")
                continue
            for rank, v in enumerate(res):
                if v["id"] not in hits or rank < hits[v["id"]][0]:
                    hits[v["id"]] = (rank, v)
                videos.setdefault(v["id"], v)
                v.setdefault("track", "mixed")
            log(f"  search {mid}: {len(res)} results ({yt.quota_used_today()} units used)")
        searched[mid] = list(hits.values())

    # ---------------- 4. build the curriculum ----------------
    curriculum = {}
    for mid in MODULE_QUERIES:
        kw = MODULE_KEYWORDS[mid]
        scored = {}
        for rank, v in searched.get(mid, []):
            scored[v["id"]] = (score(v, trusted, kw, rank), v)
        for v in videos.values():                      # catalog fills the gaps
            if v["id"] in scored:
                continue
            s = score(v, trusted, kw)                  # no search rank -> must match keywords
            if s > 0:
                scored[v["id"]] = (s, v)

        seen, picked = set(), []
        for s, v in sorted(scored.values(), key=lambda t: t[0], reverse=True):
            if s < 0:
                continue
            if v["id"] in seen or not MIN_SECS <= v["secs"] <= MAX_SECS:
                continue
            # keep the queue diverse: at most 2 videos per channel
            if sum(1 for p in picked if p["channel_id"] == v["channel_id"]) >= 2:
                continue
            seen.add(v["id"])
            picked.append({
                "id": v["id"], "title": v["title"], "channel": v["channel"], "channel_id": v["channel_id"],
                "secs": v["secs"], "views": v["views"], "published": v["published"],
                "thumb": v["thumb"], "score": round(s, 1),
            })
            if len(picked) >= args.per_module:
                break
        curriculum[mid] = {"query": " | ".join(MODULE_QUERIES[mid]), "picked": picked,
                           "generated_at": datetime.now().isoformat(timespec="seconds")}
        log(f"  {mid}: picked {len(picked)} "
            f"({sum(p['secs'] for p in picked) // 60} min total)")

    # ---------------- 5. save ----------------
    payload = {
        "synced_at": datetime.now().isoformat(timespec="seconds"),
        "quota_used_today": yt.quota_used_today(),
        "channels": {h: {k: c[k] for k in ("id", "title", "name", "track", "why", "subs", "videos", "uploads")}
                     for h, c in chans.items()},
        "broken_handles": broken,
        "videos": videos,
    }
    yt._write(CATALOG, payload)          # noqa: SLF001 - same package, deliberate
    yt._write(CURRICULUM, {"generated_at": payload["synced_at"], "modules": curriculum})

    log(f"\ncatalog  -> {CATALOG} ({len(videos)} videos, {os.path.getsize(CATALOG) // 1024} KB)")
    log(f"curriculum -> {CURRICULUM}")
    log(f"quota used today: {yt.quota_used_today()}/{yt.DAILY_QUOTA}")
    if broken:
        log("\nfix these handles in lib/yt_sources.py:")
        for h, why in broken:
            log(f"  {h}  ({why})")
        log("\nfix these queries:")
        for mid, why in searches_failed:
            log(f"  {mid}  ({why})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
