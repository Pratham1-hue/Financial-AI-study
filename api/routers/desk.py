"""Live Desk: a synthetic but realistic market you trade in real time."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import deps
from lib import market_sim as ms

router = APIRouter()


def _round_payload(rid, state):
    tick = ms.current_tick(state)
    ms.snapshot(state, tick)
    quotes = {}
    for sym in ms.SYMBOLS:
        bid, mid, ask = ms.quotes(state, sym, tick)
        quotes[sym] = {"bid": round(bid, 2), "mid": round(mid, 2), "ask": round(ask, 2),
                       "name": ms.SYMBOLS[sym]["name"], "kind": ms.SYMBOLS[sym]["kind"]}
    positions = []
    for sym, qty in state["pos"].items():
        if abs(qty) > 1e-9:
            px = state["paths"][sym][tick]
            positions.append({"sym": sym, "qty": round(qty, 2), "avg": round(state["avg"][sym], 2),
                              "px": round(px, 2), "value": round(qty * px, 2),
                              "pnl": round(qty * (px - state["avg"][sym]), 2)})
    bench0 = state["paths"][ms.BENCH][0]
    return {
        "round_id": rid,
        "tick": tick,
        "duration": state["duration"],
        "remaining": max(0, state["duration"] - tick),
        "done": tick >= state["duration"],
        "graded": state["graded"],
        "headline": state["headline"],
        "seed": state["seed"],
        "quotes": quotes,
        "positions": positions,
        "cash": round(state["cash"], 2),
        "realized": round(state["realized"], 2),
        "equity": round(ms.equity(state, tick), 2),
        "gross": round(ms.gross_exposure(state, tick), 4),
        "bench": round(ms.START_CASH * state["paths"][ms.BENCH][tick] / bench0, 2),
        "equity_curve": [round(v, 2) for v in state["equity"]],
        "bench_curve": [round(v, 2) for v in state["bench"]],
        "trades": state["trades"],
        "breaches": state["breaches"],
        "tape": ms.tape(state, tick),
        "limits": {"start_cash": ms.START_CASH, "max_gross": ms.MAX_GROSS,
                   "max_name": ms.MAX_NAME, "max_trades": ms.MAX_TRADES},
    }


class NewRound(BaseModel):
    seed: int | None = None


@router.post("/desk/new")
def new(body: NewRound | None = None):
    seed = body.seed if body else None
    rid, state = deps.create_round(seed)
    return _round_payload(rid, state)


@router.get("/desk/{rid}")
def get_round(rid: str, sym: str = "NVX"):
    state = deps.get_round(rid)
    if not state:
        raise HTTPException(status_code=404, detail="Round not found. Start a new one.")
    payload = _round_payload(rid, state)
    tick = payload["tick"]
    if sym in ms.SYMBOLS:
        bids, asks = ms.book(state, sym, tick)
        payload["book"] = {"sym": sym,
                           "bids": [{"px": round(p, 2), "size": s} for p, s in bids],
                           "asks": [{"px": round(p, 2), "size": s} for p, s in asks]}
    return payload


class TradeBody(BaseModel):
    sym: str
    qty: float


@router.post("/desk/{rid}/trade")
def trade(rid: str, body: TradeBody):
    state = deps.get_round(rid)
    if not state:
        raise HTTPException(status_code=404, detail="Round not found.")
    if body.sym not in ms.SYMBOLS:
        raise HTTPException(status_code=400, detail="Unknown symbol.")
    tick = ms.current_tick(state)
    if tick >= state["duration"]:
        raise HTTPException(status_code=400, detail="The round is over.")
    ok, message, fill = ms.trade(state, body.sym, float(body.qty), tick)
    return {"ok": ok, "message": message, "fill": fill, **_round_payload(rid, state)}


@router.post("/desk/{rid}/grade")
def grade(rid: str):
    state = deps.get_round(rid)
    if not state:
        raise HTTPException(status_code=404, detail="Round not found.")
    if not state["graded"]:
        tick = state["duration"]
        ms.snapshot(state, tick)
        result = ms.grade(state)
        state["graded"] = True
        state["result"] = result

        p = deps.progress()
        p.setdefault("desk_rounds", []).append({
            "date": date.today().isoformat(),
            "score": result["score"], "ret": result["ret"], "bench": result["bench"],
            "dd": result["dd"], "trades": result["trades"], "breaches": result["breaches"],
            "realized": result["realized"], "equity": result["equity"], "seed": result["seed"],
        })
        p["xp"] = p.get("xp", 0) + result["score"] // 2
        deps.commit(p)
        if result["trades"] > 0:
            from lib.storage import log_activity
            log_activity(p, "desk")
    return state["result"]


@router.get("/desk-history")
def history():
    p = deps.progress()
    rounds = p.get("desk_rounds", [])
    return {"rounds": rounds[-12:][::-1], "total": len(rounds)}


@router.get("/desk-symbols")
def symbols():
    return {"symbols": {k: {"name": v["name"], "kind": v["kind"]} for k, v in ms.SYMBOLS.items()},
            "limits": {"start_cash": ms.START_CASH, "max_gross": ms.MAX_GROSS,
                       "max_name": ms.MAX_NAME, "max_trades": ms.MAX_TRADES}}
