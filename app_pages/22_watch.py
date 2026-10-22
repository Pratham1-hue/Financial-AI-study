from datetime import datetime

import streamlit as st

from lib import watch, yt_data
from lib import accountability as acc
from lib.content import MODULES, MODULE_BY_ID, TRACKS, modules_for_track, modules_for_week
from lib.quotes import quote_for
from lib.storage import load_progress, log_activity, save_progress
from lib.ui import hero, inject_css, quote_inline, section

inject_css()
hero("Watch <em>the lesson</em>", "Ten hand-ranked lessons per module, pulled live from YouTube's API and "
     "ordered by relevance to what you're studying - not by whatever the algorithm wants you to see next.",
     eyebrow="Lecture block · curated curriculum", quote_tags=["focus"])

progress = load_progress()

if not yt_data.ready():
    st.warning("No synced YouTube data yet. Run `.venv\\Scripts\\python.exe scripts\\sync_youtube.py` once.",
               icon=":material/sync_problem:")
    st.stop()

# ---------- which module ----------
n, week, _ = acc.todays_assignment(progress)
week_mods = [m["id"] for m in modules_for_week(week["w"])] if week else []
default_mid = st.session_state.get("watch_mid") or (week_mods[0] if week_mods else MODULES[0]["id"])

usable_tracks = [t for t in TRACKS if modules_for_track(t)]
track = st.segmented_control("Track", usable_tracks, default=MODULE_BY_ID[default_mid]["track"],
                             format_func=lambda t: TRACKS[t]["name"], key="watch_track") or "finance"
mods = modules_for_track(track)
opts = [m["id"] for m in mods]
idx = opts.index(default_mid) if default_mid in opts else 0
mid = st.selectbox("Module", opts, index=idx,
                   format_func=lambda i: f"{i} · {MODULE_BY_ID[i]['title']}"
                                         + ("  ← this week" if i in week_mods else ""),
                   key="watch_module")

queue = yt_data.module_videos(mid)
if not queue:
    st.info("No queue synced for this module yet. Re-run the sync script.", icon=":material/hourglass_empty:")
    st.stop()
queue_ids = {v["id"] for v in queue}

done, total, secs_left = watch.queue_progress(progress, queue)
c = st.columns(4)
c[0].metric("This module", f"{done}/{total} watched")
c[1].metric("Time left here", f"{secs_left // 3600}h {secs_left % 3600 // 60:02d}m")
c[2].metric("Watched today", f"{watch.today_secs(progress) // 60} min")
c[3].metric("Lifetime", f"{watch.total_hours(progress):.1f}h")
st.progress(done / total, text=f"Module {mid} lecture progress")

# ---------- resolve what's playing ----------
sel_id = st.session_state.get("watch_sel")
sel = None
if sel_id in queue_ids:
    sel = next(v for v in queue if v["id"] == sel_id)
elif sel_id:
    sel = yt_data.video(sel_id)          # free pick from the catalog
if not sel:
    nxt = watch.next_up(progress, queue)
    sel = nxt or queue[0]
    st.session_state["watch_sel"] = sel["id"]

# ---------- player ----------
section("Now playing")
left, right = st.columns([3, 2], gap="large")
with left:
    st.video("https://www.youtube.com/watch?v=" + sel["id"])
with right:
    st.markdown(f"**{sel['title']}**")
    st.caption(f"{sel['channel']} · {sel['secs'] // 60} min · {yt_data.fmt_views(sel['views'])} · {sel['published'][:4]}")
    if watch.is_watched(progress, sel["id"]):
        st.success("Watched. It counts toward today's lecture block.", icon=":material/check_circle:")
    else:
        if st.button("Mark watched", type="primary", icon=":material/visibility:", width="stretch"):
            if watch.mark(progress, sel["id"], mid, sel["title"], sel["channel"], sel["secs"]):
                log_activity(progress, "watch")
            save_progress(progress)
            st.session_state.pop("watch_sel", None)
            st.balloons()
            st.rerun()
        st.caption("Mark it only when you actually finished it. The score is only worth what your honesty makes it worth.")
    with st.expander("Notes from this lesson", icon=":material/edit_note:"):
        note = st.text_area("What did you learn?", key=f"note_{sel['id']}", height=120,
                            label_visibility="collapsed",
                            placeholder="Explain the single most important idea in your own words...")
        if st.button("Save note", key=f"savenote_{sel['id']}"):
            progress.setdefault("lesson_notes", {})[sel["id"]] = {
                "at": datetime.now().isoformat(timespec="minutes"), "text": note, "module": mid}
            save_progress(progress)
            st.toast("Note saved.", icon=":material/done:")
    if st.button("Back to the queue", icon=":material/playlist_play:", width="stretch",
                 key="back_queue", disabled=sel["id"] in queue_ids):
        st.session_state.pop("watch_sel", None)
        st.rerun()
    st.link_button("Open on YouTube", "https://www.youtube.com/watch?v=" + sel["id"],
                   icon=":material/open_in_new:", width="stretch")

quote_inline(quote_for(f"watch-{mid}", ["focus", "grind"]))

# ---------- queue ----------
section(f"Queue · {mid}")
st.caption("Ranked by relevance to this module's lessons, then trusted channel, then length. "
           "Two videos per channel maximum, so you get range instead of one personality.")
for i, v in enumerate(queue, 1):
    played = watch.is_watched(progress, v["id"])
    with st.container(border=True):
        a, b, d = st.columns([6, 3, 1.6], vertical_alignment="center")
        with a:
            st.markdown(f"{'✅' if played else f'**{i}.**'} {v['title']}")
            st.caption(f"{v['channel']} · {v['secs'] // 60} min · {yt_data.fmt_views(v['views'])} · {v['published'][:4]}")
        with b:
            st.progress(1.0 if played else 0.0, text="watched" if played else "not yet")
        with d:
            if st.button("Play", key=f"play_{v['id']}", width="stretch",
                         type="secondary" if played else "primary"):
                st.session_state["watch_sel"] = v["id"]
                st.rerun()

# ---------- search ----------
section("Search the whole catalog")
st.caption(f"{len(list(yt_data.all_videos())):,} videos from {len(yt_data.channels())} trusted channels. "
           "Local search - costs no quota.")
q = st.text_input("Search titles, channels, descriptions",
                  placeholder="e.g. terminal value, backprop, window function")
if q:
    res = yt_data.search(q, limit=20)
    if not res:
        st.info("Nothing in the catalog matches that. Try a broader term.")
    for v in res:
        with st.container(border=True):
            a, b = st.columns([6, 1.4], vertical_alignment="center")
            with a:
                st.markdown(f"**{v['title']}**")
                st.caption(f"{v['channel']} · {v['secs'] // 60} min · {yt_data.fmt_views(v['views'])}")
            with b:
                if st.button("Play", key=f"s_{v['id']}", width="stretch"):
                    st.session_state["watch_sel"] = v["id"]
                    st.rerun()

st.divider()
with st.expander("Data health", icon=":material/monitor_heart:"):
    from lib import youtube as yt_api
    c = st.columns(4)
    c[0].metric("Videos indexed", f"{len(list(yt_data.all_videos())):,}")
    c[1].metric("Trusted channels", len(yt_data.channels()))
    c[2].metric("API quota used", f"{yt_api.quota_used_today()}/{yt_api.DAILY_QUOTA}")
    c[3].metric("Last sync", (yt_data.synced_at() or "never")[:10])
    st.caption("Browsing this page costs no quota - it reads the synced catalog. "
               "Quota is only spent by `scripts/sync_youtube.py` and live searches.")
    st.caption(f"Synced {yt_data.synced_at() or 'never'}. Refresh with `scripts/sync_youtube.py`.")

