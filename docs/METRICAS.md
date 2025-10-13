# Guia para Adicionar Novas Métricas ao Dashboard

## Visão Geral do Processo

O sistema funciona com 3 componentes principais:
1. **ETL** (`data/etl_support.py`) - Extrai e processa dados do CSV
2. **API** (FastAPI + Next.js BFF) - Serve os dados processados
3. **Dashboard** (React + Material Tailwind) - Visualiza as métricas

## ⚠️ Importante: Separação de Dados

- **CSV Kaggle**: 8.469 tickets para análise e métricas
- **SQLite**: 20+ tickets para operações CRUD
- **ETL**: Processa **APENAS** o CSV, não toca no SQLite

## Checklist Completo

### 1. Análise e Planejamento

- [ ] Definir a métrica: O que queremos medir?
- [ ] Identificar fonte de dados: Que campos do CSV serão usados?
- [ ] Definir formato de saída: Como a métrica será exibida?
- [ ] Validar necessidade: A métrica agrega valor ao negócio?

### 2. Implementação no ETL

Arquivo: `data/etl_support.py`

#### Exemplo: Adicionar "Tickets por Hora do Dia"

```python
def process_with_pandas():
    print("Iniciando ETL com pandas...")
    
    # Ler CSV com pandas
    df = pd.read_csv(CSV_PATH)
    
    # Parse de datas (já existente)
    df['Date of Purchase'] = pd.to_datetime(df['Date of Purchase'], errors='coerce')
    
    # NOVA MÉTRICA: Tickets por hora
    tickets_by_hour = {}
    for hour in range(24):
        # Exemplo: contar tickets por hora do dia
        hour_tickets = df[df['Date of Purchase'].dt.hour == hour]
        tickets_by_hour[str(hour)] = len(hour_tickets)
    
    # ... outras métricas existentes ...
    
    # Adicionar ao objeto metrics final
    metrics = {
        "tickets_by_day": [...],
        "status_counts": {...},
        "priority_counts": {...},
        "channel_counts": {...},
        "top_products": [...],
        "total_tickets": len(df),
        "avg_resolution_time_hours": ...,
        "avg_satisfaction_rating": ...,
        "resolution_rate": ...,
        "tickets_by_hour": tickets_by_hour,  # NOVA MÉTRICA
    }
    
    # Salvar métricas
    OUT_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
```

#### Regenerar métricas
```bash
make etl
# ou
python data/etl_support.py
```

### 3. Atualizar Types TypeScript

Arquivo: `frontend/src/types/index.ts`

```typescript
export interface Metrics {
  // ... tipos existentes ...
  tickets_by_hour: Record<string, number>  // NOVA MÉTRICA
}
```
