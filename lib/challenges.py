"""Auto-graded challenges (Le Wagon / Hack Reactor style) with a test harness."""
import json
from datetime import date

from lib.code_runner import run_python

MARKER = "@@DEVI_RESULTS@@"

HARNESS = """

import json as __json
__results = []
for __name, __src in __DEVI_TESTS__:
    try:
        exec(__src, globals())
        __results.append([__name, True, ""])
    except AssertionError as __e:
        __results.append([__name, False, str(__e) or "assertion failed"])
    except Exception as __e:
        __results.append([__name, False, type(__e).__name__ + ": " + str(__e)])
print("{marker}" + __json.dumps(__results))
"""

CHALLENGES = [
    # ---------------- Algorithms (toy problems) ----------------
    {"id": "t_two_sum", "track": "Algorithms", "diff": "Easy", "title": "Two sum",
     "prompt": "Write `two_sum(nums, target)` returning the indices `[i, j]` (i < j) of the two numbers that add up to `target`. Aim for O(n).",
     "starter": "def two_sum(nums, target):\n    pass\n",
     "tests": [("basic", "assert two_sum([2, 7, 11, 15], 9) == [0, 1]"),
               ("middle", "assert two_sum([3, 2, 4], 6) == [1, 2]"),
               ("duplicates", "assert two_sum([3, 3], 6) == [0, 1]")],
     "hints": ["A hash map from value -> index lets you check the complement in O(1).",
               "For each x at index i, check if target - x is already in the map before inserting x."],
     "solution": "def two_sum(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n        if target - x in seen:\n            return [seen[target - x], i]\n        seen[x] = i\n"},
    {"id": "t_max_profit", "track": "Algorithms", "diff": "Easy", "title": "Best time to buy and sell",
     "prompt": "Write `max_profit(prices)` returning the max profit from one buy then one sell (0 if no profit).",
     "starter": "def max_profit(prices):\n    pass\n",
     "tests": [("classic", "assert max_profit([7, 1, 5, 3, 6, 4]) == 5"),
               ("falling", "assert max_profit([7, 6, 4, 3, 1]) == 0"),
               ("empty", "assert max_profit([]) == 0")],
     "hints": ["Track the minimum price seen so far.", "At each price, profit candidate = price - min_so_far."],
     "solution": "def max_profit(prices):\n    best, lo = 0, float('inf')\n    for p in prices:\n        lo = min(lo, p)\n        best = max(best, p - lo)\n    return best\n"},
    {"id": "t_valid_parens", "track": "Algorithms", "diff": "Easy", "title": "Valid brackets",
     "prompt": "Write `is_valid(s)` returning True if every bracket in `s` (`()[]{}`) is closed in the right order.",
     "starter": "def is_valid(s):\n    pass\n",
     "tests": [("mixed", "assert is_valid('()[]{}') is True"), ("wrong type", "assert is_valid('(]') is False"),
               ("interleaved", "assert is_valid('([)]') is False"), ("nested", "assert is_valid('{[]}') is True"),
               ("empty", "assert is_valid('') is True")],
     "hints": ["Use a stack.", "Push openers; on a closer, the top of the stack must be its matching opener."],
     "solution": "def is_valid(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    st = []\n    for c in s:\n        if c in pairs:\n            if not st or st.pop() != pairs[c]:\n                return False\n        else:\n            st.append(c)\n    return not st\n"},
    {"id": "t_binary_search", "track": "Algorithms", "diff": "Easy", "title": "Binary search",
     "prompt": "Write `binary_search(arr, target)` on a sorted list, returning the index or -1. Must be O(log n).",
     "starter": "def binary_search(arr, target):\n    pass\n",
     "tests": [("found", "assert binary_search([1, 3, 5, 7, 9], 7) == 3"), ("missing", "assert binary_search([1, 3, 5, 7, 9], 2) == -1"),
               ("empty", "assert binary_search([], 1) == -1"), ("ends", "assert binary_search([1, 3, 5], 1) == 0 and binary_search([1, 3, 5], 5) == 2")],
     "hints": ["Keep lo and hi pointers; look at mid = (lo + hi) // 2.", "Move lo = mid + 1 or hi = mid - 1 depending on the comparison."],
     "solution": "def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        if arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n"},
    {"id": "t_moving_avg", "track": "Algorithms", "diff": "Medium", "title": "Moving average in O(n)",
     "prompt": "Write `moving_average(xs, k)` returning the list of k-period simple moving averages (length n-k+1) in O(n) using a running sum.",
     "starter": "def moving_average(xs, k):\n    pass\n",
     "tests": [("k=2", "assert moving_average([1, 2, 3, 4, 5], 2) == [1.5, 2.5, 3.5, 4.5]"),
               ("k=n", "assert moving_average([1, 2, 3, 4, 5], 5) == [3.0]"),
               ("k>n", "assert moving_average([1, 2], 3) == []")],
     "hints": ["Sum the first k values once.", "Slide: add xs[i], subtract xs[i-k]."],
     "solution": "def moving_average(xs, k):\n    if k > len(xs):\n        return []\n    s = sum(xs[:k])\n    out = [s / k]\n    for i in range(k, len(xs)):\n        s += xs[i] - xs[i - k]\n        out.append(s / k)\n    return out\n"},
    {"id": "t_merge_intervals", "track": "Algorithms", "diff": "Medium", "title": "Merge intervals",
     "prompt": "Write `merge(intervals)` that merges overlapping `[start, end]` intervals and returns them sorted.",
     "starter": "def merge(intervals):\n    pass\n",
     "tests": [("classic", "assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]"),
               ("touching", "assert merge([[1, 4], [4, 5]]) == [[1, 5]]"),
               ("unsorted", "assert merge([[8, 10], [1, 3], [2, 6]]) == [[1, 6], [8, 10]]")],
     "hints": ["Sort by start first.", "If the next start <= current end, extend the end; else start a new interval."],
     "solution": "def merge(intervals):\n    out = []\n    for s, e in sorted(intervals):\n        if out and s <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], e)\n        else:\n            out.append([s, e])\n    return out\n"},
    {"id": "t_fib_memo", "track": "Algorithms", "diff": "Easy", "title": "Fibonacci with memoization",
     "prompt": "Write `fib(n)` (fib(0)=0, fib(1)=1) that computes fib(80) instantly.",
     "starter": "def fib(n):\n    pass\n",
     "tests": [("small", "assert [fib(i) for i in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13]"),
               ("large", "assert fib(80) == 23416728348467685")],
     "hints": ["Naive recursion is exponential.", "Use functools.lru_cache, or iterate keeping two variables."],
     "solution": "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n"},
    # ---------------- Finance ----------------
    {"id": "f_cagr", "track": "Finance", "diff": "Easy", "title": "CAGR",
     "prompt": "Write `cagr(start_value, end_value, years)` returning the compound annual growth rate as a decimal.",
     "starter": "def cagr(start_value, end_value, years):\n    pass\n",
     "tests": [("double in 5y", "assert abs(cagr(100, 200, 5) - (2 ** (1 / 5) - 1)) < 1e-9"),
               ("flat", "assert abs(cagr(50, 50, 3)) < 1e-12")],
     "hints": ["end = start x (1 + g)^years.", "Solve for g: (end/start)^(1/years) - 1."],
     "solution": "def cagr(start_value, end_value, years):\n    return (end_value / start_value) ** (1 / years) - 1\n"},
    {"id": "f_npv", "track": "Finance", "diff": "Easy", "title": "Net present value",
     "prompt": "Write `npv(rate, cashflows)` where cashflows[0] occurs today (t=0), cashflows[1] at t=1, etc.",
     "starter": "def npv(rate, cashflows):\n    pass\n",
     "tests": [("project", "assert abs(npv(0.10, [-100, 60, 60]) - (-100 + 60 / 1.1 + 60 / 1.21)) < 1e-9"),
               ("zero rate", "assert abs(npv(0.0, [-10, 5, 5])) < 1e-12")],
     "hints": ["Discount each cash flow by (1 + rate)^t.", "sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))"],
     "solution": "def npv(rate, cashflows):\n    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))\n"},
    {"id": "f_irr", "track": "Finance", "diff": "Medium", "title": "IRR by bisection",
     "prompt": "Write `irr(cashflows)` returning the rate where NPV = 0 (search between -0.99 and 10). Accuracy 1e-6.",
     "starter": "def irr(cashflows):\n    pass\n",
     "tests": [("one period", "assert abs(irr([-1000, 1100]) - 0.10) < 1e-6"),
               ("two periods", "assert abs(irr([-100, 60, 60]) - 0.1306623863) < 1e-6")],
     "hints": ["NPV falls as the rate rises (for a normal project).", "Bisection: if NPV(mid) > 0 the IRR is higher, so move lo = mid."],
     "solution": "def irr(cashflows):\n    npv = lambda r: sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))\n    lo, hi = -0.99, 10.0\n    for _ in range(200):\n        mid = (lo + hi) / 2\n        if npv(mid) > 0:\n            lo = mid\n        else:\n            hi = mid\n    return (lo + hi) / 2\n"},
    {"id": "f_bond", "track": "Finance", "diff": "Medium", "title": "Bond price",
     "prompt": "Write `bond_price(face, coupon_rate, ytm, years, freq=2)` returning the price of a plain-vanilla bond.",
     "starter": "def bond_price(face, coupon_rate, ytm, years, freq=2):\n    pass\n",
     "tests": [("par bond", "assert abs(bond_price(1000, 0.05, 0.05, 10) - 1000) < 1e-6"),
               ("premium annual", "assert abs(bond_price(1000, 0.06, 0.05, 5, freq=1) - 1043.2948) < 1e-3"),
               ("discount", "assert bond_price(1000, 0.03, 0.06, 10) < 1000")],
     "hints": ["Periods n = years x freq, coupon c = face x coupon_rate / freq, rate y = ytm / freq.",
               "Price = sum(c / (1+y)^t for t=1..n) + face / (1+y)^n."],
     "solution": "def bond_price(face, coupon_rate, ytm, years, freq=2):\n    n, c, y = int(years * freq), face * coupon_rate / freq, ytm / freq\n    return sum(c / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n\n"},
    {"id": "f_sharpe", "track": "Finance", "diff": "Medium", "title": "Annualized Sharpe ratio",
     "prompt": "Write `sharpe(returns, rf=0.0, periods=252)`: mean excess return / sample std (ddof=1), annualized by sqrt(periods). `rf` is per-period.",
     "starter": "import numpy as np\n\ndef sharpe(returns, rf=0.0, periods=252):\n    pass\n",
     "tests": [("daily", "import numpy as np\nr = np.array([0.01, -0.005, 0.007, 0.002, 0.004])\nassert abs(sharpe(list(r)) - r.mean() / r.std(ddof=1) * np.sqrt(252)) < 1e-9"),
               ("with rf", "import numpy as np\nr = np.array([0.02, 0.01, 0.03, -0.01])\nx = r - 0.001\nassert abs(sharpe(list(r), rf=0.001, periods=12) - x.mean() / x.std(ddof=1) * np.sqrt(12)) < 1e-9")],
     "hints": ["Subtract rf from each return first.", "np.std(x, ddof=1) gives the sample standard deviation."],
     "solution": "import numpy as np\n\ndef sharpe(returns, rf=0.0, periods=252):\n    x = np.asarray(returns) - rf\n    return x.mean() / x.std(ddof=1) * np.sqrt(periods)\n"},
    {"id": "f_drawdown", "track": "Finance", "diff": "Medium", "title": "Maximum drawdown",
     "prompt": "Write `max_drawdown(prices)` returning the largest peak-to-trough decline as a positive fraction.",
     "starter": "def max_drawdown(prices):\n    pass\n",
     "tests": [("crash", "assert abs(max_drawdown([100, 120, 90, 130, 65]) - 0.5) < 1e-12"),
               ("rising", "assert max_drawdown([100, 110, 120]) == 0"),
               ("two dips", "assert abs(max_drawdown([100, 80, 120, 60]) - 0.5) < 1e-12")],
     "hints": ["Track the running peak.", "Drawdown at each point = 1 - price / peak; keep the max."],
     "solution": "def max_drawdown(prices):\n    peak, mdd = float('-inf'), 0.0\n    for p in prices:\n        peak = max(peak, p)\n        mdd = max(mdd, 1 - p / peak)\n    return mdd\n"},
    {"id": "f_wacc", "track": "Finance", "diff": "Easy", "title": "WACC",
     "prompt": "Write `wacc(E, D, re, rd, tax)` using market values E (equity) and D (debt).",
     "starter": "def wacc(E, D, re, rd, tax):\n    pass\n",
     "tests": [("example", "assert abs(wacc(600, 400, 0.10, 0.05, 0.25) - 0.075) < 1e-12"),
               ("all equity", "assert abs(wacc(100, 0, 0.09, 0.04, 0.3) - 0.09) < 1e-12")],
     "hints": ["V = E + D.", "WACC = E/V x re + D/V x rd x (1 - tax)."],
     "solution": "def wacc(E, D, re, rd, tax):\n    V = E + D\n    return E / V * re + D / V * rd * (1 - tax)\n"},
    {"id": "f_dcf", "track": "Finance", "diff": "Hard", "title": "DCF enterprise value",
     "prompt": "Write `dcf_value(fcfs, rate, g)`: fcfs are years 1..n. EV = PV of each FCF + PV of the Gordon terminal value FCF_n x (1+g)/(rate-g), discounted from year n.",
     "starter": "def dcf_value(fcfs, rate, g):\n    pass\n",
     "tests": [("3 years", "f=[100, 110, 121]; r=0.09; g=0.02\nexp = sum(c / (1 + r) ** (t + 1) for t, c in enumerate(f)) + f[-1] * (1 + g) / (r - g) / (1 + r) ** 3\nassert abs(dcf_value(f, r, g) - exp) < 1e-6"),
               ("growth raises value", "assert dcf_value([50, 50], 0.1, 0.03) > dcf_value([50, 50], 0.1, 0.0)")],
     "hints": ["Year t cash flow is discounted by (1 + rate)^t, with t starting at 1.",
               "Terminal value sits at year n, so discount it by (1 + rate)^n too."],
     "solution": "def dcf_value(fcfs, rate, g):\n    n = len(fcfs)\n    pv = sum(c / (1 + rate) ** (t + 1) for t, c in enumerate(fcfs))\n    tv = fcfs[-1] * (1 + g) / (rate - g)\n    return pv + tv / (1 + rate) ** n\n"},
    {"id": "f_bs_call", "track": "Finance", "diff": "Hard", "title": "Black-Scholes call + put-call parity",
     "prompt": "Write `bs_call(S, K, T, r, sigma)` and `bs_put(S, K, T, r, sigma)` (European, no dividends).",
     "starter": "import math\nfrom scipy.stats import norm\n\ndef bs_call(S, K, T, r, sigma):\n    pass\n\ndef bs_put(S, K, T, r, sigma):\n    pass\n",
     "tests": [("textbook value", "assert abs(bs_call(100, 100, 1, 0.05, 0.2) - 10.4506) < 1e-3"),
               ("put-call parity", "import math\nc = bs_call(105, 100, 0.5, 0.03, 0.25); p = bs_put(105, 100, 0.5, 0.03, 0.25)\nassert abs((c - p) - (105 - 100 * math.exp(-0.03 * 0.5))) < 1e-9"),
               ("monotonic in S", "assert bs_call(110, 100, 1, 0.05, 0.2) > bs_call(100, 100, 1, 0.05, 0.2)")],
     "hints": ["d1 = (ln(S/K) + (r + sigma^2/2) T) / (sigma sqrt(T)), d2 = d1 - sigma sqrt(T).",
               "Call = S N(d1) - K e^(-rT) N(d2); Put = K e^(-rT) N(-d2) - S N(-d1)."],
     "solution": "import math\nfrom scipy.stats import norm\n\ndef _d(S, K, T, r, sigma):\n    d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))\n    return d1, d1 - sigma * math.sqrt(T)\n\ndef bs_call(S, K, T, r, sigma):\n    d1, d2 = _d(S, K, T, r, sigma)\n    return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)\n\ndef bs_put(S, K, T, r, sigma):\n    d1, d2 = _d(S, K, T, r, sigma)\n    return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)\n"},
    {"id": "f_paper_lbo", "track": "Finance", "diff": "Medium", "title": "Paper LBO returns (timed: 10 min)",
     "prompt": "Bank-style paper LBO. Write `lbo_returns(equity_in, equity_out, years)` returning `(moic, irr)`. Try to finish in 10 minutes - that's the desk standard.",
     "starter": "def lbo_returns(equity_in, equity_out, years):\n    pass\n",
     "tests": [("2.5x in 5y", "m, i = lbo_returns(100, 250, 5)\nassert abs(m - 2.5) < 1e-12 and abs(i - (2.5 ** 0.2 - 1)) < 1e-9"),
               ("double in 3y", "m, i = lbo_returns(200, 400, 3)\nassert abs(m - 2) < 1e-12 and abs(i - (2 ** (1 / 3) - 1)) < 1e-9")],
     "hints": ["MOIC = equity_out / equity_in.", "With no interim dividends, IRR = MOIC^(1/years) - 1. Memorize: 2x/3y ≈ 26%, 2x/5y ≈ 15%, 3x/5y ≈ 25%."],
     "solution": "def lbo_returns(equity_in, equity_out, years):\n    moic = equity_out / equity_in\n    return moic, moic ** (1 / years) - 1\n"},
    # ---------------- ML & statistics ----------------
    {"id": "m_zscore", "track": "ML & stats", "diff": "Easy", "title": "Standardize features",
     "prompt": "Write `zscore(xs)` returning (x - mean) / std using the population std (ddof=0).",
     "starter": "import numpy as np\n\ndef zscore(xs):\n    pass\n",
     "tests": [("matches numpy", "import numpy as np\nx = np.array([1.0, 2, 3, 4, 10])\nassert np.allclose(zscore(x), (x - x.mean()) / x.std())"),
               ("mean 0 std 1", "import numpy as np\nz = np.asarray(zscore([5, 7, 9, 11]))\nassert abs(z.mean()) < 1e-12 and abs(z.std() - 1) < 1e-12")],
     "hints": ["Convert to a NumPy array first.", "np.std defaults to ddof=0."],
     "solution": "import numpy as np\n\ndef zscore(xs):\n    x = np.asarray(xs, dtype=float)\n    return (x - x.mean()) / x.std()\n"},
    {"id": "m_logloss", "track": "ML & stats", "diff": "Medium", "title": "Binary cross-entropy",
     "prompt": "Write `log_loss(y_true, p)`: mean binary cross-entropy, clipping p to [1e-15, 1 - 1e-15].",
     "starter": "import numpy as np\n\ndef log_loss(y_true, p):\n    pass\n",
     "tests": [("vs sklearn", "from sklearn.metrics import log_loss as sk\ny=[1, 0, 1, 1, 0]; p=[0.9, 0.2, 0.6, 0.99, 0.4]\nassert abs(log_loss(y, p) - sk(y, p)) < 1e-9"),
               ("clipping", "import math\nassert math.isfinite(log_loss([1, 0], [0.0, 1.0]))")],
     "hints": ["loss_i = -(y log p + (1-y) log(1-p)).", "np.clip(p, eps, 1 - eps) before taking logs."],
     "solution": "import numpy as np\n\ndef log_loss(y_true, p):\n    y = np.asarray(y_true, float)\n    p = np.clip(np.asarray(p, float), 1e-15, 1 - 1e-15)\n    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))\n"},
    {"id": "m_prec_rec", "track": "ML & stats", "diff": "Easy", "title": "Precision and recall",
     "prompt": "Write `precision_recall(y_true, y_pred)` returning `(precision, recall)` for the positive class 1. Return 0.0 when undefined.",
     "starter": "def precision_recall(y_true, y_pred):\n    pass\n",
     "tests": [("vs sklearn", "from sklearn.metrics import precision_score, recall_score\nyt=[1, 0, 1, 1, 0, 1, 0]; yp=[1, 1, 0, 1, 0, 1, 1]\np, r = precision_recall(yt, yp)\nassert abs(p - precision_score(yt, yp)) < 1e-12 and abs(r - recall_score(yt, yp)) < 1e-12"),
               ("no positives predicted", "assert precision_recall([1, 0], [0, 0]) == (0.0, 0.0)")],
     "hints": ["Count TP, FP, FN.", "precision = TP/(TP+FP), recall = TP/(TP+FN)."],
     "solution": "def precision_recall(y_true, y_pred):\n    tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)\n    fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)\n    fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)\n    p = tp / (tp + fp) if tp + fp else 0.0\n    r = tp / (tp + fn) if tp + fn else 0.0\n    return p, r\n"},
    {"id": "m_gd_line", "track": "ML & stats", "diff": "Medium", "title": "Linear regression by gradient descent",
     "prompt": "Write `fit_line(xs, ys, lr=0.01, epochs=5000)` returning `(w, b)` minimizing MSE with gradient descent (no closed form, no sklearn).",
     "starter": "import numpy as np\n\ndef fit_line(xs, ys, lr=0.01, epochs=5000):\n    pass\n",
     "tests": [("recovers 2x+1", "import numpy as np\nx = np.arange(10, dtype=float); y = 2 * x + 1\nw, b = fit_line(x, y)\nassert abs(w - 2) < 0.05 and abs(b - 1) < 0.05"),
               ("noisy slope", "import numpy as np\nrng = np.random.default_rng(0); x = rng.uniform(0, 5, 200); y = -3 * x + 4 + rng.normal(0, 0.1, 200)\nw, b = fit_line(x, y)\nassert abs(w + 3) < 0.1")],
     "hints": ["Prediction = w x + b; error = pred - y.", "dw = 2 mean(error x), db = 2 mean(error); update w -= lr dw, b -= lr db."],
     "solution": "import numpy as np\n\ndef fit_line(xs, ys, lr=0.01, epochs=5000):\n    x, y = np.asarray(xs, float), np.asarray(ys, float)\n    w = b = 0.0\n    for _ in range(epochs):\n        e = w * x + b - y\n        w -= lr * 2 * np.mean(e * x)\n        b -= lr * 2 * np.mean(e)\n    return w, b\n"},
    {"id": "m_kmeans_assign", "track": "ML & stats", "diff": "Easy", "title": "K-means assignment step",
     "prompt": "Write `assign(points, centroids)` returning, for each point, the index of the nearest centroid (Euclidean).",
     "starter": "import numpy as np\n\ndef assign(points, centroids):\n    pass\n",
     "tests": [("2 clusters", "assert list(assign([[0, 0], [10, 10], [1, 0], [9, 9]], [[0, 0], [10, 10]])) == [0, 1, 0, 1]"),
               ("3 clusters", "assert list(assign([[5, 5], [0, 1], [20, 20]], [[0, 0], [6, 6], [19, 19]])) == [1, 0, 2]")],
     "hints": ["Compute the distance from each point to each centroid.", "Broadcasting: P[:, None, :] - C[None, :, :], then argmin over axis 1."],
     "solution": "import numpy as np\n\ndef assign(points, centroids):\n    P, C = np.asarray(points, float), np.asarray(centroids, float)\n    return np.argmin(((P[:, None, :] - C[None, :, :]) ** 2).sum(-1), axis=1)\n"},
    {"id": "m_cosine", "track": "ML & stats", "diff": "Easy", "title": "Cosine similarity (RAG retrieval core)",
     "prompt": "Write `cosine(a, b)` and `top_k(query, docs, k)` returning indices of the k most similar doc vectors, best first.",
     "starter": "import numpy as np\n\ndef cosine(a, b):\n    pass\n\ndef top_k(query, docs, k):\n    pass\n",
     "tests": [("orthogonal", "assert abs(cosine([1, 0], [0, 1])) < 1e-12"),
               ("parallel", "assert abs(cosine([1, 2], [2, 4]) - 1) < 1e-12"),
               ("retrieval", "assert list(top_k([1, 0], [[0, 1], [1, 0.1], [0.5, 0.5]], 2)) == [1, 2]")],
     "hints": ["cos = a·b / (|a| |b|).", "Score every doc, then argsort descending and take k."],
     "solution": "import numpy as np\n\ndef cosine(a, b):\n    a, b = np.asarray(a, float), np.asarray(b, float)\n    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))\n\ndef top_k(query, docs, k):\n    s = [cosine(query, d) for d in docs]\n    return list(np.argsort(s)[::-1][:k])\n"},
    # ---------------- SQL ----------------
    {"id": "s_top_volume", "track": "SQL", "diff": "Medium", "title": "SQL: top volume day per ticker",
     "prompt": "Table `trades(ticker TEXT, day TEXT, volume INT)`. Set `QUERY` to a SQL string returning `ticker, day, volume` for each ticker's highest-volume day, ordered by ticker. Use a window function.",
     "starter": "QUERY = \"\"\"\nSELECT ...\n\"\"\"\n",
     "tests": [("correct rows", "import sqlite3\ncon = sqlite3.connect(':memory:')\ncon.execute('CREATE TABLE trades(ticker TEXT, day TEXT, volume INT)')\ncon.executemany('INSERT INTO trades VALUES (?,?,?)', [('AAPL','d1',100),('AAPL','d2',300),('AAPL','d3',200),('MSFT','d1',50),('MSFT','d2',40),('NVDA','d3',900)])\nrows = [tuple(r) for r in con.execute(QUERY)]\nassert rows == [('AAPL','d2',300),('MSFT','d1',50),('NVDA','d3',900)], rows")],
     "hints": ["ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY volume DESC) AS rn", "Wrap it in a CTE and keep rn = 1, then ORDER BY ticker."],
     "solution": "QUERY = \"\"\"\nWITH ranked AS (\n  SELECT ticker, day, volume,\n         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY volume DESC) AS rn\n  FROM trades\n)\nSELECT ticker, day, volume FROM ranked WHERE rn = 1 ORDER BY ticker\n\"\"\"\n"},
    {"id": "s_running_pnl", "track": "SQL", "diff": "Medium", "title": "SQL: running P&L",
     "prompt": "Table `pnl(day TEXT, amount REAL)`. Set `QUERY` to return `day, amount, running` where running is the cumulative sum ordered by day.",
     "starter": "QUERY = \"\"\"\nSELECT ...\n\"\"\"\n",
     "tests": [("cumulative", "import sqlite3\ncon = sqlite3.connect(':memory:')\ncon.execute('CREATE TABLE pnl(day TEXT, amount REAL)')\ncon.executemany('INSERT INTO pnl VALUES (?,?)', [('2026-01-03', -5.0), ('2026-01-01', 10.0), ('2026-01-02', 3.0)])\nrows = [tuple(r) for r in con.execute(QUERY)]\nassert rows == [('2026-01-01', 10.0, 10.0), ('2026-01-02', 3.0, 13.0), ('2026-01-03', -5.0, 8.0)], rows")],
     "hints": ["SUM(amount) OVER (ORDER BY day)", "Don't forget the outer ORDER BY day."],
     "solution": "QUERY = \"\"\"\nSELECT day, amount, SUM(amount) OVER (ORDER BY day) AS running\nFROM pnl ORDER BY day\n\"\"\"\n"},
]

CH_BY_ID = {c["id"]: c for c in CHALLENGES}
TRACKS = ["Algorithms", "Finance", "ML & stats", "SQL"]
TOY_ROTATION = [c["id"] for c in CHALLENGES if c["track"] in ("Algorithms", "Finance")]


def toy_of_the_day():
    return CH_BY_ID[TOY_ROTATION[date.today().toordinal() % len(TOY_ROTATION)]]


def grade(code, challenge, timeout=20):
    """Run user code + tests in a subprocess. Returns (results, stdout, stderr)."""
    script = code + "\n__DEVI_TESTS__ = " + repr(challenge["tests"]) + HARNESS.replace("{marker}", MARKER)
    out, err, rc = run_python(script, timeout=timeout)
    results = None
    clean = []
    for line in out.splitlines():
        if line.startswith(MARKER):
            results = json.loads(line[len(MARKER):])
        else:
            clean.append(line)
    return results, "\n".join(clean), err