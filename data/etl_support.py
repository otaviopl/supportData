import pandas as pd
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "raw" / "tickets.csv"
OUT_PATH = BASE / "processed" / "metrics.json"

def process_with_pandas():
    print("Iniciando ETL com pandas...")
    
    if not CSV_PATH.exists():
        print(f"⚠ CSV não encontrado: {CSV_PATH}")
        return
    
    # Ler CSV com pandas
    df = pd.read_csv(CSV_PATH)
    print(f"Lidos {len(df)} tickets")
    
    # Parse de datas
    df['Date of Purchase'] = pd.to_datetime(df['Date of Purchase'], errors='coerce')
    df['First Response Time'] = pd.to_datetime(df['First Response Time'], errors='coerce')
    df['Time to Resolution'] = pd.to_datetime(df['Time to Resolution'], errors='coerce')
    
    # Métricas básicas
    daily_counts = df.groupby(df['Date of Purchase'].dt.date).size()
    status_counts = df['Ticket Status'].value_counts().to_dict()
    priority_counts = df['Ticket Priority'].value_counts().to_dict()
    channel_counts = df['Ticket Channel'].value_counts().to_dict()
    top_products = df['Product Purchased'].value_counts().head(10).to_dict()
    
    # Tempo médio de resolução
    df['Resolution Time Hours'] = (df['Time to Resolution'] - df['First Response Time']).dt.total_seconds() / 3600
    avg_resolution_time = df['Resolution Time Hours'].mean()
    
    # Taxa de satisfação
    satisfaction_avg = df['Customer Satisfaction Rating'].astype(float).mean()
    
    # Taxa de resolução
    resolved_count = len(df[df['Ticket Status'].isin(['resolved', 'closed'])])
    resolution_rate = (resolved_count / len(df)) * 100
    
    metrics = {
        "tickets_by_day": [{"date": str(date), "count": int(count)} for date, count in daily_counts.items()],
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "channel_counts": channel_counts,
        "top_products": [{"product": product, "count": int(count)} for product, count in top_products.items()],
        "total_tickets": len(df),
        "avg_resolution_time_hours": round(avg_resolution_time, 2) if not pd.isna(avg_resolution_time) else None,
        "avg_satisfaction_rating": round(satisfaction_avg, 2) if not pd.isna(satisfaction_avg) else None,
        "resolution_rate": round(resolution_rate, 2)
    }
    
    # Salvar métricas
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"✓ Métricas salvas em {OUT_PATH}")
    print(f"  Total: {metrics['total_tickets']} tickets")
    print(f"  Status mais comum: {max(status_counts.items(), key=lambda x: x[1]) if status_counts else 'N/A'}")
    print(f"  Canal mais usado: {max(channel_counts.items(), key=lambda x: x[1]) if channel_counts else 'N/A'}")
    if not pd.isna(avg_resolution_time):
        print(f"  Tempo médio de resolução: {avg_resolution_time:.2f}h")

if __name__ == "__main__":
    process_with_pandas()