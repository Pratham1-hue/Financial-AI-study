"""NYC visuals: procedural skyline SVG and the locked-in-hours rank ladder."""
import random
from functools import lru_cache

WINDOW = "#F7C873"


def _windows(rnd, x, y, w, h, density):
    out = []
    cols = max(1, int((w - 6) // 7))
    rows = max(1, int((h - 8) // 9))
    for r in range(rows):
        for c in range(cols):
            if rnd.random() < density:
                op = round(rnd.uniform(0.35, 0.95), 2)
                out.append(f'<rect x="{x + 4 + c * 7:.1f}" y="{y + 6 + r * 9:.1f}" width="3" height="4" fill="{WINDOW}" opacity="{op}"/>')
    return "".join(out)


def _building(rnd, x, base, w, h, fill, density):
    y = base - h
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>']
    if rnd.random() < 0.3:
        parts.append(f'<rect x="{x + w * 0.3:.1f}" y="{y - 8}" width="{w * 0.4:.1f}" height="8" fill="{fill}"/>')
    parts.append(_windows(rnd, x, y, w, h, density))
    return "".join(parts)


def _empire_state(x, base, fill, rnd):
    tiers = [(70, 150), (54, 190), (40, 225), (26, 250), (14, 268), (6, 285)]
    parts = []
    for w, top in tiers:
        parts.append(f'<rect x="{x - w / 2}" y="{base - top}" width="{w}" height="{top}" fill="{fill}"/>')
    parts.append(f'<rect x="{x - 1.5}" y="{base - 318}" width="3" height="34" fill="{fill}"/>')
    parts.append(f'<circle class="blink" cx="{x}" cy="{base - 320}" r="2.6" fill="#FF4D4D"/>')
    parts.append(_windows(rnd, x - 35, base - 150, 70, 150, 0.45))
    parts.append(_windows(rnd, x - 20, base - 225, 40, 75, 0.5))
    return "".join(parts)


def _one_wtc(x, base, fill, rnd):
    h = 300
    parts = [
        f'<polygon points="{x - 34},{base} {x + 34},{base} {x + 16},{base - h} {x - 16},{base - h}" fill="{fill}"/>',
        f'<polygon points="{x - 34},{base} {x},{base - h} {x - 16},{base - h}" fill="#1A2647" opacity="0.6"/>',
        f'<rect x="{x - 1.2}" y="{base - h - 55}" width="2.4" height="55" fill="{fill}"/>',
        f'<circle class="blink" cx="{x}" cy="{base - h - 57}" r="2.6" fill="#FF4D4D"/>',
    ]
    parts.append(_windows(rnd, x - 22, base - 260, 44, 250, 0.35))
    return "".join(parts)


def _chrysler(x, base, fill, rnd):
    parts = [f'<rect x="{x - 22}" y="{base - 200}" width="44" height="200" fill="{fill}"/>']
    for i, w in enumerate([36, 28, 20, 12]):
        y = base - 200 - i * 14
        parts.append(f'<path d="M{x - w / 2},{y} Q{x},{y - 22} {x + w / 2},{y} Z" fill="{fill}"/>')
        parts.append(f'<path d="M{x - w / 2 + 4},{y - 2} Q{x},{y - 18} {x + w / 2 - 4},{y - 2}" stroke="{WINDOW}" stroke-width="0.8" fill="none" opacity="0.7"/>')
    parts.append(f'<rect x="{x - 1}" y="{base - 290}" width="2" height="40" fill="{fill}"/>')
    parts.append(_windows(rnd, x - 22, base - 200, 44, 200, 0.45))
    return "".join(parts)


@lru_cache(maxsize=8)
def skyline_svg(width=1400, height=340, seed=11):
    rnd = random.Random(seed)
    base = height
    out = [f'<svg viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">']
    # stars
    for _ in range(70):
        sx, sy = rnd.uniform(0, width), rnd.uniform(0, height * 0.45)
        cls = ' class="twinkle"' if rnd.random() < 0.35 else ""
        out.append(f'<circle{cls} cx="{sx:.1f}" cy="{sy:.1f}" r="{rnd.uniform(0.4, 1.3):.2f}" fill="#FFFFFF" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>')
    # moon
    out.append(f'<circle cx="{width * 0.88}" cy="60" r="22" fill="#FFF3D1" opacity="0.9"/>')
    out.append(f'<circle cx="{width * 0.88 + 9}" cy="54" r="20" fill="#0E1838" opacity="0.85"/>')
    # far layer
    x = -10
    while x < width:
        w = rnd.randint(30, 70)
        out.append(_building(rnd, x, base, w, rnd.randint(70, 170), "#111C3A", 0.12))
        x += w + rnd.randint(-6, 4)
    # near layer
    x = -10
    while x < width:
        w = rnd.randint(36, 80)
        out.append(_building(rnd, x, base, w, rnd.randint(40, 130), "#0A1226", 0.22))
        x += w + rnd.randint(2, 12)
    # landmarks
    out.append(_chrysler(width * 0.44, base, "#0B1430", rnd))
    out.append(_empire_state(width * 0.30, base, "#0B1430", rnd))
    out.append(_one_wtc(width * 0.74, base, "#0B1430", rnd))
    # river glow
    out.append(f'<rect x="0" y="{base - 4}" width="{width}" height="4" fill="#F5B942" opacity="0.25"/>')
    out.append("</svg>")
    return "".join(out)


# ---------- NYC rank ladder (by locked-in hours) ----------
RANKS = [
    (0, "Tourist in Times Square", "Everyone starts here. You just bought the ticket."),
    (5, "Subway Commuter", "You've started showing up. The city notices consistency."),
    (15, "Brooklyn Intern", "The basics are clicking. Keep stacking hours."),
    (40, "Midtown Analyst", "You can model, code, and explain. Analysts get hired here."),
    (80, "Wall Street Associate", "Real depth. Your projects start to speak for you."),
    (150, "Hudson Yards ML Engineer", "Production-grade skills. Recruiters reply now."),
    (250, "Hedge Fund VP", "Top 5% of candidates put in this many deliberate hours."),
    (400, "Quant Partner", "Elite. Interviews feel like conversations."),
    (600, "Billionaires' Row Penthouse", "You did the work most people only talk about."),
]


def rank_for(hours):
    current = RANKS[0]
    nxt = None
    for i, r in enumerate(RANKS):
        if hours >= r[0]:
            current = r
            nxt = RANKS[i + 1] if i + 1 < len(RANKS) else None
    if nxt:
        span = nxt[0] - current[0]
        pct = (hours - current[0]) / span if span else 1.0
    else:
        pct = 1.0
    return current, nxt, max(0.0, min(1.0, pct))


# Rough, public-data-based NYC total comp bands. Always verify on levels.fyi / Glassdoor.
NYC_COMP = [
    ("Quant Researcher / Trader (prop shops, hedge funds)", "$250k - $500k+"),
    ("ML Engineer (Big Tech, NYC)", "$200k - $400k"),
    ("Data Scientist (Fintech / Banks)", "$150k - $250k"),
    ("Investment Banking Analyst", "$110k - $200k"),
]