#!/bin/bash
set -e

echo "🔄 Pulling latest code from Git..."
git reset --hard
git clean -fd
git pull origin main

echo "🚀 Rebuilding containers..."
docker compose down
docker compose up --build -d

echo "✅ Deployment complete."
