#!/bin/bash

set -e

echo ">> Pulling latest code..."
cd ~/MarginWatch
git pull

echo ">> Building frontend..."
cd frontend
npm install
npm run build

echo ">> Build complete. Static site generated in ./frontend/out"
ls -l out

