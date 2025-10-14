# Support Ticket Management System

Sistema de gerenciamento de tickets de suporte com FastAPI + SQLite e processamento ETL.

## ⚠️ Arquitetura de Dados

O sistema utiliza **duas fontes de dados independentes**:

- **SQLite**: 20+ tickets para operações CRUD (listar, editar)
- **CSV Kaggle**: para análise e métricas
- **ETL**: Processa APENAS o CSV → gera métricas em JSON
- **Frontend**: Lista tickets do SQLite + Dashboard com métricas do CSV

## Dataset

**Fonte**: [Customer Support Ticket Dataset - Kaggle](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset?resource=download)

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
  "status_counts": {
    "Pending Customer Response": 2881,
    "Open": 2819,
    "Closed": 2769
  },
  "priority_counts": {
    "Medium": 2192,
    "Critical": 2129,
    "High": 2085,
    "Low": 2063
  },
  "channel_counts": {
    "Email": 2143,
    "Phone": 2132,
    "Social media": 2121,
    "Chat": 2073
  },
  "top_products": [
    {"product": "Canon EOS", "count": 240},
    {"product": "GoPro Hero", "count": 228}
  ],
  "total_tickets": 8469,
  "avg_resolution_time_hours": -0.06,
  "avg_satisfaction_rating": 2.99,
  "resolution_rate": 0.0
}
```

## Tecnologias

- **Backend**: Python 3.8+ + FastAPI + SQLite
- **ETL**: pandas + datetime parsing
- **Frontend**: Next.js 15 + TypeScript + Material Tailwind
- **Dataset**: Kaggle Customer Support Tickets (8.469 registros)

## Comandos Úteis

```bash
make install         # Instalar dependências
make run-backend     # Executar servidor
make etl            # Processar métricas
make test-api       # Testar todos os endpoints (completo)
make test-api-simple # Testar endpoints (rápido)
make clean          # Limpar arquivos
```

## Testes da API

```bash
# Teste completo (Python) - 25 testes
make test-api
# ou
python test_backend.py

# Teste rápido (Bash) - 18 testes
make test-api-simple
# ou
./test_backend.sh 8000

```

## Documentação

- **[🚀 Guia de Início](docs/GETTING_STARTED.md)** - Setup completo para novos desenvolvedores
- **[🏗️ Arquitetura](docs/ARCHITECTURE.md)** - Visão geral da arquitetura do sistema
- **[📊 Estruturas de Dados](docs/DATA_STRUCTURES.md)** - Schemas SQLite, CSV e APIs detalhados
- **[📈 Guia de Métricas](docs/METRICAS.md)** - Como adicionar novas métricas ao dashboard
- **[🔌 Documentação da API](docs/API.md)** - Endpoints, parâmetros e exemplos completos
- **[🧪 Scripts de Teste](TESTING.md)** - Testes completos para todos os endpoints