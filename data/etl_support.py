import pandas as pd
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "raw" / "tickets.csv"
OUT_PATH = BASE / "processed" / "metrics.json"

def process_with_pandas():
    print("Starting ETL with pandas...")
    
    if not CSV_PATH.exists():
        print(f"CSV not found: {CSV_PATH}")
        return
    
    # Ler CSV com pandas
    df = pd.read_csv(CSV_PATH)
    print(f"Read {len(df)} tickets")
    
    # Parse de datas (apenas o que precisamos para o dashboard atual)
    df['Date of Purchase'] = pd.to_datetime(df['Date of Purchase'], errors='coerce')
    
    # Métricas básicas (compatíveis com o Dashboard atual)
    daily_counts = df.groupby(df['Date of Purchase'].dt.date).size()
    status_counts = df['Ticket Status'].value_counts().to_dict()
    priority_counts = df['Ticket Priority'].value_counts().to_dict()
    channel_counts = df['Ticket Channel'].value_counts().to_dict()
    top_products = df['Product Purchased'].value_counts().head(10).to_dict()
    type_counts = df['Ticket Type'].value_counts().head(10).to_dict()
    
    metrics = {
        "tickets_by_day": [{"date": str(date), "count": int(count)} for date, count in daily_counts.items()],
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "channel_counts": channel_counts,
        "top_products": [{"product": product, "count": int(count)} for product, count in top_products.items()],
        "type_counts": type_counts,
        "total_tickets": len(df)
    }
    # Save metrics
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    process_with_pandas()