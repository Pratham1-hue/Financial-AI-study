import time
from datetime import date

import streamlit as st

from lib.challenges import CH_BY_ID, CHALLENGES, TRACKS, grade, toy_of_the_day
from lib.storage import load_progress, log_activity, save_progress
from lib.ui import hero, inject_css, section

HINT1 = (1, 5 * 60)      # attempts, seconds
HINT2 = (3, 12 * 60)
SOLUTION_SECS, SOLUTION_ATTEMPTS = 20 * 60, 3

inject_css()
hero("Challenge <em>lab</em>", "Auto-graded challenges with hidden tests - the Le Wagon / Hack Reactor model. "
     "Struggle first: hints unlock with effort, the solution only after 20 minutes and 3 honest attempts.",
     eyebrow="Deliberate practice · productive struggle", quote_tags=["focus"])

progress = load_progress()
state = progress.setdefault("challenges", {})
solved_ids = {k for k, v in state.items() if v.get("solved")}

toy = toy_of_the_day()
c1, c2 = st.columns([3, 1], vertical_alignment="center")
with c1:
    st.markdown(f"**Toy problem of the day:** {toy['title']} · {toy['track']} · {toy['diff']}"
                + ("  :material/check_circle: solved" if toy["id"] in solved_ids else ""))
    st.caption("Hack Reactor-style morning warm-up: do this before anything else today.")
with c2:
    if st.button("Open toy problem", type="primary", width="stretch", icon=":material/bolt:"):
        st.session_state["lab_pick"] = toy["id"]
        st.rerun()

m = st.columns(len(TRACKS) + 1)
m[0].metric("Solved", f"{len(solved_ids)}/{len(CHALLENGES)}")
for i, tr in enumerate(TRACKS, 1):
    tot = [c for c in CHALLENGES if c["track"] == tr]
    m[i].metric(tr, f"{sum(1 for c in tot if c['id'] in solved_ids)}/{len(tot)}")

track = st.segmented_control("Track", ["All"] + TRACKS, default="All", key="lab_track") or "All"
pool = [c for c in CHALLENGES if track == "All" or c["track"] == track]
labels = {c["id"]: f"{'✅ ' if c['id'] in solved_ids else ''}{c['title']} · {c['diff']}" for c in pool}
default_id = st.session_state.get("lab_pick")
ids = [c["id"] for c in pool]
idx = ids.index(default_id) if default_id in ids else 0
cid = st.selectbox("Challenge", ids, index=idx, format_func=lambda i: labels[i])
st.session_state["lab_pick"] = cid
ch = CH_BY_ID[cid]

cs = state.get(cid)
if cs is None:
    cs = state[cid] = {"first_seen": time.time(), "attempts": 0, "solved": None}
    save_progress(progress)
elapsed = time.time() - cs["first_seen"]
attempts = cs["attempts"]

section(ch["title"])
st.caption(f"{ch['track']} · {ch['diff']} · {len(ch['tests'])} hidden tests")
st.markdown(ch["prompt"])

code = st.text_area("Your solution", value=ch["starter"], height=300, key=f"code_{cid}")
run = st.button("Run tests", type="primary", icon=":material/science:")

if run:
    with st.spinner("Grading..."):
        results, out, err = grade(code, ch)
    cs["attempts"] += 1
    attempts = cs["attempts"]
    log_activity(progress, "code")
    if results is None:
        st.error("Your code crashed before the tests could run.", icon=":material/bug_report:")
        if err:
            st.code(err[-2000:], language="text")
    else:
        passed = sum(1 for r in results if r[1])
        for name, ok, msg in results:
            (st.success if ok else st.error)(f"{'PASS' if ok else 'FAIL'} · {name}" + (f" - {msg}" if msg else ""))
        if out.strip():
            st.code(out[-2000:], language="text")
        if passed == len(results):
            first_time = not cs.get("solved")
            if first_time:
                cs["solved"] = date.today().isoformat()
                progress["xp"] = progress.get("xp", 0) + {"Easy": 20, "Medium": 40, "Hard": 70}[ch["diff"]]
                log_activity(progress, "challenge")
                st.balloons()
            st.success("All tests pass. Now do the review step: compare with the reference below and note one improvement.",
                       icon=":material/task_alt:", title="Solved")
        else:
            st.warning(f"{passed}/{len(results)} tests passing. Read the failure, form a hypothesis, change one thing.",
                       icon=":material/troubleshoot:")
    save_progress(progress)

# ---------- the 20-minute rule ----------
section("Hints & solution")
mins = int(elapsed // 60)
st.caption(f"Time on this challenge: {mins} min · attempts: {attempts}")


def unlocked(rule):
    return attempts >= rule[0] or elapsed >= rule[1]


solved = bool(cs.get("solved"))
for i, (rule, hint) in enumerate([(HINT1, ch["hints"][0]), (HINT2, ch["hints"][1])], 1):
    if solved or unlocked(rule):
        with st.expander(f"Hint {i}", icon=":material/lightbulb:"):
            st.markdown(hint)
    else:
        st.caption(f":material/lock: Hint {i} unlocks after {rule[0]} failed run(s) or {rule[1] // 60} minutes.")
if solved or (elapsed >= SOLUTION_SECS and attempts >= SOLUTION_ATTEMPTS):
    with st.expander("Reference solution", icon=":material/menu_book:"):
        st.code(ch["solution"], language="python")
else:
    left = max(0, SOLUTION_SECS - elapsed) // 60
    st.caption(f":material/lock: Solution unlocks after 20 minutes *and* {SOLUTION_ATTEMPTS} attempts "
               f"({int(left)} min and {max(0, SOLUTION_ATTEMPTS - attempts)} attempt(s) to go). "
               "The struggle is the workout - looking early skips the rep.")