"""YouTube Data API v3 client - cached, quota-aware, stdlib only.

Design notes
------------
* Every response is cached on disk (`data/yt_cache.json`) with a TTL, so reruns cost
  no quota. Quota is the scarce resource: `search` costs 100 units, everything else 1.
* The free tier is 10,000 units/day. `quota_used_today()` is shown in the UI so we
  never blow through it silently.
* The key lives in `.streamlit/secrets.toml` (or the YOUTUBE_API_KEY env var) and is
  never written into the cache or the logs.
"""
import json
import os
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

from lib.paths import DATA_DIR

CACHE_FILE = os.path.join(DATA_DIR, "yt_cache.json")
QUOTA_FILE = os.path.join(DATA_DIR, "yt_quota.json")

_LOCK = threading.Lock()        # the cache/quota files are shared by concurrent checks

API = "https://www.googleapis.com/youtube/v3/"
DAILY_QUOTA = 10_000
COST = {"search": 100, "videos": 1, "channels": 1, "playlistItems": 1, "playlists": 1}
TTL = {"search": 7 * 86400, "videos": 3 * 86400, "channels": 7 * 86400,
       "playlistItems": 86400, "playlists": 7 * 86400}


class YouTubeError(RuntimeError):
    pass


# ---------------------------------------------------------------- credentials
def api_key():
    """Secrets file first, then environment. Returns None when unconfigured."""
    try:
        import streamlit as st
        key = st.secrets.get("YOUTUBE_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("YOUTUBE_API_KEY")


def available():
    return bool(api_key())


# ---------------------------------------------------------------- plumbing
def _read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def _cache():
    return _read(CACHE_FILE, {"entries": {}})


def _cache_get(name, params):
    with _LOCK:
        e = _cache()["entries"].get(name)
    if not e:
        return None
    age = (datetime.now() - datetime.fromisoformat(e["at"])).total_seconds()
    if age > e["ttl"] or e["params"] != params:
        return None
    return e["data"]


def _cache_put(name, params, data, ttl):
    entry = {"at": datetime.now().isoformat(timespec="seconds"),
             "ttl": ttl, "params": params, "data": data}
    try:
        with _LOCK:
            c = _cache()
            c["entries"][name] = entry
            now = datetime.now()
            c["entries"] = {k: v for k, v in c["entries"].items()
                            if (now - datetime.fromisoformat(v["at"])).total_seconds() < v["ttl"] * 2}
            _write(CACHE_FILE, c)
    except OSError:
        pass                     # the cache is best-effort; never fail a call over it


def quota_used_today():
    with _LOCK:
        q = _read(QUOTA_FILE, {})
    return q.get(date.today().isoformat(), {}).get("used", 0)


def _charge(units, endpoint):
    today = date.today().isoformat()
    try:
        with _LOCK:
            q = _read(QUOTA_FILE, {})
            day = q.setdefault(today, {"used": 0, "calls": {}})
            day["used"] += units
            day["calls"][endpoint] = day["calls"].get(endpoint, 0) + 1
            for k in sorted(q)[:-14]:
                q.pop(k, None)
            _write(QUOTA_FILE, q)
    except OSError:
        pass


def _call(endpoint, use_cache=True, **params):
    key = api_key()
    if not key:
        raise YouTubeError("No YouTube API key. Add YOUTUBE_API_KEY to .streamlit/secrets.toml.")
    params = {k: v for k, v in params.items() if v not in (None, "")}
    sig = {"p": params}
    name = endpoint + ":" + json.dumps(params, sort_keys=True)
    if use_cache:
        hit = _cache_get(name, sig)
        if hit is not None:
            return hit

    used = quota_used_today()
    if used + COST.get(endpoint, 1) > DAILY_QUOTA:
        raise YouTubeError(f"Daily YouTube quota reached ({used}/{DAILY_QUOTA} units). Resets at midnight PT.")

    url = API + endpoint + "?" + urllib.parse.urlencode({**params, "key": key})
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "ProjectDEVI/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body)["error"]["message"]
        except Exception:
            msg = body[:300]
        raise YouTubeError(f"{endpoint} failed ({e.code}): {msg}") from None
    except Exception as e:
        raise YouTubeError(f"{endpoint} unreachable: {e}") from None

    _charge(COST.get(endpoint, 1), endpoint)
    if use_cache:
        _cache_put(name, sig, data, TTL.get(endpoint, 3600))
    return data


# ---------------------------------------------------------------- formatting
_DUR = re.compile(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def parse_duration(iso):
    if not iso:
        return 0
    m = _DUR.fullmatch(iso)
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def fmt_duration(secs):
    h, rem = divmod(int(secs or 0), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_views(n):
    n = int(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K views"
    return f"{n} views"


# ---------------------------------------------------------------- resources
def _video_obj(it):
    sn = it.get("snippet", {})
    st_ = it.get("statistics", {})
    cd = it.get("contentDetails", {})
    thumbs = sn.get("thumbnails", {})
    thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url", "")
    secs = parse_duration(cd.get("duration"))
    return {
        "id": it["id"] if isinstance(it.get("id"), str) else it["id"].get("videoId", ""),
        "title": sn.get("title", ""),
        "channel": sn.get("channelTitle", ""),
        "channel_id": sn.get("channelId", ""),
        "published": (sn.get("publishedAt") or "")[:10],
        "desc": (sn.get("description") or "").strip(),
        "thumb": thumb,
        "secs": secs,
        "views": int(st_.get("viewCount") or 0),
        "url": "https://www.youtube.com/watch?v=" + (it["id"] if isinstance(it.get("id"), str) else it["id"].get("videoId", "")),
    }


def videos(ids):
    """Fetch details for up to 50 ids. Returns {id: video}."""
    ids = [i for i in ids if i][:50]
    if not ids:
        return {}
    d = _call("videos", part="snippet,statistics,contentDetails", id=",".join(ids), maxResults=50)
    return {v["id"]: v for v in map(_video_obj, d.get("items", [])) if v["id"]}


def channel(handle_or_id):
    if handle_or_id.startswith("UC") and len(handle_or_id) > 20:
        d = _call("channels", part="snippet,statistics,contentDetails", id=handle_or_id)
    else:
        h = handle_or_id if handle_or_id.startswith("@") else "@" + handle_or_id
        d = _call("channels", part="snippet,statistics,contentDetails", forHandle=h)
    items = d.get("items", [])
    if not items:
        return None
    it = items[0]
    return {"id": it["id"], "title": it["snippet"]["title"],
            "subs": int(it.get("statistics", {}).get("subscriberCount") or 0),
            "videos": int(it.get("statistics", {}).get("videoCount") or 0),
            "uploads": it["contentDetails"]["relatedPlaylists"]["uploads"],
            "desc": it["snippet"].get("description", "")}


def channel_videos(channel_id, limit=50):
    """Newest uploads for a channel (2 calls max)."""
    ch = channel(channel_id)
    if not ch:
        return []
    ids, token = [], None
    while len(ids) < limit:
        d = _call("playlistItems", part="contentDetails", playlistId=ch["uploads"],
                  maxResults=min(50, limit - len(ids)), pageToken=token)
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        token = d.get("nextPageToken")
        if not token:
            break
    return list(videos(ids).values())


def search_videos(q, max_results=25, order="relevance"):
    """Search costs 100 units - cached for a week."""
    d = _call("search", part="snippet", type="video", q=q, maxResults=max_results, order=order,
              relevanceLanguage="en", regionCode="US")
    ids = [it["id"]["videoId"] for it in d.get("items", []) if it.get("id", {}).get("videoId")]
    return list(videos(ids).values())


def playlist_videos(playlist_id, limit=100):
    ids, token = [], None
    while len(ids) < limit:
        d = _call("playlistItems", part="contentDetails", playlistId=playlist_id,
                  maxResults=min(50, limit - len(ids)), pageToken=token)
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        token = d.get("nextPageToken")
        if not token:
            break
    return list(videos(ids).values())


def verify_url(url):
    """Check a YouTube URL exists. Returns (ok, canonical_id_or_None, kind)."""
    try:
        u = urllib.parse.urlparse(url)
        path = u.path.strip("/")
        if "youtu.be" in u.netloc:
            vid = path.split("/")[0]
            return (bool(videos([vid])), vid, "video")
        if path.startswith("@"):
            ch = channel(path.split("/")[0])
            return (bool(ch), ch["id"] if ch else None, "channel")
        if path.startswith("channel/"):
            ch = channel(path.split("/")[1])
            return (bool(ch), ch["id"] if ch else None, "channel")
        if path.startswith("playlist"):
            pid = urllib.parse.parse_qs(u.query).get("list", [""])[0]
            d = _call("playlists", part="snippet", id=pid)
            return (bool(d.get("items")), pid, "playlist")
        if path.startswith("watch"):
            vid = urllib.parse.parse_qs(u.query).get("v", [""])[0]
            return (bool(videos([vid])), vid, "video")
        if path.startswith("embed") or path.startswith("v/"):
            vid = path.split("/")[1]
            return (bool(videos([vid])), vid, "video")
    except ValueError:
        pass
    return (False, None, "unknown")


def status():
    """Cheap health check for the UI (no quota spent when cached)."""
    if not available():
        return {"ok": False, "reason": "no key", "quota": 0}
    try:
        ch = channel("@statquest")
        return {"ok": bool(ch), "reason": "" if ch else "channel lookup returned nothing",
                "quota": quota_used_today()}
    except YouTubeError as e:
        return {"ok": False, "reason": str(e), "quota": quota_used_today()}
