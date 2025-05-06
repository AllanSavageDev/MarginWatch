#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
DB_SERVICE_NAME="db"

FORCE_RESTART=false

if [ "$1" == "--all" ]; then
  FORCE_RESTART=true
  echo "[INFO] --all flag detected. Will force restart all services."
fi

echo ""
echo "======================================"
echo "  Starting Full Local Dev Stack
======================================"

# Step 1: Ensure Postgres container is running
echo "[INFO] Checking Postgres container..."
if ! docker ps | grep -q "$DB_SERVICE_NAME"; then
  echo "[INFO] Postgres container not running — starting it via docker-compose..."
  docker compose up -d "$DB_SERVICE_NAME"
else
  echo "[OK] Postgres container already running."
fi

# Step 2: Launch FastAPI backend
echo ""
echo "[INFO] Checking FastAPI (uvicorn) on port 8000..."
if lsof -i :8000 | grep -q LISTEN; then
  if [ "$FORCE_RESTART" = true ]; then
    echo "[INFO] Killing existing FastAPI process..."
    lsof -ti :8000 | xargs kill -9
    sleep 1
  else
    echo "[SKIP] FastAPI already running. Use --all to restart."
  fi
fi

if ! lsof -i :8000 | grep -q LISTEN; then
  echo "[INFO] Starting FastAPI backend..."
  cd "$BACKEND_DIR" || exit 1
  export MW_ENV=dev
  uvicorn service:app --reload &
  echo "[OK] FastAPI running at http://127.0.0.1:8000"
fi

# Step 3: Launch frontend
echo ""
echo "[INFO] Checking frontend on port 3000..."
if lsof -i :3000 | grep -q LISTEN; then
  if [ "$FORCE_RESTART" = true ]; then
    echo "[INFO] Killing existing frontend process..."
    lsof -ti :3000 | xargs kill -9
    sleep 1
  else
    echo "[SKIP] Frontend already running. Use --all to restart."
  fi
fi

if ! lsof -i :3000 | grep -q LISTEN; then
  echo "[INFO] Starting frontend (Next.js)..."
  cd "$FRONTEND_DIR" || exit 1
  if [ ! -d "node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    npm install || exit 1
  fi
  echo "[OK] Frontend launching at http://localhost:3000"
  npm run dev
fi

echo ""
echo "🚀 All systems go."
echo "🔗 API:     http://127.0.0.1:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "🛢️  Postgres: running via Docker on port 5435"
echo ""
