import time
from datetime import date, datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from lib import focus
from lib.nyc import RANKS, rank_for
from lib.quotes import break_tip, rotating_quote
from lib.storage import load_profile, load_progress
from lib.ui import glass_card, hero, inject_css, quote_inline, rank_ladder, section, timer_ring

inject_css()
hero(
    "Lock-in <em>mode</em>",
    "The city never sleeps. Neither does your ambition. Phone away, one tab, full send.",
    eyebrow="Focus · Pomodoro · Deep work",
    quote_tags=["focus"],
)

state = focus.load_state()
active = state["status"] in ("running", "paused")
running = state["status"] == "running"
profile = load_profile()

left, right = st.columns([3, 2], gap="large")

# Setup first, so the timer below reads the freshly saved state.
with right:
    with st.container(border=True):
        st.markdown("**Session setup**")
        if active:
            st.caption(":material/lock: Settings are locked while a session is active.")
        mode = st.segmented_control("Mode", list(focus.MODES), default=state["mode"],
                                    disabled=active, key="li_mode") or state["mode"]
        st.caption(focus.MODES[mode]["desc"])
        custom = dict(state["custom"])
        if mode == "Custom":
            c1, c2, c3 = st.columns(3)
            custom["focus"] = c1.number_input("Focus (min)", 5, 180, int(custom["focus"]), disabled=active)
            custom["short"] = c2.number_input("Short break", 1, 60, int(custom["short"]), disabled=active)
            custom["long"] = c3.number_input("Long break", 1, 90, int(custom["long"]), disabled=active)
        subject = st.selectbox("Subject", focus.SUBJECTS,
                               index=focus.SUBJECTS.index(state["subject"]) if state["subject"] in focus.SUBJECTS else 0,
                               disabled=active)
        label = st.text_input("What are you locking in on?", value=state["label"], disabled=active,
                              placeholder="e.g. Karpathy makemore pt. 2, DCF model for NVDA")
        t1, t2 = st.columns(2)
        auto = t1.toggle("Auto-start breaks", value=state["auto_break"])
        sound = t2.toggle("Chime on finish", value=state["sound"])

        changed = False
        if not active and (mode, custom, subject, label) != (state["mode"], state["custom"], state["subject"], state["label"]):
            state.update(mode=mode, custom=custom, subject=subject, label=label)
            changed = True
        if (auto, sound) != (state["auto_break"], state["sound"]):
            state.update(auto_break=auto, sound=sound)
            changed = True
        if changed:
            focus.save_state(state)

    with st.container(border=True):
        st.markdown("**Lock-in rules**")
        st.checkbox("Phone in another room (or face-down on DND)", key="rule_phone")
        st.checkbox("One tab. Everything else closed.", key="rule_tab")
        st.checkbox("Water on the desk", key="rule_water")
        st.checkbox("I know exactly what this block is for", key="rule_goal")

    progress = load_progress()
    goal_min = int(profile.get("daily_hours", 6)) * 60
    today = focus.today_minutes(progress)
    with st.container(border=True):
        st.markdown("**Today's locked-in goal**")
        st.progress(min(1.0, today / max(goal_min, 1)),
                    text=f"{focus.fmt_hm(today)} of {focus.fmt_hm(goal_min)}")
        left_min = max(0, goal_min - today)
        if left_min == 0:
            st.success("Daily goal smashed. Manhattan is closer tonight.", icon=":material/emoji_events:")
        else:
            blocks = -(-left_min // focus.mode_cfg(state)["focus"])
            st.caption(f"{focus.fmt_hm(left_min)} to go - about {blocks} more {state['mode']} block(s).")

with left:
    @st.fragment(run_every=1 if running else None)
    def timer_panel():
        s = focus.load_state()
        ev = focus.tick(s)
        if ev:
            st.session_state["devi_event"] = ev
            st.rerun()

        rem, tot = focus.remaining(s), focus.total(s)
        phase, status = s["phase"], s["status"]
        what = s["label"] or s["subject"]
        if status == "idle":
            meta = f"{s['mode']} · {what}" if phase == "focus" else "Breathe. Then go again."
        elif status == "running":
            meta = f"{what} · ends {datetime.fromtimestamp(s['ends_at']).strftime('%H:%M')}"
        else:
            meta = what
        timer_ring(rem, tot, focus.PHASE_LABEL[phase], focus.PHASE_COLOR[phase],
                   focus.fmt_clock(rem), meta, paused=status == "paused")

        every = focus.mode_cfg(s)["every"]
        filled = s["cycles"] % every
        dots = " ".join(":material/radio_button_checked:" if i < filled else ":material/radio_button_unchecked:"
                        for i in range(every))
        st.markdown(f"<div style='text-align:center'>{dots}</div>", unsafe_allow_html=True)
        st.caption(f"<div style='text-align:center'>{filled}/{every} focus blocks until a long break · "
                   f"{s['cycles']} completed this run</div>", unsafe_allow_html=True)

        c = st.columns(4)
        if status == "running":
            if c[0].button("Pause", icon=":material/pause:", width="stretch"):
                focus.pause(s)
                st.rerun()
        else:
            start_label = "Resume" if status == "paused" else ("Lock in" if phase == "focus" else "Start break")
            if c[0].button(start_label, type="primary", icon=":material/play_arrow:", width="stretch"):
                focus.start(s)
                st.rerun()
        if c[1].button("Stop & log", icon=":material/stop_circle:", width="stretch",
                       disabled=not (phase == "focus" and status != "idle")):
            st.session_state["devi_event"] = {"type": "stopped", "minutes": focus.stop_and_log(s)}
            st.rerun()
        if c[2].button("Skip", icon=":material/skip_next:", width="stretch"):
            focus.skip(s)
            st.rerun()
        if c[3].button("Reset", icon=":material/restart_alt:", width="stretch"):
            focus.reset(s)
            st.rerun()

        slot = int(time.time() // 300)
        if phase == "focus":
            quote_inline(rotating_quote(slot, ["focus", "grind"]))
        else:
            st.info(break_tip(slot), icon=":material/self_improvement:")

    timer_panel()

# ---------- stats ----------
progress = load_progress()
section("Your locked-in hours")
hours = focus.total_hours(progress)
m = st.columns(5)
m[0].metric("Today", focus.fmt_hm(focus.today_minutes(progress)))
m[1].metric("Sessions today", focus.sessions_today(progress))
m[2].metric("Last 7 days", focus.fmt_hm(focus.week_minutes(progress)))
m[3].metric("All-time", f"{hours:.1f} h")
m[4].metric("Focus streak", f"{focus.focus_streak(progress)} days")

current, nxt, pct = rank_for(hours)
r1, r2 = st.columns([3, 2], gap="large")
with r1:
    to_next = f"{nxt[0] - hours:.1f} h to <b>{nxt[1]}</b>" if nxt else "Top of the skyline."
    glass_card("Your NYC rank", current[1], f"{current[2]}<br><br>{to_next}")
    st.progress(pct)

    log = progress.get("focus_log", [])
    if log:
        df = pd.DataFrame(log)
        df["date"] = pd.to_datetime(df["date"])
        start = pd.Timestamp(date.today() - timedelta(days=13))
        df = df[df["date"] >= start]
        agg = df.groupby(["date", "subject"], as_index=False)["minutes"].sum()
        agg["hours"] = agg["minutes"] / 60
        bars = alt.Chart(agg).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("date:T", title=None, scale=alt.Scale(domain=[start, pd.Timestamp(date.today())])),
            y=alt.Y("hours:Q", title="Hours"),
            color=alt.Color("subject:N", title="Subject"),
            tooltip=["date:T", "subject:N", alt.Tooltip("hours:Q", format=".1f")],
        )
        goal = alt.Chart(pd.DataFrame({"g": [goal_min / 60]})).mark_rule(
            color="#F5B942", strokeDash=[6, 4]).encode(y="g:Q")
        st.altair_chart((bars + goal).properties(height=260, title="Last 14 days (dashed = daily goal)"),
                        alt="Locked-in hours per day over the last 14 days, by subject")
    else:
        st.info("Finish your first block to start your chart. The first one is the hardest.",
                icon=":material/rocket_launch:")
with r2:
    st.markdown("**The ladder to Billionaires' Row**")
    rank_ladder(RANKS, current[1])

if progress.get("focus_log"):
    section("Session log")
    recent = pd.DataFrame(progress["focus_log"][::-1][:25])[["ended_at", "minutes", "subject", "label", "mode"]]
    st.dataframe(recent, hide_index=True, alt="Most recent focus sessions",
                 column_config={"ended_at": "Ended", "minutes": st.column_config.NumberColumn("Minutes"),
                                "subject": "Subject", "label": "Task", "mode": "Mode"})