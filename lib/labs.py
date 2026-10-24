"""Hands-on lab engine: SQL, credit risk, valuation.

Pure Python - no Streamlit, no UI. The FastAPI server and (optionally) the old
Streamlit page both call into this. Every task is auto-graded.
"""
from __future__ import annotations

import re
import sqlite3
from functools import lru_cache

import numpy as np
import pandas as pd

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

SCHEMA = (
    "companies(id, name, sector, market_cap_m)\n"
    "prices(company_id, date, close)            -- 240 business days\n"
    "financials(company_id, year, revenue_m, net_income_m, assets_m, liabilities_m)"
)


@lru_cache(maxsize=1)
def db():
    """In-memory SQLite with 24 companies, 240 days of prices, 2 years of financials."""
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

SQL_BY_ID = {t["id"]: t for t in SQL_TASKS}

_BAD = ("insert", "update", "delete", "drop", "alter", "attach", "pragma", "create")


def looks_safe(sql: str):
    """Read-only guard. Returns (ok, message)."""
    s = re.sub(r"--[^\n]*", " ", sql or "").strip().lower()
    if not s:
        return False, "Write a query."
    if s.count(";") > 0 and not s.rstrip().endswith(";"):
        return False, "One statement at a time."
    if not (s.startswith("select") or s.startswith("with")):
        return False, "Read-only: SELECT or WITH only."
    for bad in _BAD:
        if re.search(rf"\b{bad}\b", s):
            return False, f"`{bad}` is not allowed here."
    return True, ""


def _same_result(user: pd.DataFrame, ref: pd.DataFrame) -> bool:
    if user is None or ref is None or user.shape != ref.shape:
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
        elif not (u[col].astype(str).values == r[col].astype(str).values).all():
            return False
    return True


def _frame_preview(df: pd.DataFrame, limit=50):
    head = df.head(limit)
    return {
        "columns": [str(c) for c in head.columns],
        "rows": [[_cell(v) for v in row] for row in head.itertuples(index=False, name=None)],
    }


def _cell(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return round(float(v), 6)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return v if isinstance(v, (int, float, str, bool)) else str(v)


def run_sql(sql: str):
    """Execute a read-only query. Returns (preview, error)."""
    ok, why = looks_safe(sql)
    if not ok:
        return None, why
    try:
        df = pd.read_sql_query(sql, db())
    except Exception as e:  # noqa: BLE001 - surfaced to the user
        return None, f"SQL error: {e}"
    return _frame_preview(df), None


def check_sql(task_id: str, sql: str, attempt: int = 1):
    """Grade a SQL answer against the reference query."""
    task = SQL_BY_ID.get(task_id)
    if not task:
        return {"ok": False, "error": "Unknown task."}
    ok, why = looks_safe(sql)
    if not ok:
        return {"ok": False, "error": why, "hint": task["hint"]}
    try:
        user = pd.read_sql_query(sql, db())
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"SQL error: {e}", "hint": task["hint"]}

    ref = pd.read_sql_query(task["sql"], db())
    correct = _same_result(user, ref)
    out = {
        "ok": correct,
        "error": None,
        "preview": _frame_preview(user),
        "rows": int(len(user)),
        "cols": int(len(user.columns)),
        "expected_rows": int(ref.shape[0]),
        "expected_cols": int(ref.shape[1]),
        "hint": task["hint"],
        "reference": task["sql"] if attempt >= 3 else None,
    }
    if not correct and user.shape != ref.shape:
        out["error"] = (f"Not yet. You returned {len(user)} rows x {len(user.columns)} columns; "
                        f"the answer has {ref.shape[0]} rows x {ref.shape[1]} columns. "
                        f"Check your filter, join keys and rounding.")
    elif not correct:
        out["error"] = "Same shape, different values. Check the ordering key, grouping or rounding."
    return out


# ------------------------------------------------------------------ credit risk
@lru_cache(maxsize=4)
def credit_data(n: int = 4000, seed: int = 7) -> pd.DataFrame:
    rnd = np.random.default_rng(seed)
    income_k = rnd.lognormal(3.9, 0.45, n)
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


CREDIT_FEATURES = ["income_k", "dti", "ltv", "delinquencies", "employment_years",
                   "loan_amount_k", "credit_score"]
CREDIT_MODELS = ["Logistic regression", "Random forest", "Gradient boosting"]


def run_credit(features, model_name="Logistic regression", threshold=0.30):
    """Train and evaluate. Returns metrics, confusion matrix and feature weights."""
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                                 precision_score, recall_score, roc_auc_score)
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    features = [f for f in (features or []) if f in CREDIT_FEATURES]
    if not features:
        return {"error": "Pick at least one feature."}

    df = credit_data()
    X, y = df[features], df["default"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)

    if model_name == "Logistic regression":
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    elif model_name == "Random forest":
        model = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=0, n_jobs=-1)
    else:
        model = GradientBoostingClassifier(random_state=0)

    model.fit(Xtr, ytr)
    proba = model.predict_proba(Xte)[:, 1]
    pred = (proba >= float(threshold)).astype(int)

    base = max(yte.mean(), 1 - yte.mean())
    cm = confusion_matrix(yte, pred)
    if model_name == "Logistic regression":
        weights = list(zip(features, [float(c) for c in model[-1].coef_[0]]))
    else:
        weights = list(zip(features, [float(i) for i in model.feature_importances_]))
    weights.sort(key=lambda t: t[1])

    return {
        "auc": float(roc_auc_score(yte, proba)),
        "accuracy": float(accuracy_score(yte, pred)),
        "precision": float(precision_score(yte, pred, zero_division=0)),
        "recall": float(recall_score(yte, pred, zero_division=0)),
        "f1": float(f1_score(yte, pred, zero_division=0)),
        "base": float(base),
        "naive_accuracy": float(base),
        "n_test": int(len(yte)),
        "confusion": [[int(cm[0][0]), int(cm[0][1])], [int(cm[1][0]), int(cm[1][1])]],
        "missed_defaults": int(cm[1][0]),
        "total_defaults": int(cm[1].sum()),
        "weights": [{"name": n, "value": round(v, 5)} for n, v in weights],
        "usable": bool(roc_auc_score(yte, proba) > 0.72),
        "features": features,
        "model": model_name,
        "threshold": float(threshold),
    }


# ------------------------------------------------------------------ valuation
@lru_cache(maxsize=64)
def valuation_case(seed: int) -> dict:
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
        "seed": seed, "wacc": wacc, "g": g, "gt": gt, "fcf0": fcf0, "shares": shares,
        "net_debt": net_debt, "ev": ev, "equity": equity, "per_share": equity / shares,
        "fcfs": [round(f, 4) for f in fcfs], "pv": round(pv, 4), "tv": round(tv, 4),
        "pv_tv": round(tv / (1 + wacc) ** 5, 4),
    }


def public_case(seed: int) -> dict:
    """Case inputs only - the answers are stripped."""
    c = valuation_case(seed)
    return {k: c[k] for k in ("seed", "wacc", "g", "gt", "fcf0", "shares", "net_debt")}


def _close(a, b, tol=0.01):
    return abs(float(a) - float(b)) <= max(abs(float(b)) * tol, 0.5)


def grade_valuation(seed: int, ev, equity, per_share):
    c = valuation_case(seed)
    checks = [
        {"label": "Enterprise value", "you": float(ev), "answer": round(c["ev"], 2), "ok": _close(ev, c["ev"])},
        {"label": "Equity value", "you": float(equity), "answer": round(c["equity"], 2), "ok": _close(equity, c["equity"])},
        {"label": "Value per share", "you": float(per_share), "answer": round(c["per_share"], 2), "ok": _close(per_share, c["per_share"])},
    ]
    passed = sum(1 for c2 in checks if c2["ok"])
    return {
        "passed": passed, "of": 3, "checks": checks, "correct": passed == 3,
        "workings": {
            "fcfs": c["fcfs"], "pv": round(c["pv"], 2), "tv": round(c["tv"], 2),
            "pv_tv": round(c["pv_tv"], 2), "ev": round(c["ev"], 2),
            "equity": round(c["equity"], 2), "per_share": round(c["per_share"], 2),
        },
    }
