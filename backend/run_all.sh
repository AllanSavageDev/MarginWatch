#!/bin/bash
set -e

# Fetch the latest margin file
bash /app/fetch_IB_margin_file.sh

# Process it into the database
python /app/main.py