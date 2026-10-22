from datetime import date

import pandas as pd
import streamlit as st

from lib import srs
from lib.quiz_bank import Q_BY_ID
from lib.storage import load_progress, log_activity
from lib.ui import hero, inject_css, quote_inline, section
from lib.quotes import quote_for

inject_css()
hero("Daily <em>drill</em>", "Spaced repetition: you see each idea right before you'd forget it. "
     "This is how you remember everything for interviews four months from now.",
     eyebrow="Active recall · Leitner boxes", quote_tags=["focus"])

progress = load_progress()
today = date.today().isoformat()
due, new = srs.due_cards(progress)
queue = due + new
reviewed = progress.get("activity", {}).get(today, {}).get("review", 0)

m = st.columns(4)
m[0].metric("Due reviews", len(due))
m[1].metric("New cards left today", len(new))
m[2].metric("Reviewed today", reviewed)
m[3].metric("Proven retention", f"{srs.overall_retention(progress) * 100:.0f}%")

result = st.session_state.get("drill_result")

if not queue and not result:
    if not progress.get("activity", {}).get(today, {}).get("drill_clear"):
        log_activity(progress, "drill_clear")
    st.success("Drill cleared for today. Your memory is on schedule.", icon=":material/verified:",
               title="Retention locked in")
    quote_inline(quote_for("drill-clear", ["focus", "grind"]))
else:
    if result:
        qid, correct, chosen = result
    else:
        qid = st.session_state.get("drill_card")
        if qid not in queue:
            qid = queue[0]
            st.session_state["drill_card"] = qid
    q = Q_BY_ID[qid]
    card = progress.get("srs", {}).get(qid)
    box = card["box"] if card else 0
    with st.container(border=True):
        st.caption(f"{q['track'].upper()} · {q['module']} · {'New card' if box == 0 else f'Box {box} of 5'}")
        st.markdown(f"### {q['q']}")
        if not result:
            with st.form(f"drill_{qid}"):
                choice = st.radio("Your answer", q["opts"], index=None, label_visibility="collapsed")
                if st.form_submit_button("Check", type="primary"):
                    if choice is None:
                        st.warning("Commit to an answer. Guessing and being wrong teaches more than skipping.")
                    else:
                        ok = choice == q["opts"][q["ans"]]
                        srs.grade(progress, qid, ok)
                        st.session_state["drill_result"] = (qid, ok, choice)
                        st.rerun()
        else:
            new_card = progress["srs"][qid]
            if correct:
                st.success(f"Correct. Promoted to box {new_card['box']} - next review {new_card['due']}.",
                           icon=":material/check_circle:")
            else:
                st.error(f"You chose: {chosen}. Correct: {q['opts'][q['ans']]}. Back to box 1 - you'll see it tomorrow.",
                         icon=":material/replay:")
            st.info(q["exp"], icon=":material/lightbulb:")
            if st.button("Next card", type="primary", icon=":material/arrow_forward:"):
                st.session_state.pop("drill_result", None)
                st.session_state.pop("drill_card", None)
                st.rerun()

section("Mastery map")
st.caption("Khan-style levels from *proven* recall over time - not from pages read. "
           "Familiar → Proficient → Mastered requires answering correctly across growing gaps (1, 3, 7, 16, 35 days).")
table = pd.DataFrame(srs.mastery_table(progress))
if not table.empty:
    st.dataframe(table, hide_index=True, alt="Mastery level per module",
                 column_config={"module": "Module", "title": "Title", "track": "Track",
                                "mastery": st.column_config.ProgressColumn("Mastery", min_value=0, max_value=100, format="%d%%"),
                                "level": "Level"})