FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

COPY data/raw/seed_tickets.json ./data/raw/seed_tickets.json
COPY data/etl_support.py ./data/etl_support.py

EXPOSE 8000

COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
