"""Project DEVI API - FastAPI in front of the existing lib/ engine.

In production this also serves the built React app from web/dist, so Render runs
a single free web service (API + static site, no CORS, one deploy).
"""
from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.routers import core, debrief, desk, exam, focus as focus_router, labs, learn, quiz, backup
from api.security import COOKIE, verify_token

app = FastAPI(title="Project DEVI", version="2.0.0")

_origins = os.environ.get(
    "DEVI_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPEN_PATHS = {"/api/health", "/api/session", "/api/login"}


@app.middleware("http")
async def auth_gate(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/") and path not in OPEN_PATHS:
        if not verify_token(request.cookies.get(COOKIE)):
            return JSONResponse({"detail": "Not authenticated."}, status_code=401)
    return await call_next(request)


@app.get("/_stcore/health")
def legacy_health():
    """Kept so the existing keep-alive pinger and Render health check still work."""
    return {"status": "ok"}


for r in (core.router, learn.router, focus_router.router, quiz.router, desk.router,
          labs.router, exam.router, debrief.router, backup.router):
    app.include_router(r, prefix="/api")

DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "dist")

if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        # Unknown /api/* paths are API errors, not the SPA shell. Without this
        # the catch-all answered 200 text/html and the client tried to parse it.
        if full_path == "api" or full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found."}, status_code=404)
        candidate = os.path.join(DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(DIST, "index.html"))

else:
    @app.get("/")
    def no_build():
        return {"detail": "web/dist not built. Run: cd web && npm run build"}
