# Support Ticket Management System -  Stale

Sistema completo de gerenciamento de tickets de suporte com backend FastAPI + SQLite e métricas ETL.

## Estrutura do Projeto

```
├─ backend/
│  ├─ app.py              # FastAPI application
│  ├─ db.py               # Database connection & setup
│  ├─ models.py           # Pydantic models & enums
│  ├─ repositories.py     # Database operations (CRUD)
│  ├─ seed.py             # Seed data loader
│  └─ requirements.txt    # Python dependencies
├─ scripts/
│  └─ etl_support.py      # ETL script for metrics
├─ data/
│  ├─ raw/
│  │  └─ seed_tickets.json    # Initial ticket data (~20 records)
│  └─ processed/
│     └─ metrics.json         # Generated metrics (via ETL)
├─ .env.example           # Environment variables template
├─ Makefile               # Convenience commands
└─ README.md              # This file
```

## Quick Start

### 1. Instalar Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
make install
# ou
pip install -r backend/requirements.txt
```

### 2. Executar Backend

```bash
make run-backend
# ou
uvicorn backend.app:app --reload
```

O backend estará disponível em: **http://localhost:8000**

- Documentação interativa (Swagger): http://localhost:8000/docs
- Documentação alternativa (ReDoc): http://localhost:8000/redoc

### 3. Gerar Métricas (ETL)

```bash
make etl
# ou
python scripts/etl_support.py
```

Isso irá:
- Ler dados do arquivo `data/raw/tickets.csv`
- Computar métricas detalhadas (status, canais, produtos, satisfação, etc.)
- Salvar em `data/processed/metrics.json`

## 📚 API Endpoints

### GET /tickets

Listar tickets com paginação, busca e filtros.

**Query Parameters:**
- `page` (int, default=1): Número da página
- `page_size` (int, default=20): Items por página
- `q` (string, opcional): Busca em `subject` ou `customer_name`
- `status` (enum, opcional): Filtrar por status
- `priority` (enum, opcional): Filtrar por prioridade
- `channel` (enum, opcional): Filtrar por canal

**Exemplo:**
```bash
curl "http://localhost:8000/tickets?page=1&page_size=10&status=open&priority=high"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "created_at": "2025-09-20T13:22:00Z",
      "updated_at": "2025-09-20T13:22:00Z",
      "customer_name": "Acme Ltd",
      "channel": "email",
      "subject": "Erro ao finalizar pedido",
      "description": "Checkout retorna 500 em cartões AMEX",
      "status": "open",
      "priority": "high"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 23
}
```

### GET /tickets/{id}

Obter um ticket específico por ID.

**Exemplo:**
```bash
curl "http://localhost:8000/tickets/1"
```

### PATCH /tickets/{id}

Atualizar status e/ou prioridade de um ticket (idempotente).

**Body:**
```json
{
  "status": "in_progress",
  "priority": "urgent"
}
```

**Exemplo:**
```bash
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "priority": "urgent"}'
```

**Response:**
```json
{
  "id": 1,
  "status": "in_progress",
  "priority": "urgent",
  "updated_at": "2025-10-10T18:30:00Z"
}
```

**Validações:**
- 400: Enum inválido ou nenhum campo fornecido
- 404: ID não encontrado

### GET /metrics

Retornar métricas computadas pelo ETL.

**Exemplo:**
```bash
curl "http://localhost:8000/metrics"
```

**Response:**
```json
{
  "tickets_by_day": [
    {"date": "2020-01-01", "count": 8},
    {"date": "2020-01-02", "count": 12}
  ],
  "status_counts": {
    "open": 2819,
    "pending customer response": 2881,
    "closed": 2769
  },
  "channel_counts": {
    "email": 2143,
    "social media": 2121,
    "phone": 2132,
    "chat": 2073
  },
  "top_products": [
    {"product": "Canon EOS", "count": 240},
    {"product": "GoPro Hero", "count": 228}
  ],
  "total_tickets": 8469,
  "resolution_rate": 32.7,
  "avg_resolution_time_hours": -0.06,
  "avg_satisfaction_rating": null
}
```

**Nota:** Retorna 404 se `metrics.json` não existir. Execute `python scripts/etl_support.py` para gerar.

## 🗃️ Enums

### Status
- `open` - Ticket aberto
- `in_progress` - Em andamento
- `on_hold` - Em espera
- `resolved` - Resolvido
- `closed` - Fechado

### Priority
- `low` - Baixa
- `medium` - Média
- `high` - Alta
- `urgent` - Urgente

### Channel
- `email` - Email
- `slack` - Slack
- `whatsapp` - WhatsApp
- `web` - Web
- `phone` - Telefone

## 🗄️ Database Schema

```sql
CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,        -- ISO8601
  updated_at TEXT NOT NULL,        -- ISO8601
  customer_name TEXT NOT NULL,
  channel TEXT NOT NULL,           -- enum textual
  subject TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL,
  priority TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
```

## 🔧 Comandos Úteis

```bash
# Limpar banco de dados e arquivos gerados
make clean

# Recarregar seeds (após clean)
make seed

# Ver todos os comandos disponíveis
make help
```

## 🧪 Testes

Para testar os endpoints:

```bash
# Listar tickets
curl "http://localhost:8000/tickets"

# Buscar tickets com filtros
curl "http://localhost:8000/tickets?q=erro&status=open"

# Atualizar ticket
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'

# Ver métricas
curl "http://localhost:8000/metrics"
```

## ✅ Critérios de Aceite

### Backend

- ✅ Rodar com `uvicorn backend.app:app --reload`
- ✅ GET /tickets devolve paginação correta e aplica filtros/busca
- ✅ PATCH /tickets/{id} atualiza e persiste; `updated_at` muda
- ✅ GET /metrics retorna exatamente o JSON do arquivo processado
- ✅ Seeds só inserem quando a tabela está vazia
- ✅ Validação de enums com mensagens de erro apropriadas
- ✅ Endpoints idempotentes e RESTful

## 📝 Notas Técnicas

- **SQLite** usado para simplicidade (sem instalação externa)
- **Seeds automáticos** carregados no startup do FastAPI
- **CORS habilitado** para acesso do frontend
- **Documentação automática** via Swagger UI
- **Type hints completos** com Pydantic v2
- **Context managers** para gerenciamento seguro de conexões DB

## 🐛 Troubleshooting

**Problema:** Erro "ModuleNotFoundError: No module named 'backend'"

**Solução:** Execute os comandos a partir do diretório raiz do projeto:
```bash
cd /home/tata/Stale/teste1-tecnico
python -m backend.app
```

**Problema:** Métricas retornam 404

**Solução:** Execute o script ETL primeiro:
```bash
make etl
```

## 📄 Licença

Este projeto foi desenvolvido como teste técnico.


