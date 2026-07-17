#!/usr/bin/env bash
# Run from the backend directory: bash backend/start.sh
# First-time setup: bash backend/setup_dev.sh
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "No .venv found — run setup_dev.sh first:"
  echo "  bash backend/setup_dev.sh"
  exit 1
fi

source .venv/bin/activate

echo "Starting CommAi API server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --env-file ../.env
