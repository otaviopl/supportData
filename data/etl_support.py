import json, csv
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "raw" / "tickets.csv"
OUT_PATH = BASE / "processed" / "metrics.json"

def read_csv():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def parse_date(date_str):
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date().isoformat()
    except:
        return None

def parse_datetime(dt_str):
    if not dt_str or dt_str.strip() == "":
        return None
    try:
        return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")
    except:
        return None

def calculate_resolution_time(first_response, resolution_time):
    if not first_response or not resolution_time:
        return None
    try:
        first = parse_datetime(first_response)
        resolution = parse_datetime(resolution_time)
        if first and resolution:
            return (resolution - first).total_seconds() / 3600
    except:
        pass
    return None

def main():
    print("Iniciando ETL...")
    
    if not CSV_PATH.exists():
        print(f"⚠ CSV não encontrado: {CSV_PATH}")
        return
    
    rows = read_csv()
    print(f"Lidos {len(rows)} tickets")
    
    tickets_by_day = Counter()
    tickets_by_status = Counter()
    tickets_by_priority = Counter()
    tickets_by_channel = Counter()
    tickets_by_type = Counter()
    tickets_by_gender = Counter()
    products_purchased = Counter()
    resolution_times = []
    satisfaction_ratings = []
    
    for ticket in rows:
        # Data de criação
        purchase_date = parse_date(ticket.get("Date of Purchase", ""))
        if purchase_date:
            tickets_by_day[purchase_date] += 1
        
        # Status
        status = ticket.get("Ticket Status", "").strip().lower()
        if status:
            tickets_by_status[status] += 1
        
        # Prioridade
        priority = ticket.get("Ticket Priority", "").strip().lower()
        if priority:
            tickets_by_priority[priority] += 1
        
        # Canal
        channel = ticket.get("Ticket Channel", "").strip().lower()
        if channel:
            tickets_by_channel[channel] += 1
        
        # Tipo
        ticket_type = ticket.get("Ticket Type", "").strip().lower()
        if ticket_type:
            tickets_by_type[ticket_type] += 1
        
        # Gênero
        gender = ticket.get("Customer Gender", "").strip().lower()
        if gender:
            tickets_by_gender[gender] += 1
        
        # Produto
        product = ticket.get("Product Purchased", "").strip()
        if product:
            products_purchased[product] += 1
        
        # Tempo de resolução
        resolution_time = calculate_resolution_time(
            ticket.get("First Response Time", ""),
            ticket.get("Time to Resolution", "")
        )
        if resolution_time:
            resolution_times.append(resolution_time)
        
        # Satisfação
        rating = ticket.get("Customer Satisfaction Rating", "").strip()
        if rating and rating.isdigit():
            satisfaction_ratings.append(int(rating))
    
    # Métricas calculadas
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else None
    avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else None
    
    metrics = {
        "tickets_by_day": [{"date": d, "count": c} for d, c in sorted(tickets_by_day.items())],
        "status_counts": dict(tickets_by_status),
        "priority_counts": dict(tickets_by_priority),
        "channel_counts": dict(tickets_by_channel),
        "type_counts": dict(tickets_by_type),
        "gender_distribution": dict(tickets_by_gender),
        "top_products": [{"product": p, "count": c} for p, c in products_purchased.most_common(10)],
        "total_tickets": len(rows),
        "avg_resolution_time_hours": round(avg_resolution_time, 2) if avg_resolution_time else None,
        "avg_satisfaction_rating": round(avg_satisfaction, 2) if avg_satisfaction else None,
        "resolution_rate": round((tickets_by_status.get("resolved", 0) + tickets_by_status.get("closed", 0)) / len(rows) * 100, 2) if rows else 0
    }
    
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Métricas salvas em {OUT_PATH}")
    print(f"  Total: {metrics['total_tickets']} tickets")
    print(f"  Status mais comum: {max(tickets_by_status.items(), key=lambda x: x[1]) if tickets_by_status else 'N/A'}")
    print(f"  Canal mais usado: {max(tickets_by_channel.items(), key=lambda x: x[1]) if tickets_by_channel else 'N/A'}")
    if avg_resolution_time:
        print(f"  Tempo médio de resolução: {avg_resolution_time:.2f}h")

if __name__ == "__main__":
    main()
