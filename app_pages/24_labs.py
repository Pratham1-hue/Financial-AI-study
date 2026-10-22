"""Hands-on labs: SQL, credit risk, valuation. Every task is auto-graded.

No multiple choice. You write the query, choose the model, or compute the number,
and the app tells you whether it is right - the way the job actually works.
"""
import re
import sqlite3
import time
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from lib.storage import load_progress, log_activity, save_progress
from lib.ui import hero, inject_css, section

inject_css()
hero(
    "The <em>labs</em>",
    "Three skills that get tested in interviews and on the job: SQL against a real schema, "
    "credit risk you can measure, and a valuation you compute under a clock.",
    eyebrow="Hands-on · auto-graded",
    quote_tags=["practice", "work"],
)

progress = load_progress()
runs = progress.setdefault("lab_runs", [])


def record(lab, ok, detail=""):
    runs.append({"date": date.today().isoformat(), "lab": lab, "ok": bool(ok), "detail": detail})
    if ok:
        progress["xp"] = progress.get("xp", 0) + 15
        log_activity(progress, "lab")
    save_progress(progress)


# =====================================================================  SQL
COMPANIES = [
    (1, "Northwind Capital", "Financials", 48000), (2, "Atlas Bank", "Financials", 91000),
    (3, "Meridian Insurance", "Financials", 22000), (4, "Helios Semis", "Technology", 305000),
    (5, "Vector Cloud", "Technology", 178000), (6, "Kestrel Software", "Technology", 64000),
    (7, "Orion Devices", "Technology", 41000), (8, "BlueRiver Health", "Healthcare", 88000),
    (9, "Cedar Pharma", "Healthcare", 52000), (10, "Summit Devices", "Healthcare", 19000),
    (11, "Ironclad Energy", "Energy", 76000), (12, "Pioneer Grid", "Energy", 33000),
    (13, "Redwood Retail", "Consumer", 45000), (14, "Harbor Foods", "Consumer", 28000),
    (15, "Union Apparel", "Consumer", 12000), (16, "Apex Logistics", "Industrials", 39000),
    (17, "Foundry Works", "Industrials", 27000), (18, "Skyline Builders", "Industrials", 15000),
    (19, "Nimbus Media", "Media", 36000), (20, "Lantern Studios", "Media", 18000),
    (21, "Comet Telecom", "Media", 59000), (22, "Terra Materials", "Materials", 24000),
    (23, "Granite Steel", "Materials", 31000), (24, "Aurora Chemicals", "Materials", 21000),
]

SECTORS = ["Technology", "Financials", "Healthcare", "Energy", "Consumer",
           "Industrials", "Media", "Materials"]


@st.cache_resource(show_spinner=False)
def _db():
    rnd = np.random.default_rng(11)
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    pd.DataFrame(COMPANIES, columns=["id", "name", "sector", "market_cap_m"]).to_sql(
        "companies", conn, index=False)

    rows = []
    dates = pd.bdate_range("2025-01-02", periods=240)
    for cid, _, _, cap in COMPANIES:
        base = cap / 18.0
        rets = rnd.normal(0.0004, 0.014, len(dates))
        path = base * np.exp(np.cumsum(rets))
        for d, px in zip(dates, path):
            rows.append((cid, d.date().isoformat(), round(float(px), 2)))
    pd.DataFrame(rows, columns=["company_id", "date", "close"]).to_sql("prices", conn, index=False)

    fin = []
    for cid, _, sector, cap in COMPANIES:
        revenue = cap / rnd.uniform(2.0, 5.0)
        margin = rnd.uniform(0.04, 0.26) if sector != "Financials" else rnd.uniform(0.18, 0.33)
        for year in (2024, 2025):
            growth = rnd.uniform(-0.05, 0.28)
            revenue = revenue * (1 + growth)
            assets = revenue * rnd.uniform(1.2, 3.4)
            liab = assets * rnd.uniform(0.35, 0.78)
            fin.append((cid, year, round(revenue, 1), round(revenue * margin, 1),
                        round(assets, 1), round(liab, 1)))
    pd.DataFrame(fin, columns=["company_id", "year", "revenue_m", "net_income_m",
                               "assets_m", "liabilities_m"]).to_sql("financials", conn, index=False)
    return conn


SQL_TASKS = [
    {
        "id": "sql1", "level": "Warm-up",
        "prompt": "Return `name` and `market_cap_m` for every Technology company, largest first.",
        "cols": "name, market_cap_m",
        "sql": """SELECT name, market_cap_m FROM companies
WHERE sector = 'Technology' ORDER BY market_cap_m DESC""",
        "hint": "Filter with WHERE, then ORDER BY ... DESC.",
    },
    {
        "id": "sql2", "level": "Warm-up",
        "prompt": "Average closing price per company across all dates. Return `name` and the average rounded to 2 decimals, highest first.",
        "cols": "name, avg_close",
        "sql": """SELECT c.name, ROUND(AVG(p.close), 2) AS avg_close
FROM prices p JOIN companies c ON c.id = p.company_id
GROUP BY c.name ORDER BY avg_close DESC""",
        "hint": "JOIN, then GROUP BY the company name. ROUND(AVG(close), 2).",
    },
    {
        "id": "sql3", "level": "Join",
        "prompt": "Latest closing price per company. Return `name` and `close` for the most recent date only, highest price first.",
        "cols": "name, close",
        "sql": """SELECT c.name, p.close FROM prices p
JOIN companies c ON c.id = p.company_id
WHERE p.date = (SELECT MAX(date) FROM prices) ORDER BY p.close DESC""",
        "hint": "A scalar subquery for MAX(date) is the cleanest way.",
    },
    {
        "id": "sql4", "level": "Aggregate",
        "prompt": "Total market cap by sector. Return `sector` and `total_cap_m`, largest first, top 3 only.",
        "cols": "sector, total_cap_m",
        "sql": """SELECT sector, SUM(market_cap_m) AS total_cap_m FROM companies
GROUP BY sector ORDER BY total_cap_m DESC LIMIT 3""",
        "hint": "GROUP BY sector, SUM, ORDER BY the alias, LIMIT 3.",
    },
    {
        "id": "sql5", "level": "Business logic",
        "prompt": "2025 net margin above 15%. Return `name` and `margin_pct` (net income / revenue * 100, 1 decimal), highest first.",
        "cols": "name, margin_pct",
        "sql": """SELECT c.name, ROUND(100.0 * f.net_income_m / f.revenue_m, 1) AS margin_pct
FROM financials f JOIN companies c ON c.id = f.company_id
WHERE f.year = 2025 AND 100.0 * f.net_income_m / f.revenue_m > 15
ORDER BY margin_pct DESC""",
        "hint": "SQLite will not accept a SELECT alias in WHERE. Repeat the expression.",
    },
    {
        "id": "sql6", "level": "Window",
        "prompt": "Rank companies by market cap within each sector. Return `sector`, `name`, `market_cap_m`, `rnk` ordered by sector then rank.",
        "cols": "sector, name, market_cap_m, rnk",
        "sql": """SELECT sector, name, market_cap_m,
RANK() OVER (PARTITION BY sector ORDER BY market_cap_m DESC) AS rnk
FROM companies ORDER BY sector, rnk""",
        "hint": "RANK() OVER (PARTITION BY sector ORDER BY market_cap_m DESC).",
    },
]


def _looks_safe(sql):
    s = re.sub(r"--[^\n]*", " ", sql).strip().lower()
    if not s:
        return False, "Write a query."
    if s.count(";") > 0 and not s.rstrip().endswith(";"):
        return False, "One statement at a time."
    if not (s.startswith("select") or s.startswith("with")):
        return False, "Read-only: SELECT or WITH only."
    for bad in ("insert", "update", "delete", "drop", "alter", "attach", "pragma", "create"):
        if re.search(rf"\b{bad}\b", s):
            return False, f"`{bad}` is not allowed here."
    return True, ""


def _same_result(user, ref):
    if user is None or ref is None:
        return False
    if user.shape != ref.shape:
        return False
    u, r = user.copy(), ref.copy()
    r.columns = u.columns
    try:
        u = u.sort_values(by=list(u.columns), key=lambda s: s.astype(str)).reset_index(drop=True)
        r = r.sort_values(by=list(r.columns), key=lambda s: s.astype(str)).reset_index(drop=True)
    except Exception:
        return False
    for col in u.columns:
        if pd.api.types.is_numeric_dtype(u[col]) and pd.api.types.is_numeric_dtype(r[col]):
            if not np.allclose(u[col].astype(float), r[col].astype(float), atol=0.02, rtol=1e-6):
                return False
        else:
            if not (u[col].astype(str).values == r[col].astype(str).values).all():
                return False
    return True


def sql_lab():
    st.markdown(
        "A small but real schema: `companies`, `prices` (240 trading days), `financials` (FY2024-25). "
        "Every answer is checked against a reference query."
    )
    conn = _db()
    with st.expander("Schema", expanded=False):
        st.code(
            "companies(id, name, sector, market_cap_m)\n"
            "prices(company_id, date, close)            -- 240 business days\n"
            "financials(company_id, year, revenue_m, net_income_m, assets_m, liabilities_m)",
            language="text",
        )

    task_id = st.selectbox("Task", [t["id"] for t in SQL_TASKS],
                           format_func=lambda i: f"{next(t['level'] for t in SQL_TASKS if t['id'] == i)} · "
                                                 f"{next(t['prompt'][:70] for t in SQL_TASKS if t['id'] == i)}...")
    task = next(t for t in SQL_TASKS if t["id"] == task_id)
    st.markdown(f"**{task['prompt']}**")
    st.caption(f"Return exactly these columns, in this order: `{task['cols']}` (row order does not matter).")

    key = f"sql_{task_id}"
    sql = st.text_area("Your query", key=key, height=130,
                       placeholder="SELECT ...\nFROM ...\nWHERE ...")
    b1, b2, _ = st.columns([1, 1, 3])
    run = b1.button("Run", type="primary", icon=":material/play_arrow:", key=f"run_{task_id}")
    check = b2.button("Check", icon=":material/check:", key=f"chk_{task_id}")

    attempts_key = f"sql_attempts_{task_id}"
    if "sql_attempts" not in st.session_state:
        st.session_state["sql_attempts"] = {}
    attempts = st.session_state["sql_attempts"].get(task_id, 0)

    if run or check:
        ok, why = _looks_safe(sql)
        if not ok:
            st.error(why)
        else:
            try:
                user = pd.read_sql_query(sql, conn)
            except Exception as e:
                st.error(f"SQL error: {e}")
                user = None
            else:
                st.dataframe(user.head(50), hide_index=True, width="stretch")
                st.caption(f"{len(user)} rows")
                if check:
                    ref = pd.read_sql_query(task["sql"], conn)
                    if _same_result(user, ref):
                        st.success("Correct. That is the answer a reviewer would accept.", icon=":material/check_circle:")
                        st.session_state["sql_attempts"][task_id] = attempts + 1
                        if not st.session_state.get(f"solved_{task_id}"):
                            st.session_state[f"solved_{task_id}"] = True
                            record("SQL", True, task_id)
                    else:
                        attempts += 1
                        st.session_state["sql_attempts"][task_id] = attempts
                        st.warning(
                            f"Not yet. You returned {len(user)} rows x {len(user.columns)} columns; "
                            f"the answer has {ref.shape[0]} rows x {ref.shape[1]} columns. "
                            f"Check your filter, join keys and rounding."
                        )
                        record("SQL", False, task_id)

    with st.expander("Hint", expanded=False):
        st.markdown(task["hint"])
        if attempts >= 3:
            st.markdown("**Reference query**")
            st.code(task["sql"], language="sql")
        else:
            st.caption(f"Reference query unlocks after 3 attempts ({attempts} so far).")

    solved = sum(1 for t in SQL_TASKS if st.session_state.get(f"solved_{t['id']}"))
    st.progress(solved / len(SQL_TASKS), text=f"{solved}/{len(SQL_TASKS)} tasks solved this session")


# =====================================================================  ML
@st.cache_data(show_spinner=False)
def credit_data(n=4000, seed=7):
    rnd = np.random.default_rng(seed)
    income_k = rnd.lognormal(3.9, 0.45, n)              # ~$50k
    dti = np.clip(rnd.beta(2.2, 3.0, n), 0.05, 0.85)
    ltv = np.clip(rnd.normal(0.82, 0.12, n), 0.30, 1.15)
    delinq = rnd.poisson(0.35, n)
    emp_years = rnd.gamma(2.0, 2.5, n)
    loan_k = rnd.uniform(5, 60, n)
    score = rnd.normal(690, 60, n)

    z = (-4.4 + 3.6 * dti + 2.4 * ltv + 0.55 * delinq - 0.055 * emp_years
         + 0.012 * loan_k - 0.004 * (score - 690) - 0.02 * income_k)
    p = 1 / (1 + np.exp(-z))
    default = (rnd.random(n) < p).astype(int)

    return pd.DataFrame({
        "income_k": income_k.round(1),
        "dti": dti.round(3),
        "ltv": ltv.round(3),
        "delinquencies": delinq,
        "employment_years": emp_years.round(1),
        "loan_amount_k": loan_k.round(1),
        "credit_score": score.round(0),
        "default": default,
    })


def credit_lab():
    st.markdown(
        "**4,000 borrowers.** Predict who defaults. The naive model (always say 'no default') "
        "is ~78% accurate and completely useless - so accuracy is not the metric you report."
    )
    df = credit_data()
    feats = ["income_k", "dti", "ltv", "delinquencies", "employment_years",
             "loan_amount_k", "credit_score"]
    c1, c2, c3 = st.columns([3, 2, 2])
    chosen = c1.multiselect("Features", feats, default=["dti", "ltv", "delinquencies", "credit_score"])
    model_name = c2.selectbox("Model", ["Logistic regression", "Random forest", "Gradient boosting"])
    threshold = c3.slider("Default threshold", 0.10, 0.80, 0.30, 0.05)

    if not chosen:
        st.info("Pick at least one feature.")
        return

    X, y = df[chosen], df["default"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)

    if model_name == "Logistic regression":
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    elif model_name == "Random forest":
        model = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=0, n_jobs=-1)
    else:
        model = GradientBoostingClassifier(random_state=0)

    model.fit(Xtr, ytr)
    proba = model.predict_proba(Xte)[:, 1]
    pred = (proba >= threshold).astype(int)

    base = max(yte.mean(), 1 - yte.mean())
    acc = accuracy_score(yte, pred)
    prec = precision_score(yte, pred, zero_division=0)
    rec = recall_score(yte, pred, zero_division=0)
    f1 = f1_score(yte, pred, zero_division=0)
    auc = roc_auc_score(yte, proba)

    m = st.columns(5)
    m[0].metric("AUC", f"{auc:.3f}", help="Ranking quality. 0.5 is a coin flip; 0.75+ is usable.")
    m[1].metric("Recall (defaults caught)", f"{rec:.0%}")
    m[2].metric("Precision", f"{prec:.0%}")
    m[3].metric("F1", f"{f1:.3f}")
    m[4].metric("Accuracy", f"{acc:.0%}", delta=f"{acc - base:+.0%} vs naive", delta_color="off")

    cm = confusion_matrix(yte, pred)
    left, right = st.columns([2, 3])
    with left:
        st.markdown("**Confusion matrix**")
        st.dataframe(pd.DataFrame(cm, index=["Actually paid", "Actually defaulted"],
                                  columns=["Predicted paid", "Predicted default"]),
                     width="stretch")
        st.caption(f"Missed defaults: **{cm[1, 0]}** of {cm[1].sum()}. That is the number a credit committee cares about.")
    with right:
        st.markdown("**What the model is using**")
        if model_name == "Logistic regression":
            coefs = pd.Series(model[-1].coef_[0], index=chosen).sort_values()
            st.bar_chart(coefs, height=250, color="#d4af37")
            st.caption("Standardised coefficients: direction and relative weight.")
        else:
            imp = pd.Series(model.feature_importances_, index=chosen).sort_values()
            st.bar_chart(imp, height=250, color="#d4af37")

    st.markdown(
        "**The tradeoff to internalise:** lowering the threshold catches more defaults "
        "and rejects more good borrowers. There is no free lunch - only a decision about "
        "which error costs more."
    )
    if st.button("Bank this result", icon=":material/save:", key="bank_credit"):
        record("Credit ML", auc > 0.72, f"{model_name} auc={auc:.3f}")
        st.success(f"Logged: {model_name}, AUC {auc:.3f}. The bar for 'usable' is 0.72.")


# =====================================================================  valuation
@st.cache_data(show_spinner=False)
def valuation_case(seed):
    rnd = np.random.default_rng(seed)
    wacc = float(rnd.uniform(0.085, 0.125))
    g = float(rnd.uniform(0.06, 0.16))
    gt = float(rnd.uniform(0.015, min(0.03, wacc - 0.04)))
    fcf0 = float(rnd.uniform(90, 380))
    shares = float(rnd.uniform(60, 420))
    net_debt = float(rnd.uniform(-150, 700))

    fcfs = [fcf0 * (1 + g) ** t for t in range(1, 6)]
    pv = sum(f / (1 + wacc) ** t for t, f in enumerate(fcfs, 1))
    tv = fcfs[-1] * (1 + gt) / (wacc - gt)
    ev = pv + tv / (1 + wacc) ** 5
    equity = ev - net_debt
    return {
        "wacc": wacc, "g": g, "gt": gt, "fcf0": fcf0, "shares": shares,
        "net_debt": net_debt, "ev": ev, "equity": equity, "per_share": equity / shares,
        "fcfs": fcfs, "pv": pv, "tv": tv,
    }


def valuation_lab():
    st.markdown(
        "**Five minutes. One company. Three numbers.** No spreadsheet - if you understand the "
        "mechanics you can do this on a whiteboard, which is exactly what an interview asks for."
    )
    st.markdown(
        "Forecast FCF for five years at the stated growth rate, discount at WACC, add a Gordon "
        "terminal value, subtract net debt, divide by shares."
    )

    if "val" not in st.session_state:
        st.session_state["val"] = {"seed": int(np.random.default_rng().integers(1, 10**6)),
                                   "start": None, "done": False}
    v = st.session_state["val"]
    case = valuation_case(v["seed"])

    c = st.columns(5)
    c[0].metric("FCF (year 0)", f"${case['fcf0']:.1f}m")
    c[1].metric("Growth (5y)", f"{case['g']:.1%}")
    c[2].metric("WACC", f"{case['wacc']:.2%}")
    c[3].metric("Terminal growth", f"{case['gt']:.2%}")
    c[4].metric("Net debt", f"${case['net_debt']:.0f}m")
    st.caption(f"Shares outstanding: {case['shares']:.1f}m. Currency: USD millions except per share.")

    if v["start"] is None:
        if st.button("Start the clock", type="primary", icon=":material/timer:"):
            v["start"] = time.time()
            st.rerun()
        return

    @st.fragment(run_every=1.0)
    def clock():
        left = 300 - (time.time() - v["start"])
        if left <= 0 and not v["done"]:
            v["done"] = True
            st.rerun()
        st.progress(max(0.0, left / 300), text=f"{int(max(0, left)) // 60}:{int(max(0, left)) % 60:02d} left")

    clock()

    q = st.columns(3)
    ev_in = q[0].number_input("Enterprise value ($m)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
    eq_in = q[1].number_input("Equity value ($m)", min_value=-1e9, value=0.0, step=10.0, format="%.2f")
    ps_in = q[2].number_input("Value per share ($)", min_value=0.0, value=0.0, step=1.0, format="%.2f")

    if st.button("Submit", type="primary", icon=":material/check:", disabled=v["done"] and v.get("scored")):
        def close(a, b, tol=0.01):
            return abs(a - b) <= max(abs(b) * tol, 0.5)

        checks = [("Enterprise value", ev_in, case["ev"]),
                  ("Equity value", eq_in, case["equity"]),
                  ("Per share", ps_in, case["per_share"])]
        passed = sum(close(a, b) for _, a, b in checks)
        v["scored"] = True
        v["done"] = True
        if passed == 3:
            st.success("All three. That is the standard: mechanics you can do without a model.", icon=":material/workspace_premium:")
            record("Valuation", True, f"seed={v['seed']}")
        else:
            st.warning(f"{passed}/3 correct. Work backwards from the ones you missed.")
            record("Valuation", False, f"{passed}/3")
        for label, a, b in checks:
            st.markdown(f"- {label}: you said **{a:,.2f}**, answer **{b:,.2f}** {'✓' if close(a, b) else '✗'}")

    with st.expander("Show the mechanics"):
        st.latex(r"EV=\sum_{t=1}^{5}\frac{FCF_0(1+g)^t}{(1+WACC)^t}+\frac{TV}{(1+WACC)^5}")
        st.latex(r"TV=\frac{FCF_5(1+g_T)}{WACC-g_T}\qquad Equity=EV-NetDebt")
        st.markdown("Year-by-year cash flows for this case:")
        st.dataframe(pd.DataFrame({"Year": [1, 2, 3, 4, 5],
                                   "FCF": [round(f, 2) for f in case["fcfs"]],
                                   "PV": [round(f / (1 + case["wacc"]) ** t, 2)
                                          for t, f in enumerate(case["fcfs"], 1)]}),
                     hide_index=True, width="stretch")
        st.caption(f"Terminal value {case['tv']:,.1f}; PV of terminal {case['tv'] / (1 + case['wacc']) ** 5:,.1f}.")

    if v.get("done"):
        if st.button("New case", icon=":material/refresh:"):
            st.session_state["val"] = {"seed": int(np.random.default_rng().integers(1, 10**6)),
                                       "start": None, "done": False}
            st.rerun()


# =====================================================================  page
tab_sql, tab_ml, tab_val = st.tabs(["SQL lab", "Credit risk lab", "Valuation sprint"])
with tab_sql:
    sql_lab()
with tab_ml:
    credit_lab()
with tab_val:
    valuation_lab()

section("Today's lab log")
today = date.today().isoformat()
todays = [r for r in runs if r["date"] == today]
s1, s2, s3 = st.columns(3)
s1.metric("Attempts today", len(todays))
s2.metric("Correct today", sum(1 for r in todays if r["ok"]))
s3.metric("All-time correct", sum(1 for r in runs if r["ok"]))
if runs:
    recent = pd.DataFrame(runs[-12:])
    recent["ok"] = recent["ok"].map({True: "✓", False: "—"})
    recent.columns = ["Date", "Lab", "Correct", "Detail"]
    st.dataframe(recent, hide_index=True, width="stretch")
