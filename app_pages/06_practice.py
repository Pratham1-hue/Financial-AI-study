import streamlit as st
from lib.ui import hero, section, inject_css, badge
from lib.storage import load_progress

inject_css()
hero("Practice Materials", "Problem sets, case studies, and datasets to drill.")

progress = load_progress()

PRACTICE = [
    {"title": "Finance: DCF Valuation Drill", "track": "finance", "diff": "Medium",
     "desc": "Value a company using a 5-year DCF with terminal value. Compute WACC, project FCF, derive intrinsic value per share.",
     "tasks": ["Compute WACC from given inputs", "Project revenue/EBITDA/FCF for 5 years", "Compute terminal value (Gordon growth)", "Derive per-share value and margin of safety"]},
    {"title": "Finance: Ratio Analysis of a 10-K", "track": "finance", "diff": "Easy",
     "desc": "Pick any S&P 500 company, download 10-K, compute 15 ratios and interpret.",
     "tasks": ["Gross/operating/net margin", "ROE, ROA, ROIC", "Current ratio, quick ratio", "D/E, interest coverage", "P/E, P/B, EV/EBITDA"]},
    {"title": "Quant: Black-Scholes Greeks", "track": "quant", "diff": "Hard",
     "desc": "Implement all Greeks (delta, gamma, theta, vega, rho) and plot vs spot.",
     "tasks": ["Implement d1, d2", "Compute each Greek", "Plot delta vs spot price", "Verify put-call parity numerically"]},
    {"title": "Quant: Monte Carlo Option Pricing", "track": "quant", "diff": "Hard",
     "desc": "Price an Asian option via Monte Carlo with variance reduction.",
     "tasks": ["Simulate GBM paths", "Compute payoff", "Apply control variate", "Compare to Black-Scholes"]},
    {"title": "Quant: Backtester", "track": "quant", "diff": "Hard",
     "desc": "Build a moving-average crossover backtester with transaction costs.",
     "tasks": ["Load price data", "Generate signals", "Simulate trades with costs", "Compute Sharpe, max drawdown"]},
    {"title": "AI: EDA on a Dataset", "track": "ai", "diff": "Easy",
     "desc": "Perform full EDA: distributions, correlations, missing values, outliers.",
     "tasks": ["Summary statistics", "Missing value handling", "Correlation heatmap", "Feature insights"]},
    {"title": "AI: Classification Pipeline", "track": "ai", "diff": "Medium",
     "desc": "Build sklearn pipeline: preprocessing + model + CV + tuning.",
     "tasks": ["Train/test split", "Preprocessing (scale, encode)", "Cross-validation", "Hyperparameter tuning", "Evaluation report"]},
    {"title": "AI: Neural Net from Scratch", "track": "ai", "diff": "Hard",
     "desc": "Implement a 2-layer NN with backprop using only NumPy.",
     "tasks": ["Forward pass", "Loss computation", "Backprop", "Gradient descent update", "Train on XOR or MNIST subset"]},
    {"title": "AI: CNN Image Classifier", "track": "ai", "diff": "Medium",
     "desc": "Train a CNN on CIFAR-10 with PyTorch, achieve >80% accuracy.",
     "tasks": ["Data loading & augmentation", "Model definition", "Training loop", "Evaluation & confusion matrix"]},
    {"title": "AI: RAG over 10-K Filings", "track": "ai", "diff": "Hard",
     "desc": "Build retrieval-augmented QA over company filings.",
     "tasks": ["Ingest & chunk PDFs", "Embed with sentence-transformers", "Vector store (FAISS/Chroma)", "Retrieval + LLM answer with citations"]},
    {"title": "AI: LLM Fine-tuning", "track": "ai", "diff": "Hard",
     "desc": "Fine-tune a small LLM with LoRA on a finance Q&A dataset.",
     "tasks": ["Prepare dataset", "Configure LoRA", "Train with PEFT", "Evaluate vs base"]},
    {"title": "SQL: Window Functions Drill", "track": "ai", "diff": "Medium",
     "desc": "Solve 10 SQL problems using window functions (running totals, ranks).",
     "tasks": ["ROW_NUMBER, RANK, DENSE_RANK", "Running sum", "Moving average", "LAG/LEAD"]},
    {"title": "Career: LeetCode 75", "track": "career", "diff": "Medium",
     "desc": "Complete NeetCode 150 / LeetCode 75 curated list.",
     "tasks": ["Arrays & hashing", "Two pointers", "Sliding window", "Trees", "Graphs", "DP"]},
    {"title": "Career: System Design", "track": "career", "diff": "Hard",
     "desc": "Design a recommendation system and a fraud detection system.",
     "tasks": ["Requirements", "High-level architecture", "Data flow", "Scaling & tradeoffs"]},
    {"title": "Career: Mock Interview", "track": "career", "diff": "Medium",
     "desc": "Conduct a 45-min mock technical + behavioral interview.",
     "tasks": ["Coding problem (30 min)", "Behavioral STAR (10 min)", "Feedback & action items"]},
]

track_f = st.segmented_control("Track", options=["all", "finance", "ai", "quant", "career"], default="all")
diff_f = st.selectbox("Difficulty", options=["All", "Easy", "Medium", "Hard"], index=0)

items = PRACTICE
if track_f != "all":
    items = [p for p in items if p["track"] == track_f]
if diff_f != "All":
    items = [p for p in items if p["diff"] == diff_f]

st.caption(f"{len(items)} practice items")

for p in items:
    with st.container(border=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"### {p['title']}")
            st.caption(f"{p['track'].upper()} · {p['diff']}")
            st.markdown(p["desc"])
        with c2:
            st.markdown("")
        with st.expander("Tasks"):
            for t in p["tasks"]:
                st.checkbox(t, key=f"task_{p['title']}_{t}")