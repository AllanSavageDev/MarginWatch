#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "❌ Commit message required."
  echo "Usage: ./local.commit.sh \"Your commit message here\""
  exit 1
fi

git add .
git commit -m "$1"
git push origin main
echo "✅ Code committed and pushed."
