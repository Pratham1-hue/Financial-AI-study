from datetime import datetime

import streamlit as st

from lib import gates
from lib.content import MODULES, TRACKS
from lib.storage import load_progress, log_activity, save_progress
from lib.ui import hero, inject_css, section

inject_css()
hero("Mastery <em>gates</em>", "No conveyor belt. You move to the next topic only when you've proven mastery of this one - "
     "the same principle Launch School builds its entire curriculum on.",
     eyebrow="Mastery-based learning · local mastery before integration", quote_tags=["focus", "grind"])

progress = load_progress()
statuses = {m["id"]: gates.status(progress, m["id"]) for m in MODULES}
count = lambda s: sum(1 for v in statuses.values() if v == s)

m = st.columns(4)
m[0].metric("Mastered", f"{count('Mastered')}/{len(MODULES)}")
m[1].metric("Ready to attempt", count("Ready"))
m[2].metric("Not yet (cooling down)", count("Not yet"))
m[3].metric("Locked", count("Locked"))

with st.expander("How the gates work", icon=":material/info:"):
    st.markdown(
        f"- **Prerequisites first.** A module unlocks only when the modules it builds on are mastered (atomic concepts before integrated ones).\n"
        f"- **Two parts.** Multiple choice (pass at {gates.MCQ_PASS}%+) and an oral-style *teach-back*: you explain two core ideas in writing "
        f"({gates.ORAL_MIN_CHARS}+ characters each), then honestly check them against a rubric (pass at {gates.ORAL_PASS}%+ of points).\n"
        "- **\"Not yet\", never \"fail\".** First Not yet = 24h wait before retaking. Second Not yet = 72h wait, and that module's drill cards reset "
        "to box 1 so you rebuild the foundation.\n"
        "- **No timelines inside a gate.** The 16-week plan sets your pace; the gates set the standard. If they disagree, the gate wins."
    )

ICON = {"Mastered": ":material/workspace_premium:", "Ready": ":material/lock_open:",
        "Not yet": ":material/hourglass_top:", "Locked": ":material/lock:"}

active = st.session_state.get("gate_attempt")

if not active:
    section("Skill tree")
    for tr, info in TRACKS.items():
        mods = [mm for mm in MODULES if mm["track"] == tr]
        if not mods:
            continue
        st.markdown(f"**{info['name']}**")
        cols = st.columns(3)
        for i, mod in enumerate(mods):
            s = statuses[mod["id"]]
            with cols[i % 3]:
                with st.container(border=True, height="stretch"):
                    st.markdown(f"{ICON[s]} **{mod['id']} · {mod['title']}**")
                    if s == "Mastered":
                        st.caption(f"Mastered on {progress['gates'][mod['id']]['passed_on']}")
                    elif s == "Locked":
                        st.caption("Needs: " + ", ".join(f"{p} {gates.title(p)}" for p in gates.missing_prereqs(progress, mod["id"])))
                    elif s == "Not yet":
                        left = gates.cooldown_left(progress, mod["id"])
                        h, rem = divmod(int(left.total_seconds()), 3600)
                        st.caption(f"Retake in {h}h {rem // 60}m. Use the time: drill, re-study, re-explain.")
                    else:
                        g = progress.get("gates", {}).get(mod["id"], {})
                        st.caption(f"{len(gates.mcq_for(mod['id']))} MCQ + 2 teach-backs · attempts so far: {g.get('attempts', 0)}")
                        if st.button("Attempt gate", key=f"start_{mod['id']}", type="primary", icon=":material/flag:"):
                            st.session_state["gate_attempt"] = {"mid": mod["id"], "phase": "answer",
                                                                "started": datetime.now().isoformat()}
                            st.rerun()
else:
    mid = active["mid"]
    mod = next(mm for mm in MODULES if mm["id"] == mid)
    mcq = gates.mcq_for(mid)
    oral = gates.ORAL[mid]
    section(f"Gate · {mid} {mod['title']}")

    if active["phase"] == "answer":
        st.caption("Closed book. No notes, no AI, no tabs. Treat this exactly like the real interview it simulates.")
        with st.form(f"gate_{mid}"):
            st.markdown("**Part 1 · Multiple choice**")
            picks = []
            for i, q in enumerate(mcq, 1):
                picks.append(st.radio(f"Q{i}. {q['q']}", q["opts"], index=None, key=f"g_{mid}_{q['id']}"))
            st.markdown("**Part 2 · Teach-back** (explain as if to a smart interviewer who will probe every gap)")
            texts = [st.text_area(prompt, key=f"o_{mid}_{j}", height=150) for j, (prompt, _) in enumerate(oral)]
            if st.form_submit_button("Submit for grading", type="primary"):
                if any(p is None for p in picks):
                    st.error("Answer every multiple-choice question.")
                elif any(len(t.strip()) < gates.ORAL_MIN_CHARS for t in texts):
                    st.error(f"Each teach-back needs {gates.ORAL_MIN_CHARS}+ characters. Vague answers don't pass real interviews either.")
                else:
                    correct = sum(1 for q, p in zip(mcq, picks) if p == q["opts"][q["ans"]])
                    active.update(phase="rubric", mcq_pct=round(100 * correct / len(mcq)), texts=texts,
                                  mcq_review=[(q["q"], p, q["opts"][q["ans"]], q["exp"]) for q, p in zip(mcq, picks)])
                    st.rerun()
    else:
        st.metric("Multiple choice", f"{active['mcq_pct']}%", help=f"Pass mark {gates.MCQ_PASS}%")
        with st.expander("Review multiple choice"):
            for qtext, pick, right, exp in active["mcq_review"]:
                (st.success if pick == right else st.error)(f"{qtext} - you: {pick} | correct: {right}")
                st.caption(exp)
        st.markdown("**Grade your teach-backs honestly.** Tick only points you clearly and correctly explained.")
        hit = total = 0
        for j, (prompt, points) in enumerate(oral):
            with st.container(border=True):
                st.markdown(f"**{prompt}**")
                st.markdown(f"> {active['texts'][j]}")
                for k, p in enumerate(points):
                    hit += st.checkbox(p, key=f"r_{mid}_{j}_{k}")
                    total += 1
        oral_pct = round(100 * hit / total)
        st.progress(oral_pct / 100, text=f"Teach-back: {oral_pct}% (pass {gates.ORAL_PASS}%)")
        c1, c2 = st.columns(2)
        if c1.button("Finalize result", type="primary", icon=":material/gavel:", width="stretch"):
            passed, reset = gates.record_attempt(progress, mid, active["mcq_pct"], oral_pct,
                                                 {"teach_back": active["texts"]})
            if passed:
                progress["xp"] = progress.get("xp", 0) + 150
            save_progress(progress)
            log_activity(progress, "gate")
            if passed:
                log_activity(progress, "gate_pass")
            st.session_state["gate_result"] = (mid, passed, reset)
            st.session_state.pop("gate_attempt")
            st.rerun()
        if c2.button("Abandon attempt", width="stretch"):
            st.session_state.pop("gate_attempt")
            st.rerun()

res = st.session_state.pop("gate_result", None)
if res:
    mid, passed, reset = res
    if passed:
        st.balloons()
        st.success(f"{mid} mastered. New modules may have unlocked in the skill tree.", icon=":material/workspace_premium:",
                   title="Gate passed")
    else:
        st.warning(("Second Not yet: 72-hour wait, and this module's drill cards were reset to box 1. "
                    if reset else "24-hour wait before you can retake. ")
                   + "Re-study the gaps you couldn't explain - that's exactly where the learning is.",
                   icon=":material/hourglass_top:", title="Not yet")