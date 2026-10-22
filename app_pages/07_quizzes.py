import streamlit as st
from lib.ui import hero, section, inject_css, progress_bar
from lib.storage import load_progress, save_progress, record_quiz
from lib.quiz_bank import QUESTIONS, Q_BY_ID
from lib.content import MODULES, MODULE_BY_ID

inject_css()
hero("Quizzes", "Khan Academy style: instant feedback, mastery tracking.")

progress = load_progress()

# Onboarding hand-off: a preset lets "Start the quiz" launch a module quiz directly.
_pre = st.session_state.pop("quiz_preset", None)
_TRACKS = ["all", "finance", "ai", "quant", "career"]
_d_track = _TRACKS.index(_pre["track"]) if _pre and _pre.get("track") in _TRACKS else 0

# Setup
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        track = st.selectbox("Track", options=_TRACKS, index=_d_track)
    with c2:
        mods = ["All"] + [m["id"] for m in MODULES if (track == "all" or m["track"] == track)]
        _d_mod = mods.index(_pre["module"]) if _pre and _pre.get("module") in mods else 0
        mod = st.selectbox("Module", options=mods, index=_d_mod)
    with c3:
        diff = st.selectbox("Difficulty", options=["All", "easy", "medium", "hard"], index=0)
    with c4:
        n = st.number_input("# Questions", min_value=3, max_value=30, value=10)

    pool = QUESTIONS
    if track != "all":
        pool = [q for q in pool if q["track"] == track]
    if mod != "All":
        pool = [q for q in pool if q["module"] == mod]
    if diff != "All":
        pool = [q for q in pool if q["diff"] == diff]

    st.caption(f"Pool size: {len(pool)}")

    if _pre and pool and not st.session_state.get("quiz_qs"):
        import random
        random.seed()
        chosen = list(pool)
        random.shuffle(chosen)
        chosen = chosen[: min(int(_pre.get("n", 5)), len(chosen))]
        st.session_state["quiz_qs"] = [q["id"] for q in chosen]
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_score"] = None
        st.rerun()

    if st.button("Start / Reset Quiz", type="primary"):
        import random
        random.seed()
        chosen = list(pool)
        random.shuffle(chosen)
        chosen = chosen[: min(n, len(chosen))]
        st.session_state["quiz_qs"] = [q["id"] for q in chosen]
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_score"] = None
        st.rerun()

if "quiz_qs" not in st.session_state or not st.session_state["quiz_qs"]:
    st.info("Configure and start a quiz above.")
    st.stop()

qids = st.session_state["quiz_qs"]
questions = [Q_BY_ID[qid] for qid in qids if qid in Q_BY_ID]

# Render questions
answers = st.session_state.get("quiz_answers", {})
for i, q in enumerate(questions, 1):
    st.markdown(f"**Q{i}. {q['q']}**")
    st.caption(f"{q['track'].upper()} · {q['module']} · {q['diff']}")
    opts = q["opts"]
    key = f"q_{q['id']}"
    default = answers.get(q["id"])
    # index of default option
    idx = None
    if default is not None:
        try:
            idx = opts.index(default)
        except ValueError:
            idx = None
    choice = st.radio(
        "Select answer",
        options=opts,
        index=idx,
        key=key,
        label_visibility="collapsed",
    )
    answers[q["id"]] = choice
    st.session_state["quiz_answers"] = answers
    st.markdown("---")

submitted = st.session_state.get("quiz_submitted", False)
if not submitted:
    if st.button("Submit Quiz", type="primary", width="stretch"):
        # score
        score = 0
        total = len(questions)
        wrong_topics = []
        for q in questions:
            chosen = answers.get(q["id"])
            if chosen is not None and chosen == q["opts"][q["ans"]]:
                score += 1
            else:
                wrong_topics.append(q["module"])
        pct = record_quiz(progress, f"quiz_{track}_{mod}_{diff}", score, total)
        st.session_state["quiz_submitted"] = True
        st.session_state["quiz_score"] = (score, total, pct)
        # weak topics update
        from collections import Counter
        c = Counter(wrong_topics)
        weak = [m for m, _ in c.most_common(3)]
        progress["weak_topics"] = list(set(progress.get("weak_topics", []) + weak))
        save_progress(progress)
        st.rerun()
else:
    score, total, pct = st.session_state["quiz_score"]
    section("Results")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Score", f"{score}/{total}")
    with c2:
        st.metric("Percentage", f"{pct}%")
    with c3:
        if pct >= 80:
            st.success("Mastery!")
        elif pct >= 60:
            st.warning("Good, review weak areas")
        else:
            st.error("Needs practice")
    progress_bar(pct, 100, "Mastery threshold 80%")
    from lib.quotes import quote_for
    from lib.ui import quote_inline
    quote_inline(quote_for(f"quiz-{pct}", ["grind", "focus"] if pct < 80 else ["finance", "ai", "nyc"]))

    section("Review")
    for q in questions:
        chosen = answers.get(q["id"])
        correct = q["opts"][q["ans"]]
        ok = chosen == correct
        with st.container(border=True):
            st.markdown(f"**{q['q']}**")
            if ok:
                st.success(f"Correct: {correct}")
            else:
                st.error(f"Your answer: {chosen}  |  Correct: {correct}")
            st.caption(q["exp"])

    if st.button("Retake / New Quiz"):
        st.session_state["quiz_qs"] = []
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_score"] = None
        st.rerun()