"""Smoke test for the FastAPI layer. Run: .venv\\Scripts\\python.exe scripts\\api_smoke.py"""
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Never touch the real study record. Unless a data dir is supplied explicitly,
# run against a throwaway directory (the old script mutated data/progress.json).
if not (os.environ.get("LAKSH_DATA_DIR") or os.environ.get("DEVI_DATA_DIR")):
    os.environ["LAKSH_DATA_DIR"] = tempfile.mkdtemp(prefix="laksh-smoke-")
    print(f"data dir: {os.environ['LAKSH_DATA_DIR']} (temporary)")

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

c = TestClient(app)


def show(label, value):
    print(f"{label}: {value}")


show("health", c.get("/api/health").json())
show("session", c.get("/api/session").json())

b = c.get("/api/bootstrap").json()
show("plan", f"day {b['plan']['day']} - {b['plan']['assignment'][:60]}")
show("metrics", {k: b["metrics"][k] for k in ("day_score", "streak", "xp", "level_title")})
show("stock", f"{b['stock']['symbol']} {b['stock']['price']} {b['stock']['rating']}")
show("loop", [f"{x['name']}{'✓' if x['done'] else '·'}" for x in b["loop"]])

mods = c.get("/api/modules?track=ai").json()
show("ai modules", len(mods))
m = c.get("/api/modules/A1").json()
show("A1", f"{m['title']} | videos {len(m['videos'])} | resources {len(m['resources'])} | watch {m['watch']}")

f = c.get("/api/focus").json()
show("focus", f"{f['state']['status']} {f['state']['mode']} rem={f['state']['remaining']} ladder={len(f['rank']['ladder'])}")
s = c.post("/api/focus/start", json={"mode": "Pomodoro", "subject": "Python & SQL", "label": "smoke"}).json()
show("start", f"{s['state']['status']} rem={s['state']['remaining']} label={s['state']['label']}")
show("pause", c.post("/api/focus/pause").json()["state"]["status"])
# Resume sends no body on purpose: this used to 422.
show("resume", c.post("/api/focus/start").json()["state"]["status"])
show("skip", c.post("/api/focus/skip").json()["state"]["phase"])
show("reset", c.post("/api/focus/reset").json()["state"]["status"])

bank = c.get("/api/quiz/bank").json()
show("bank", f"{len(bank['questions'])} questions, leaks ans? {'ans' in bank['questions'][0]}")
qids = [q["id"] for q in bank["questions"][:10]]
sub = c.post("/api/quiz/submit",
             json={"quiz_id": "smoke", "qids": qids, "answers": {"f1_1": 0, "f1_2": 2}}).json()
show("submit", f"{sub['score']}/{sub['total']} = {sub['pct']}% review={len(sub['review'])}")

dr = c.get("/api/drill").json()
show("drill", f"due={dr['due_count']} new={dr['new_count']} retention={dr['retention']}")
if dr["new"]:
    g = c.post("/api/drill/grade", json={"qid": dr["new"][0]["id"], "correct": True}).json()
    show("drill grade", g["card"])

show("gates", len(c.get("/api/gates").json()))
gd = c.get("/api/gates/F1").json()
show("gate F1", f"{gd['status']} mcq={len(gd['mcq'])} oral={len(gd['oral'])} pass={gd['pass_marks']}")

r = c.post("/api/desk/new", json={"seed": 42}).json()
show("desk new", f"{r['round_id']} tick={r['tick']} quotes={list(r['quotes'])} cash={r['cash']}")
t = c.post(f"/api/desk/{r['round_id']}/trade", json={"sym": "NVX", "qty": 100}).json()
show("trade", f"ok={t['ok']} {t['message']} equity={t['equity']} gross={t['gross']}")
bk = c.get(f"/api/desk/{r['round_id']}?sym=NVX").json()
show("book", f"bids={len(bk.get('book', {}).get('bids', []))} asks={len(bk.get('book', {}).get('asks', []))}")

lm = c.get("/api/labs").json()
show("labs", f"sql={len(lm['sql'])} credit_feats={len(lm['credit']['features'])}")
sql = "SELECT name, market_cap_m FROM companies WHERE sector = 'Technology' ORDER BY market_cap_m DESC"
sq = c.post("/api/labs/sql/check", json={"task_id": "sql1", "sql": sql, "attempt": 1}).json()
show("sql1", f"correct={sq['ok']} rows={sq.get('rows')} expected={sq.get('expected_rows')}")
bad = c.post("/api/labs/sql/check", json={"task_id": "sql1", "sql": "SELECT * FROM companies"}).json()
show("sql1 wrong", f"correct={bad['ok']} err={(bad.get('error') or '')[:60]}")
val = c.post("/api/labs/valuation", json={}).json()
show("valuation case", f"seed={val['case']['seed']} wacc={round(val['case']['wacc'], 3)}")

# --- integrity + new surfaces
eq = c.get("/api/exams/E1").json()["questions"]
one = c.post("/api/exams/E1/submit", json={"answers": {eq[0]["id"]: 0}}).json()
show("exam partial", f"{one['score']}/{one['total']} = {one['pct']}% (full set graded)")
show("resources", c.get("/api/resources?limit=1000").json()["total"])
na = c.get("/api/does-not-exist")
show("api 404", f"{na.status_code} {na.headers.get('content-type')}")
show("debrief short", c.post("/api/debrief", json={"concept": "x", "explain": "too short", "first": "y"}).status_code)
db = c.post("/api/debrief", json={"concept": "Duration", "explain": "d" * 220,
                                 "gaps": "sign", "win": "shipped", "first": "9am", "energy": 4}).json()
show("debrief", f"is_new={db['is_new']} +{db['xp_gain']} xp={db['xp']}")
show("backup inspect", c.get("/api/backup/inspect").json())

print("\nSMOKE OK")
