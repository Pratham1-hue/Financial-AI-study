import html
from datetime import date, datetime

import streamlit as st

from lib import accountability as acc
from lib import focus, gates
from lib.content import MODULES
from lib.nyc import NYC_COMP, rank_for
from lib.quotes import quote_of_the_day
from lib.storage import load_profile, load_progress, streak_days
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

# ---------- first run: the only three things to do ----------
if not (progress.get("xp") or progress.get("contract") or progress.get("watched")
        or progress.get("activity")):
    with st.container(border=True):
        st.markdown("**Start here · Day 1 of 112**")
        st.caption("Three moves, in order. The rest of this page is context — this is the work.")
        _s1, _s2, _s3 = st.columns(3)
        with _s1:
            st.markdown("**1 · Today's mission**")
            st.caption("The exact assignment for today. Read it before anything else.")
            st.page_link("app_pages/15_mission.py", label="Open the mission", icon=":material/flag:")
        with _s2:
            st.markdown("**2 · Lock in 25 minutes**")
            st.caption("Start the timer, then open the lesson. One block is enough to begin.")
            st.page_link("app_pages/12_lock_in.py", label="Start the timer", icon=":material/bolt:")
        with _s3:
            st.markdown("**3 · Sign the contract**")
            st.caption("The rules you are holding yourself to. Two minutes, once.")
            st.page_link("app_pages/14_contract.py", label="Read and sign", icon=":material/gavel:")

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