# Support Tickets – Guia Rápido

Sistema de suporte com FastAPI (SQLite) + ETL em pandas (CSV do Kaggle) + Next.js.

## O que é cada parte
- SQLite: tickets CRUD (lista/edita).
- CSV Kaggle: somente métricas. ETL gera `data/processed/metrics.json`.
- Frontend: páginas de Tickets e Dashboard (lendo `/tickets` e `/metrics`).

Dataset: `Customer Support Ticket Dataset` (Kaggle).

## Como rodar (Docker)
```bash
docker compose up -d --build
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
```
O backend executa seed e ETL automaticamente na inicialização do container.

### Docker (passo a passo)
```bash
# na raiz do projeto
docker compose up -d             # inicia em segundo plano
docker compose up -d --build     # (primeira vez ou após mudanças)

# status dos serviços
docker compose ps

# logs
docker compose logs -f backend
docker compose logs -f frontend

# entrar no container
docker compose exec backend sh
docker compose exec frontend sh

# parar
docker compose down
# parar e remover volumes (remove app.db e metrics.json do volume)
docker compose down -v
```

## Como rodar (local)
```bash
# Backend
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# ETL (gera metrics.json)
python data/etl_support.py

# Frontend
cd frontend && pnpm install && pnpm dev
```

## Primeira execução (se rodar local)
```bash
make seed   # carrega ~20 tickets no SQLite
make etl    # processa CSV e escreve metrics.json
```

## Endpoints
- GET `/tickets` – lista com filtros (`status`, `priority`, `channel`, `search`).
  - Ex.: `curl "http://localhost:8000/tickets?status=open&priority=high"`
- PATCH `/tickets/{id}` – atualiza `status` e/ou `priority`.
  - Ex.:
    ```bash
    curl -X PATCH http://localhost:8000/tickets/1 \
      -H 'Content-Type: application/json' \
      -d '{"status":"resolved"}'
    ```
- POST `/tickets` – cria um novo ticket.
### Webhook (n8n)
Se a criação/atualização resultar em `status = closed` ou `priority = high`, o backend envia um POST para a URL definida em `N8N_WEBHOOK_URL` (ou `n8n_webhook_url`).

Corpo do POST (JSON):
```json
{
  "id": 1,
  "status": "closed",
  "priority": "high",
  "customer_name": "Maria",
  "subject": "Problema de acesso",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T01:00:00Z"
}
```

Configuração:
- `.env` local: defina `N8N_WEBHOOK_URL=https://seu-n8n/webhook/...`
- Docker Compose: adicione a variável de ambiente ao serviço `backend`.

  - Body (JSON):
    ```json
    {
      "customer_name": "Nome do Cliente",
      "channel": "email|slack|whatsapp|web|phone",
      "subject": "Assunto do ticket",
      "description": "Texto opcional",
      "status": "open|in_progress|on_hold|resolved|closed",
      "priority": "low|medium|high|urgent",
      "created_at": "2025-01-01T00:00:00Z" // opcional; se ausente, gerado no backend
    }
    ```
  - Ex.:
    ```bash
    curl -X POST http://localhost:8000/tickets \
      -H 'Content-Type: application/json' \
      -d '{
        "customer_name":"Maria",
        "channel":"email",
        "subject":"Problema de acesso",
        "description":"Não consigo logar",
        "status":"open",
        "priority":"medium"
      }'
    ```
- GET `/metrics` – retorna métricas do CSV processadas pelo pandas.
  - Ex.: `curl http://localhost:8000/metrics`

## Comandos úteis
```bash
make run-backend   # inicia FastAPI (dev)
make etl           # roda ETL do CSV
make clean         # remove app.db e metrics.json
```

## UI – Criar Ticket
Na página de lista de tickets (`frontend/src/components/TicketList.tsx`) há um botão "Criar Ticket" que abre um modal com os campos:
- Cliente (customer_name)
- Assunto (subject)
- Descrição (description)
- Status
- Prioridade
- Canal

Ao confirmar, o frontend chama `POST /tickets` (via rota Next.js em `/api/tickets`) e atualiza a lista.

## Estrutura do projeto (mini)
```text
.
├── backend/        # FastAPI + SQLite (seeds/CRUD)
├── data/           # ETL pandas (CSV -> metrics.json)
├── frontend/       # Next.js (tickets + dashboard)
├── Dockerfile      # Frontend
├── backend/Dockerfile
├── docker-compose.yml
├── Makefile        # seed, etl, run-backend, test
└── README.md
```

## Variáveis importantes
- `DB_PATH` (opcional): caminho do SQLite (default `./app.db`). No Docker já vai como `/app/app.db`.

Pronto. Use Docker para o caminho mais simples, ou o modo local para desenvolvimento.