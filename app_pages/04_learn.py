import streamlit as st
from lib.ui import hero, section, inject_css, badge, progress_bar
from lib.storage import load_progress, mark_task, is_task_done, log_activity, save_progress
from lib.content import MODULES, MODULE_BY_ID, modules_for_track
from lib.resources import resources_by_ids

inject_css()
hero("Learn", "Module-by-module structured learning. A module is complete only when you pass its mastery gate.")

progress = load_progress()

track = st.segmented_control("Track", options=["finance", "ai", "quant", "career"], default="finance") or "finance"
mods = modules_for_track(track)

mod_choice = st.selectbox("Module", options=[f"{m['id']} - {m['title']}" for m in mods])
mid = mod_choice.split(" - ")[0]
m = MODULE_BY_ID[mid]

with st.container(border=True):
    st.markdown(f"## {m['id']}: {m['title']}")
    st.caption(f"Track: {m['track'].upper()} · Level: {m['level']} · Weeks: {', '.join(str(w) for w in m['weeks'])}")
    st.markdown(m["summary"])
    from lib import gates
    gstatus = gates.status(progress, m["id"])
    if gstatus == "Mastered":
        st.success("Mastery gate passed - this module is proven.", icon=":material/workspace_premium:")
    elif gstatus == "Locked":
        need = ", ".join(f"{p} {gates.title(p)}" for p in gates.missing_prereqs(progress, m["id"]))
        st.warning(f"Prerequisites first: {need}. Study ahead if you like, but the gate opens only after them.",
                   icon=":material/lock:")
    elif gstatus == "Not yet":
        st.info("Not yet - you're in the retake wait. Drill and re-explain the gaps.", icon=":material/hourglass_top:")
    else:
        if st.button("Take the mastery gate", type="primary", icon=":material/flag:", key=f"gate_{m['id']}"):
            st.switch_page("app_pages/18_gates.py")

section("Lessons")
for i, les in enumerate(m["lessons"], 1):
    st.markdown(f"{i}. {les}")

section("Outcomes")
for o in m["outcomes"]:
    st.markdown(f"- {o}")

section("Watch the lesson")
from lib import watch, yt_data
_vids = yt_data.module_videos(m["id"])
if _vids:
    _done, _tot, _left = watch.queue_progress(progress, _vids)
    st.caption(f"{_done}/{_tot} watched · {_left // 60} min left in this module's queue · ranked by relevance")
    _nxt = watch.next_up(progress, _vids) or _vids[0]
    _l, _r = st.columns([3, 2], gap="large")
    with _l:
        st.video("https://www.youtube.com/watch?v=" + _nxt["id"])
    with _r:
        st.markdown(f"**{_nxt['title']}**")
        st.caption(f"{_nxt['channel']} · {_nxt['secs'] // 60} min · {yt_data.fmt_views(_nxt['views'])}")
        if st.button("Mark watched", key=f"mw_{_nxt['id']}", type="primary", icon=":material/visibility:",
                     width="stretch"):
            if watch.mark(progress, _nxt["id"], m["id"], _nxt["title"], _nxt["channel"], _nxt["secs"]):
                log_activity(progress, "watch")
            save_progress(progress)
            st.rerun()
        if st.button("Open the full queue", key=f"wq_{m['id']}", width="stretch", icon=":material/playlist_play:"):
            st.session_state["watch_mid"] = m["id"]
            st.switch_page("app_pages/22_watch.py")
    with st.expander(f"All {len(_vids)} lessons for {m['id']}"):
        for _v in _vids:
            st.markdown(f"{'✅' if watch.is_watched(progress, _v['id']) else '•'} "
                        f"[{_v['title']}](https://www.youtube.com/watch?v={_v['id']}) "
                        f"— {_v['channel']}, {_v['secs'] // 60} min")
else:
    st.caption("No video queue synced for this module yet.")

section("Resources for this module")
for r in resources_by_ids(m["resources"]):
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"**{r['title']}**")
            st.caption(f"{r['type']} · {r['track'].upper()}")
            st.markdown(r.get("desc", ""))
        with c2:
            st.link_button("Open", r["url"])

section("Mini practice")
qs = [q for q in __import__("lib.quiz_bank", fromlist=["QUESTIONS"]).QUESTIONS if q["module"] == m["id"]]
if qs:
    st.caption(f"{len(qs)} quiz questions available for this module.")
    st.page_link("app_pages/07_quizzes.py", label="Practice these in Quizzes", icon=":material/quiz:")
else:
    st.caption("No dedicated quiz questions yet for this module.")