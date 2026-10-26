import json
import os
from datetime import date, datetime, timedelta

import streamlit as st

from lib import backup
from lib.env import get
from lib.storage import load_profile, save_profile
from lib.ui import hero, inject_css, section

inject_css()
hero("Profile & <em>mission</em>", "Write down the dream. Then come back every day and earn it.", quote_tags=["grind"])

profile = load_profile()

try:
    target_default = date.fromisoformat(profile["target_date"]) if profile.get("target_date") else date.today() + timedelta(days=120)
except ValueError:
    target_default = date.today() + timedelta(days=120)

with st.form("profile_form"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Name", value=profile.get("name", ""))
    role = c2.text_input("Target role", value=profile.get("target_role", ""))
    c3, c4, c5 = st.columns(3)
    target = c3.date_input("NYC offer target date", value=target_default)
    hours = c4.slider("Daily locked-in hours goal", 1, 12, value=int(profile.get("daily_hours", 6)))
    levels = ["Beginner", "Intermediate", "Advanced"]
    level = c5.selectbox("Current level", options=levels, index=levels.index(profile.get("level", "Beginner")))
    day_start = st.slider("Bootcamp day starts at (hour)", 5, 14, value=int(profile.get("day_start", 9)))
    why = st.text_area("Your why (shown on your dashboard every day)", value=profile.get("why", ""), height=100)
    companies = st.text_input("Dream companies (comma-separated)", value=profile.get("dream_companies", ""))
    if st.form_submit_button("Save profile", type="primary"):
        save_profile({"name": name, "target_role": role, "target_date": target.isoformat(),
                      "daily_hours": hours, "level": level, "why": why, "dream_companies": companies,
                      "day_start": day_start})
        st.success("Saved.")
        st.rerun()

section("Backup & restore")
_on_render = os.environ.get("RENDER", "").lower() == "true"
if _on_render and not get("DATA_DIR"):
    st.warning(
        "This is a free Render instance: the filesystem is wiped on restart, deploy or "
        "spin-down. Download a backup after each session and restore it when you return.",
        icon=":material/warning:",
    )

_snap = backup.snapshot()
_b = st.columns([1, 1], vertical_alignment="bottom")
with _b[0]:
    st.download_button(
        "Download backup",
        data=backup.dumps(),
        file_name=f"laksh-backup-{date.today():%Y%m%d}.json",
        mime="application/json",
        type="primary",
        icon=":material/download:",
        width="stretch",
    )
with _b[1]:
    st.caption(
        f"{_snap['progress'].get('xp', 0)} XP · "
        f"{len(_snap['progress'].get('watched', {}))} lessons watched · "
        f"{len(_snap['progress'].get('completed_tasks', []))} tasks done · "
        f"exported {datetime.now():%d %b %H:%M}"
    )

uploaded = st.file_uploader("Restore from a backup file", type=["json"])
if uploaded is not None:
    try:
        _payload = json.load(uploaded)
        _info = backup.inspect(_payload)
    except Exception as e:
        st.error(f"Could not read that file: {e}")
    else:
        st.info(
            f"Backup from {_info['exported_at'] or 'an unknown date'} · "
            f"{_info['xp']} XP · {_info['tasks']} tasks · {_info['watched']} lessons"
            + (" · profile included" if _info["has_profile"] else "")
        )
        st.caption("Restoring replaces the progress, profile and focus state on this instance.")
        if st.button("Restore this backup", type="primary", icon=":material/restore:"):
            try:
                _written = backup.restore(_payload)
            except Exception as e:
                st.error(f"Restore failed: {e}")
            else:
                st.success(f"Restored: {', '.join(_written)}.")
                st.rerun()

section("About Project Laksh")
st.markdown(
    "Project Laksh is your personal Finance + AI academy. Strict 16-week plan, "
    "curated resources, practice console, quizzes, and exams - built to land the "
    "greatest job in New York City. No zero days."
)