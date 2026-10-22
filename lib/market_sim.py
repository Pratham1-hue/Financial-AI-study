"""A dummy but realistic market you can trade in real time.

The tape is synthetic (seeded, reproducible) but behaves like a market: correlated
moves, jumps, spread, market impact and a benchmark. Rounds are short (3 minutes)
so practice is repeatable, and every round is graded on return *and* discipline.

No network. No real money. No random rewards for button-mashing: overtrading and
risk-limit breaches cost you score.
"""
from __future__ import annotations

import math
import random
import time

TICKS = 180                 # one tick per second, 3 minute rounds
START_CASH = 100_000.0
MAX_GROSS = 2.0             # gross exposure <= 2x equity
MAX_NAME = 0.35             # single name <= 35% of equity
MAX_TRADES = 14             # beyond this you are gambling, not trading
BENCH = "SPX"

SYMBOLS = {
    "SPX": {"name": "S&P 500 Index", "px": 5210.0, "vol": 0.00030, "drift": 0.000008,
            "spread": 0.00006, "beta": 1.00, "kind": "index"},
    "NDX": {"name": "Nasdaq 100", "px": 18340.0, "vol": 0.00042, "drift": 0.000012,
            "spread": 0.00008, "beta": 1.15, "kind": "index"},
    "NVX": {"name": "NVX Semiconductor", "px": 118.40, "vol": 0.00105, "drift": 0.000030,
            "spread": 0.00020, "beta": 1.60, "kind": "stock"},
    "BTC": {"name": "Bitcoin", "px": 67250.0, "vol": 0.00150, "drift": 0.000020,
            "spread": 0.00040, "beta": 0.70, "kind": "crypto"},
}

HEADLINES = [
    "Desk chatter: flows are thin into the close.",
    "A large seller is working an order in semis.",
    "Rates tick higher after a strong auction.",
    "Risk parity funds are rebalancing today.",
    "Volatility buyers step in; dealers shorten gamma.",
    "Macro headline crosses: growth revised slightly higher.",
    "Breadth improves; small caps outperform.",
    "A big print lifts the tape, then fades.",
]


# ---------------------------------------------------------------- the tape
def build_paths(seed):
    """Correlated geometric random walks with occasional jumps. Deterministic."""
    rnd = random.Random(seed)
    n = TICKS + 1
    market = [0.0]
    for _ in range(n - 1):
        market.append(market[-1] + rnd.gauss(0.0, 0.00030))

    paths = {}
    for sym, cfg in SYMBOLS.items():
        series = [cfg["px"]]
        for i in range(1, n):
            r = cfg["drift"] + cfg["beta"] * (market[i] - market[i - 1]) + rnd.gauss(0.0, cfg["vol"])
            if rnd.random() < 0.0018:                       # a genuine jump
                r += rnd.choice((-1.0, 1.0)) * cfg["vol"] * rnd.uniform(4.0, 7.0)
            series.append(max(0.01, series[-1] * math.exp(r)))
        paths[sym] = series
    return paths


def new_round(seed=None, duration=TICKS):
    seed = seed if seed is not None else random.randrange(1_000_000)
    paths = build_paths(seed)
    return {
        "seed": seed,
        "duration": duration,
        "paths": paths,
        "start": time.time(),
        "cash": START_CASH,
        "pos": {s: 0.0 for s in SYMBOLS},
        "avg": {s: 0.0 for s in SYMBOLS},
        "realized": 0.0,
        "trades": [],
        "equity": [],
        "bench": [],
        "breaches": 0,
        "done": False,
        "graded": False,
        "headline": HEADLINES[seed % len(HEADLINES)],
        "last": {s: paths[s][0] for s in SYMBOLS},
    }


def current_tick(state):
    elapsed = time.time() - state["start"]
    return max(0, min(int(elapsed), state["duration"]))


def quotes(state, sym, tick):
    """(bid, mid, ask) with a half-spread."""
    mid = state["paths"][sym][tick]
    half = SYMBOLS[sym]["spread"] / 2.0
    return mid * (1 - half), mid, mid * (1 + half)


def position_value(state, tick):
    return sum(q * state["paths"][s][tick] for s, q in state["pos"].items())


def equity(state, tick):
    return state["cash"] + position_value(state, tick)


def gross_exposure(state, tick):
    gross = sum(abs(q * state["paths"][s][tick]) for s, q in state["pos"].items())
    eq = max(equity(state, tick), 1.0)
    return gross / eq


def max_drawdown(curve):
    peak, worst = -1e18, 0.0
    for v in curve:
        peak = max(peak, v)
        if peak > 0:
            worst = min(worst, v / peak - 1.0)
    return worst


# ---------------------------------------------------------------- trading
def trade(state, sym, qty, tick):
    """Market order. Returns (ok, message, fill_price)."""
    if qty == 0:
        return False, "Size is zero.", None
    bid, mid, ask = quotes(state, sym, tick)
    side = 1 if qty > 0 else -1
    fill = ask if qty > 0 else bid
    notional = abs(qty) * fill

    # market impact grows with size relative to the account
    impact = min(0.0025, notional / (START_CASH * 12))
    fill *= 1 + side * impact

    if notional < 50:
        return False, "Minimum order is $50 notional.", None

    new_pos = state["pos"][sym] + qty
    new_gross = (sum(abs(q * state["paths"][s][tick]) for s, q in state["pos"].items()
                     if s != sym) + abs(new_pos * fill)) / max(equity(state, tick), 1.0)
    name_pct = abs(new_pos * fill) / max(equity(state, tick), 1.0)

    if new_gross > MAX_GROSS + 1e-9:
        state["breaches"] += 1
        return False, f"Rejected: gross exposure would be {new_gross:.0%} (limit {MAX_GROSS:.0%}).", None
    if name_pct > MAX_NAME + 1e-9:
        state["breaches"] += 1
        return False, f"Rejected: {sym} would be {name_pct:.0%} of equity (limit {MAX_NAME:.0%}).", None

    old_qty, old_avg = state["pos"][sym], state["avg"][sym]
    state["cash"] -= qty * fill

    if old_qty == 0 or (old_qty > 0) == (qty > 0):
        total = old_qty + qty
        state["avg"][sym] = (abs(old_qty) * old_avg + abs(qty) * fill) / abs(total)
    else:
        closing = min(abs(qty), abs(old_qty))
        pnl = closing * (fill - old_avg) * (1 if old_qty > 0 else -1)
        state["realized"] += pnl
        if abs(qty) >= abs(old_qty):
            state["avg"][sym] = 0.0 if abs(qty) == abs(old_qty) else fill
        # partial close keeps the old average
    state["pos"][sym] = new_pos if abs(new_pos) > 1e-9 else 0.0
    if state["pos"][sym] == 0.0:
        state["avg"][sym] = 0.0

    state["trades"].append({
        "t": tick, "sym": sym, "qty": qty, "px": round(fill, 2),
        "side": "BUY" if qty > 0 else "SELL",
    })
    return True, f"Filled {abs(qty):,.0f} {sym} @ {fill:,.2f}", fill


def book(state, sym, tick, levels=5):
    """Synthetic depth around the mid, stable for a given tick."""
    bid, mid, ask = quotes(state, sym, tick)
    rnd = random.Random(f"{state['seed']}:{sym}:{tick}")
    step = mid * 0.00025
    bids = [(bid - i * step, rnd.randint(20, 400)) for i in range(levels)]
    asks = [(ask + i * step, rnd.randint(20, 400)) for i in range(levels)]
    return bids, asks


def tape(state, tick, n=7):
    """Recent prints, mixing the participant's fills with market colour."""
    mine = [t for t in state["trades"] if t["t"] <= tick][-4:]
    rnd = random.Random(f"{state['seed']}:tape:{tick}")
    for _ in range(n - len(mine)):
        sym = rnd.choice(list(SYMBOLS))
        bid, mid, ask = quotes(state, sym, tick)
        px = bid if rnd.random() < 0.5 else ask
        mine.append({"t": tick, "sym": sym, "qty": rnd.choice((-1, 1)) * rnd.randint(1, 250),
                     "px": round(px, 2), "side": "BUY" if px == ask else "SELL"})
    return sorted(mine, key=lambda r: r["t"])[-n:]


# ---------------------------------------------------------------- grading
def snapshot(state, tick):
    """Append equity and benchmark points exactly once per tick."""
    if tick <= state.get("_last_snap", -1):
        return
    state["_last_snap"] = tick
    state["equity"].append(equity(state, tick))
    p0 = state["paths"][BENCH][0]
    state["bench"].append(START_CASH * state["paths"][BENCH][tick] / p0)


def grade(state):
    """Score 0-100. Return is only half the story; discipline is the rest."""
    tick = state["duration"]
    end_eq = equity(state, tick)
    ret = end_eq / START_CASH - 1.0
    bench = state["paths"][BENCH][tick] / state["paths"][BENCH][0] - 1.0
    dd = max_drawdown(state["equity"] or [START_CASH, end_eq])
    n_trades = len(state["trades"])

    score = 50.0
    score += max(-30.0, min(35.0, ret * 2000))          # 1% = 20 points
    score += max(-10.0, min(10.0, (ret - bench) * 800))  # versus benchmark
    score -= max(0.0, (abs(dd) - 0.01) * 900)            # drawdown hurts
    score -= max(0, n_trades - MAX_TRADES) * 2.5         # overtrading
    score -= state["breaches"] * 8                       # rejected risk
    if n_trades == 0:
        score = min(score, 40.0)                         # no decisions, no credit

    score = round(max(0.0, min(100.0, score)))

    notes = []
    if n_trades == 0:
        notes.append("You never traded. Practice means making decisions under uncertainty.")
    if state["breaches"]:
        notes.append(f"{state['breaches']} risk-limit breach(es). Size to the limit, not past it.")
    if n_trades > MAX_TRADES:
        notes.append(f"{n_trades} trades in 3 minutes. That's clicking, not a thesis.")
    if dd < -0.02:
        notes.append(f"Max drawdown {dd:.1%}. You were sized too big for your conviction.")
    if ret > bench + 0.002:
        notes.append(f"Beat the benchmark by {(ret - bench) * 100:.2f} pts.")
    elif ret < bench - 0.002:
        notes.append(f"Underperformed the benchmark by {(bench - ret) * 100:.2f} pts.")
    if not notes:
        notes.append("Clean round: sane size, no breaches.")

    return {
        "score": score,
        "ret": round(ret, 5),
        "bench": round(bench, 5),
        "dd": round(dd, 5),
        "trades": n_trades,
        "breaches": state["breaches"],
        "realized": round(state["realized"], 2),
        "equity": round(end_eq, 2),
        "notes": notes,
        "seed": state["seed"],
    }
