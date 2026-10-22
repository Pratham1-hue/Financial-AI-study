import streamlit as st
import pandas as pd
import plotly.express as px
from lib.ui import hero, section, inject_css, xp_level, progress_bar
from lib.storage import load_progress, streak_days

inject_css()
hero("Progress & Analytics", "Track your journey to the NYC offer.")

progress = load_progress()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("XP", progress["xp"])
with c2:
    lvl, title = xp_level(progress["xp"])
    st.metric("Level", f"{lvl} - {title}")
with c3:
    st.metric("Streak", f"{streak_days(progress)} days")
with c4:
    st.metric("Study days", len(progress["study_days"]))

section("Quiz performance")
if progress["quiz_scores"]:
    rows = []
    for qid, info in progress["quiz_scores"].items():
        rows.append({"quiz": qid, "best": info.get("best", 0), "last": info.get("last", 0), "attempts": info.get("attempts", 0)})
    df = pd.DataFrame(rows)
    fig = px.bar(df, x="quiz", y="best", title="Best quiz scores (%)", color="best",
                 color_continuous_scale="Teal")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.caption("No quiz data yet.")

section("Exam performance")
if progress["exam_scores"]:
    rows = []
    for eid, info in progress["exam_scores"].items():
        rows.append({"exam": eid, "score": info.get("score", 0), "at": info.get("at", "")})
    df = pd.DataFrame(rows)
    fig = px.bar(df, x="exam", y="score", title="Exam scores (%)", color="score",
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.caption("No exam data yet.")

section("Study activity (last 30 days)")
if progress["study_days"]:
    days = sorted(progress["study_days"].keys())
    df = pd.DataFrame({"date": days, "sessions": [progress["study_days"][d] for d in days]})
    df["date"] = pd.to_datetime(df["date"])
    fig = px.line(df.tail(30), x="date", y="sessions", title="Study sessions per day", markers=True)
    st.plotly_chart(fig, width="stretch")
else:
    st.caption("Log study days by visiting the app daily.")

section("Weak topics")
weak = progress.get("weak_topics", [])
if weak:
    for t in weak:
        st.markdown(f"- {t}")
else:
    st.caption("No weak topics identified yet. Take quizzes.")

section("Completed tasks")
tasks = progress.get("completed_tasks", [])
st.caption(f"{len(tasks)} tasks completed")
if tasks:
    st.write(tasks)

section("Reset progress")
if st.button("Reset all progress (danger)"):
    from lib.storage import save_progress, fresh_progress
    save_progress(fresh_progress())
    st.success("Progress reset.")
    st.rerun()