import html
from datetime import date, datetime

import streamlit as st

from lib import accountability as acc
from lib.storage import load_profile, load_progress, save_progress
from lib.ui import hero, inject_css, section

AVERAGE = "I choose to be average"

NON_NEGOTIABLES = [
    "Hit my daily locked-in hours",
    "Clear my retention drill",
    "Prove it: one quiz at 80%+",
    "Write code or practice every day",
    "Feynman debrief every night",
    "No phone during focus blocks",
    "Sleep 7+ hours (the brain encodes memory while you sleep)",
]

inject_css()
progress, profile = load_progress(), load_profile()
goal_min = int(profile.get("daily_hours", 6)) * 60
contract = progress.get("contract")

hero("The <em>contract</em>", "Motivation fades by Thursday. A signed commitment with real stakes doesn't.",
     eyebrow="Binding between you and the person you're becoming", quote_tags=["grind"])

if not contract:
    st.html(
        '<div class="contract"><h2>THE OATH</h2>'
        '<p>I am not here to get a job. I am here to become one of the best in the world at finance and AI - '
        'and the best job in New York City will be the consequence.</p>'
        '<p>I will learn the way the best learn: active recall over rereading, spaced repetition over cramming, '
        'explaining over highlighting, building over watching.</p>'
        '<p>I will not have zero days. If I break this contract, I will write an honest incident report and '
        'pay the stake I set below - no excuses, no renegotiation.</p>'
        '<p>Sixteen weeks. Then the city.</p></div>'
    )
    with st.form("sign"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name (your signature)", value=profile.get("name", ""))
        partner = c2.text_input("Accountability partner (name + how they'll know)", placeholder="e.g. Rahul - I'll send him my $TICKER every Sunday")
        stakes = st.text_area("My stake if I break it", height=80,
                              placeholder="e.g. Donate $50 to a cause I dislike / no gaming for a week / tell my partner and post my failure")
        nn = st.multiselect("My non-negotiables", NON_NEGOTIABLES, default=NON_NEGOTIABLES[:5])
        hard = st.toggle("Hard mode: lock the app after a zero day until I file an incident report", value=True)
        confirm = st.text_input("Type your full name again to sign")
        if st.form_submit_button("Sign the contract", type="primary", icon=":material/draw:"):
            if not name.strip() or confirm.strip() != name.strip():
                st.error("Signatures don't match. Commitment starts with precision.")
            elif not stakes.strip():
                st.error("A contract without stakes is a wish. Set a real stake.")
            else:
                progress["contract"] = {"name": name.strip(), "partner": partner.strip(), "stakes": stakes.strip(),
                                        "non_negotiables": nn, "hard_mode": hard,
                                        "signed_on": date.today().isoformat(),
                                        "signed_at": datetime.now().isoformat(timespec="minutes")}
                save_progress(progress)
                st.balloons()
                st.rerun()
    st.stop()

# ---------- signed ----------
days_in = (date.today() - date.fromisoformat(contract["signed_on"])).days
breaches = acc.unresolved_breaches(progress, goal_min)
incidents = progress.get("incidents", {})

m = st.columns(4)
m[0].metric("Days under contract", days_in)
m[1].metric("Open breaches", len(breaches))
m[2].metric("Incidents filed", len(incidents))
m[3].metric("Hard mode", "On" if contract.get("hard_mode") else "Off")

nn_html = "".join(f"<li>{html.escape(x)}</li>" for x in contract.get("non_negotiables", []))
st.html(
    f'<div class="contract"><h2>THE CONTRACT</h2>'
    f'<p>I am not here to get a job. I am here to become one of the best in the world at finance and AI - '
    f'and the best job in New York City will be the consequence.</p>'
    f'<p><b>My non-negotiables:</b></p><ul>{nn_html}</ul>'
    f'<p><b>If I break this, I will:</b> {html.escape(contract.get("stakes", ""))}</p>'
    f'<p><b>Witness:</b> {html.escape(contract.get("partner") or "myself")}</p>'
    f'<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:18px">'
    f'<div><div class="signature">{html.escape(contract["name"])}</div>Signed {contract["signed_at"].replace("T", " ")}</div>'
    f'<div style="text-align:right">New York, NY<br>Day {days_in} of 112</div></div></div>'
)

if breaches:
    section("Breaches - file your incident reports")
    st.error(f"You broke the contract on {len(breaches)} day(s). Pay your stake: {contract.get('stakes')}",
             icon=":material/gavel:", title="Contract breached")
    for d in breaches:
        with st.form(f"incident_{d}"):
            st.markdown(f"**Incident report · {date.fromisoformat(d).strftime('%A, %B %d')}**")
            what = st.text_area("What actually happened? (no excuses, just facts)", key=f"w_{d}")
            cause = st.text_area("Root cause - what system failed?", key=f"c_{d}")
            fix = st.text_area("The specific change I'm making so it never happens again", key=f"f_{d}")
            paid = st.checkbox(f"I have paid my stake: {contract.get('stakes')}", key=f"p_{d}")
            if st.form_submit_button("File report", type="primary"):
                if min(len(what.strip()), len(cause.strip()), len(fix.strip())) < 20 or not paid:
                    st.error("Every field needs real thought (20+ characters) and the stake must be paid.")
                else:
                    progress.setdefault("incidents", {})[d] = {"what": what, "cause": cause, "fix": fix,
                                                               "filed": datetime.now().isoformat(timespec="minutes")}
                    save_progress(progress)
                    st.rerun()
else:
    st.success("Contract intact. Keep it that way.", icon=":material/verified:")

if incidents:
    with st.expander(f"Incident history ({len(incidents)})"):
        for d, r in sorted(incidents.items(), reverse=True):
            st.markdown(f"**{d}** - *Fix:* {r['fix']}")

section("Hard mode")
if contract.get("hard_mode"):
    st.caption("To turn hard mode off, type the phrase below exactly. Read it out loud first.")
    phrase = st.text_input(f'Type "{AVERAGE}"', key="avg_phrase")
    if st.button("Turn off hard mode", disabled=phrase.strip() != AVERAGE):
        contract["hard_mode"] = False
        save_progress(progress)
        st.rerun()
else:
    st.warning("Hard mode is off. The best don't need a lock - but they don't need an escape hatch either.",
               icon=":material/lock_open:")
    if st.button("Turn hard mode back on", type="primary", icon=":material/lock:"):
        contract["hard_mode"] = True
        save_progress(progress)
        st.rerun()