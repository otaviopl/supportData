.PHONY: help install run-backend seed etl clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install backend dependencies"
	@echo "  make run-backend  - Run FastAPI backend server"
	@echo "  make seed         - Load seed data into database"
	@echo "  make etl          - Run ETL script to generate metrics"
	@echo "  make clean        - Remove database and generated files"

install:
	@echo "Installing backend dependencies..."
	pip install -r backend/requirements.txt

run-backend:
	@echo "Starting FastAPI backend..."
	uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

seed:
	@echo "Loading seed data..."
	python -m backend.seed

etl:
	@echo "Running ETL process..."
	python data/etl_support.py

clean:
	@echo "Cleaning up..."
	rm -f app.db
	rm -f data/processed/metrics.json
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

