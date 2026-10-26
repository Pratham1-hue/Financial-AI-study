# Project Laksh — web

The React front end for Project Laksh: a personal finance + AI academy that renders the
`lib/` engine through a FastAPI API.

Vite + React 19 + TypeScript + Tailwind CSS v4 + React Router 7.

## Develop

The API must be running on `:8000` (see the repo README):

```powershell
cd ..; .venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
npm run dev
```

`vite.config.ts` proxies `/api` and `/_stcore` to `http://localhost:8000`.

## Build

```powershell
npm run build     # type-checks with tsc -b, then writes dist/
```

`dist/` is served by FastAPI in production (`api/main.py` mounts it and falls back to
`index.html` for client-side routes). The Dockerfile builds this stage with Node.

## Layout

```
src/lib/api.ts         typed fetch client + every response shape
src/lib/hooks.ts       useApi / usePoll / useLocalStorage
src/theme.tsx          light (default) + dark, persisted in localStorage
src/components/        Shell (sidebar, ticker, theme toggle), ui kit, charts, TimerRing, Skyline
src/pages/             Dashboard, Learn, Focus, Quizzes, Desk, Labs, Login
src/index.css          design tokens (CSS variables) + Tailwind @theme mapping
```

Theme colours live in `:root` / `[data-theme='dark']` in `src/index.css`. Add a token
there, map it in `@theme inline`, and it becomes a utility (`bg-*`, `text-*`, `border-*`).
