"""Curriculum content: topics, modules, lessons, resources.
Each module carries ``specialties`` so the learner can steer toward:
  * ai_researcher  - publishable ML/AI research (SOTA, papers, novel methods)
  * ml_engineer    - production ML systems (serving, MLOps, feature stores)
  * finance_ib     - investment banking NYC (modeling, valuation, deals)
  * finance_quant  - hedge fund / prop trading (probability, microstructure)
  * finance_corp   - corporate finance / FP&A (3-statement, DCF, budgeting)
"""
from lib.resources import RESOURCES

TRACKS = {
    "finance": {"name": "Finance & Markets", "color": "#D97706", "icon": "trending_up"},
    "ai": {"name": "AI & Machine Learning", "color": "#2563EB", "icon": "psychology"},
    "quant": {"name": "Quantitative", "color": "#7C3AED", "icon": "functions"},
    "career": {"name": "Career & Interview", "color": "#059669", "icon": "work"},
    "research": {"name": "Research & Open Source", "color": "#DC2626", "icon": "science"},
}

SPECIALTIES = {
    "ai_researcher": "AI Researcher",
    "ml_engineer": "ML Engineer",
    "finance_ib": "Investment Banking (NYC)",
    "finance_quant": "Hedge Fund / Quant",
    "finance_corp": "Corporate Finance",
}

MODULES = [
    # ============================================================
    # SHARED FOUNDATIONS (Weeks 1-4) - everyone starts here
    # ============================================================
    {
        "id": "F1", "track": "finance", "title": "Financial Literacy & Markets Basics",
        "weeks": [1], "level": "Beginner",
        "specialties": ["finance_ib", "finance_quant", "finance_corp"],
        "summary": "Money, markets, instruments, and how the financial system moves.",
        "lessons": [
            "What is money, inflation, interest rates, and time value of money",
            "Stocks vs bonds vs ETFs vs crypto vs real estate",
            "How stock exchanges work: NYSE, NASDAQ, order books, market makers",
            "Reading a ticker, candlesticks, volume, market cap",
            "Bull/bear markets, cycles, and sentiment",
            "Risk vs return, diversification, correlation",
            "Personal finance: budgeting, emergency fund, debt, credit score",
            "NYC cost of living and salary expectations for entry-level roles",
        ],
        "outcomes": ["Explain how markets price assets", "Read any stock chart", "Build a basic portfolio"],
        "resources": ["r_plainbagel", "r_khan_finance", "r_investopedia", "rf_yale_econ252", "rf_yt_howmoneyworks", "rf_yt_bloomberg"],
    },
    {
        "id": "A1", "track": "ai", "title": "Python for Data & ML",
        "weeks": [1, 2], "level": "Beginner",
        "specialties": ["ai_researcher", "ml_engineer", "finance_quant"],
        "summary": "Master Python, NumPy, pandas, and the data toolchain.",
        "lessons": [
            "Python basics: types, control flow, functions, OOP",
            "NumPy: arrays, broadcasting, vectorization",
            "pandas: Series, DataFrame, groupby, merge, pivot",
            "Data cleaning: missing values, outliers, types",
            "Visualization: matplotlib, seaborn, plotly",
            "Jupyter, virtualenv, git workflow",
            "Performance: vectorization, profiling",
            "Writing research-quality code (reproducible, documented, tested)",
        ],
        "outcomes": ["Manipulate any dataset", "Write clean Python", "Use git professionally"],
        "resources": ["r_python_org", "r_kaggle_learn_python", "r_realpython", "ra_sklearn", "ra_jax", "r_yt_python"],
    },
    {
        "id": "F2", "track": "finance", "title": "Accounting & Financial Statements",
        "weeks": [2], "level": "Beginner",
        "specialties": ["finance_ib", "finance_corp"],
        "summary": "Read and analyze balance sheets, income statements, cash flow statements.",
        "lessons": [
            "The accounting equation: Assets = Liabilities + Equity",
            "Income statement: revenue, COGS, gross/operating/net margin",
            "Balance sheet: current vs non-current, working capital",
            "Cash flow statement: operating, investing, financing",
            "Key ratios: P/E, P/B, ROE, ROA, current ratio, D/E",
            "Red flags in financial statements (Enron-style)",
            "Hands-on: analyze 3 real 10-K filings",
            "3-statement modeling basics (linking the statements)",
        ],
        "outcomes": ["Read any 10-K", "Compute 20+ ratios", "Spot accounting red flags"],
        "resources": ["rf_openstax_acc1", "r_damodaran", "r_sec_edgar", "rf_wsp_knowledge", "rf_sec_structured", "r_yt_accounting"],
    },
    {
        "id": "A2", "track": "ai", "title": "Math & Statistics for ML",
        "weeks": [2, 3], "level": "Beginner",
        "specialties": ["ai_researcher", "ml_engineer", "finance_quant"],
        "summary": "Linear algebra, calculus, probability, statistics — the ML foundation.",
        "lessons": [
            "Linear algebra: vectors, matrices, eigenvalues, SVD, PCA",
            "Calculus: derivatives, gradients, chain rule",
            "Probability: distributions, Bayes, conditional probability",
            "Statistics: hypothesis testing, confidence intervals, p-values",
            "Information theory: entropy, KL divergence",
            "Optimization: gradient descent, convexity",
            "Math for deep learning: backprop intuition",
            "Probability puzzles and brain teasers (quant interview prep)",
        ],
        "outcomes": ["Derive gradients", "Apply Bayes", "Understand ML math"],
        "resources": ["ra_mml", "ra_isl", "ra_esl", "r_3b1b", "r_statquest", "r_khan_stats"],
    },
    # ============================================================
    # PHASE 2 - CORE (Weeks 5-8) - branching begins
    # ============================================================
    {
        "id": "F3", "track": "finance", "title": "Corporate Finance & Valuation",
        "weeks": [3, 4], "level": "Intermediate",
        "specialties": ["finance_ib", "finance_corp"],
        "summary": "DCF, comparables, precedent transactions, M&A, capital structure.",
        "lessons": [
            "Time value of money, NPV, IRR, payback",
            "WACC and cost of capital",
            "DCF valuation end-to-end",
            "Comparable company analysis (Comps)",
            "Precedent transactions",
            "M&A: accretion/dilution, synergies",
            "Capital structure: debt vs equity, Modigliani-Miller",
            "Dividend policy and buybacks",
            "Investment banking technicals: walking through a DCF in an interview",
        ],
        "outcomes": ["Value any company with DCF", "Build a 3-statement model", "Pitch a stock"],
        "resources": ["rf_damodaran", "rf_mit_15401", "rf_wsp_knowledge", "rf_yt_kenji", "rf_yt_rareliquid", "rf_damodaran_data"],
    },
    {
        "id": "A3", "track": "ai", "title": "Machine Learning Fundamentals",
        "weeks": [3, 4, 5], "level": "Intermediate",
        "specialties": ["ai_researcher", "ml_engineer"],
        "summary": "Supervised/unsupervised learning, model evaluation, feature engineering.",
        "lessons": [
            "ML taxonomy: supervised, unsupervised, RL",
            "Linear & logistic regression",
            "Decision trees, random forests, gradient boosting (XGBoost, LightGBM)",
            "SVM, kNN, naive Bayes",
            "Clustering: K-means, hierarchical, DBSCAN",
            "Dimensionality reduction: PCA, t-SNE, UMAP",
            "Model evaluation: train/val/test, CV, metrics",
            "Feature engineering and selection",
            "Bias-variance tradeoff, regularization",
            "Hyperparameter tuning, pipelines (sklearn)",
            "Writing ML research code vs production ML code",
        ],
        "outcomes": ["Build end-to-end ML pipeline", "Choose right model", "Avoid overfitting"],
        "resources": ["ra_cs229", "ra_isl", "r_sklearn_docs", "ra_xgboost", "ra_mit_6036", "r_andrewng"],
    },
    {
        "id": "F4", "track": "finance", "title": "Investing & Portfolio Theory",
        "weeks": [4, 5], "level": "Intermediate",
        "specialties": ["finance_ib", "finance_quant", "finance_corp"],
        "summary": "Modern portfolio theory, asset allocation, factor investing, behavioral finance.",
        "lessons": [
            "Mean-variance optimization, efficient frontier",
            "CAPM, beta, alpha, Sharpe, Sortino",
            "Factor models: Fama-French, momentum, value",
            "Asset allocation: 60/40, risk parity, All-Weather",
            "Rebalancing and tax-aware investing",
            "Behavioral finance: biases, prospect theory",
            "Index funds vs active management",
            "ESG and sustainable investing",
        ],
        "outcomes": ["Construct an efficient portfolio", "Backtest a strategy", "Explain behavioral biases"],
        "resources": ["rf_french", "rf_aqr", "rf_alphaarchitect", "rf_mit_15401", "r_bogleheads", "r_yt_investing"],
    },
    {
        "id": "A4", "track": "ai", "title": "Deep Learning & Neural Networks",
        "weeks": [5, 6, 7], "level": "Advanced",
        "specialties": ["ai_researcher", "ml_engineer"],
        "summary": "Neural nets, CNNs, RNNs, transformers, and training at scale.",
        "lessons": [
            "Perceptron, MLP, activation functions",
            "Backpropagation and autograd",
            "CNNs: convolutions, pooling, ResNet",
            "RNNs, LSTMs, GRUs",
            "Attention mechanism and Transformers",
            "Training: optimizers (Adam), LR schedules, batch norm, dropout",
            "Regularization and data augmentation",
            "Transfer learning and fine-tuning",
            "PyTorch fundamentals",
            "GPU/TPU and mixed precision",
            "Reading and reproducing DL papers (for researcher track)",
        ],
        "outcomes": ["Build CNN/RNN/Transformer in PyTorch", "Train and debug DL models"],
        "resources": ["ra_d2l", "rr_nanogpt", "ra_pytorch", "ra_dlbook", "ra_cs231n", "r_karpathy"],
    },
    # ============================================================
    # PHASE 3 - ADVANCED (Weeks 9-12) - specialization deepens
    # ============================================================
    {
        "id": "F5", "track": "quant", "title": "Quantitative Finance & Risk",
        "weeks": [6, 7], "level": "Advanced",
        "specialties": ["finance_quant"],
        "summary": "Stochastic processes, VaR, Monte Carlo, and systematic trading.",
        "lessons": [
            "Random walks, Brownian motion, geometric Brownian motion",
            "Ito's lemma, Black-Scholes derivation",
            "Value at Risk (VaR), Expected Shortfall",
            "Monte Carlo simulation for pricing",
            "Backtesting: look-ahead bias, overfitting, transaction costs",
            "Risk management: position sizing, Kelly criterion",
            "High-frequency trading basics and market microstructure",
            "Quant libraries: QuantLib, zipline, backtrader",
            "Probability brain teasers (prop shop interview prep)",
        ],
        "outcomes": ["Price options via Monte Carlo", "Build a backtester", "Compute VaR"],
        "resources": ["rq_quantlib", "rf_french", "rq_arch", "rf_bis_qr", "r_yt_patrickboyle", "rf_mit_15997"],
    },
    {
        "id": "F6", "track": "quant", "title": "Derivatives & Options",
        "weeks": [7], "level": "Advanced",
        "specialties": ["finance_quant"],
        "summary": "Options, futures, swaps, Greeks, and hedging.",
        "lessons": [
            "Calls, puts, strike, expiry, premium",
            "Put-call parity",
            "The Greeks: delta, gamma, theta, vega, rho",
            "Black-Scholes model",
            "Implied volatility and the vol smile",
            "Futures and forwards, contango/backwardation",
            "Swaps and interest rate derivatives",
            "Hedging strategies: covered calls, protective puts, collars",
        ],
        "outcomes": ["Compute Greeks", "Price with Black-Scholes", "Design a hedge"],
        "resources": ["r_yt_options", "r_cboe", "r_book_hull", "rq_quantlib", "r_yt_patrickboyle", "rf_yt_bloomberg_tv"],
    },
    {
        "id": "F7", "track": "finance", "title": "Macroeconomics & Monetary Policy",
        "weeks": [8], "level": "Intermediate",
        "specialties": ["finance_ib", "finance_quant", "finance_corp"],
        "summary": "GDP, inflation, Fed policy, rates, FX, and global macro.",
        "lessons": [
            "GDP, unemployment, CPI, PCE",
            "Federal Reserve: mandate, tools, FOMC",
            "Interest rate transmission",
            "Yield curve and recession signals",
            "FX markets and carry trade",
            "Quantitative easing and balance sheet",
            "Global macro: China, Europe, emerging markets",
            "Reading macro data releases",
            "How macro moves markets (NYC trading desk context)",
        ],
        "outcomes": ["Interpret Fed decisions", "Read yield curve", "Track macro indicators"],
        "resources": ["rf_fed_h15", "rf_fed_data", "rf_bis_qr", "rf_imf_weo", "rf_nyfed_lse", "rf_bls"],
    },
    {
        "id": "F8", "track": "finance", "title": "Fintech, Data & Market Microstructure",
        "weeks": [9], "level": "Advanced",
        "specialties": ["finance_quant", "ml_engineer"],
        "summary": "Modern fintech, HFT, crypto, and data-driven finance.",
        "lessons": [
            "Market microstructure: order types, dark pools, NBBO",
            "Algorithmic trading architecture",
            "Crypto: blockchain, DeFi, stablecoins",
            "Payments, lending, robo-advisors",
            "RegTech and compliance (SEC, FINRA)",
            "Alternative data for alpha",
            "APIs: Alpaca, Polygon, Yahoo Finance",
            "Building a low-latency trading pipeline",
        ],
        "outcomes": ["Build a simple algo trader", "Use market data APIs", "Understand HFT"],
        "resources": ["r_polygon", "rf_bis_stats", "rf_janestreet_talks", "rq_nautilus", "rf_man", "r_alpaca"],
    },
    {
        "id": "A5", "track": "ai", "title": "NLP & Large Language Models",
        "weeks": [8, 9], "level": "Advanced",
        "specialties": ["ai_researcher", "ml_engineer"],
        "summary": "Text processing, embeddings, transformers, LLMs, RAG, agents.",
        "lessons": [
            "Text preprocessing, tokenization, embeddings",
            "Word2Vec, GloVe, fastText",
            "Transformer architecture deep dive",
            "BERT, GPT, T5 families",
            "Prompt engineering and few-shot",
            "Fine-tuning: LoRA, QLoRA, PEFT",
            "RAG: chunking, vector DBs, retrieval",
            "Agents, tool use, function calling",
            "Evaluation: hallucination, benchmarks",
            "Hugging Face ecosystem",
            "Reading and reproducing NLP papers (researcher track)",
            "Serving LLMs at scale (engineer track)",
        ],
        "outcomes": ["Build a RAG app", "Fine-tune an LLM", "Deploy an LLM agent"],
        "resources": ["ra_hf_course", "ra_p_attention", "ra_jurafsky", "ra_lilian", "ra_p_rag", "ra_llm_course"],
    },
    {
        "id": "A6", "track": "ai", "title": "MLOps & Production",
        "weeks": [10, 11], "level": "Advanced",
        "specialties": ["ml_engineer"],
        "summary": "Deploy, monitor, and maintain ML systems in production.",
        "lessons": [
            "ML lifecycle and experiment tracking (MLflow, W&B)",
            "Model serving: FastAPI, TorchServe, Triton",
            "Containerization with Docker",
            "CI/CD for ML",
            "Feature stores",
            "Monitoring: drift, latency, cost",
            "A/B testing and shadow deployment",
            "Cost optimization and scaling",
            "Building ML platforms (engineer track focus)",
        ],
        "outcomes": ["Deploy a model as API", "Set up monitoring", "Containerize ML app"],
        "resources": ["ra_mlops_zoomcamp", "ra_madewithml", "ra_fsdl", "ra_mlflow", "ra_evidently", "r_docker"],
    },
    {
        "id": "A7", "track": "ai", "title": "Data Engineering & SQL",
        "weeks": [3, 9], "level": "Intermediate",
        "specialties": ["ml_engineer", "finance_quant"],
        "summary": "SQL, databases, pipelines, and data warehousing.",
        "lessons": [
            "SQL: SELECT, JOIN, GROUP BY, window functions",
            "Database design and normalization",
            "PostgreSQL, BigQuery, Snowflake",
            "ETL/ELT pipelines, Airflow",
            "Data modeling: star schema, slowly changing dims",
            "Streaming: Kafka basics",
            "Data quality and testing",
            "Financial data pipelines (quant/finance focus)",
        ],
        "outcomes": ["Write complex SQL", "Design a data warehouse", "Build a pipeline"],
        "resources": ["r_sqlbolt", "r_mode_sql", "rr_dbt", "rr_airflow", "rq_duckdb", "rr_great_expectations"],
    },
    {
        "id": "A8", "track": "ai", "title": "Advanced AI: CV, RL & Agents",
        "weeks": [11, 12], "level": "Advanced",
        "specialties": ["ai_researcher"],
        "summary": "Computer vision, reinforcement learning, and autonomous agents.",
        "lessons": [
            "Object detection: YOLO, Faster R-CNN",
            "Segmentation: U-Net, SAM",
            "Generative models: GANs, VAEs, diffusion",
            "RL: MDPs, Q-learning, PPO, DQN",
            "Multi-agent systems",
            "Vision-language models",
            "AI safety and alignment basics",
            "Reading and reproducing research papers (researcher track)",
            "Novel method development and experimentation",
        ],
        "outcomes": ["Train a CV model", "Implement RL agent", "Build multi-modal app"],
        "resources": ["ra_cs231n", "ra_spinningup", "ra_p_react", "rr_diffusers", "ra_cs25", "r_openai_cookbook"],
    },
    # ============================================================
    # PHASE 4 - JOB HUNT (Weeks 13-16) - NYC placement
    # ============================================================
    {
        "id": "C1", "track": "career", "title": "Interview Prep & Job Hunt (NYC)",
        "weeks": [13, 14, 15, 16], "level": "All",
        "specialties": ["ai_researcher", "ml_engineer", "finance_ib", "finance_quant", "finance_corp"],
        "summary": "Coding interviews, ML system design, finance cases, behavioral, networking.",
        "lessons": [
            "LeetCode patterns: arrays, trees, graphs, DP, two pointers",
            "SQL interview questions",
            "ML system design: recommendations, fraud, forecasting",
            "Finance case studies and brain teasers",
            "Investment banking technicals: DCF walkthrough, accretion/dilution",
            "Quant/prop shop: probability, brain teasers, market questions",
            "Behavioral: STAR method, leadership stories",
            "Resume and LinkedIn optimization for NYC",
            "Networking: meetups, alumni, cold outreach",
            "Mock interviews and feedback loops",
            "Salary negotiation (NYC comp bands)",
        ],
        "outcomes": ["Crack technical interviews", "Land NYC offers", "Negotiate top compensation"],
        "resources": ["rc_neetcode", "rc_quantguide", "rc_levelsfyi", "rc_systemdesign", "rc_wso", "rc_ml_interviews"],
    },
    {
        "id": "C2", "track": "career", "title": "Capstone Projects & Portfolio",
        "weeks": [12, 13, 14], "level": "Advanced",
        "specialties": ["ai_researcher", "ml_engineer", "finance_ib", "finance_quant", "finance_corp"],
        "summary": "Build 3 portfolio projects that get you hired in NYC.",
        "lessons": [
            "Project 1: Quant trading backtester with ML signals (finance_quant)",
            "Project 2: LLM-powered financial analyst (RAG over 10-Ks) (finance_ib/ml_engineer)",
            "Project 3: ML risk model / credit scoring (finance_corp/ml_engineer)",
            "Project 4 (AI researcher): Reproduce a SOTA paper or novel architecture",
            "Project 5 (ML engineer): Production ML system with monitoring and feature store",
            "GitHub polish, READMEs, demos",
            "Deployment: Streamlit Cloud, Hugging Face Spaces, AWS",
            "Blog posts and thought leadership",
            "Open-source contributions",
        ],
        "outcomes": ["3 deployed projects", "Strong GitHub", "Public portfolio"],
        "resources": ["r_github", "r_hf_spaces", "r_streamlit_cloud", "rr_nanogpt", "ra_fsdl", "ra_madewithml"],
    },
]

# Map module id -> module
MODULE_BY_ID = {m["id"]: m for m in MODULES}


def modules_for_week(w):
    return [m for m in MODULES if w in m["weeks"]]


def modules_for_track(track):
    return [m for m in MODULES if m["track"] == track]


def all_module_ids():
    return [m["id"] for m in MODULES]


def modules_for_specialty(specialty):
    """Modules relevant to a given career specialty."""
    return [m for m in MODULES if specialty in m.get("specialties", [])]


def specialty_summary():
    return {
        "ai_researcher": {
            "name": "AI Researcher",
            "tagline": "Publishable ML/AI research — SOTA, papers, novel methods.",
            "key_modules": ["A2", "A4", "A5", "A8"],
            "focus": "Math foundations, DL papers, reproduction, novel methods.",
        },
        "ml_engineer": {
            "name": "ML Engineer",
            "tagline": "Production ML systems — serving, MLOps, feature stores.",
            "key_modules": ["A3", "A4", "A5", "A6", "A7"],
            "focus": "Deployment, monitoring, containers, CI/CD, scale.",
        },
        "finance_ib": {
            "name": "Investment Banking (NYC)",
            "tagline": "IB technicals — modeling, valuation, deals.",
            "key_modules": ["F1", "F2", "F3", "F4", "F7"],
            "focus": "3-statement models, DCF, comps, M&A, interview technicals.",
        },
        "finance_quant": {
            "name": "Hedge Fund / Quant",
            "tagline": "Prop trading — probability, microstructure, systematic strategies.",
            "key_modules": ["A1", "A2", "A7", "F5", "F6", "F8"],
            "focus": "Stochastic processes, derivatives, backtesting, HFT.",
        },
        "finance_corp": {
            "name": "Corporate Finance",
            "tagline": "Corporate finance / FP&A — 3-statement, DCF, budgeting.",
            "key_modules": ["F1", "F2", "F3", "F4", "F7"],
            "focus": "Accounting, valuation, financial planning, analysis.",
        },
    }
