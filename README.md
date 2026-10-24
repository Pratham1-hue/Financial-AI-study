# Project DEVI - Finance & AI Academy

A personal, strict 16-week learning platform to master **Financial Knowledge + AI/ML** and land the greatest job in New York City.

## Where to start

Open the app and use the **Start here — your first session** card at the top of the Command center. One path, in order:

1. **Lock in 25 minutes.** One button starts the Pomodoro and takes you to the timer. The block runs while you study.
2. **Learn — Python basics.** Kaggle's interactive Python course, Lesson 1 (~30 min). Do it inside the block from step 1.
3. **Prove it.** A 5-question quiz on the same material. 80% is mastery.
4. *Optional:* sign the contract to make the plan binding.

Ignore every other page today. After the first session, **Today's mission** is your daily plan and the five-block loop (Learn -> Drill -> Build -> Prove -> Debrief) is your daily map.

## Two front ends, one engine

The primary UI is a **React 19 + TypeScript + Tailwind v4** SPA in `web/`, served in production by the same FastAPI process that owns the data. The original Streamlit app (`streamlit_app.py`, `app_pages/`) is kept in the repo as a fallback and still runs locally, but it is no longer in the Docker image.

```powershell
# API: imports lib/ unchanged, owns auth + the clock + grading
.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
# SPA: hot reload on :5173, proxies /api to :8000
cd web; npm run dev
```

Core pages: **Dashboard** (day score, the five-block loop, $DEVI, phase progress), **Learn** (18 modules, video queue with watch tracking, curated reading), **Focus** (locked-in-hours Pomodoro whose clock runs server-side), **Quizzes** (practice sets, Leitner daily drill, mastery gates with written teach-back), **The Desk** (live 3-minute market), **Labs** (SQL, credit ML, DCF).

Everything the Streamlit version did is behind these pages and the API:

- Dashboard with XP, levels, streaks, mastery index, career stock
- 16-week structured study plan (phase-gated)
- Curated resource library (90+ resources: YouTube, open source, books, courses, tools)
- Research library (440 resources across finance, quant, AI, career and research: papers, repos, datasets, benchmarks, tools, blogs)
- Module-by-module learning (18 modules across Finance, Quant, AI, Career)
- Practice materials & problem sets
- Quizzes (Khan Academy style) with instant feedback, graded server-side
- Phase-gate exams with honest, self-assessed teach-back rubrics
- Progress analytics & weak-area tracking
- Light theme by default with a dark NYC-night toggle

### Become the best (the job is the side effect)
- **Today's mission** - auto-assigned plan task for the day, live 0-100 day score, non-negotiables, Feynman debrief (200+ chars or it's rejected)
- **Lock-in mode** - persistent Pomodoro / Deep Work / Monk Mode timer that logs real focus hours, sidebar mini-timer on every page, chime + celebrations, NYC rank ladder (Tourist in Times Square -> Billionaires' Row Penthouse)
- **Career stock ($TICKER)** - your career as a traded stock: rises with your day score, -8% on zero days; candlesticks, analyst rating, live ticker tape on every page
- **Mastery Index** - proven retention + exams + deep work + interview reps + debriefs; unblurs a vision offer letter from your dream firm
- **The Desk** - a live synthetic market: 3-minute rounds, real bid/ask spread, market impact, enforced risk limits, P&L and drawdown, graded on return *and* discipline (overtrading and rejected orders cost you)
- **Hands-on labs, auto-graded** - SQL against a real 3-table schema (6 tasks), a credit-default model where accuracy is deliberately the wrong metric, and a timed 5-minute DCF/valuation sprint
- **The five-block day** - Learn 25 → Drill 15 → Build 45 → Prove 15 → Debrief 10, tracked as a strip on the dashboard; watching alone caps you at 60/100
- **The contract** - signed oath with stakes; hard mode locks the app after a zero day until you file an incident report (turning it off requires typing "I choose to be average")
- **Daily drill** - Leitner spaced repetition with Khan-style mastery levels per module
- **Interview gauntlet** - timed mock interviews (behavioral, finance, quant, ML, coding/SQL, markets, ML system design) with model key points and self-scoring
- Light "daylight Manhattan" theme by default, a one-click dark NYC-night toggle, procedural skyline, 55+ famous quotes throughout

### Bootcamp teaching patterns (researched, rebuilt)
- **Bootcamp playbook** - what Launch School, Le Wagon, Hack Reactor, App Academy, Interview Kickstart, Codesmith, Wall Street analyst training and quant-firm prep actually do, with sources, mapped to DEVI features
- **Mastery gates** (Launch School) - 18-module prerequisite tree; each gate = MCQ (80%+) + written teach-back graded against a rubric (75%+); "Not yet" = 24h wait, second "Not yet" = 72h + drill cards reset
- **Challenge lab** (Le Wagon / Hack Reactor) - 25 auto-graded challenges (algorithms, finance, ML & stats, SQL) with hidden tests, toy problem of the day, and the 20-minute rule: hints unlock with effort, solution only after 20 min + 3 attempts
- **Speed drills** (trading-firm screens) - timed mental math (+ − × ÷), 2/5/8-minute rounds, speed curve
- **Bootcamp day** (Le Wagon rhythm) - warm-up → lecture → challenges → retrieval → review → debrief, scaled to your daily goal
- Hiring/placement services intentionally excluded until expertise is built

### YouTube, actually integrated (Data API v3)
- **Watch** page - a real curriculum, not a link list: 10 hand-ranked lessons per module (180 total), embedded player, notes, and watch tracking
- **Ranking** - YouTube's own relevance order for two precise queries per module, then filtered: no shorts, no news commentary, no non-English titles, no clickbait caps, max 2 videos per channel so you get range instead of one personality
- **Inside the app** - Learn pages embed the module queue; watching a lesson earns the "Lecture watched" score component (10 pts, capped at 20 min/day) and marks the lecture block of the bootcamp day
- **Offline-first** - the sync script writes `data/yt_catalog.json` (3,200+ videos from 47 trusted channels) and `data/yt_curriculum.json`; the app reads them, so browsing costs **zero** API quota
- **Quota aware** - 10,000 units/day free tier is tracked and displayed; searches cost 100 units, everything else 1. A full cold sync is ~8,800 units; warm runs are free (7-day cache)
- **Key** - `YOUTUBE_API_KEY` in `.streamlit/secrets.toml` (gitignored) or the environment

### Practice that behaves like the job
- **The Desk** (`Practice -> The Desk`) - a synthetic tape that ticks once a second for 3 minutes. You trade against a real spread, your size moves the price, and the risk limits are enforced the way a desk enforces them. The score is 50% return, 50% discipline: drawdown, overtrading and rejected orders all cost you. Zero trades scores 40, because no decision is not a strategy.
- **Hands-on labs** (`Practice -> Hands-on labs`) - three auto-graded tracks:
  - *SQL*: 6 tasks against `companies`, `prices` (240 days) and `financials`. Your query is compared to a reference result, so aliases don't matter but the rows do. Reference query unlocks after 3 attempts.
  - *Credit risk*: 4,000 borrowers, your choice of features and model. Accuracy is shown next to the naive baseline on purpose - the useful numbers are AUC, recall and the confusion matrix.
  - *Valuation sprint*: a randomised company, five minutes, three numbers (EV, equity, per share). 1% tolerance. The mechanics are revealed only after you submit.
- **Scoring** - a Desk round with at least one trade, or a lab task you get right, counts toward the 10-point hands-on component of the daily score. Desk rounds log `desk_rounds` plus XP. Watching videos alone caps the day at 60/100 by design.

### The systematic loop
Every day is the same five blocks, in order: **Learn 25 -> Drill 15 -> Build 45 -> Prove 15 -> Debrief 10**.
It is rendered as a live strip on the dashboard, so a skipped block is visible before the day ends.
The week adds one build artifact (Saturday) and one scored mock interview plus a written review (Sunday).

### Verified, not assumed

- **Link checker** - all 440 resource URLs checked for real (`scripts/check_links.py`): YouTube objects through the API, everything else by HTTP. Current state: 398 live, 42 unverified (paywalls and bot walls that refuse automated probes), **0 dead**
- The Resources page shows the verdict on every card, plus a "Start here" row, and the check is re-runnable
- New in this pass: finance grew 18 -> 78 and quant 19 -> 54, closing the gap with AI (187)

## Refreshing the data

```bash
.venv\Scripts\python.exe scripts\sync_youtube.py   # channels, catalogs, per-module curriculum
.venv\Scripts\python.exe scripts\check_links.py    # verify every resource URL
```

Resources live in `lib/resources.py` (core set) plus `lib/res_finance.py`, `lib/res_ai.py`
and `lib/res_career.py` (batch 2). Duplicate URLs are merged automatically, so adding a
resource that already exists costs nothing. After adding links, re-run the checker.

## Run

**React UI (primary)** — two terminals:

```powershell
cd "D:\Machine Learning Projects\Project Devi"
.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000   # API
cd web; npm run dev                                                     # SPA on :5173
```

Then open http://localhost:5173. To run the production shape (FastAPI serving the built SPA), `cd web; npm run build` and open http://localhost:8000.

**Streamlit UI (fallback)**:

```bash
.venv\Scripts\activate
streamlit run streamlit_app.py     # http://localhost:8501
```

Or double-click `run.bat`.

## Deploy

Render's free Docker tier works, with one caveat: its filesystem is wiped on every
restart, deploy and spin-down, so the app ships a one-click **Profile -> Backup & restore**
and a keep-alive workflow. Free instances sleep after 15 idle minutes; `.github/workflows/keepalive.yml`
(or an UptimeRobot monitor) prevents that.

The image is a single service: stage 1 builds the SPA with Node, stage 2 installs
`requirements-api.txt` (no Streamlit) and runs uvicorn, which serves both `/api/*` and
`web/dist`. One process, no CORS, no second host. `Dockerfile` and `render.yaml`
(free plan, no disk) are included; the full walkthrough, limits and upgrade path are in
**[DEPLOY.md](DEPLOY.md)**.

```bash
docker build -t project-devi .
docker run --rm -p 8000:8000 -e DEVI_PASSWORD=test project-devi
```

Env vars that matter in production: `DEVI_PASSWORD` (gates the API), `DEVI_SECRET`
(session-cookie pepper), `DEVI_COOKIE_SECURE=1` (HTTPS-only cookie), and, only if you
attach a disk, `DEVI_DATA_DIR`.

A cursor jiggler does not keep Render awake — only real HTTP requests count. The health
endpoints `/api/health` and `/_stcore/health` are the right targets: no password, no
session, no data writes.

## Stack

Python 3.14 locally, 3.13 in the container. Engine: NumPy, pandas, scikit-learn, scipy.
API: FastAPI + uvicorn, JSON state in `data/`. UI: React 19, TypeScript, Vite 8,
Tailwind CSS v4, React Router 7. Streamlit 1.66 remains installed locally for the fallback UI.