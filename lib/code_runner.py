"""Run user Python code in a subprocess with timeout."""
import subprocess
import sys
import os
import tempfile


def run_python(code, timeout=15):
    """Execute code in a fresh Python process. Returns (stdout, stderr, returncode)."""
    py = sys.executable
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        path = f.name
    try:
        proc = subprocess.run(
            [py, path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(os.path.abspath(__file__)) + "/..",
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timed out after {timeout}s (possible infinite loop).", -1
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


STARTER_EXERCISES = [
    {
        "title": "Hello, DEVI",
        "prompt": "Print 'Hello, DEVI!' and compute 2+2.",
        "starter": "print('Hello, DEVI!')\nprint(2 + 2)\n",
        "solution": "print('Hello, DEVI!')\nprint(2 + 2)\n",
    },
    {
        "title": "NumPy: array stats",
        "prompt": "Create a NumPy array of 1..10, print mean, std, and reshape to 2x5.",
        "starter": "import numpy as np\narr = np.arange(1, 11)\nprint('mean', arr.mean())\nprint('std', arr.std())\nprint(arr.reshape(2, 5))\n",
        "solution": "import numpy as np\narr = np.arange(1, 11)\nprint('mean', arr.mean())\nprint('std', arr.std())\nprint(arr.reshape(2, 5))\n",
    },
    {
        "title": "pandas: groupby",
        "prompt": "Build a small DataFrame of trades and compute total PnL per ticker.",
        "starter": """import pandas as pd
df = pd.DataFrame({
    'ticker': ['AAPL','AAPL','MSFT','MSFT','GOOG'],
    'pnl': [100, -30, 50, 20, -10]
})
print(df.groupby('ticker')['pnl'].sum())
""",
        "solution": """import pandas as pd
df = pd.DataFrame({
    'ticker': ['AAPL','AAPL','MSFT','MSFT','GOOG'],
    'pnl': [100, -30, 50, 20, -10]
})
print(df.groupby('ticker')['pnl'].sum())
""",
    },
    {
        "title": "Black-Scholes call price",
        "prompt": "Implement Black-Scholes European call price given S, K, r, T, sigma.",
        "starter": """import numpy as np
from scipy.stats import norm

def bs_call(S, K, r, T, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

print(bs_call(100, 100, 0.05, 1, 0.2))
""",
        "solution": """import numpy as np
from scipy.stats import norm

def bs_call(S, K, r, T, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

print(bs_call(100, 100, 0.05, 1, 0.2))
""",
    },
    {
        "title": "Linear regression from scratch",
        "prompt": "Fit y = 2x+1 with gradient descent, print final weights.",
        "starter": """import numpy as np
X = np.array([1.,2,3,4,5])
y = 2*X + 1
w, b = 0.0, 0.0
lr = 0.01
for _ in range(1000):
    pred = w*X + b
    dw = (2/len(X))*np.sum((pred-y)*X)
    db = (2/len(X))*np.sum(pred-y)
    w -= lr*dw; b -= lr*db
print('w', round(w,3), 'b', round(b,3))
""",
        "solution": """import numpy as np
X = np.array([1.,2,3,4,5])
y = 2*X + 1
w, b = 0.0, 0.0
lr = 0.01
for _ in range(1000):
    pred = w*X + b
    dw = (2/len(X))*np.sum((pred-y)*X)
    db = (2/len(X))*np.sum(pred-y)
    w -= lr*dw; b -= lr*db
print('w', round(w,3), 'b', round(b,3))
""",
    },
    {
        "title": "sklearn: train a classifier",
        "prompt": "Train a RandomForest on iris and print accuracy.",
        "starter": """from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)
clf = RandomForestClassifier(random_state=42).fit(Xtr, ytr)
print('accuracy', accuracy_score(yte, clf.predict(Xte)))
""",
        "solution": """from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)
clf = RandomForestClassifier(random_state=42).fit(Xtr, ytr)
print('accuracy', accuracy_score(yte, clf.predict(Xte)))
""",
    },
    {
        "title": "Monte Carlo pi",
        "prompt": "Estimate pi with 1e6 random points.",
        "starter": """import numpy as np
rng = np.random.default_rng(0)
pts = rng.random((1_000_000, 2))
inside = np.sum(pts[:,0]**2 + pts[:,1]**2 <= 1)
print(4*inside/len(pts))
""",
        "solution": """import numpy as np
rng = np.random.default_rng(0)
pts = rng.random((1_000_000, 2))
inside = np.sum(pts[:,0]**2 + pts[:,1]**2 <= 1)
print(4*inside/len(pts))
""",
    },
    {
        "title": "SQL with sqlite3",
        "prompt": "Create a table, insert rows, query with GROUP BY.",
        "starter": """import sqlite3
con = sqlite3.connect(':memory:')
con.execute('CREATE TABLE t(ticker TEXT, pnl REAL)')
con.executemany('INSERT INTO t VALUES (?,?)', [('A',10),('A',-3),('B',5)])
for row in con.execute('SELECT ticker, SUM(pnl) FROM t GROUP BY ticker'):
    print(row)
""",
        "solution": """import sqlite3
con = sqlite3.connect(':memory:')
con.execute('CREATE TABLE t(ticker TEXT, pnl REAL)')
con.executemany('INSERT INTO t VALUES (?,?)', [('A',10),('A',-3),('B',5)])
for row in con.execute('SELECT ticker, SUM(pnl) FROM t GROUP BY ticker'):
    print(row)
""",
    },
]