# Deploying Project DEVI on Render (free tier)

**Verdict:** Render's free Docker web service works. Vercel does not.

| Host | Works? | Why |
|---|---|---|
| **Render free — Docker** | **Yes, with backups** | Long-lived Python process and websockets; but the filesystem is ephemeral and it sleeps |
| Render Starter ($7/mo) | Yes, durable | Paid instances never sleep and accept a persistent disk |
| Fly.io / Railway | Yes | Same shape: container + volume |
| Streamlit Community Cloud | Runs, resets | Free and public; no disk, so progress is lost on reboot |
| Vercel | **No** | Serverless functions are short-lived and stateless; Streamlit needs a persistent websocket server and a writable filesystem |

A Vercel deploy is not a config change — it is a rewrite: a static React frontend on Vercel plus a separate API host for the Python and the JSON store.

---

## Read this before you deploy: what "free" costs you

Render's free web service gives you 512 MB RAM, 0.1 CPU, **750 instance-hours/month**, 5 GB bandwidth, and **no persistent disk**. Two behaviours matter:

1. **It sleeps after 15 minutes without HTTP traffic.** The next visit takes 30-60 seconds to wake.
2. **The filesystem is ephemeral.** Render's docs are explicit: local changes are lost every time the service **redeploys, restarts, or spins down**. This app keeps `progress.json`, `profile.json` and `focus.json` on that filesystem.

Point 2 is the one that bites. A single 15-minute sleep can wipe a 40-day streak. So the free-tier setup has three parts:

- **A keep-alive pinger** so the instance never idles out (below).
- **A one-click backup** (Profile -> Backup & restore) so you can survive the restarts Render reserves the right to do.
- **One instance only** — the JSON store is single-writer.

If that trade feels wrong, the upgrade path at the bottom is a five-minute change.

---

## What is already prepared

- `Dockerfile` — Python 3.13 slim, installs `requirements.txt`, binds `0.0.0.0:$PORT`
- `render.yaml` — free Docker web service, health check, no disk, `autoDeploy: false`
- `lib/paths.py` — `DEVI_DATA_DIR` support (unused on free, ready for a disk later)
- `lib/backup.py` + Profile page — export/restore progress, profile and focus in one file
- `DEVI_PASSWORD` gate — the whole app (including the code console) behind a login
- `DEVI_ALLOW_CONSOLE=0` — disables the Python console on a shared instance
- `.github/workflows/keepalive.yml` — pings `/_stcore/health` every 10 minutes

The image ships with the synced YouTube catalog (47 channels, ~3,255 videos) and the verified link report, so browsing costs **no** YouTube quota. The API key is only used for deliberate re-syncs.

---

## Deploy in five steps

### 1. Put the project on GitHub

```powershell
cd "D:\Machine Learning Projects\Project Devi"
git init
git add .
git commit -m "Project DEVI"
git branch -M main
git remote add origin https://github.com/<you>/project-devi.git
git push -u origin main
```

`.gitignore` excludes `.streamlit/secrets.toml`, the YouTube cache, and your local `progress.json` / `profile.json` / `focus.json`. Check `git status` before pushing.

### 2. Create the service

**Blueprint:** Render Dashboard -> **New +** -> **Blueprint** -> pick the repo. It reads `render.yaml` (free plan, no disk) and asks for the two secrets.

**Manual:** **New +** -> **Web Service** -> repo -> Runtime **Docker** -> Plan **Free** -> Health check `/_stcore/health`. Add env vars:

| Key | Value |
|---|---|
| `DEVI_PASSWORD` | a long random string |
| `YOUTUBE_API_KEY` | your key (only needed for re-syncs) |

Do **not** set `PORT`; Render injects it and the Dockerfile forwards it to Streamlit. Do not add a disk — the free plan does not support one.

### 3. Keep it awake

Without this, the app sleeps and the sleep wipes progress. Pick one:

- **UptimeRobot (recommended):** free monitor, HTTP(s), 5-minute interval, URL
  `https://<app>.onrender.com/_stcore/health`.
- **GitHub Actions:** the included workflow. Settings -> Secrets and variables -> Actions -> **Variables** -> new variable `DEVI_URL = https://<app>.onrender.com`. It pings every 10 minutes. Until you set `DEVI_URL`, the scheduled job **skips** instead of failing, so a red X in the Actions tab means the app itself is not answering - not a missing variable.
  Caveats: GitHub can delay scheduled runs under load, and disables schedules after 60 days of repo inactivity. UptimeRobot is more reliable for this.
- **Any external cron:** `curl https://<app>.onrender.com/_stcore/health` every 10 minutes.

Use `/_stcore/health`, not the app root: it returns `ok`, needs no password, starts no session, and never touches your data.

Why not a cursor jiggler or autoclicker? Render measures **requests that reach the server**. Mouse movement in your browser is not traffic. An open tab may keep the websocket alive (Render counts websocket traffic as activity since February 2026), but the timer starts the moment you close it.

### 4. First boot

Open the URL: password screen -> dashboard. Check:

- `https://<app>.onrender.com/_stcore/health` returns `ok`
- Login works
- Dashboard streak starts at 1
- `/desk` ticks without a page reload
- `/labs` SQL task 1 checks correctly

### 5. Build the backup habit

At the end of a session: **Profile -> Backup & restore -> Download backup**. It writes one file with progress, profile and focus state.

Before you `git push` (which triggers a manual deploy): download a backup, deploy, then restore it. `autoDeploy` is off in `render.yaml` for exactly this reason — a content update should not silently reset your streak.

---

## Persistence, precisely

| Event | Local files |
|---|---|
| Page refresh / new tab | Survive |
| 15 minutes idle (no pinger) | **Lost** — spin-down wipes the filesystem |
| Deploy (manual or auto) | **Lost** |
| Render-initiated restart | **Lost** |
| Pinger running 24/7 | Survive between restarts |

Backup file contents:

```
progress.json   XP, tasks, quizzes, gates, SRS, desk rounds, lab runs, watched lessons
profile.json    name, goals, why, dream companies
focus.json      current Pomodoro/deep-work state
```

Restore merges the file over the defaults, so an older backup from before a feature existed still loads.

**Monthly limits:** 750 instance-hours (~730 in a 31-day month) means a 24/7 pinger uses almost the whole allowance. One free service only. Bandwidth is 5 GB/month; the app is text and charts, so personal use is far below that.

---

## Refreshing content (no shell on free)

Free instances have no shell, so sync locally:

```powershell
.venv\Scripts\python.exe scripts\sync_youtube.py
.venv\Scripts\python.exe scripts\check_links.py
git add data/yt_catalog.json data/yt_curriculum.json data/link_check.json
git commit -m "refresh content"
git push
```

Then **Render Dashboard -> Manual Deploy**. The new image carries the refreshed JSON. Back up before deploying, restore after.

This burns YouTube quota locally, not on the server (~8,800 units cold). Don't re-sync while the daily quota is nearly spent.

---

## Security

- **Set `DEVI_PASSWORD`.** Without it the app is open — including progress and the code console.
- **The Python console is remote code execution by design.** On a URL you share, set `DEVI_ALLOW_CONSOLE=0`.
- **Rotate the YouTube key** if it was ever exposed; update it in Render's environment. Never commit `.streamlit/secrets.toml`.
- Password auth is a shared secret, not user accounts. Fine for a personal app; for a cohort, put Cloudflare Access or an OAuth proxy in front and move state to Postgres.

---

## Upgrade later: make it durable in five minutes

1. Render Dashboard -> the service -> **Settings -> Instance Type -> Starter**.
2. **Disks -> Add Disk**: name `devi-data`, mount path `/var/data`, 1 GB.
3. Add env var `DEVI_DATA_DIR=/var/data`.
4. In `render.yaml`, set `plan: starter`, add the disk block, and add `DEVI_DATA_DIR`.
5. Deploy. Restore your latest backup once; from then on the volume carries it across deploys.

Starter is $7/month; the disk is ~$0.25/GB/month. No more pinger, no more sleep, no more manual restores.

---

## Local Docker test (same image Render builds)

```powershell
cd "D:\Machine Learning Projects\Project Devi"
docker build -t project-devi .
docker run --rm -p 8501:8501 `
  -e DEVI_PASSWORD=test `
  -v devi-data:/var/data `
  -e DEVI_DATA_DIR=/var/data `
  project-devi
```

Open `http://localhost:8501`, log in, run a desk round, restart the container, confirm the round is still in your record. The volume there simulates the paid setup; for the free setup, run without `-e DEVI_DATA_DIR` and confirm the data is gone after a restart — that is the behaviour you are backing up against.
