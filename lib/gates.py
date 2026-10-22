"""Mastery gates (Launch School-style mastery-based learning).

A module unlocks only when its prerequisites are mastered. Each gate is an assessment:
multiple choice (>= MCQ_PASS) + oral-style teach-back (>= ORAL_PASS of rubric points).
Failing is "Not yet": 24h wait, and a second "Not yet" means 72h + the module's drill cards reset.
"""
from datetime import datetime, timedelta

from lib.content import MODULE_BY_ID, MODULES
from lib.quiz_bank import QUESTIONS

MCQ_PASS = 80
ORAL_PASS = 75
ORAL_MIN_CHARS = 150

PREREQS = {
    "F1": [], "A1": [], "A2": [],
    "F2": ["F1"], "F7": ["F1"], "A7": ["A1"],
    "F3": ["F2", "A2"], "A3": ["A1", "A2"],
    "F4": ["F3"], "A4": ["A3"], "A6": ["A3", "A7"],
    "F5": ["F4", "A1"], "A5": ["A4"], "A8": ["A4"],
    "F6": ["F5"], "F8": ["F4", "A7"],
    "C1": ["A3", "F3"], "C2": ["A3", "F4"],
}

ORAL = {
    "F1": [("Explain the time value of money, and why a bond's price falls when interest rates rise.",
            ["Money today can be invested to earn a return", "PV = CF / (1+r)^t", "Higher r lowers the PV of fixed cash flows",
             "So bond prices and yields move inversely"]),
           ("Why does diversification reduce risk, and what risk can't it remove?",
            ["Assets are imperfectly correlated, so moves partly offset", "Removes idiosyncratic (firm-specific) risk",
             "Systematic / market risk remains", "Portfolio variance depends on covariances, not just individual variances"])],
    "F2": [("Walk through how the three financial statements connect.",
            ["Net income from the income statement starts the cash flow statement", "Ending cash on the CFS becomes cash on the balance sheet",
             "Net income (less dividends) flows into retained earnings", "D&A and capex link to PP&E"]),
           ("How can a profitable company run out of cash?",
            ["Accrual profit is not cash", "Growth in receivables / inventory (working capital) absorbs cash",
             "Capex and debt repayments consume cash", "Profit ≠ operating cash flow"])],
    "F3": [("Explain WACC and why it's used to discount free cash flow in a DCF.",
            ["Weighted average of cost of equity and after-tax cost of debt", "Weights by market values of equity and debt",
             "Unlevered FCF belongs to all capital providers", "Discounting at WACC gives enterprise value"]),
           ("What drives terminal value, and why is it dangerous?",
            ["Often 60-80% of total DCF value", "Gordon growth: FCF x (1+g) / (r-g)", "Highly sensitive to g and r",
             "g must not exceed long-run economic growth"])],
    "F4": [("Explain CAPM and beta.",
            ["E[R] = rf + beta x (market return - rf)", "Beta = cov(asset, market) / var(market)",
             "Only systematic risk is rewarded", "Alpha = return above what CAPM predicts"]),
           ("What does the efficient frontier show?",
            ["Portfolios with the highest return for each level of risk", "Comes from diversification across correlations",
             "Adding a risk-free asset gives the capital market line / tangency (max Sharpe) portfolio",
             "Investors pick a point based on risk tolerance"])],
    "F5": [("What is Value at Risk, and what is its main weakness?",
            ["Loss threshold at a confidence level over a horizon (e.g. 95%, 1 day)", "Says nothing about losses beyond the threshold",
             "Expected shortfall averages the tail", "Normality assumptions underestimate fat tails"]),
           ("How would you price a European option with Monte Carlo?",
            ["Simulate risk-neutral GBM paths with drift r", "Compute the payoff at maturity on each path",
             "Average payoffs and discount by e^(-rT)", "Error shrinks like 1/sqrt(N); use variance reduction"])],
    "F6": [("Explain delta and how a market maker delta-hedges.",
            ["Delta = sensitivity of option value to the underlying", "Hedge by holding -delta units of the underlying",
             "Rebalance as delta changes (gamma)", "Hedging P&L trades gamma against theta"]),
           ("What is implied volatility, and why is there a volatility skew?",
            ["The volatility that makes the model price equal the market price", "Black-Scholes assumes constant volatility",
             "Markets price crash risk / fat tails", "Downside puts are relatively expensive, creating the skew"])],
    "F7": [("How does the Fed fight inflation, and how does that reach the real economy?",
            ["Raises the policy rate and/or shrinks its balance sheet (QT)", "Borrowing costs rise across the economy",
             "Credit, housing and investment demand slow", "Expectations and a stronger dollar also cool inflation"]),
           ("Why is an inverted yield curve considered a recession signal?",
            ["Short rates above long rates", "Markets expect future rate cuts / weaker growth",
             "Bank lending margins get squeezed, so credit tightens", "Historically it preceded US recessions with a lag"])],
    "F8": [("Explain how a limit order book works.",
            ["Bids and asks queued at price levels", "Price-time priority", "Market orders take liquidity and cross the spread",
             "Limit orders provide liquidity; spread and depth measure it"]),
           ("What makes an algorithmic trading backtest unrealistic?",
            ["Ignoring latency and queue position", "Ignoring fees and slippage", "Ignoring market impact",
             "Look-ahead or survivorship bias"])],
    "A1": [("Explain NumPy vectorization and why it beats Python loops.",
            ["Operations run in compiled C over whole arrays", "Avoids per-element interpreter overhead",
             "Broadcasting aligns shapes without copies", "Contiguous memory is cache-friendly"]),
           ("Explain pandas groupby with a finance example.",
            ["Split rows by a key (e.g. ticker)", "Apply an aggregation or transform", "Combine results into a new frame",
             "Example: total P&L or average volume per ticker"])],
    "A2": [("Explain gradient descent intuitively.",
            ["The gradient points in the direction of steepest increase", "Step in the opposite direction to reduce loss",
             "Learning rate sets step size (too big diverges, too small is slow)", "Converges to a (local) minimum"]),
           ("Explain Bayes' theorem with a fraud-detection example.",
            ["Posterior = likelihood x prior / evidence", "Base rates matter", "With a rare event, false positives can dominate",
             "Evidence updates belief rather than replacing it"])],
    "A3": [("Explain overfitting and three ways to prevent it.",
            ["Model memorizes noise instead of signal", "Low training error, high validation error",
             "Regularization / simpler model / early stopping", "More data and proper cross-validation"]),
           ("Explain how gradient boosting works.",
            ["Trees are added sequentially", "Each tree fits the residuals (negative gradients) of the current model",
             "A learning rate shrinks each tree's contribution", "Mainly reduces bias; tune depth, trees, early stopping"])],
    "A4": [("Explain backpropagation.",
            ["Forward pass computes outputs and loss", "Chain rule propagates gradients backward layer by layer",
             "Intermediate results are reused for efficiency", "An optimizer then updates the weights"]),
           ("Why do transformers use attention instead of recurrence?",
            ["Whole sequence processed in parallel", "Direct paths between any two tokens capture long-range dependencies",
             "Attention weights come from query-key similarity", "Positional encodings supply word order"])],
    "A5": [("Explain how retrieval-augmented generation (RAG) works end to end.",
            ["Chunk and embed documents into a vector store", "Embed the query and retrieve the top-k chunks",
             "Insert retrieved context into the prompt", "Generate with citations; evaluate retrieval and faithfulness"]),
           ("What is LoRA and why is it efficient?",
            ["Base model weights stay frozen", "Learns a low-rank update (two small matrices)",
             "Far fewer trainable parameters and less memory", "Adapters can be swapped per task"])],
    "A6": [("What is data drift, and how do you monitor for it?",
            ["Production inputs shift away from the training distribution", "Track feature statistics (PSI, KS tests)",
             "Track prediction distributions and delayed-label performance", "Alert and retrain when thresholds are crossed"]),
           ("How do you deploy a model as a reliable service?",
            ["Package with Docker", "Serve behind an API (e.g. FastAPI)", "Version models in a registry with CI/CD tests",
             "Monitor latency/errors; canary releases and rollback"])],
    "A7": [("Explain window functions versus GROUP BY.",
            ["GROUP BY collapses rows into groups", "Window functions keep every row", "OVER (PARTITION BY ... ORDER BY ...) defines the window",
             "Examples: ROW_NUMBER, running SUM, LAG"]),
           ("What is a star schema and why is it used?",
            ["Central fact table of measures", "Surrounding dimension tables (date, ticker, customer)",
             "Simple joins and fast analytical queries", "Dimensions are denormalized for readability"])],
    "A8": [("Explain the explore-exploit tradeoff in reinforcement learning.",
            ["The agent must try actions to learn their value", "It also wants to exploit the best-known action",
             "Strategies: epsilon-greedy, UCB, entropy bonuses", "Too little exploration locks in a suboptimal policy"]),
           ("How do diffusion models generate images?",
            ["A forward process gradually adds noise", "A network learns to predict and remove the noise",
             "Sampling iteratively denoises from pure noise", "Conditioning (e.g. text) guides generation"])],
    "C1": [("How do you approach an unseen coding problem in an interview?",
            ["Clarify requirements and walk through examples", "State a brute-force approach first, then optimize",
             "Talk through time and space complexity", "Code cleanly and test edge cases out loud"]),
           ("How do you answer 'Tell me about yourself' for a quant/ML role?",
            ["Present -> past -> future structure", "Lead with the most relevant finance + ML skills",
             "One or two concrete proof points", "Close with why this firm; about 90 seconds"])],
    "C2": [("Pitch your best project in 60 seconds.",
            ["The problem and why it matters", "Your approach and stack", "A measurable result against a baseline",
             "What you'd improve next, plus a demo link"]),
           ("How do you prove a trading or ML model isn't overfit?",
            ["Out-of-sample / walk-forward evaluation", "Comparison against a simple baseline",
             "Realistic costs included", "Robust across time periods and parameters; limited number of trials"])],
}


def gate(progress, mid):
    return progress.setdefault("gates", {}).get(mid)


def is_mastered(progress, mid):
    g = progress.get("gates", {}).get(mid)
    return bool(g and g.get("status") == "mastered")


def missing_prereqs(progress, mid):
    return [p for p in PREREQS.get(mid, []) if not is_mastered(progress, p)]


def cooldown_left(progress, mid):
    g = progress.get("gates", {}).get(mid)
    if not g or not g.get("retake_after"):
        return None
    left = datetime.fromisoformat(g["retake_after"]) - datetime.now()
    return left if left.total_seconds() > 0 else None


def status(progress, mid):
    if is_mastered(progress, mid):
        return "Mastered"
    if missing_prereqs(progress, mid):
        return "Locked"
    if cooldown_left(progress, mid):
        return "Not yet"
    return "Ready"


def mcq_for(mid):
    return [q for q in QUESTIONS if q["module"] == mid]


def record_attempt(progress, mid, mcq_pct, oral_pct, answers):
    gates = progress.setdefault("gates", {})
    g = gates.setdefault(mid, {"status": "open", "attempts": 0, "not_yet": 0, "history": []})
    g["attempts"] += 1
    passed = mcq_pct >= MCQ_PASS and oral_pct >= ORAL_PASS
    now = datetime.now()
    g["history"].append({"at": now.isoformat(timespec="minutes"), "mcq": mcq_pct, "oral": oral_pct,
                         "passed": passed, "answers": answers})
    reset_cards = False
    if passed:
        g.update(status="mastered", passed_on=now.date().isoformat(), retake_after=None)
    else:
        g["not_yet"] += 1
        hours = 24 if g["not_yet"] == 1 else 72
        g.update(status="not_yet", retake_after=(now + timedelta(hours=hours)).isoformat(timespec="minutes"))
        if g["not_yet"] >= 2:
            reset_cards = True
            today = now.date().isoformat()
            for q in mcq_for(mid):
                if q["id"] in progress.get("srs", {}):
                    progress["srs"][q["id"]].update(box=1, due=today)
    return passed, reset_cards


def mastered_count(progress):
    return sum(1 for m in MODULES if is_mastered(progress, m["id"]))


def week_gate_issues(progress, modules):
    """For this week's modules, list those whose prerequisites aren't mastered yet."""
    out = []
    for m in modules:
        miss = missing_prereqs(progress, m["id"])
        if miss:
            out.append((m, miss))
    return out


def title(mid):
    return MODULE_BY_ID[mid]["title"] if mid in MODULE_BY_ID else mid