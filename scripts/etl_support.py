"""
ETL script to compute support metrics from tickets.
Generates data/processed/metrics.json
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter


def get_db_path() -> Path:
    """Get the database path."""
    return Path(__file__).parent.parent / "app.db"


def get_tickets_from_db():
    """Fetch all tickets from the database."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"⚠ Database not found at {db_path}")
        print("Please run the backend first to initialize the database.")
        return []
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, updated_at, customer_name, channel,
               subject, description, status, priority
        FROM tickets
    """)
    
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return tickets


def compute_metrics(tickets: list[dict]) -> dict:
    """
    Compute various metrics from tickets.
    
    Returns a dictionary with:
    - tickets_by_day: count of tickets created per day
    - top_categories: top channels by ticket count
    - status_counts: count of tickets per status
    - resolution_hours_avg: average time to resolve (if applicable)
    - pct_within_sla: percentage within SLA (if applicable)
    """
    if not tickets:
        return {
            "tickets_by_day": [],
            "top_categories": [],
            "status_counts": {},
            "total_tickets": 0,
        }
    
    # Tickets by day
    tickets_by_day_counter = Counter()
    for ticket in tickets:
        created_date = ticket["created_at"][:10]  # Extract YYYY-MM-DD
        tickets_by_day_counter[created_date] += 1
    
    tickets_by_day = [
        {"date": date, "count": count}
        for date, count in sorted(tickets_by_day_counter.items())
    ]
    
    # Top categories (channels)
    channel_counter = Counter(ticket["channel"] for ticket in tickets)
    top_categories = [
        {"category": channel, "count": count}
        for channel, count in channel_counter.most_common()
    ]
    
    # Status counts
    status_counter = Counter(ticket["status"] for ticket in tickets)
    status_counts = dict(status_counter)
    
    # Resolution time (for resolved/closed tickets)
    resolution_times = []
    for ticket in tickets:
        if ticket["status"] in ["resolved", "closed"]:
            try:
                created = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
                updated = datetime.fromisoformat(ticket["updated_at"].replace("Z", "+00:00"))
                duration_hours = (updated - created).total_seconds() / 3600
                resolution_times.append(duration_hours)
            except Exception:
                continue
    
    resolution_hours_avg = None
    if resolution_times:
        resolution_hours_avg = round(sum(resolution_times) / len(resolution_times), 2)
    
    # SLA compliance (example: assuming 48h SLA for high/urgent priority)
    within_sla = 0
    total_resolved = len(resolution_times)
    
    if total_resolved > 0:
        for i, ticket in enumerate(tickets):
            if ticket["status"] in ["resolved", "closed"] and i < len(resolution_times):
                if ticket["priority"] in ["high", "urgent"]:
                    # SLA is 48 hours
                    if resolution_times[i] <= 48:
                        within_sla += 1
                else:
                    # SLA is 120 hours for low/medium
                    if resolution_times[i] <= 120:
                        within_sla += 1
        
        pct_within_sla = round((within_sla / total_resolved) * 100, 2)
    else:
        pct_within_sla = None
    
    return {
        "tickets_by_day": tickets_by_day,
        "top_categories": top_categories,
        "status_counts": status_counts,
        "total_tickets": len(tickets),
        "resolution_hours_avg": resolution_hours_avg,
        "pct_within_sla": pct_within_sla,
    }


def save_metrics(metrics: dict) -> None:
    """Save metrics to JSON file."""
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "metrics.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metrics saved to {output_file}")


def main():
    """Main ETL process."""
    print("Starting ETL process...")
    
    # Extract
    print("Extracting tickets from database...")
    tickets = get_tickets_from_db()
    print(f"Found {len(tickets)} tickets")
    
    # Transform
    print("Computing metrics...")
    metrics = compute_metrics(tickets)
    
    # Load
    print("Saving metrics...")
    save_metrics(metrics)
    
    print("\n✓ ETL process completed!")
    print(f"  Total tickets: {metrics['total_tickets']}")
    print(f"  Unique days: {len(metrics['tickets_by_day'])}")
    print(f"  Top category: {metrics['top_categories'][0]['category'] if metrics['top_categories'] else 'N/A'}")
    if metrics.get('resolution_hours_avg'):
        print(f"  Avg resolution time: {metrics['resolution_hours_avg']} hours")
    if metrics.get('pct_within_sla'):
        print(f"  SLA compliance: {metrics['pct_within_sla']}%")


if __name__ == "__main__":
    main()


