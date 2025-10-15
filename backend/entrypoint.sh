#!/bin/sh
set -e

if [ "${SEED_ON_START:-true}" = "true" ]; then
  echo "Seeding database and running ETL via make..."
  make -C /app seed || python -m backend.seed
else
  echo "Skipping seed (SEED_ON_START=false). Ensuring DB schema..."
  python - <<'PY'
from backend.db import init_db
init_db()
print("✓ DB schema ensured")
PY
fi

# Always refresh metrics if desired (optional: guard via ETL_ON_START)
if [ "${ETL_ON_START:-true}" = "true" ]; then
  make -C /app etl || python /app/data/etl_support.py
else
  echo "Skipping ETL (ETL_ON_START=false)"
fi

echo "Starting FastAPI server..."
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000
