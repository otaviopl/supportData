# Support Ticket Management System

Sistema de gerenciamento de tickets de suporte com FastAPI + SQLite e processamento ETL.

## Estrutura

```
├─ backend/               # FastAPI backend
│  ├─ app.py
│  ├─ db.py
│  ├─ models.py
│  ├─ repositories.py
│  ├─ seed.py
│  └─ requirements.txt
├─ frontend/              # Next.js frontend
│  ├─ src/
│  │  ├─ app/            # App Router
│  │  ├─ components/     # React components
│  │  ├─ lib/            # Utilities
│  │  └─ types/          # TypeScript types
│  ├─ package.json
│  └─ .nvmrc            # Node 20.11.0
├─ data/
│  ├─ etl_support.py
│  ├─ raw/
│  └─ processed/
├─ Makefile
└─ README.md
```

## Setup

### Backend

```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Executar servidor
uvicorn backend.app:app --reload
```

Backend: http://localhost:8000

### Frontend

```bash
cd frontend

# Instalar dependências
pnpm install

# Executar servidor
pnpm dev
```

Frontend: http://localhost:3000

### ETL (Métricas)

```bash
python data/etl_support.py
```

## API Endpoints

### GET /tickets

Listar tickets com paginação e filtros.

Parâmetros:
- `page` (int, default=1)
- `page_size` (int, default=20, max=100)
- `q` (string): busca em subject ou customer_name
- `status`, `priority`, `channel` (enum): filtros

Exemplo:
```bash
curl "http://localhost:8000/tickets?q=erro&status=open"
```

### PATCH /tickets/{id}

Atualizar status e/ou prioridade.

Exemplo:
```bash
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

### GET /metrics

Retornar métricas processadas pelo ETL.

```bash
curl "http://localhost:8000/metrics"
```

## Enums

**Status:** open, in_progress, on_hold, resolved, closed
**Priority:** low, medium, high, urgent  
**Channel:** email, slack, whatsapp, web, phone

## Database Schema

```sql
CREATE TABLE tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  channel TEXT NOT NULL,
  subject TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL,
  priority TEXT NOT NULL
);
```

## Comandos

```bash
make install    # Instalar dependências
make run-backend # Executar servidor
make etl        # Processar métricas
make clean      # Limpar arquivos
```

## Testes

```bash
# Listar tickets
curl "http://localhost:8000/tickets"

# Buscar com filtros
curl "http://localhost:8000/tickets?q=erro&status=open"

# Atualizar ticket
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'

# Ver métricas
curl "http://localhost:8000/metrics"
```


