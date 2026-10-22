import streamlit as st
from lib.ui import hero, section, inject_css, progress_bar
from lib.storage import load_progress, save_progress, record_exam
from lib.quiz_bank import Q_BY_ID, exam_questions
from lib.study_plan import EXAMS

inject_css()
hero("Exams", "Phase-gate exams. Pass to unlock the next phase.")

progress = load_progress()

exam_id = st.selectbox("Exam", options=list(EXAMS.keys()), format_func=lambda e: f"{e} - {EXAMS[e]['title']}")
exam = EXAMS[exam_id]
st.caption(f"Passing score: {exam['pass']}%")

qs = exam_questions(exam_id)
st.caption(f"{len(qs)} questions")

if exam_id in progress.get("exam_scores", {}):
    st.info(f"Previous best: {progress['exam_scores'][exam_id]['score']}%")

# session state key per exam
ss_key = f"exam_{exam_id}"
if ss_key not in st.session_state:
    st.session_state[ss_key] = {"started": False, "answers": {}, "submitted": False, "score": None}

state = st.session_state[ss_key]

if not state["started"]:
    if st.button("Start Exam", type="primary"):
        state["started"] = True
        state["answers"] = {}
        state["submitted"] = False
        state["score"] = None
        st.rerun()
    st.stop()

if not state["submitted"]:
    for i, q in enumerate(qs, 1):
        st.markdown(f"**Q{i}. {q['q']}**")
        opts = q["opts"]
        default = state["answers"].get(q["id"])
        idx = opts.index(default) if default in opts else None
        choice = st.radio("Answer", options=opts, index=idx, key=f"exam_{exam_id}_{q['id']}", label_visibility="collapsed")
        state["answers"][q["id"]] = choice
        st.markdown("---")
    if st.button("Submit Exam", type="primary", width="stretch"):
        score = 0
        for q in qs:
            if state["answers"].get(q["id"]) == q["opts"][q["ans"]]:
                score += 1
        pct = record_exam(progress, exam_id, score, len(qs))
        state["submitted"] = True
        state["score"] = (score, len(qs), pct)
        st.rerun()
else:
    score, total, pct = state["score"]
    section("Result")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Score", f"{score}/{total}")
    with c2:
        st.metric("Percentage", f"{pct}%")
    with c3:
        if pct >= exam["pass"]:
            st.success("PASSED")
        else:
            st.error("FAILED - review and retake")
    progress_bar(pct, 100, f"Pass: {exam['pass']}%")
    from lib.quotes import quote_for
    from lib.ui import quote_inline
    quote_inline(quote_for(f"exam-{exam_id}-{pct}", ["nyc", "finance"] if pct >= exam["pass"] else ["grind"]))

    with st.expander("Review answers"):
        for q in qs:
            chosen = state["answers"].get(q["id"])
            correct = q["opts"][q["ans"]]
            if chosen == correct:
                st.success(f"{q['q']} -> {correct}")
            else:
                st.error(f"{q['q']} -> yours: {chosen} | correct: {correct}")
            st.caption(q["exp"])

    if st.button("Retake"):
        state["started"] = False
        state["submitted"] = False
        state["answers"] = {}
        state["score"] = None
        st.rerun()