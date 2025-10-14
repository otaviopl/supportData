#!/bin/sh

# Seed database and generate metrics

python -m backend.seed

python data/etl_support.py

# Start FastAPI server
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000
