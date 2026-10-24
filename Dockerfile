# ---- stage 1: build the React app -------------------------------------------
FROM node:24-alpine AS web

WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web/ ./
RUN npm run build


# ---- stage 2: FastAPI serves the API + the built SPA ------------------------
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Only the API dependencies: no streamlit in the image.
COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .
COPY --from=web /web/dist ./web/dist

ENV PORT=8000
EXPOSE 8000

# Render/Fly inject $PORT. Single uvicorn worker: JSON storage is single-writer.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
