#!/bin/bash
set -e

echo "Starting run_all.sh"

bash /app/fetch_IB_margin_file.sh || { echo "Fetch failed"; exit 1; }

echo "Fetch complete, running main.py..."
python /app/main.py || { echo "main.py failed"; exit 1; }

echo "Done"
