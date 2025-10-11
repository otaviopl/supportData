import json
from pathlib import Path
from backend.db import table_is_empty, init_db
from backend.repositories import create_ticket


def load_seed_data() -> None:
    init_db()
    if not table_is_empty():
        print("✓ Tickets table already has data, skipping seed.")
        return
    
    seed_file = Path(__file__).parent.parent / "data" / "raw" / "seed_tickets.json"
    if not seed_file.exists():
        print(f"⚠ Seed file not found at {seed_file}")
        return
    
    with open(seed_file, "r", encoding="utf-8") as f:
        seed_tickets = json.load(f)
    
    count = 0
    for ticket_data in seed_tickets:
        create_ticket(
            created_at=ticket_data["created_at"],
            customer_name=ticket_data["customer_name"],
            channel=ticket_data["channel"],
            subject=ticket_data["subject"],
            description=ticket_data.get("description"),
            status=ticket_data["status"],
            priority=ticket_data["priority"],
        )
        count += 1
    print(f"✓ Loaded {count} seed tickets into database.")


if __name__ == "__main__":
    load_seed_data()

