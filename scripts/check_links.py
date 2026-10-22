"""Verify every resource URL in lib/resources.py.

YouTube links go through the Data API (cheap, cached); everything else gets a real HTTP
request. Output: data/link_check.json, consumed by the Resources page.

Run:  .venv\\Scripts\\python.exe scripts\\check_links.py
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import youtube as yt          # noqa: E402
from lib.paths import DATA_DIR         # noqa: E402
from lib.resources import RESOURCES    # noqa: E402

OUT = os.path.join(DATA_DIR, "link_check.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Hosts that serve 403/404 to anything that isn't a real browser session. A status code from
# these says nothing about whether the page exists, so they are reported as unverified.
BOTWALLED = ("kaggle.com", "leetcode.com", "glassdoor.com", "economist.com",
             "sec.gov", "bogleheads.org", "imf.org", "bloomberg.com", "wsj.com",
             "linkedin.com", "twitter.com", "x.com", "reddit.com",
             # real, high-value sites that refuse automated probes (403/401/400/TLS/timeout)
             "capitalallocators.com", "hackerrank.com", "fred.stlouisfed.org",
             "stanford.edu", "msci.com", "epchan.blogspot.com")


def http_check(url, timeout=15):
    """(ok, status, note). HEAD first, then a ranged GET for servers that refuse HEAD."""
    host = urllib.parse.urlparse(url).netloc.lower()
    walled = any(h in host for h in BOTWALLED)
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={
                "User-Agent": UA, "Accept": "text/html,*/*",
                **({"Range": "bytes=0-2048"} if method == "GET" else {}),
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return True, r.status, "reachable"
        except urllib.error.HTTPError as e:
            if walled:
                return None, e.code, "bot-walled (cannot verify)"
            if e.code in (400, 401, 403, 429, 999, 503):
                return None, e.code, "server refused probe (cannot verify)"
            if e.code in (301, 302, 307, 308):
                return True, e.code, "redirect"
            if e.code == 405 and method == "HEAD":
                continue
            return False, e.code, str(e.reason)
        except Exception as e:
            if method == "HEAD":
                continue
            if walled or host.endswith("ecb.europa.eu"):
                return None, 0, "TLS/bot protection (cannot verify)"
            if "timed out" in str(e).lower():
                return None, 0, "timeout (host did not answer)"
            return False, 0, type(e).__name__
    return False, 0, "unreachable"


def check(key, r):
    url = r["url"]
    rec = {"title": r["title"], "track": r.get("track"), "type": r.get("type"),
           "checked_at": datetime.now().isoformat(timespec="seconds")}
    if "youtube.com" in url or "youtu.be" in url:
        try:
            ok, vid, kind = yt.verify_url(url)
            rec.update(ok=ok, kind=kind, status=200 if ok else 404,
                       note=f"YouTube {kind} resolved" if ok else "YouTube object not found")
            if ok and kind == "channel" and vid:
                ch = yt.channel(vid)
                if ch:
                    rec["resolved_title"] = ch["title"]
                    rec["subs"] = ch["subs"]
            rec["spent_api"] = True
        except yt.YouTubeError as e:
            rec.update(ok=None, kind="youtube", status=0, note=str(e))
    else:
        ok, status, note = http_check(url)
        rec.update(ok=ok, kind="http", status=status, note=note)
    rec["url"] = url
    return key, rec


def main():
    print(f"checking {len(RESOURCES)} resources...", flush=True)
    out = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = [pool.submit(check, k, r) for k, r in RESOURCES.items()]
        for i, f in enumerate(futs, 1):
            k, rec = f.result()
            out[k] = rec
            if i % 40 == 0:
                print(f"  {i}/{len(RESOURCES)}", flush=True)

    payload = {"checked_at": datetime.now().isoformat(timespec="seconds"), "links": out}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)

    ok = [k for k, v in out.items() if v["ok"] is True]
    blocked = [k for k, v in out.items() if v["ok"] is None]
    dead = [k for k, v in out.items() if v["ok"] is False]
    print(f"\nreachable {len(ok)} · blocked/unknown {len(blocked)} · dead {len(dead)}")
    if dead:
        print("\nDEAD:")
        for k in dead:
            v = out[k]
            print(f"  {v['status']:>4}  {v['url']}  ({v['title']})")
    if blocked:
        print("\nUNVERIFIED:")
        for k in blocked:
            v = out[k]
            print(f"  {v['status']:>4}  {v['url']}  ({v['note']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
