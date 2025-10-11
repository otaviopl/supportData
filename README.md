# Support Ticket Management System

Sistema de gerenciamento de tickets de suporte com FastAPI + SQLite e processamento ETL.

## Dataset

**Fonte**: [Customer Support Ticket Dataset - Kaggle](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset?resource=download)

- 29.808 tickets de suporte ao cliente
- Campos: Data, Status, Prioridade, Canal, Produto, Satisfação
- Formato: CSV com dados históricos reais

## Setup Rápido

### 1. Backend
```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Executar servidor
uvicorn backend.app:app --reload
```

### 2. ETL (Métricas)
```bash
# Processar dados do CSV com pandas
python data/etl_support.py
```

### 3. Frontend (Opcional)
```bash
cd frontend
pnpm install
pnpm dev
```

## API Endpoints

### GET /tickets
Lista tickets com paginação e filtros.

**Parâmetros:**
- `page` (int): Página (default: 1)
- `page_size` (int): Itens por página (default: 20, max: 100)
- `q` (string): Busca em assunto/cliente
- `status` (enum): open, in_progress, on_hold, resolved, closed
- `priority` (enum): low, medium, high, urgent
- `channel` (enum): email, slack, whatsapp, web, phone

**Exemplo:**
```bash
curl "http://localhost:8000/tickets?status=open&priority=high"
```

### PATCH /tickets/{id}
Atualiza status e/ou prioridade de um ticket.

**Body:**
```json
{
  "status": "resolved",
  "priority": "medium"
}
```

**Exemplo:**
```bash
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

### GET /metrics
Retorna métricas processadas do dataset Kaggle.

**Exemplo:**
```bash
curl "http://localhost:8000/metrics"
```

**Resposta:**
```json
{
  "tickets_by_day": [{"date": "2020-01-01", "count": 8}],
  "status_counts": {"open": 1500, "resolved": 800},
  "priority_counts": {"high": 600, "medium": 1200},
  "channel_counts": {"email": 2000, "web": 800},
  "top_products": [{"product": "Product A", "count": 500}],
  "total_tickets": 29808,
  "avg_resolution_time_hours": 24.5,
  "avg_satisfaction_rating": 4.2,
  "resolution_rate": 85.3
}
```

## Teste Rápido

```bash
# 1. Listar tickets
curl "http://localhost:8000/tickets"

# 2. Alterar status do ticket 1
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# 3. Ver métricas
curl "http://localhost:8000/metrics"
```

## Estrutura do Projeto

```
├─ backend/               # FastAPI + SQLite
│  ├─ app.py             # Endpoints principais
│  ├─ models.py          # Enums e validações
│  ├─ repositories.py    # CRUD operations
│  └─ db.py              # Configuração SQLite
├─ data/
│  ├─ raw/tickets.csv    # Dataset do Kaggle
│  ├─ processed/         # Métricas geradas
│  └─ etl_support.py     # Script ETL com pandas
└─ frontend/             # Next.js (opcional)
```

## Tecnologias

- **Backend**: Python 3.8+ + FastAPI + SQLite
- **ETL**: pandas + datetime parsing
- **Frontend**: Next.js 15 + TypeScript + Material Tailwind
- **Dataset**: Kaggle Customer Support Tickets (29.808 registros)

## Comandos Úteis

```bash
make install      # Instalar dependências
make run-backend  # Executar servidor
make etl          # Processar métricas
make clean        # Limpar arquivos
```