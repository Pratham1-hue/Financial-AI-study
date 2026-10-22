import html
from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from lib import accountability as acc
from lib.nyc import NYC_COMP
from lib.storage import load_profile, load_progress
from lib.ui import glass_card, hero, inject_css, section

inject_css()
progress, profile = load_progress(), load_profile()
goal_min = int(profile.get("daily_hours", 6)) * 60
sym = acc.ticker_symbol(profile)

hero(f"${sym} <em>· your career, publicly traded</em>",
     "Every focused hour, every recall, every honest debrief moves the price. Zero days crash it. "
     "The market doesn't care about intentions - only output.",
     eyebrow=f"NYSE: {sym} · IPO {acc.start_date(progress).strftime('%b %d, %Y')} at $100.00",
     quote_tags=["finance"])

rows = acc.stock_series(progress, goal_min)
df = pd.DataFrame(rows)
last = rows[-1]
prev_close = rows[-2]["close"] if len(rows) > 1 else 100.0
chg = (last["close"] / prev_close - 1) * 100
rating, avg5 = acc.analyst_rating(rows)
index, index_parts = acc.mastery_index(progress)
shares = 10_000_000
mcap = last["close"] * shares

m = st.columns(6)
m[0].metric("Price (live)", f"${last['close']:.2f}", f"{chg:+.2f}% today")
m[1].metric("All-time high", f"${df['high'].max():.2f}")
m[2].metric("Market cap", f"${mcap / 1e9:.2f}B")
m[3].metric("Analyst rating", rating)
m[4].metric("Today's score", f"{last['score']}/100")
m[5].metric("Mastery Index", f"{index:.0f}/100")

if last["score"] < acc.ZERO_DAY:
    st.error("Zero-day sell-off in progress: you're down 8% today. Lock in and the market will reprice you.",
             icon=":material/trending_down:", title=f"${sym} is crashing")
elif chg >= 0:
    st.success(f"Up {chg:.2f}% today. Keep stacking - one more block could add another point.",
               icon=":material/trending_up:", title="Buyers are stepping in")
else:
    st.warning("Trading below yesterday's close. Debrief + drill alone add 35 points to today's score.",
               icon=":material/show_chart:", title="Below the open")

# ---------- candlestick ----------
df["date"] = pd.to_datetime(df["date"])
df["dir"] = (df["close"] >= df["open"]).map({True: "Up", False: "Down"})
color = alt.Color("dir:N", scale=alt.Scale(domain=["Up", "Down"], range=["#34D399", "#F87171"]), legend=None)
base = alt.Chart(df).encode(x=alt.X("date:T", title=None))
wick = base.mark_rule().encode(y=alt.Y("low:Q", title="Price ($)", scale=alt.Scale(zero=False)), y2="high:Q", color=color)
body = base.mark_bar(size=14).encode(
    y="open:Q", y2="close:Q", color=color,
    tooltip=[alt.Tooltip("date:T"), "open:Q", "close:Q", "high:Q", "low:Q",
             alt.Tooltip("score:Q", title="Day score"), alt.Tooltip("volume:Q", title="Focus minutes")])
ipo = alt.Chart(pd.DataFrame({"y": [100]})).mark_rule(color="#F5B942", strokeDash=[4, 4]).encode(y="y:Q")
vol = base.mark_bar(size=14, opacity=.7).encode(y=alt.Y("volume:Q", title="Focus min"), color=color).properties(height=90)
st.altair_chart(alt.vconcat((wick + body + ipo).properties(height=300), vol).resolve_scale(x="shared"),
                alt=f"Candlestick chart of ${sym}: daily price driven by your study score, with focus minutes as volume")
st.caption("Daily return = (score - 50) / 50 x 6%. Zero day (score < 10) = -8%. Dashed line = $100 IPO price.")

# ---------- today's tape ----------
left, right = st.columns(2, gap="large")
with left:
    section("Today's earnings breakdown")
    parts, fm = acc.day_parts(progress, date.today(), goal_min)
    for k, v in parts.items():
        st.progress(v / acc.PART_MAX[k], text=f"{k}: {v:.0f}/{acc.PART_MAX[k]}")
    if st.button("Go to today's mission", type="primary", icon=":material/flag:"):
        st.switch_page("app_pages/15_mission.py")
with right:
    section("Mastery Index breakdown")
    for k, v in index_parts.items():
        st.progress(v / acc.MI_MAX[k], text=f"{k}: {v:.1f}/{acc.MI_MAX[k]}")
    st.caption("Mastery Index measures what you can *prove*, not what you consumed. It's the route; the job is the result.")

# ---------- offer letter ----------
section("The letter you're earning")
company = (profile.get("dream_companies") or "Your dream firm").split(",")[0].strip()
role = profile.get("target_role", "Quantitative ML Engineer")
band = NYC_COMP[0][1] if "quant" in role.lower() else NYC_COMP[1][1]
try:
    start_on = date.fromisoformat(profile["target_date"]) + timedelta(days=30)
except (KeyError, ValueError):
    start_on = date.today() + timedelta(days=150)
blur = max(0.0, (90 - index) / 90 * 7)
lock = "" if index >= 90 else (
    f'<div class="offer-lock">Sealed · Mastery Index {index:.0f}/90'
    f'<small>Every point of mastery removes the blur. At 90, it is fully legible.</small></div>')
st.html(
    f'<div class="offer-wrap"><div class="offer" style="filter: blur({blur:.2f}px)">'
    f'<div class="lh"><span class="co">{html.escape(company.upper())}</span><span>New York, NY</span></div>'
    f'<p>Dear {html.escape(profile["name"])},</p>'
    f'<p>On behalf of {html.escape(company)}, I am delighted to offer you the position of '
    f'<b>{html.escape(role)}</b> in our New York office, with a proposed start date of {start_on.strftime("%B %d, %Y")}.</p>'
    f'<p>Your total first-year compensation is expected in the range of <b>{band}</b>, including base salary, '
    f'performance bonus and benefits. What set you apart was not a credential - it was the depth of your understanding '
    f'and the evidence of how relentlessly you learn.</p>'
    f'<p>We look forward to building the future of markets and intelligence with you.</p>'
    f'<p style="margin-top:22px">Sincerely,<br><b>Head of Talent</b><br>{html.escape(company)}</p></div>{lock}</div>'
)
st.caption("A vision letter, not a real offer. Become the best and the real one follows.")