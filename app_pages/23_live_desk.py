import time
from datetime import date

import pandas as pd
import streamlit as st

from lib import market_sim as ms
from lib.storage import load_progress, log_activity, save_progress
from lib.ui import hero, inject_css, section

inject_css()
hero(
    "The <em>Desk</em>",
    "A live tape you can trade. Three minutes, real spread, real drawdown, no real money. "
    "This is the closest thing to a trading floor you can run in a browser tab.",
    eyebrow="Dummy real-time practice",
    quote_tags=["risk", "practice"],
)

progress = load_progress()
state = st.session_state.get("desk")


def _start(duration):
    st.session_state["desk"] = ms.new_round(duration=duration)
    st.session_state.pop("desk_result", None)


def _fmt_money(v):
    return f"-${abs(v):,.0f}" if v < 0 else f"${v:,.0f}"


# ---------------------------------------------------------------- start screen
if state is None:
    left, right = st.columns([3, 2], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("### How this works")
            st.markdown(
                "You start with **$100,000**. The tape ticks once a second for three minutes. "
                "Buy or sell at the touch, and the price moves against you when you take size."
            )
            st.markdown(
                "- **Spread is real.** You buy the ask, sell the bid.\n"
                "- **Risk limits are enforced.** 35% per name, 200% gross.\n"
                "- **Return is half the score.** Drawdown, overtrading and rejected orders cost you.\n"
                "- **No thesis, no credit.** Zero trades scores 40."
            )
        with st.container(border=True):
            st.markdown("### The one rule")
            st.markdown(
                "Write the trade **before** you click: what is the edge, where is the stop, "
                "what size makes the stop irrelevant. If you cannot say it in one sentence, don't trade."
            )
            st.caption("A round is a rep. Ten rounds is a habit. The score is there to make you honest, not to make you feel good.")
    with right:
        with st.container(border=True):
            st.markdown("### Start a round")
            duration = st.segmented_control("Length", [120, 180, 300], default=180,
                                            format_func=lambda s: f"{s // 60} min") or 180
            if st.button("Ring the bell", type="primary", icon=":material/notifications_active:",
                         width="stretch"):
                _start(duration)
                st.rerun()
            st.caption(f"Use the {duration // 60}-minute round to match a real desk's attention span.")

        rounds = progress.get("desk_rounds", [])
        if rounds:
            st.markdown("### Your record")
            df = pd.DataFrame(rounds[-8:])[["date", "score", "ret", "bench", "trades"]]
            df["ret"] = (df["ret"] * 100).round(2).astype(str) + "%"
            df["bench"] = (df["bench"] * 100).round(2).astype(str) + "%"
            df.columns = ["Date", "Score", "Return", "S&P", "Trades"]
            st.dataframe(df, hide_index=True, width="stretch")
            avg = sum(r["score"] for r in rounds) / len(rounds)
            st.caption(f"{len(rounds)} rounds · average score {avg:.0f} · best {max(r['score'] for r in rounds)}")
        else:
            st.info("No rounds yet. Your first one is the hardest; the tenth is where it clicks.",
                    icon=":material/flag:")

elif not state.get("done"):
    # ------------------------------------------------------------ live round
    tick = ms.current_tick(state)

    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1], vertical_alignment="bottom")
        sym = c1.selectbox("Instrument", list(ms.SYMBOLS), key="desk_sym",
                           format_func=lambda k: f"{k} · {ms.SYMBOLS[k]['name']}")
        size = c2.number_input("Size ($)", min_value=500, max_value=200_000, value=10_000,
                               step=1_000, key="desk_size")
        bid, mid, ask = ms.quotes(state, sym, tick)
        shares = round(size / max(ask, 0.01), 2)
        if c3.button("Buy", type="primary", width="stretch", key="desk_buy"):
            ok, msg, _ = ms.trade(state, sym, shares, tick)
            if ok:
                st.toast(msg)
            else:
                st.warning(msg)
        if c4.button("Sell", width="stretch", key="desk_sell"):
            ok, msg, _ = ms.trade(state, sym, -shares, tick)
            if ok:
                st.toast(msg)
            else:
                st.warning(msg)
        if c5.button("Flatten", width="stretch", key="desk_flat"):
            for name, q in list(state["pos"].items()):
                if q:
                    ms.trade(state, name, -q, tick)
            st.toast("Flat. Cash is a position.")

        st.caption(f"{sym}  ≈ {shares:,.2f} units  ·  bid {bid:,.2f}  ·  mid {mid:,.2f}  ·  ask {ask:,.2f}  ·  "
                   f"spread {ms.SYMBOLS[sym]['spread'] * 1e4:.0f} bps  ·  "
                   f"max size {ms.MAX_NAME * ms.equity(state, tick):,.0f}")

    @st.fragment(run_every=1.0)
    def panel():
        s = st.session_state["desk"]
        t = ms.current_tick(s)
        if t >= s["duration"]:
            s["done"] = True
            st.rerun()

        ms.snapshot(s, t)
        eq = ms.equity(s, t)
        pnl = eq - ms.START_CASH
        dd = ms.max_drawdown(s["equity"])
        left = s["duration"] - t

        m = st.columns(5)
        m[0].metric("Equity", _fmt_money(eq), f"{pnl / ms.START_CASH * 100:+.2f}%")
        m[1].metric("P&L", _fmt_money(pnl))
        m[2].metric("Max drawdown", f"{dd * 100:.2f}%")
        m[3].metric("Trades", len(s["trades"]), f"limit {ms.MAX_TRADES}")
        m[4].metric("Time left", f"{left // 60}:{left % 60:02d}")

        st.progress(t / s["duration"], text=f"tick {t} / {s['duration']}")

        chart = pd.DataFrame({"You": s["equity"], "S&P 500": s["bench"]})
        st.line_chart(chart, height=260, color=["#d4af37", "#6b7280"])

        st.markdown(f"_{s['headline']}_")

        p1, p2, p3 = st.columns([2, 2, 2], gap="medium")
        with p1:
            st.markdown("**Positions**")
            rows = []
            for name, q in s["pos"].items():
                if not q:
                    continue
                px = s["paths"][name][t]
                upnl = (px - s["avg"][name]) * q
                rows.append({"Sym": name, "Qty": f"{q:,.2f}", "Avg": f"{s['avg'][name]:,.2f}",
                             "Mark": f"{px:,.2f}", "uP&L": f"{upnl:+,.0f}"})
            if rows:
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            else:
                st.caption("Flat. Waiting for an edge.")
            st.caption(f"Gross {ms.gross_exposure(s, t):.0%} of equity (limit {ms.MAX_GROSS:.0%}) · "
                       f"realised {s['realized']:+,.0f}")

        with p2:
            st.markdown("**Order book**")
            bids, asks = ms.book(s, sym, t)
            book = pd.DataFrame(
                [{"Side": "ASK", "Price": f"{p:,.2f}", "Size": n} for p, n in reversed(asks)] +
                [{"Side": "BID", "Price": f"{p:,.2f}", "Size": n} for p, n in bids]
            )
            st.dataframe(book, hide_index=True, width="stretch", height=228)

        with p3:
            st.markdown("**Tape**")
            prints = pd.DataFrame(ms.tape(s, t))
            prints["qty"] = prints["qty"].map(lambda q: f"{q:+,.0f}")
            prints["px"] = prints["px"].map(lambda p: f"{p:,.2f}")
            prints = prints[["sym", "side", "qty", "px"]]
            prints.columns = ["Sym", "Side", "Qty", "Price"]
            st.dataframe(prints, hide_index=True, width="stretch", height=228)

    panel()

    if st.button("Abandon round", icon=":material/close:"):
        st.session_state.pop("desk", None)
        st.rerun()

# ---------------------------------------------------------------- debrief
if state is not None and state.get("done"):
    if not state.get("graded"):
        result = ms.grade(state)
        state["graded"] = True
        state["result"] = result
        rec = {"date": date.today().isoformat(), **result}
        progress.setdefault("desk_rounds", []).append(rec)
        progress["xp"] = progress.get("xp", 0) + result["score"] // 2
        save_progress(progress)
        if result["trades"] > 0:
            log_activity(progress, "desk")
    result = state["result"]

    section("Round debrief")
    d = st.columns(4)
    d[0].metric("Score", result["score"])
    d[1].metric("Return", f"{result['ret'] * 100:+.2f}%", f"S&P {result['bench'] * 100:+.2f}%")
    d[2].metric("Max drawdown", f"{result['dd'] * 100:.2f}%")
    d[3].metric("Trades", result["trades"], f"{result['breaches']} breaches")

    for note in result["notes"]:
        st.markdown(f"- {note}")

    st.caption(f"Realised P&L {result['realized']:+,.0f} · ending equity ${result['equity']:,.0f} · seed {result['seed']}")

    with st.container(border=True):
        st.markdown("**The question that matters**")
        st.markdown(
            "What was your edge on the trade you made? If the answer is 'it was going up', "
            "you did not have one — you had a direction. Write the real answer, then run another round."
        )
        st.text_area("One line: my edge was...", key="desk_edge", height=80,
                     placeholder="e.g. sold strength into a thin tape after a 1.5 sigma move, stop above the high")

    c = st.columns(2)
    if c[0].button("Run another round", type="primary", icon=":material/replay:", width="stretch"):
        _start(state["duration"])
        st.rerun()
    if c[1].button("Leave the desk", icon=":material/logout:", width="stretch"):
        st.session_state.pop("desk", None)
        st.rerun()

    rounds = progress.get("desk_rounds", [])
    if len(rounds) > 1:
        section("Your record")
        hist = pd.DataFrame(rounds)[["date", "score", "ret", "dd", "trades"]]
        hist["ret"] = (hist["ret"] * 100).round(2)
        hist["dd"] = (hist["dd"] * 100).round(2)
        hist.columns = ["Date", "Score", "Return %", "Max DD %", "Trades"]
        st.dataframe(hist.tail(12), hide_index=True, width="stretch")
