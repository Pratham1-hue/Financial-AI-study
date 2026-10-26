import os

import streamlit as st
from lib.env import get
from lib.ui import hero, section, inject_css
from lib.code_runner import run_python, STARTER_EXERCISES
from lib.storage import load_progress, save_progress

inject_css()
hero("Practice Console", "Write and run Python. ML, finance, quant - all in one sandbox.")

if get("ALLOW_CONSOLE", "1") == "0":
    st.info(
        "The Python console is disabled on this deployment because it executes code on the "
        "server. Set `LAKSH_ALLOW_CONSOLE=1` on a private instance to turn it back on.",
        icon=":material/lock:",
    )
    st.stop()

progress = load_progress()

ex = st.selectbox("Exercise", options=[e["title"] for e in STARTER_EXERCISES] + ["Blank"])
if ex == "Blank":
    starter = "# Write your Python code here\nprint('hello')\n"
    prompt = "Free-form scratchpad."
else:
    chosen = next(e for e in STARTER_EXERCISES if e["title"] == ex)
    starter = chosen["starter"]
    prompt = chosen["prompt"]

st.info(prompt)

code = st.text_area("Code", value=starter, height=320, key="console_code")

c1, c2, c3 = st.columns([1, 1, 4])
with c1:
    run = st.button("Run", type="primary", width="stretch")
with c2:
    if ex != "Blank":
        if st.button("Show solution", width="stretch"):
            chosen = next(e for e in STARTER_EXERCISES if e["title"] == ex)
            st.code(chosen["solution"], language="python")
with c3:
    timeout = st.slider("Timeout (s)", 5, 30, 15)

if run:
    with st.spinner("Running..."):
        out, err, rc = run_python(code, timeout=timeout)
    progress["practice_runs"] = progress.get("practice_runs", 0) + 1
    from lib.storage import log_activity
    log_activity(progress, "code")
    if rc == 0:
        st.success("Completed successfully")
    else:
        st.error(f"Exited with code {rc}")
    if out:
        st.markdown("**stdout**")
        st.code(out, language="text")
    if err:
        st.markdown("**stderr**")
        st.code(err, language="text")
    if not out and not err:
        st.caption("(no output)")

section("Tips")
st.markdown(
    "- Use `print()` to see output.\n"
    "- numpy, pandas, scikit-learn, scipy, matplotlib, plotly are available.\n"
    "- Infinite loops are killed after the timeout.\n"
    "- Save your best snippets in a .py file for your portfolio."
)