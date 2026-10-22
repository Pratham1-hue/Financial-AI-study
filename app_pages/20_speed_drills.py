import random
import time
from datetime import date

import pandas as pd
import streamlit as st

from lib.storage import load_progress, log_activity, save_progress
from lib.ui import hero, inject_css, quote_inline, section
from lib.quotes import quote_for

OPS = ["+", "−", "×", "÷"]

inject_css()
hero("Speed <em>drills</em>", "Timed mental math in the format trading firms use to screen candidates: "
     "addition 2-100, subtraction, multiplication 2-12 × 2-100, and division. Speed and accuracy under a clock.",
     eyebrow="Quant & trading screens", quote_tags=["focus"])


def make_question(rnd, ops):
    op = rnd.choice(ops)
    if op in ("+", "−"):
        a, b = rnd.randint(2, 100), rnd.randint(2, 100)
        return (f"{a} + {b}", a + b) if op == "+" else (f"{a + b} − {a}", b)
    a, b = rnd.randint(2, 12), rnd.randint(2, 100)
    return (f"{a} × {b}", a * b) if op == "×" else (f"{a * b} ÷ {a}", b)


progress = load_progress()
sd = st.session_state.get("speed")

if not sd:
    with st.container(border=True):
        c1, c2 = st.columns(2, vertical_alignment="bottom")
        minutes = c1.segmented_control("Duration", [2, 5, 8], default=8, format_func=lambda m: f"{m} min") or 8
        ops = c2.pills("Operations", OPS, selection_mode="multi", default=OPS)
        st.caption("Benchmark: about 80 correct in 8 minutes is the bar many candidates train toward. Type the answer and press Enter.")
        if st.button("Start the clock", type="primary", icon=":material/timer:", disabled=not ops):
            seed = random.randrange(10 ** 9)
            rnd = random.Random(seed)
            st.session_state["speed"] = {"start": time.time(), "dur": minutes * 60, "ops": ops, "seed": seed,
                                         "rnd_state": None, "correct": 0, "wrong": 0, "q": make_question(rnd, ops),
                                         "n": 1, "done": False}
            st.rerun()
elif not sd["done"]:
    @st.fragment(run_every=1)
    def clock():
        s = st.session_state["speed"]
        left = s["dur"] - (time.time() - s["start"])
        if left <= 0:
            s["done"] = True
            st.rerun()
        st.progress(max(0.0, left / s["dur"]), text=f"{int(left) // 60}:{int(left) % 60:02d} left · score {s['correct']}")

    clock()
    st.markdown(f"<div style='font-size:3.4rem;font-weight:800;text-align:center;font-variant-numeric:tabular-nums'>"
                f"{sd['q'][0]} = ?</div>", unsafe_allow_html=True)
    with st.form("answer", clear_on_submit=True, border=False):
        ans = st.text_input("Answer", label_visibility="collapsed", placeholder="Type and press Enter")
        submitted = st.form_submit_button("Submit", width="stretch")
    if submitted and ans.strip():
        try:
            ok = int(ans.strip()) == sd["q"][1]
        except ValueError:
            ok = False
        if ok:
            sd["correct"] += 1
            rnd = random.Random(sd["seed"] + sd["n"])
            sd["q"] = make_question(rnd, sd["ops"])
            sd["n"] += 1
        else:
            sd["wrong"] += 1
            st.toast("Not quite - try again.", icon=":material/close:")
        st.rerun()
    if st.button("Quit", icon=":material/close:"):
        st.session_state.pop("speed")
        st.rerun()
else:
    mins = sd["dur"] / 60
    rate = sd["correct"] / mins
    if not sd.get("saved"):
        progress.setdefault("speed_drills", []).append({"date": date.today().isoformat(), "score": sd["correct"],
                                                        "wrong": sd["wrong"], "minutes": mins, "ops": "".join(sd["ops"])})
        progress["xp"] = progress.get("xp", 0) + sd["correct"]
        save_progress(progress)
        log_activity(progress, "speed")
        sd["saved"] = True
    section("Time")
    c = st.columns(4)
    c[0].metric("Correct", sd["correct"])
    c[1].metric("Mistakes", sd["wrong"])
    c[2].metric("Per minute", f"{rate:.1f}")
    c[3].metric("8-min equivalent", f"{rate * 8:.0f}")
    quote_inline(quote_for(f"speed-{sd['correct']}", ["focus", "grind"]))
    if st.button("Again", type="primary", icon=":material/replay:"):
        st.session_state.pop("speed")
        st.rerun()

hist = progress.get("speed_drills", [])
if hist:
    section("Your speed curve")
    df = pd.DataFrame(hist)
    df["per_8_min"] = df["score"] / df["minutes"] * 8
    df["attempt"] = range(1, len(df) + 1)
    st.line_chart(df, x="attempt", y="per_8_min", height=220)
    st.caption(f"Best: {df['per_8_min'].max():.0f} per 8 minutes. Daily 8-minute reps compound fast.")