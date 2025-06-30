#!/usr/bin/env bash
set -e

# Optionally load .env (if you’re using python-dotenv in config.py)
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Activate local venv if in-project
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# Run Uvicorn with auto‐reload for development
poetry run uvicorn jewelry_inventory.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000