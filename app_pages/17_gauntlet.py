import random
import time
from datetime import date

import pandas as pd
import streamlit as st

from lib.interview_bank import CATEGORIES, INTERVIEW_QUESTIONS, IQ_BY_ID
from lib.quotes import quote_for
from lib.storage import load_progress, log_activity
from lib.ui import hero, inject_css, quote_inline, section

inject_css()
hero("Interview <em>gauntlet</em>", "Timed, out-loud, no notes. Answer like it's the final round at your dream firm - "
     "then grade yourself against what a top candidate would say.",
     eyebrow="Final-round simulator", quote_tags=["grind", "nyc"])

progress = load_progress()
g = st.session_state.get("gauntlet")

if not g:
    with st.container(border=True):
        cats = st.pills("Categories", CATEGORIES, selection_mode="multi", default=CATEGORIES)
        c1, c2 = st.columns(2, vertical_alignment="bottom")
        rounds = c1.slider("Questions", 3, 10, 5)
        pressure = c2.toggle("Pressure mode (visible countdown)", value=True)
        st.caption("Tip: say your answer out loud while typing bullet points. Interviews are spoken, not written.")
        if st.button("Enter the gauntlet", type="primary", icon=":material/sports_martial_arts:", disabled=not cats):
            pool = [q["id"] for q in INTERVIEW_QUESTIONS if q["cat"] in cats]
            random.shuffle(pool)
            st.session_state["gauntlet"] = {"qids": pool[:rounds], "i": 0, "q_start": time.time(),
                                            "revealed": False, "elapsed": None, "pressure": pressure, "scores": []}
            st.rerun()
elif g["i"] >= len(g["qids"]):
    scores = g["scores"]
    avg = sum(scores) / len(scores) if scores else 0
    section("Gauntlet complete")
    c = st.columns(3)
    c[0].metric("Questions", len(scores))
    c[1].metric("Average self-score", f"{avg:.1f}/5")
    c[2].metric("Verdict", "Offer-ready" if avg >= 4.5 else "Strong" if avg >= 3.5 else "Needs reps")
    quote_inline(quote_for(f"gauntlet-{avg:.1f}", ["nyc", "finance"] if avg >= 4 else ["grind", "focus"]))
    if st.button("Run it again", type="primary", icon=":material/replay:"):
        st.session_state.pop("gauntlet")
        st.rerun()
else:
    qid = g["qids"][g["i"]]
    q = IQ_BY_ID[qid]
    st.progress(g["i"] / len(g["qids"]), text=f"Question {g['i'] + 1} of {len(g['qids'])} · {q['cat']}")
    with st.container(border=True):
        st.markdown(f"### {q['q']}")
        st.caption(f"Target time: {q['secs'] // 60}:{q['secs'] % 60:02d}")

        @st.fragment(run_every=1 if g["pressure"] and not g["revealed"] else None)
        def clock():
            state = st.session_state["gauntlet"]
            if state["revealed"]:
                el = state["elapsed"]
                st.caption(f"You took {int(el) // 60}:{int(el) % 60:02d}" + (" - overtime." if el > q["secs"] else "."))
                return
            rem = q["secs"] - (time.time() - state["q_start"])
            if rem > 0:
                st.progress(rem / q["secs"], text=f"{int(rem) // 60}:{int(rem) % 60:02d} left")
            else:
                st.error("Time's up. In the real room, you'd be wrapping up now.", icon=":material/timer_off:")

        clock()
        st.text_area("Your answer (bullet points while you speak)", key=f"ans_{g['i']}_{qid}", height=180,
                     disabled=g["revealed"])
        if not g["revealed"]:
            if st.button("Reveal what a top candidate says", type="primary", icon=":material/visibility:"):
                g["revealed"] = True
                g["elapsed"] = time.time() - g["q_start"]
                st.rerun()
        else:
            st.markdown("**Did you hit these?**")
            hits = sum(st.checkbox(p, key=f"hit_{g['i']}_{qid}_{j}") for j, p in enumerate(q["points"]))
            st.markdown("**Rate your answer honestly**")
            stars = st.feedback("stars", key=f"stars_{g['i']}_{qid}")
            if st.button("Lock score and continue", type="primary", icon=":material/arrow_forward:", disabled=stars is None):
                score = stars + 1
                progress.setdefault("interviews", []).append({
                    "date": date.today().isoformat(), "id": qid, "category": q["cat"], "score": score,
                    "hits": hits, "points": len(q["points"]), "overtime": g["elapsed"] > q["secs"]})
                progress["xp"] = progress.get("xp", 0) + 15 * score
                log_activity(progress, "interview")
                g["scores"].append(score)
                g.update(i=g["i"] + 1, q_start=time.time(), revealed=False, elapsed=None)
                st.rerun()
    if st.button("Abandon gauntlet", icon=":material/close:"):
        st.session_state.pop("gauntlet")
        st.rerun()

hist = progress.get("interviews", [])
if hist:
    section("Your interview record")
    df = pd.DataFrame(hist)
    c = st.columns(3)
    c[0].metric("Total reps", len(df))
    c[1].metric("Average score", f"{df['score'].mean():.1f}/5")
    c[2].metric("On time", f"{(~df['overtime']).mean() * 100:.0f}%")
    by = df.groupby("category", as_index=False)["score"].mean().rename(columns={"score": "avg score"})
    st.bar_chart(by, x="category", y="avg score", height=240)
    st.caption("60 reps at 4.5+ average is the bar the Mastery Index rewards.")