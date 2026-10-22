"""Shared UI helpers and NYC-night styling for Project DEVI."""
import html as _html
import math

import streamlit as st

from lib.nyc import skyline_svg
from lib.quotes import quote_for

DEVI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,500&family=Inter:wght@400;500;600;700&family=Great+Vibes&family=JetBrains+Mono:wght@400;700&display=swap');
:root {
  --gold: #F5B942; --gold-2: #FFD982; --ink: #E8ECF4; --muted: #94A3B8;
  --card: rgba(15, 23, 41, 0.78); --border: #22304D; --night: #070B16;
}
.stApp {
  background:
    radial-gradient(1100px 520px at 85% -8%, rgba(245,185,66,0.10), transparent 60%),
    radial-gradient(900px 480px at -10% 8%, rgba(59,130,246,0.12), transparent 60%),
    #070B16;
}
/* Streamlit's fixed header sits on top of the ticker (60px, z-index 999990).
   This is a personal app, so the custom ticker replaces the chrome. */
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0.8rem !important; }
.block-container { padding-top: 0.8rem; padding-bottom: 3rem; max-width: 1280px; }

/* ---------- hero ---------- */
.nyc-hero {
  position: relative; overflow: hidden; border-radius: 22px;
  border: 1px solid var(--border);
  background: linear-gradient(180deg, #081029 0%, #0F1B3F 40%, #2A1E46 72%, #4A2A45 100%);
  padding: 22px 32px 0 32px; margin-bottom: 16px;
  box-shadow: 0 24px 70px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.05);
}
.nyc-hero.big { padding-top: 26px; }
.nyc-eyebrow { letter-spacing: .28em; font-size: .7rem; color: var(--gold);
  text-transform: uppercase; font-weight: 600; font-family: Inter, sans-serif; }
.nyc-hero h1 { font-family: 'Playfair Display', serif; color: #FFFFFF; font-size: 2.2rem;
  line-height: 1.12; margin: .3rem 0 .25rem 0; padding: 0; font-weight: 700; }
.nyc-hero.big h1 { font-size: 2.5rem; }
.nyc-hero h1 em { color: var(--gold-2); font-style: italic; }
.nyc-hero p.sub { color: #CBD5E1; margin: 0; font-size: .98rem; max-width: 760px; }
.nyc-quote { margin-top: 11px; max-width: 760px; font-family: 'Playfair Display', serif;
  font-style: italic; color: #F8E7C0; font-size: 1rem; line-height: 1.45;
  border-left: 3px solid var(--gold); padding-left: 14px; }
.nyc-quote .by { display: block; font-family: Inter, sans-serif; font-style: normal;
  font-size: .72rem; color: var(--gold); margin-top: 3px; letter-spacing: .08em; text-transform: uppercase; }
.skyline { margin: 10px -32px 0 -32px; line-height: 0; height: 112px; overflow: hidden; }
.nyc-hero.big .skyline { height: 118px; }
.skyline svg { width: 100%; height: 100%; display: block; }
.blink { animation: devi-blink 1.8s infinite; }
.twinkle { animation: devi-twinkle 3.2s infinite ease-in-out; }
@keyframes devi-blink { 0%, 100% { opacity: 1; } 50% { opacity: .1; } }
@keyframes devi-twinkle { 0%, 100% { opacity: .9; } 50% { opacity: .2; } }

/* ---------- cards ---------- */
.gold-card { background: linear-gradient(135deg, rgba(245,185,66,.14), rgba(245,185,66,.02));
  border: 1px solid rgba(245,185,66,.38); border-radius: 18px; padding: 18px 22px; margin-bottom: 14px; }
.glass-card { background: var(--card); border: 1px solid var(--border); border-radius: 18px;
  padding: 18px 22px; margin-bottom: 14px; backdrop-filter: blur(8px); }
.card-kicker { font-size: .7rem; letter-spacing: .22em; text-transform: uppercase; color: var(--gold);
  font-weight: 600; margin-bottom: 6px; }
.card-title { font-family: 'Playfair Display', serif; font-size: 1.55rem; color: #FFF; margin: 0 0 4px 0; }
.card-body { color: #CBD5E1; font-size: .96rem; line-height: 1.55; }
.quote-big { font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.35rem;
  color: #FBEFD5; line-height: 1.5; }
.quote-big .by { display: block; margin-top: 10px; font-family: Inter, sans-serif; font-style: normal;
  font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; color: var(--gold); }
.quote-inline { font-family: 'Playfair Display', serif; font-style: italic; color: #F3E3BF;
  border-left: 3px solid var(--gold); padding: 4px 0 4px 14px; margin: 10px 0 16px 0; }
.quote-inline .by { font-family: Inter, sans-serif; font-style: normal; font-size: .75rem;
  color: var(--gold); letter-spacing: .08em; text-transform: uppercase; margin-left: 6px; }

/* ---------- rank ladder ---------- */
.ladder { display: flex; flex-direction: column-reverse; gap: 6px; }
.rung { display: flex; justify-content: space-between; padding: 7px 12px; border-radius: 10px;
  border: 1px solid var(--border); color: var(--muted); font-size: .88rem; background: rgba(10,16,32,.6); }
.rung.done { color: #E2E8F0; border-color: rgba(245,185,66,.25); }
.rung.now { color: #0B1020; background: linear-gradient(90deg, #F5B942, #FFD982); border-color: #F5B942;
  font-weight: 700; box-shadow: 0 0 24px rgba(245,185,66,.35); }

/* ---------- timer ---------- */
.timer-shell { position: relative; width: 100%; max-width: 360px; margin: 6px auto 0 auto; aspect-ratio: 1 / 1; }
.timer-shell svg { width: 100%; height: 100%; filter: drop-shadow(0 0 28px rgba(245,185,66,.18)); }
.timer-center { position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center; }
.timer-phase { font-size: .78rem; letter-spacing: .3em; text-transform: uppercase; font-weight: 700; }
.timer-clock { font-family: 'Inter', sans-serif; font-variant-numeric: tabular-nums;
  font-size: 4.1rem; font-weight: 700; color: #FFFFFF; line-height: 1.05; margin: 4px 0; }
.timer-meta { font-size: .85rem; color: var(--muted); max-width: 230px; }
.mini-timer { border: 1px solid rgba(245,185,66,.4); border-radius: 14px; padding: 10px 14px;
  background: linear-gradient(135deg, rgba(245,185,66,.16), rgba(245,185,66,.03)); }
.mini-timer .ph { font-size: .66rem; letter-spacing: .24em; text-transform: uppercase; font-weight: 700; }
.mini-timer .clk { font-size: 1.9rem; font-weight: 700; color: #FFF; font-variant-numeric: tabular-nums; line-height: 1.1; }
.mini-timer .lb { font-size: .78rem; color: var(--muted); }

/* ---------- ticker tape ---------- */
.ticker-tape { overflow: hidden; white-space: nowrap; border: 1px solid var(--border); border-radius: 10px;
  background: #04070F; margin-bottom: 14px; width: 100%; max-width: 100%; contain: inline-size; }
.stHtml:has(.ticker-tape), div[data-testid="stHtml"]:has(.ticker-tape) { min-width: 0; max-width: 100%; overflow: hidden; }
.ticker-track { display: inline-block; padding: 7px 0; animation: devi-marquee 45s linear infinite;
  font-family: 'JetBrains Mono', monospace; font-size: .8rem; }
.ticker-track span { margin: 0 24px; color: #CBD5E1; }
.ticker-track .sym { color: #FFD982; font-weight: 700; }
.ticker-track .up { color: #34D399; } .ticker-track .down { color: #F87171; }
@keyframes devi-marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }

/* ---------- offer letter & contract ---------- */
.offer-wrap { position: relative; border-radius: 14px; overflow: hidden; }
.offer { background: #FBF8F1; color: #1E293B; padding: 32px 38px; font-family: Georgia, 'Times New Roman', serif; line-height: 1.6; }
.offer .lh { display: flex; justify-content: space-between; align-items: baseline;
  border-bottom: 2px solid #B08D3C; padding-bottom: 10px; margin-bottom: 18px; }
.offer .co { font-size: 1.45rem; font-weight: 700; letter-spacing: .04em; color: #0F172A; }
.offer-lock { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
  justify-content: center; background: rgba(7,11,22,.30); color: #FFD982; font-weight: 800;
  letter-spacing: .18em; text-transform: uppercase; text-align: center; text-shadow: 0 2px 12px #000; }
.offer-lock small { letter-spacing: .05em; text-transform: none; font-weight: 500; color: #F8E7C0; margin-top: 6px; }
.contract { background: #FBF8F1; color: #1E293B; font-family: Georgia, serif; padding: 30px 38px;
  border-radius: 14px; border: 6px double #B08D3C; line-height: 1.7; }
.contract h2 { font-family: 'Playfair Display', serif; color: #0F172A; text-align: center; margin: 0 0 12px 0; letter-spacing: .06em; }
.signature { font-family: 'Great Vibes', cursive; font-size: 2.6rem; color: #1E3A8A; line-height: 1.2; }
.breach { background: linear-gradient(135deg, #3B0A0A, #140405); border: 1px solid #DC2626; border-radius: 20px;
  padding: 30px 34px; margin-bottom: 18px; box-shadow: 0 0 60px rgba(220,38,38,.25); }
.breach h1 { font-family: 'Playfair Display', serif; color: #FCA5A5; margin: 0 0 8px 0; font-size: 2.3rem; }
.breach p { color: #FECACA; margin: 0; }
.score-big { font-family: 'Playfair Display', serif; font-size: 4.2rem; font-weight: 800; line-height: 1; }

/* ---------- streamlit elements ---------- */
.devi-section-title { font-family: 'Playfair Display', serif; font-size: 1.45rem; font-weight: 700;
  color: #FFFFFF; margin: 1.6rem 0 .7rem 0; padding-left: .75rem; border-left: 4px solid var(--gold); }
div[data-testid="stMetric"] { background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; padding: 12px 16px; backdrop-filter: blur(6px); }
div[data-testid="stMetricValue"] { color: var(--gold-2); }
div[data-testid="stMetricLabel"] p { letter-spacing: .06em; text-transform: uppercase; font-size: .72rem; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 6px 14px; }
</style>
"""


def inject_css():
    st.markdown(DEVI_CSS, unsafe_allow_html=True)


def _esc(s):
    return _html.escape(str(s))


def hero(title, subtitle, eyebrow="New York City · 40.7128° N, 74.0060° W", big=False, quote_tags=None, show_quote=True):
    q = quote_for(title, quote_tags) if show_quote else None
    quote_html = (f'<div class="nyc-quote">&ldquo;{_esc(q["text"])}&rdquo;'
                  f'<span class="by">&mdash; {_esc(q["author"])}</span></div>') if q else ""
    st.html(
        f'<div class="nyc-hero{" big" if big else ""}">'
        f'<div class="nyc-eyebrow">{_esc(eyebrow)}</div>'
        f'<h1>{title}</h1><p class="sub">{_esc(subtitle)}</p>{quote_html}'
        f'<div class="skyline">{skyline_svg()}</div></div>'
    )


def section(title):
    st.markdown(f'<div class="devi-section-title">{_esc(title)}</div>', unsafe_allow_html=True)


def quote_inline(q):
    st.html(f'<div class="quote-inline">&ldquo;{_esc(q["text"])}&rdquo;<span class="by">&mdash; {_esc(q["author"])}</span></div>')


def quote_card(q, kicker="Quote of the day"):
    st.html(
        f'<div class="gold-card"><div class="card-kicker">{_esc(kicker)}</div>'
        f'<div class="quote-big">&ldquo;{_esc(q["text"])}&rdquo;<span class="by">&mdash; {_esc(q["author"])}</span></div></div>'
    )


def glass_card(kicker, title, body_html):
    st.html(
        f'<div class="glass-card"><div class="card-kicker">{_esc(kicker)}</div>'
        f'<div class="card-title">{title}</div><div class="card-body">{body_html}</div></div>'
    )


def rank_ladder(ranks, current_name):
    rows = []
    reached = True
    for hrs, name, _ in ranks:
        if name == current_name:
            cls = "now"
        elif reached:
            cls = "done"
        else:
            cls = ""
        rows.append(f'<div class="rung {cls}"><span>{_esc(name)}</span><span>{hrs}h</span></div>')
        if name == current_name:
            reached = False
    st.html(f'<div class="ladder">{"".join(rows)}</div>')


def timer_ring(remaining_s, total_s, phase_label, color, clock, meta, paused=False):
    r = 130
    circ = 2 * math.pi * r
    frac = 0.0 if total_s <= 0 else max(0.0, min(1.0, 1 - remaining_s / total_s))
    offset = circ * (1 - frac)
    stroke = "#64748B" if paused else color
    ticks = []
    for i in range(60):
        a = 2 * math.pi * i / 60
        r1, r2 = (150, 158) if i % 5 == 0 else (153, 157)
        x1, y1 = 170 + r1 * math.sin(a), 170 - r1 * math.cos(a)
        x2, y2 = 170 + r2 * math.sin(a), 170 - r2 * math.cos(a)
        ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#334155" stroke-width="{2 if i % 5 == 0 else 1}"/>')
    st.html(
        f'<div class="timer-shell"><svg viewBox="0 0 340 340" xmlns="http://www.w3.org/2000/svg">'
        f'{"".join(ticks)}'
        f'<circle cx="170" cy="170" r="{r}" stroke="#16213D" stroke-width="16" fill="none"/>'
        f'<circle cx="170" cy="170" r="{r}" stroke="{stroke}" stroke-width="16" fill="none" stroke-linecap="round" '
        f'stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}" transform="rotate(-90 170 170)"/>'
        f'</svg><div class="timer-center">'
        f'<div class="timer-phase" style="color:{stroke}">{_esc(phase_label)}{" · paused" if paused else ""}</div>'
        f'<div class="timer-clock">{_esc(clock)}</div>'
        f'<div class="timer-meta">{_esc(meta)}</div></div></div>'
    )


def progress_bar(value, maxv=100, label=""):
    pct = min(100, round(100 * value / max(maxv, 1)))
    if label:
        st.caption(label)
    st.progress(pct / 100)


def badge(text, kind="core"):
    return f"**{text}**"


def xp_level(xp):
    level = xp // 500 + 1
    title = {1: "Novice", 2: "Apprentice", 3: "Practitioner", 4: "Specialist",
             5: "Expert", 6: "Master", 7: "Grandmaster"}.get(min(level, 7), "Legend")
    return level, title