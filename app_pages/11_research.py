import streamlit as st
from collections import Counter, defaultdict

from lib.ui import hero, section, inject_css
from lib.resources import RESOURCES, ALIASES, all_categories
from lib import linkcheck

inject_css()
hero(
    "Research & Open-Source Library",
    "Flooded with the best open research: papers, repos, datasets, benchmarks, tools, blogs.",
)

ok, unknown, dead, checked = linkcheck.counts()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Resources", len(RESOURCES))
c2.metric("Verified live", ok)
c3.metric("Unverified", unknown, help="Real sites that refuse automated probes (paywalls, bot walls).")
c4.metric("Dead", dead, help="Broken links. Rerun scripts/check_links.py to refresh.")

track_counts = Counter(v.get("track") for v in RESOURCES.values())
st.caption("  ·  ".join(f"{t.upper()} {n}" for t, n in sorted(track_counts.items())))

# ---------------------------------------------------------------- start here
START_HERE = {
    "r_damodaran": "Valuation, from the man who wrote the book",
    "rf_yale_econ252": "Shiller's conceptual foundation",
    "rf_mit_15401": "Andrew Lo's finance theory",
    "rf_bis_qr": "How the institutions actually talk",
    "rf_french": "The factor data every paper uses",
    "r_quantlib": "Derivatives pricing in real code",
    "rq_lean": "Institutional backtesting engine",
    "r_fastai": "Deep learning, top-down",
    "rr_nanogpt": "LLMs in readable code",
    "ra_p_attention": "The transformer paper",
    "rc_neetcode": "The 150 problems that matter",
    "r_levels": "Know your number",
}

section("Start here")
picks = [(k, RESOURCES[k], why) for k, why in START_HERE.items() if k in RESOURCES]
for row_start in range(0, len(picks), 4):
    cols = st.columns(4)
    for col, (k, v, why) in zip(cols, picks[row_start:row_start + 4]):
        with col:
            with st.container(border=True):
                st.markdown(f"**{v['title']}**")
                st.caption(why)
                st.link_button("Open", v["url"], width="stretch")

# ---------------------------------------------------------------- filters
section("The full library")
f1, f2, f3 = st.columns([2, 2, 3])
with f1:
    track = st.segmented_control(
        "Track",
        options=["all", "finance", "quant", "ai", "career", "research"],
        default="all",
    )
with f2:
    types = ["All"] + sorted({v.get("type", "") for v in RESOURCES.values()})
    typ = st.selectbox("Type", options=types, index=0)
with f3:
    search = st.text_input("Search", placeholder="transformer, repo, dataset, valuation, rag...")

cat = st.selectbox("Category", options=["All"] + all_categories(), index=0)

items = list(RESOURCES.items())
if track != "all":
    items = [(k, v) for k, v in items if v.get("track") == track]
if typ != "All":
    items = [(k, v) for k, v in items if v.get("type") == typ]
if cat != "All":
    items = [(k, v) for k, v in items if v.get("cat") == cat]
if search:
    q = search.lower()
    items = [
        (k, v) for k, v in items
        if q in v["title"].lower()
        or q in v.get("desc", "").lower()
        or q in v.get("type", "").lower()
        or q in v.get("track", "").lower()
    ]

st.caption(f"Showing {len(items)} of {len(RESOURCES)} resources.")
if not items:
    st.info("Nothing matches. Widen the filters.")

groups = defaultdict(list)
for k, v in items:
    groups[v.get("cat", "Other")].append((k, v))

VERDICT = {True: "verified live", False: "dead link — needs replacing", None: "unverified (bot-walled)"}
for group in sorted(groups):
    section(f"{group} ({len(groups[group])})")
    cols = st.columns(2)
    for i, (k, v) in enumerate(sorted(groups[group], key=lambda x: x[1]["title"])):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{v['title']}**")
                st.caption(f"{v['track'].upper()} · {v['type']} · {v.get('cat', '')}")
                st.markdown(v.get("desc", ""))
                rec = linkcheck.for_key(k)
                if rec is not None:
                    st.caption(f"Link check: {VERDICT.get(rec.get('ok'), 'unknown')}")
                st.link_button("Open", v["url"], width="content")

# ---------------------------------------------------------------- stats
section("Catalog stats")
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("**By track**")
    for t, c in sorted(track_counts.items()):
        st.markdown(f"- {t}: {c}")
with s2:
    st.markdown("**By category**")
    for c, n in Counter(v.get("cat") for v in RESOURCES.values()).most_common():
        st.markdown(f"- {c}: {n}")
with s3:
    st.markdown("**By type**")
    for t, n in Counter(v.get("type") for v in RESOURCES.values()).most_common():
        st.markdown(f"- {t}: {n}")
if linkcheck.checked_at():
    st.caption(f"Links last verified {linkcheck.checked_at()} · refresh with `scripts\\check_links.py`")
