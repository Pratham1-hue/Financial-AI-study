"""Curated YouTube sources: channels we trust, playlists, and per-module search queries.

The sync script resolves every handle live against the API, so a wrong handle is reported
rather than silently shipped. Queries are deliberately specific - a vague query returns
clickbait, and this app is not a recommendation feed.
"""

# handle -> (display name, track, why it earns a place)
CHANNELS = {
    # ---------- finance ----------
    "@ThePlainBagel": ("The Plain Bagel", "finance", "Rigorous, evidence-based investing and personal finance."),
    "@BenFelixCSI": ("Ben Felix", "finance", "Academic research applied to real portfolios."),
    "@EconomicsExplained": ("Economics Explained", "finance", "Macro and national economies made concrete."),
    "@PBoyle": ("Patrick Boyle", "quant", "Ex-hedge-fund trader; derivatives, risk and market history."),
    "@AccountingStuff": ("Accounting Stuff", "finance", "The clearest free accounting fundamentals anywhere."),
    "UCLvnJL8htRR1T9cbSccaoVw": ("Aswath Damodaran", "finance", "NYU Stern valuation course - the canonical free valuation lectures."),
    "@CFAInstitute": ("CFA Institute", "finance", "Curriculum-grade finance from the charter body."),
    "@IMF": ("IMF", "finance", "Primary-source macro and monetary policy."),
    "@federalreserve": ("Federal Reserve", "finance", "The Fed explaining itself - FOMC, tools, transmission."),
    "@GoldmanSachs": ("Goldman Sachs", "career", "How the bank itself frames markets and careers."),
    "@markets": ("Bloomberg Markets", "finance", "Market structure and macro, from the terminal people."),
    "@business": ("Bloomberg Originals", "finance", "Documentary-grade reporting on markets and collapses."),
    "@yahoofinance": ("Yahoo Finance", "finance", "Longer executive and investor interviews than TV allows."),
    "@FinancialTimes": ("Financial Times", "finance", "The paper the industry reads, in short video form."),
    "@wsj": ("The Wall Street Journal", "finance", "Well-produced explainers on the Fed, deals and markets."),
    "@MoneyMacro": ("Money & Macro", "finance", "Monetary economics with actual data, from an economist."),
    "@HowMoneyWorks": ("How Money Works", "finance", "Clear explainers on money, banking and bubbles."),
    "@rareliquid": ("rareliquid", "finance", "Ex-banker walking through DCFs, LBOs and recruiting honestly."),
    "@KenjiExplains": ("Kenji Explains", "finance", "Financial modeling and Excel at a followable pace."),
    "@excelisfun": ("ExcelIsFun", "finance", "The best free Excel teaching on the internet."),
    "@JosephCarlsonShow": ("Joseph Carlson", "finance", "Portfolio construction and business analysis, spreadsheets shown."),
    "@cnbc": ("CNBC", "finance", "Fast market reaction and executive interviews; sentiment, not analysis."),
    # ---------- quant ----------
    "@DimitriBianco": ("Dimitri Bianco", "quant", "A working quant on risk, model validation and hiring."),
    "@RyanOConnellCFA": ("Ryan O'Connell", "quant", "Ex-banker on valuation, Excel and finance careers."),
    "@QuantInsti": ("QuantInsti", "quant", "Systematic trading and backtesting, taught by practitioners."),
    # ---------- AI / ML ----------
    "@3blue1brown": ("3Blue1Brown", "ai", "Linear algebra, calculus and neural nets, visualised."),
    "@statquest": ("StatQuest", "ai", "Statistics and ML, one small step at a time."),
    "@AndrejKarpathy": ("Andrej Karpathy", "ai", "Build GPT and backprop from scratch, with the person who did it at scale."),
    "@SerranoAcademy": ("Luis Serrano", "ai", "Math-first intuition for ML and LLMs."),
    "@campusx-official": ("CampusX", "ai", "Complete, structured ML and deep-learning curricula."),
    "@krishnaik06": ("Krish Naik", "ai", "Applied ML and MLOps with end-to-end projects."),
    "@coreyms": ("Corey Schafer", "ai", "The best free Python tutorials, full stop."),
    "@freecodecamp": ("freeCodeCamp", "ai", "Full-length university-grade courses."),
    "@YannicKilcher": ("Yannic Kilcher", "ai", "Paper walkthroughs by a working researcher."),
    "@aiexplained-official": ("AI Explained", "ai", "Careful, hype-resistant analysis of frontier models."),
    "@lexfridman": ("Lex Fridman", "ai", "Long-form conversations with the people building the field."),
    "@sentdex": ("Sentdex", "ai", "Practical Python for data and trading."),
    "@dataschool": ("Data School", "ai", "pandas and scikit-learn, taught cleanly."),
    "@mreflow": ("Matt Wolfe", "ai", "Fast-moving survey of AI tools and releases."),
    # ---------- quant ----------
    "@QuantPy": ("QuantPy", "quant", "Python for quantitative finance, from first principles."),
    "@MITOCW": ("MIT OpenCourseWare", "quant", "Actual MIT courses: probability, linear algebra, finance."),
    "@Computerphile": ("Computerphile", "quant", "Algorithms and systems explained by academics."),
    "@OxfordMathematics": ("Oxford Mathematics", "quant", "Rigorous maths for stochastic calculus and optimisation."),
    # ---------- career ----------
    "@NeetCode": ("NeetCode", "career", "The clearest coding-interview pattern explanations."),
    "@DanCroitor": ("Dan Croitor", "career", "Amazon leadership-principle and behavioural interview prep."),
    "UCjm_qVkCPjOVDz9BWjNqO9A": ("Exponent", "career", "Mock interviews and system-design walkthroughs."),
    "@TechWithTim": ("Tech With Tim", "career", "Project-based Python, useful for portfolio work."),
}

# Playlists worth pulling whole: id -> (title, module)
PLAYLISTS = {
    "PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ": ("Neural Networks: Zero to Hero", "A4"),
}

# Two precise queries per module. `search` costs 100 units each, cached for a week.
# The first is conceptual, the second is the technical / worked-example pass.
MODULE_QUERIES = {
    "F1": ["financial markets explained for beginners stocks bonds ETFs interest rates",
           "how the stock market works order book market makers"],
    "F2": ["how to read financial statements income statement balance sheet cash flow statement",
           "financial ratio analysis tutorial ROE ROA P/E"],
    "F3": ["DCF valuation tutorial WACC discounted cash flow",
           "investment banking valuation methods comparable company analysis"],
    "F4": ["CAPM beta efficient frontier portfolio theory explained",
           "fama french factor model momentum value investing lecture"],
    "F5": ["black scholes option pricing derivation quantitative finance",
           "value at risk expected shortfall risk management explained"],
    "F6": ["options greeks delta gamma theta vega explained",
           "options trading course calls puts implied volatility",
           "option pricing black scholes greeks university lecture"],
    "F7": ["federal reserve monetary policy interest rates inflation explained",
           "yield curve inversion recession explained macroeconomics",
           "macroeconomics monetary policy lecture university"],
    "F8": ["market microstructure limit order book explained",
           "dark pools high frequency trading explained"],
    "A1": ["python numpy pandas tutorial for data analysis full course",
           "python object oriented programming tutorial"],
    "A2": ["linear algebra for machine learning full course",
           "probability statistics for machine learning bayes theorem"],
    "A3": ["machine learning fundamentals gradient boosting random forest explained",
           "logistic regression linear regression machine learning tutorial"],
    "A4": ["neural network backpropagation deep learning explained from scratch",
           "convolutional neural networks CNN explained"],
    "A5": ["transformers attention mechanism large language models explained",
           "word embeddings word2vec explained NLP"],
    "A6": ["mlops model deployment fastapi docker tutorial",
           "machine learning model production monitoring data drift"],
    "A7": ["sql window functions tutorial for data analysis",
           "database design normalization star schema explained"],
    "A8": ["diffusion models explained stable diffusion",
           "reinforcement learning q learning policy gradient explained"],
    "C1": ["coding interview patterns leetcode explained",
           "machine learning system design interview"],
    "C2": ["end to end machine learning project portfolio tutorial",
           "rag retrieval augmented generation project tutorial",
           "build full stack machine learning app portfolio project"],
}

# Keywords per module: used to score candidates by title relevance.
MODULE_KEYWORDS = {
    "F1": ["stock", "bond", "market", "etf", "interest rate", "inflation", "invest"],
    "F2": ["financial statement", "income statement", "balance sheet", "cash flow", "accounting", "10-k"],
    "F3": ["dcf", "valuation", "wacc", "npv", "irr", "discounted cash flow", "terminal value"],
    "F4": ["capm", "portfolio", "efficient frontier", "beta", "diversification", "sharpe", "factor"],
    "F5": ["black scholes", "brownian", "stochastic", "value at risk", "var", "quantitative finance", "monte carlo"],
    "F6": ["option", "greeks", "delta", "gamma", "theta", "vega", "put", "call", "implied volatility"],
    "F7": ["federal reserve", "fed", "monetary policy", "inflation", "interest rate", "fomc", "gdp", "yield curve"],
    "F8": ["market microstructure", "order book", "dark pool", "algorithmic trading", "hft", "limit order", "defi"],
    "A1": ["python", "numpy", "pandas", "dataframe", "tutorial"],
    "A2": ["linear algebra", "statistics", "probability", "calculus", "gradient", "bayes", "eigen"],
    "A3": ["machine learning", "regression", "random forest", "gradient boosting", "xgboost", "classification", "overfitting"],
    "A4": ["neural network", "backpropagation", "deep learning", "cnn", "pytorch", "gradient descent"],
    "A5": ["transformer", "attention", "llm", "language model", "gpt", "embedding", "rag"],
    "A6": ["mlops", "deployment", "fastapi", "docker", "mlflow", "serving", "production"],
    "A7": ["sql", "window function", "join", "database", "postgres", "data engineering", "snowflake"],
    "A8": ["diffusion", "reinforcement learning", "object detection", "yolo", "gan", "segmentation", "agent"],
    "C1": ["interview", "leetcode", "coding", "algorithm", "system design", "behavioral"],
    "C2": ["project", "portfolio", "end to end", "capstone", "deploy", "github"],
}
