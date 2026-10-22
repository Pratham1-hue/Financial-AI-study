import streamlit as st
from lib.ui import hero, section, inject_css, progress_bar, badge
from lib.storage import load_progress, save_progress, mark_task, is_task_done
from lib.study_plan import WEEKS, PHASES, EXAMS

inject_css()
hero("Structured Study Plan", "16 weeks. Strict. No zero days. Finance + AI -> NYC.")

progress = load_progress()

section("The method: five blocks, one day")
st.caption("Every day has the same shape. The content changes, the loop does not. "
           "Skipping a block is visible in your score that night.")

blocks = [
    ("1 · Learn", "25 min", "One lesson. Pen in hand, no second tab.", "app_pages/04_learn.py", "school"),
    ("2 · Drill", "15 min", "Retrieval before it feels comfortable.", "app_pages/16_drill.py", "repeat"),
    ("3 · Build", "45 min", "Trade the tape, write the SQL, compute the valuation.", "app_pages/24_labs.py", "biotech"),
    ("4 · Prove", "15 min", "Quiz or gate. 80% or it didn't happen.", "app_pages/07_quizzes.py", "quiz"),
    ("5 · Debrief", "10 min", "Explain it in your own words, out loud.", "app_pages/15_mission.py", "flag"),
]
for col, (title, mins, body, path, icon) in zip(st.columns(5), blocks):
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(mins)
            st.markdown(body)
            st.page_link(path, label="Open", icon=f":material/{icon}:")

with st.expander("Weekly rhythm (and what 'done' means)"):
    st.markdown(
        "- **Mon-Fri:** one module per day, five blocks each. The module gate is the proof.\n"
        "- **Saturday:** build day. One artifact that exists outside your notes - a model, a memo, a backtest, a dashboard.\n"
        "- **Sunday:** one mock interview, one written review (what broke, what you avoided), then next week's plan.\n"
        "- **Done for the week** means: all five gates attempted, one artifact shipped, one interview scored, zero zero-days."
    )
    st.caption("Hands-on credit comes from the Desk and the Labs. Watching videos alone caps you at 60/100 - by design.")

section("The 16 weeks")

# Filters
phase_filter = st.segmented_control("Phase", options=["All"] + PHASES, default="All")
col1, col2 = st.columns([3, 1])
with col2:
    show_done = st.toggle("Show completed only", value=False)

weeks_to_show = WEEKS
if phase_filter and phase_filter != "All":
    weeks_to_show = [w for w in weeks_to_show if w["phase"] == phase_filter]

for w in weeks_to_show:
    wid = f"w{w['w']}"
    done = is_task_done(progress, wid)
    if show_done and not done:
        continue
    with st.container(border=True):
        head = st.columns([6, 2, 2])
        with head[0]:
            st.markdown(f"### Week {w['w']} - {w['title']}")
            st.caption(w["phase"])
        with head[1]:
            st.metric("Hours", w["hours"])
        with head[2]:
            if done:
                st.success("Done")
            else:
                if st.button("Mark week done", key=f"btn_{wid}"):
                    mark_task(progress, wid)
                    progress = load_progress()
                    st.rerun()
        st.markdown(f"**Focus:** {w['focus']}")
        with st.expander("Daily breakdown"):
            for d in w["days"]:
                st.markdown(f"- {d}")
        st.markdown(f"**Milestone:** {w['milestone']}")
        if w.get("exam"):
            st.warning(f"Exam at end of week: {w['exam']} ({EXAMS[w['exam']]['title']})")
        st.page_link("app_pages/08_exams.py", label=f"Go to exams", icon=":material/assignment:")

section("Phase summary")
for ph in PHASES:
    wks = [w for w in WEEKS if w["phase"] == ph]
    completed = sum(1 for w in wks if is_task_done(progress, f"w{w['w']}"))
    st.markdown(f"**{ph}**: {completed}/{len(wks)} weeks complete")
    progress_bar(completed, len(wks))