from collections import defaultdict

import streamlit as st

from lib import linkcheck
from lib.resources import RESOURCES
from lib.ui import hero, section, inject_css

inject_css()
hero("Resource <em>library</em>", f"{len(RESOURCES)} hand-picked resources from YouTube, open source, books, courses and tools - "
     "every link checked by machine, not assumed.",
     eyebrow="Verified · not aspirational")

ok, unknown, dead, checked = linkcheck.counts()
if checked:
    c = st.columns(4)
    c[0].metric("Resources", len(RESOURCES))
    c[1].metric("Verified live", ok)
    c[2].metric("Unverifiable", unknown, help="Bot-walled sites (Kaggle, SEC, LeetCode) block automated checks.")
    c[3].metric("Dead", dead)
    st.caption(f"Link check run {linkcheck.checked_at()}. Re-run with `scripts/check_links.py`.")
else:
    st.info("Links have not been checked yet. Run `scripts/check_links.py`.", icon=":material/link:")

f1, f2, f3 = st.columns([2, 2, 3])
track = f1.segmented_control("Track", ["all", "finance", "ai", "quant", "career", "research"], default="all") or "all"
rtype = f2.selectbox("Type", ["All"] + sorted({v["type"] for v in RESOURCES.values()}))
search = f3.text_input("Search", placeholder="e.g. karpathy, valuation, sql...")

items = list(RESOURCES.items())
if track != "all":
    items = [(k, v) for k, v in items if v.get("track") == track]
if rtype != "All":
    items = [(k, v) for k, v in items if v.get("type") == rtype]
if search:
    q = search.lower()
    items = [(k, v) for k, v in items if q in v["title"].lower() or q in v.get("desc", "").lower()]

st.caption(f"{len(items)} resources")

BADGE = {True: ("✅ verified", "green"), None: ("◍ unverified", "orange"), False: ("✗ dead", "red")}
groups = defaultdict(list)
for k, v in items:
    groups[v["type"]].append((k, v))

for typ, lst in sorted(groups.items()):
    section(typ)
    cols = st.columns(2)
    for i, (k, v) in enumerate(lst):
        chk = linkcheck.for_key(k) or {}
        label, color = BADGE.get(chk.get("ok"), ("· unchecked", "gray"))
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{v['title']}**")
                meta = f"{v['track'].upper()} · {v['type']}"
                if chk.get("subs"):
                    meta += f" · {chk['subs']:,} subscribers"
                st.caption(meta)
                st.markdown(v.get("desc", ""))
                a, b = st.columns([1, 1], vertical_alignment="center")
                with a:
                    st.link_button("Open", v["url"], width="stretch",
                                   disabled=chk.get("ok") is False)
                with b:
                    st.caption(f":{color}[{label}]")
