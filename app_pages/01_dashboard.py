import html
from datetime import date, datetime

import streamlit as st

from lib import accountability as acc
from lib import focus, gates
from lib.content import MODULES
from lib.nyc import NYC_COMP, rank_for
from lib.quotes import quote_of_the_day
from lib.storage import load_profile, load_progress, save_progress, streak_days
from lib.study_plan import PHASES, WEEKS
from lib.ui import glass_card, hero, inject_css, progress_bar, quote_card, section, xp_level

inject_css()
progress = load_progress()
profile = load_profile()

hour = datetime.now().hour
greet = ("Good morning" if 5 <= hour < 12 else "Good afternoon" if hour < 17
         else "Good evening" if hour < 22 else "The city's still awake")
hero(
    f"{greet}, <em>{html.escape(profile['name'])}</em>.",
    "The goal isn't to get a job. It's to become one of the best in finance and AI - "
    "the greatest job in New York City is just what happens next.",
    big=True,
    quote_tags=["nyc"],
)

# ---------- first run: one guided path, one obvious first move ----------
_lesson_done = bool(progress.get("onboarding_lesson")) or bool(progress.get("watched"))
_quiz_done = bool(progress.get("quiz_scores"))
if not (_lesson_done and _quiz_done and bool(progress.get("focus_log"))):
    _focus_done = bool(progress.get("focus_log")) or focus.today_minutes(progress) > 0
    _contract_done = bool(progress.get("contract"))
    _, _, _assignment = acc.todays_assignment(progress)
    _done_n = sum([_focus_done, _lesson_done, _quiz_done])
    _next = next((i for i, ok in enumerate([_focus_done, _lesson_done, _quiz_done]) if not ok), 3)
    _fs = focus.load_state()
    _busy = _fs["status"] in ("running", "paused")

    with st.container(border=True):
        st.markdown(f"#### Start here — your first session · {_done_n}/3")
        st.caption("One path. Every other page can wait. About 60–90 minutes, start to finish.")
        st.info(f"**Today's assignment** · {_assignment}", icon=":material/flag:")

        _a, _b = st.columns([5, 2])
        with _a:
            st.markdown(f"{'✅' if _focus_done else '**1 ·**'} **Lock in 25 minutes**")
            st.caption("One Pomodoro. Phone in another room, one tab, full send. The timer keeps running "
                       "while you study.")
        with _b:
            if _busy:
                if st.button("Resume the session", type="primary", icon=":material/play_arrow:",
                             width="stretch", key="ob_resume"):
                    st.switch_page("app_pages/12_lock_in.py")
            elif not _focus_done:
                if st.button("Start the block", type="primary", icon=":material/bolt:",
                             width="stretch", key="ob_start"):
                    _s = focus.load_state()
                    _s.update(mode="Pomodoro", subject="Python & SQL", label="A1 · Python basics")
                    focus.start(_s)
                    st.switch_page("app_pages/12_lock_in.py")
            else:
                st.markdown(":material/check_circle: **Done**")

        _a, _b = st.columns([5, 2])
        with _a:
            st.markdown(f"{'✅' if _lesson_done else '**2 ·**'} **Learn — Python basics**")
            st.caption("Kaggle's interactive Python course, Lesson 1: ~30 min, runs in your browser. "
                       "Do it inside the 25-minute block from step 1.")
        with _b:
            if not _lesson_done:
                st.link_button("Open Kaggle Python", "https://www.kaggle.com/learn/python",
                               icon=":material/open_in_new:", width="stretch")
                if st.button("Mark Lesson 1 done", width="stretch", key="ob_lesson"):
                    progress["onboarding_lesson"] = True
                    save_progress(progress)
                    st.rerun()
            else:
                st.markdown(":material/check_circle: **Done**")

        _a, _b = st.columns([5, 2])
        with _a:
            st.markdown(f"{'✅' if _quiz_done else '**3 ·**'} **Prove it — 5 quick questions**")
            st.caption("Instant feedback on Python basics. 80% is mastery. This is how the app knows it stuck.")
        with _b:
            if not _quiz_done:
                if st.button("Start the quiz", type="primary" if _next == 2 else "secondary",
                             icon=":material/quiz:", width="stretch", key="ob_quiz"):
                    st.session_state["quiz_preset"] = {"module": "A1", "track": "ai", "n": 5}
                    st.switch_page("app_pages/07_quizzes.py")
            else:
                st.markdown(":material/check_circle: **Done**")

        _a, _b = st.columns([5, 2])
        with _a:
            st.markdown(f"{'✅' if _contract_done else '**4 ·**'} **Sign the contract** *(optional today)*")
            st.caption("The rules you are holding yourself to. Two minutes, once, and the plan becomes binding.")
        with _b:
            st.page_link("app_pages/14_contract.py", label="Read and sign", icon=":material/gavel:")

        st.caption("Prefer to study inside the app? Open the module instead, and the app tracks every video you watch.")
        if st.button("Open A1 — Python for Data & ML in Learn", icon=":material/school:",
                     width="stretch", key="ob_learn"):
            st.session_state["learn_module"] = "A1"
            st.switch_page("app_pages/04_learn.py")

        st.caption("When this is done, **Today's mission** is your daily plan and the five-block loop below "
                   "is your daily map.")

# ---------- headline numbers ----------
countdown_label, countdown_value = "Plan day", "Day 1 / 112"
try:
    if profile.get("target_date"):
        days_left = (date.fromisoformat(profile["target_date"]) - date.today()).days
        countdown_label, countdown_value = "Days to NYC offer", f"{max(days_left, 0)}"
    elif progress.get("started_at"):
        day_n = (date.today() - date.fromisoformat(progress["started_at"])).days + 1
        countdown_value = f"Day {day_n} / 112"
except ValueError:
    pass

goal_min = int(profile.get("daily_hours", 6)) * 60
today_min = focus.today_minutes(progress)
hours = focus.total_hours(progress)
lvl, lvl_title = xp_level(progress["xp"])

m = st.columns(5)
m[0].metric(countdown_label, countdown_value)
m[1].metric("Locked in today", f"{focus.fmt_hm(today_min)} / {goal_min // 60}h")
m[2].metric("All-time focus", f"{hours:.1f} h")
m[3].metric("Mastery Index", f"{acc.mastery_index(progress)[0]:.0f}/100")
m[4].metric("Study streak", f"{streak_days(progress)} days")

# ---------- today's loop: the five blocks ----------
_today = date.today().isoformat()
_a = progress.get("activity", {}).get(_today, {})
_learn_secs = sum(v.get("secs", 0) for v in progress.get("watched", {}).values()
                  if v.get("date") == _today)
_blocks = [
    ("Learn", _learn_secs >= 600 or bool(_a.get("watch")), "app_pages/04_learn.py", "school"),
    ("Drill", bool(_a.get("drill_clear")) or _a.get("review", 0) >= 5, "app_pages/16_drill.py", "repeat"),
    ("Build", any(_a.get(k) for k in ("code", "desk", "lab", "challenge", "speed", "task")),
     "app_pages/24_labs.py", "biotech"),
    ("Prove", any(_a.get(k) for k in ("quiz", "quiz80", "gate", "gate_pass", "exam")),
     "app_pages/07_quizzes.py", "quiz"),
    ("Debrief", _today in progress.get("debriefs", {}), "app_pages/15_mission.py", "flag"),
]
_done = sum(1 for _, ok, _, _ in _blocks if ok)
with st.container(border=True):
    st.markdown(f"**Today's loop — {_done}/5 blocks**")
    st.progress(_done / 5)
    cols = st.columns(5)
    for col, (name, ok, path, icon) in zip(cols, _blocks):
        col.markdown(f"**{'✓' if ok else '○'} {name}**")
        col.page_link(path, label="Open" if not ok else "Again",
                      icon=f":material/{icon}:")
    if _done == 5:
        st.success("All five blocks closed. That is a complete day - not a busy one.", icon=":material/verified:")

# ---------- motivation row ----------
left, right = st.columns([3, 2], gap="large")
with left:
    quote_card(quote_of_the_day())
    b1, b2 = st.columns(2)
    if b1.button("Lock in now", type="primary", icon=":material/bolt:", width="stretch"):
        st.switch_page("app_pages/12_lock_in.py")
    if b2.button("Today's mission", icon=":material/flag:", width="stretch"):
        st.switch_page("app_pages/15_mission.py")

    current = next((w for w in WEEKS if f"w{w['w']}" not in progress["completed_tasks"]), None)
    if current:
        days = "".join(f"<li>{html.escape(d)}</li>" for d in current["days"])
        glass_card(f"This week · Week {current['w']} of 16 · {current['phase']}", current["title"],
                   f"{html.escape(current['focus'])}<ul style='margin-top:8px'>{days}</ul>"
                   f"<b>Milestone:</b> {html.escape(current['milestone'])}")
    else:
        glass_card("All 16 weeks complete", "Go get the offer.", "Applications, referrals, negotiation. You earned this.")

with right:
    rank, nxt, pct = rank_for(hours)
    to_next = f"{nxt[0] - hours:.1f} locked-in hours to <b>{html.escape(nxt[1])}</b>" if nxt else "You've reached the top."
    glass_card("Your NYC rank", html.escape(rank[1]), f"{html.escape(rank[2])}<br><br>{to_next}")
    st.progress(pct)

    chips = " ".join(
        f"<span style='display:inline-block;margin:3px 4px 0 0;padding:3px 10px;border-radius:999px;"
        f"border:1px solid rgba(245,185,66,.4);color:#FFD982;font-size:.8rem'>{html.escape(c.strip())}</span>"
        for c in profile.get("dream_companies", "").split(",") if c.strip()
    )
    glass_card("Your why", html.escape(profile["target_role"]),
               f"<i>{html.escape(profile.get('why', ''))}</i><div style='margin-top:10px'>{chips}</div>")

# ---------- NYC prize ----------
section("What's waiting for you in New York")
cols = st.columns(len(NYC_COMP))
for col, (role, comp) in zip(cols, NYC_COMP):
    with col:
        glass_card("Total comp (approx.)", comp, html.escape(role))
st.caption("Rough ranges from public compensation data. Verify current numbers on Levels.fyi and Glassdoor.")

# ---------- plan progress ----------
section("Phase progress")
pc = st.columns(len(PHASES))
for col, ph in zip(pc, PHASES):
    wks = [w for w in WEEKS if w["phase"] == ph]
    done = sum(1 for w in wks if f"w{w['w']}" in progress["completed_tasks"])
    with col:
        with st.container(border=True):
            st.markdown(f"**{ph}**")
            progress_bar(done, len(wks), f"{done}/{len(wks)} weeks complete")

section("Weak areas to drill")
weak = progress.get("weak_topics", [])
if weak:
    st.pills("Weak modules", weak, disabled=True, label_visibility="collapsed")
else:
    st.caption("Take quizzes to find out where you're losing points.")

section("Module overview")
tracks = {}
for mod in MODULES:
    tracks.setdefault(mod["track"], []).append(mod)
for tr, mods in tracks.items():
    with st.expander(f"{tr.upper()} track · {len(mods)} modules"):
        for mod in mods:
            icon = {"Mastered": ":material/workspace_premium:", "Locked": ":material/lock:", "Not yet": ":material/hourglass_top:",
                    "Ready": ":material/lock_open:"}[gates.status(progress, mod["id"])]
            st.markdown(f"{icon} **{mod['id']}** {mod['title']} ({', '.join('W' + str(w) for w in mod['weeks'])})")