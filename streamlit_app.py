"""Project DEVI - entry point."""
import hmac
import os
import time
from datetime import datetime

import streamlit as st

from lib import accountability as acc
from lib import focus, srs
from lib.nyc import rank_for
from lib.storage import load_profile, load_progress, log_study_day
from lib.ui import inject_css

st.set_page_config(
    page_title="Project DEVI - Finance & AI Academy",
    page_icon=":material/location_city:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


def _configured_password():
    """Secret first, then environment. No value means the gate is off (local use)."""
    try:
        value = st.secrets.get("DEVI_PASSWORD")
        if value:
            return str(value)
    except Exception:
        pass
    return os.environ.get("DEVI_PASSWORD")


_GATE = _configured_password()

if _GATE and not st.session_state.get("devi_authed"):
    _, _mid, _ = st.columns([1, 1.15, 1])
    with _mid:
        st.html(
            '<div style="text-align:center;margin:10vh 0 18px">'
            '<div class="nyc-eyebrow">Private</div>'
            '<h1 style="margin:6px 0 2px">Project <em>DEVI</em></h1>'
            '<p style="color:#94A3B8;margin:0">Finance &amp; AI academy. Members only.</p>'
            "</div>"
        )
        with st.form("devi_login", border=True):
            _pw = st.text_input("Password", type="password", label_visibility="collapsed",
                                placeholder="Password")
            _entered = st.form_submit_button("Enter", type="primary", width="stretch")
        if _entered:
            if hmac.compare_digest(_pw.encode("utf-8"), _GATE.encode("utf-8")):
                st.session_state["devi_authed"] = True
                st.rerun()
            time.sleep(0.6)
            st.error("Wrong password.")
        st.caption("Access is gated because `DEVI_PASSWORD` is set for this deployment.")
    st.stop()

log_study_day(load_progress())


pages = {
    "Command center": [
        st.Page("app_pages/01_dashboard.py", title="Dashboard", icon=":material/location_city:", default=True),
        st.Page("app_pages/15_mission.py", title="Today's mission", icon=":material/flag:", url_path="mission"),
        st.Page("app_pages/12_lock_in.py", title="Lock-in mode", icon=":material/timer:", url_path="lock-in"),
        st.Page("app_pages/13_career_stock.py", title="Career stock", icon=":material/candlestick_chart:", url_path="stock"),
        st.Page("app_pages/14_contract.py", title="The contract", icon=":material/gavel:", url_path="contract"),
        st.Page("app_pages/02_study_plan.py", title="Study plan", icon=":material/calendar_month:"),
        st.Page("app_pages/09_progress.py", title="Progress", icon=":material/insights:"),
    ],
    "Learn": [
        st.Page("app_pages/04_learn.py", title="Learn", icon=":material/school:"),
        st.Page("app_pages/22_watch.py", title="Watch", icon=":material/smart_display:", url_path="watch"),
        st.Page("app_pages/18_gates.py", title="Mastery gates", icon=":material/account_tree:", url_path="gates"),
        st.Page("app_pages/21_playbook.py", title="Bootcamp playbook", icon=":material/menu_book:", url_path="playbook"),
        st.Page("app_pages/03_resources.py", title="Resources", icon=":material/library_books:"),
        st.Page("app_pages/11_research.py", title="Research library", icon=":material/science:"),
    ],
    "Practice": [
        st.Page("app_pages/16_drill.py", title="Daily drill", icon=":material/repeat:", url_path="drill"),
        st.Page("app_pages/23_live_desk.py", title="The Desk (live)", icon=":material/candlestick_chart:", url_path="desk"),
        st.Page("app_pages/24_labs.py", title="Hands-on labs", icon=":material/biotech:", url_path="labs"),
        st.Page("app_pages/19_challenge_lab.py", title="Challenge lab", icon=":material/science:", url_path="lab"),
        st.Page("app_pages/20_speed_drills.py", title="Speed drills", icon=":material/speed:", url_path="speed"),
        st.Page("app_pages/05_console.py", title="Practice console", icon=":material/terminal:"),
        st.Page("app_pages/06_practice.py", title="Practice materials", icon=":material/edit_note:"),
    ],
    "Prove it": [
        st.Page("app_pages/07_quizzes.py", title="Quizzes", icon=":material/quiz:"),
        st.Page("app_pages/08_exams.py", title="Exams", icon=":material/assignment:"),
        st.Page("app_pages/17_gauntlet.py", title="Interview gauntlet", icon=":material/sports_martial_arts:", url_path="gauntlet"),
    ],
    "You": [
        st.Page("app_pages/10_profile.py", title="Profile", icon=":material/person:"),
    ],
}

nav = st.navigation(pages)

# Catch phases that ended while the app was closed or on another page.
_state = focus.load_state()
_ev = focus.tick(_state)
if _ev:
    st.session_state["devi_event"] = _ev

with st.sidebar:
    if nav.url_path != "lock-in":
        if _state["status"] in ("running", "paused"):
            @st.fragment(run_every=1 if _state["status"] == "running" else None)
            def mini_timer():
                s = focus.load_state()
                ev = focus.tick(s)
                if ev:
                    st.session_state["devi_event"] = ev
                    st.rerun()
                color = "#64748B" if s["status"] == "paused" else focus.PHASE_COLOR[s["phase"]]
                st.html(
                    f'<div class="mini-timer"><div class="ph" style="color:{color}">'
                    f'{focus.PHASE_LABEL[s["phase"]]}{" · paused" if s["status"] == "paused" else ""}</div>'
                    f'<div class="clk">{focus.fmt_clock(focus.remaining(s))}</div>'
                    f'<div class="lb">{(s["label"] or s["subject"])[:60]}</div></div>'
                )
            mini_timer()
            st.page_link("app_pages/12_lock_in.py", label="Open lock-in mode", icon=":material/open_in_full:")
        else:
            st.page_link("app_pages/12_lock_in.py", label="Lock in now", icon=":material/bolt:")
    _p = load_progress()
    _goal = int(load_profile().get("daily_hours", 6)) * 60
    _today = focus.today_minutes(_p)
    st.progress(min(1.0, _today / max(_goal, 1)),
                text=f"Today: {focus.fmt_hm(_today)} / {focus.fmt_hm(_goal)} locked in")
    st.caption(f"NYC · {datetime.now().strftime('%a %d %b, %H:%M')} local")
    if os.environ.get("RENDER", "").lower() == "true" and not os.environ.get("DEVI_DATA_DIR"):
        st.warning("Free instance: progress resets on restart.", icon=":material/warning:")
        st.page_link("app_pages/10_profile.py", label="Back up progress",
                     icon=":material/download:")
    if _GATE and st.button("Sign out", icon=":material/logout:", width="stretch"):
        st.session_state.pop("devi_authed", None)
        st.rerun()

# Celebrations and alerts (set by any timer fragment).
_event = st.session_state.pop("devi_event", None)
if _event:
    _s = focus.load_state()
    if _event["type"] == "focus_done":
        st.toast(f"Block complete: +{_event['minutes']} min locked in on {_event['subject']}. Take your break.",
                 icon=":material/emoji_events:")
        st.balloons()
    elif _event["type"] == "break_done":
        st.toast("Break's over. Back to the grind - New York is waiting.", icon=":material/bolt:")
    elif _event["type"] == "stopped":
        mins = _event.get("minutes", 0)
        st.toast(f"Logged {mins} min." if mins else "Session ended (under a minute, not logged).",
                 icon=":material/stop_circle:")
    if _s.get("sound", True) and _event["type"] in ("focus_done", "break_done"):
        st.html(f'<audio autoplay src="data:audio/wav;base64,{focus.chime_b64()}"></audio>')

# ---------- ticker tape (every page) ----------
_profile = load_profile()
_rows = acc.stock_series(_p, _goal)
_last, _prev = _rows[-1], (_rows[-2]["close"] if len(_rows) > 1 else 100.0)
_chg = (_last["close"] / _prev - 1) * 100
_rank = rank_for(focus.total_hours(_p))[0][1]
_mi, _ = acc.mastery_index(_p)
_due, _new = srs.due_cards(_p)
_rating, _ = acc.analyst_rating(_rows)
_cls = "up" if _chg >= 0 else "down"
_items = [
    f'<span><span class="sym">${acc.ticker_symbol(_profile)}</span> {_last["close"]:.2f} '
    f'<span class="{_cls}">{"▲" if _chg >= 0 else "▼"} {_chg:+.2f}%</span></span>',
    f'<span>DAY SCORE <span class="{"up" if _last["score"] >= 60 else "down"}">{_last["score"]}/100</span></span>',
    f'<span>MASTERY INDEX <span class="sym">{_mi:.0f}</span></span>',
    f'<span>LOCKED IN TODAY {focus.fmt_hm(_today)}</span>',
    f'<span>DRILL DUE <span class="{"up" if not (_due or _new) else "down"}">{len(_due) + len(_new)}</span></span>',
    f'<span>RATING <span class="sym">{_rating.upper()}</span></span>',
    f'<span>RANK {_rank.upper()}</span>',
    f'<span>PLAN DAY {acc.plan_day(_p)}/112</span>',
]
st.html(f'<div class="ticker-tape"><div class="ticker-track">{"".join(_items) * 2}</div></div>')

# ---------- hard mode gate ----------
_breaches = acc.unresolved_breaches(_p, _goal)
_contract = _p.get("contract") or {}
if _breaches and _contract.get("hard_mode") and nav.url_path not in ("contract", "lock-in", "drill", "mission"):
    st.html(
        f'<div class="breach"><div class="nyc-eyebrow" style="color:#FCA5A5">Hard mode · access suspended</div>'
        f'<h1>Contract breached.</h1><p>You had {len(_breaches)} zero day(s): {", ".join(_breaches)}. '
        f'The best don\'t skip days - and when they do, they own it immediately.</p>'
        f'<p style="margin-top:10px">Stake owed: <b>{_contract.get("stakes", "")}</b></p></div>'
    )
    st.markdown("File your incident report to unlock the app. Lock-in mode, the drill and today's mission stay open.")
    c1, c2 = st.columns(2)
    if c1.button("File incident report", type="primary", icon=":material/gavel:", width="stretch"):
        st.switch_page("app_pages/14_contract.py")
    if c2.button("Lock in now", icon=":material/timer:", width="stretch"):
        st.switch_page("app_pages/12_lock_in.py")
    st.stop()

nav.run()