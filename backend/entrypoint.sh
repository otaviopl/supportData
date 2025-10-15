#!/bin/sh
set -e

echo "Seeding database and running ETL via make..."
make -C /app seed || python -m backend.seed
make -C /app etl || python /app/data/etl_support.py

echo "Starting FastAPI server..."
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000
