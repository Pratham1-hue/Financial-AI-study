import html
from datetime import date, datetime

import streamlit as st

from lib import accountability as acc
from lib import gates, srs
from lib.content import modules_for_week
from lib.storage import is_task_done, load_profile, load_progress, log_activity, mark_task, save_progress
from lib.ui import glass_card, hero, inject_css, section

MIN_FEYNMAN = 200

inject_css()
progress, profile = load_progress(), load_profile()
goal_min = int(profile.get("daily_hours", 6)) * 60
today = date.today()
n, week, assignment = acc.todays_assignment(progress)

hero(f"Today's <em>mission</em>",
     f"{today.strftime('%A, %B %d')} · Day {n} of {acc.PLAN_DAYS}. Learn it so well you could teach it. That's the bar.",
     eyebrow="Daily briefing", quote_tags=["focus", "grind"])

parts, fm = acc.day_parts(progress, today, goal_min)
score = round(sum(parts.values()))
color = "#F87171" if score < acc.ZERO_DAY else "#FBBF24" if score < 60 else "#34D399"
status = ("ZERO DAY - the stock is crashing" if score < acc.ZERO_DAY else
          "Below standard - not done yet" if score < 60 else
          "Strong day" if score < 90 else "World-class day")

left, right = st.columns([2, 3], gap="large")
with left:
    st.html(f'<div class="glass-card"><div class="card-kicker">Today\'s score</div>'
            f'<div class="score-big" style="color:{color}">{score}<span style="font-size:1.6rem;color:#64748B">/100</span></div>'
            f'<div class="card-body" style="margin-top:6px">{status}</div></div>')
    st.progress(score / 100)
    st.caption("60 = acceptable. 90+ = the standard of the people you'll be competing with.")
with right:
    if week:
        tid = f"plan-d{n}"
        done = is_task_done(progress, tid)
        glass_card(f"Week {week['w']} · {week['title']}", html.escape(assignment),
                   f"Focus this week: {html.escape(week['focus'])}<br>Milestone: {html.escape(week['milestone'])}")
        if done:
            st.success("Today's assignment is done.", icon=":material/task_alt:")
        elif st.button("Mark today's assignment complete", type="primary", icon=":material/check:"):
            mark_task(progress, tid)
            st.rerun()
    else:
        glass_card("Post-plan", "Keep compounding", html.escape(assignment))

if week:
    issues = gates.week_gate_issues(progress, modules_for_week(week["w"]))
    if issues:
        lines = "  \n".join(f"**{m['id']} {m['title']}** needs: {', '.join(f'{p} {gates.title(p)}' for p in miss)}"
                            for m, miss in issues)
        st.warning(f"This week's modules sit on foundations you haven't proven yet. Go back up the tree first - "
                   f"the gate wins over the calendar.  \n{lines}", icon=":material/account_tree:", title="Mastery before pace")
        if st.button("Open mastery gates", icon=":material/flag:"):
            st.switch_page("app_pages/18_gates.py")

section("Your bootcamp day")
st.caption("Le Wagon's daily rhythm + Hack Reactor's morning warm-up, scaled to your daily goal. Same structure every day = zero decisions.")
now = datetime.now()
for i, b in enumerate(acc.bootcamp_day(goal_min, int(profile.get("day_start", 9)))):
    current = b["start"] <= now < b["end"]
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 6, 2], vertical_alignment="center")
        c1.markdown(f"**{b['start'].strftime('%H:%M')}-{b['end'].strftime('%H:%M')}**  \n{b['mins']} min")
        c2.markdown(f"{':material/play_circle:' if current else ':material/schedule:'} **{b['name']}**"
                    f"{' · now' if current else ''}  \n{b['desc']}")
        if c3.button("Go", key=f"block_{i}", width="stretch", type="primary" if current else "secondary"):
            st.switch_page(b["page"])

section("Non-negotiables")
links = {
    "Deep work": ("app_pages/12_lock_in.py", "Lock in", acc.PART_MAX["Deep work"]),
    "Lesson watched": ("app_pages/22_watch.py", "Watch a lesson", acc.PART_MAX["Lesson watched"]),
    "Retention drill": ("app_pages/16_drill.py", "Start drill", acc.PART_MAX["Retention drill"]),
    "Proof (quiz 80%+)": ("app_pages/07_quizzes.py", "Take a quiz", acc.PART_MAX["Proof (quiz 80%+)"]),
    "Hands-on practice": ("app_pages/05_console.py", "Write code", acc.PART_MAX["Hands-on practice"]),
    "Feynman debrief": (None, "Write below", acc.PART_MAX["Feynman debrief"]),
}
due, new = srs.due_cards(progress)
from lib import watch as _watch
detail = {
    "Deep work": f"{fm} / {goal_min} min locked in",
    "Lesson watched": f"{_watch.today_secs(progress) // 60} min of lessons today (20 min earns full credit)",
    "Retention drill": f"{len(due)} due + {len(new)} new cards left",
    "Proof (quiz 80%+)": "Score 80%+ on any quiz",
    "Hands-on practice": "Run code, practice an interview, or finish a task",
    "Feynman debrief": "Explain today's hardest idea simply",
}
for k, v in parts.items():
    page, cta, mx = links[k]
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 3, 2], vertical_alignment="center")
        icon = ":material/check_circle:" if v >= mx else ":material/pending:" if v > 0 else ":material/cancel:"
        c1.markdown(f"{icon} **{k}**  \n{detail[k]}")
        c2.progress(v / mx, text=f"{v:.0f}/{mx} pts")
        if page and v < mx and c3.button(cta, key=f"go_{k}", width="stretch"):
            st.switch_page(page)

section("How the best learn")
lc = st.columns(3)
tips = [
    ("Active recall", "Close the book and retrieve. Testing yourself beats rereading by a wide margin."),
    ("Spaced repetition", "Review right before you'd forget. The drill schedules this for you."),
    ("The Feynman technique", "If you can't explain it simply, you don't understand it yet. Your debrief finds the gaps."),
    ("Deliberate practice", "Work at the edge of your ability, with immediate feedback. Comfortable = not growing."),
    ("Interleaving", "Mix finance, ML and coding in one day. Harder in the moment, better retention."),
    ("Sleep", "Memory consolidates while you sleep. Pulling all-nighters erases the work."),
]
for i, (t, b) in enumerate(tips):
    with lc[i % 3]:
        glass_card("Principle", t, b)

# ---------- Feynman debrief ----------
section("Evening debrief - the Feynman test")
key = today.isoformat()
existing = progress.get("debriefs", {}).get(key, {})
with st.form("debrief"):
    concept = st.text_input("The hardest concept I worked on today", value=existing.get("concept", ""))
    explain = st.text_area(f"Explain it like you're teaching a smart 12-year-old (min {MIN_FEYNMAN} characters, no jargon)",
                           value=existing.get("explain", ""), height=170)
    gaps = st.text_area("Where did my explanation break down? (study these gaps first tomorrow)",
                        value=existing.get("gaps", ""), height=80)
    c1, c2 = st.columns(2)
    win = c1.text_input("Biggest win today", value=existing.get("win", ""))
    first = c2.text_input("Tomorrow's first focus block will be", value=existing.get("first", ""))
    energy = st.select_slider("Energy / focus today", options=[1, 2, 3, 4, 5], value=existing.get("energy", 3))
    if st.form_submit_button("Submit debrief", type="primary", icon=":material/history_edu:"):
        if len(explain.strip()) < MIN_FEYNMAN:
            st.error(f"That's {len(explain.strip())} characters - a tweet, not an explanation. "
                     f"Go to {MIN_FEYNMAN}+. The struggle to explain is where the learning happens.")
        elif not concept.strip() or not first.strip():
            st.error("Name the concept and commit to tomorrow's first block.")
        else:
            is_new = key not in progress.get("debriefs", {})
            progress.setdefault("debriefs", {})[key] = {
                "concept": concept, "explain": explain, "gaps": gaps, "win": win, "first": first,
                "energy": energy, "at": datetime.now().isoformat(timespec="minutes")}
            if is_new:
                progress["xp"] = progress.get("xp", 0) + 50
                log_activity(progress, "debrief")
            else:
                save_progress(progress)
            st.rerun()
if existing:
    st.success("Debrief filed. Sleep well - your brain does the rest tonight.", icon=":material/bedtime:")

journal = sorted(progress.get("debriefs", {}).items(), reverse=True)
if journal:
    with st.expander(f"Learning journal ({len(journal)} entries)"):
        for d, e in journal[:14]:
            st.markdown(f"**{d} · {e['concept']}**")
            st.markdown(f"> {e['explain']}")
            if e.get("gaps"):
                st.caption(f"Gaps: {e['gaps']}")