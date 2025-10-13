# Documentação da API - Support Ticket Management

Este documento descreve todos os endpoints da API FastAPI, incluindo parâmetros, respostas, exemplos e códigos de erro.

## Base URL

```
http://localhost:8000
```

## Autenticação

Atualmente não há autenticação implementada. Todos os endpoints são públicos.

## Endpoints

### 1. Informações da API

#### GET /

Retorna informações básicas sobre a API.

**Resposta:**
```json
{
  "message": "Support Ticket API",
  "version": "1.0.0",
  "endpoints": ["GET /tickets", "PATCH /tickets/{id}", "GET /metrics"]
}
```

**Exemplo:**
```bash
curl "http://localhost:8000/"
```

---

### 2. Tickets

#### GET /tickets

Lista tickets com paginação e filtros opcionais.

**Query Parameters:**

| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `page` | integer | ❌ | 1 | Número da página (≥ 1) |
| `page_size` | integer | ❌ | 20 | Itens por página (1-100) |
| `q` | string | ❌ | - | Busca em subject e customer_name |
| `status` | enum | ❌ | - | open, in_progress, on_hold, resolved, closed |
| `priority` | enum | ❌ | - | low, medium, high, urgent |
| `channel` | enum | ❌ | - | email, slack, whatsapp, web, phone |

**Response Model:**
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
  "page_size": 20,
  "total": 1
}
```

**Exemplos:**

```bash
# Listar todos os tickets (primeira página)
curl "http://localhost:8000/tickets"

# Buscar tickets abertos com prioridade alta
curl "http://localhost:8000/tickets?status=open&priority=high"

# Buscar por texto
curl "http://localhost:8000/tickets?q=erro"

# Paginação
curl "http://localhost:8000/tickets?page=2&page_size=10"

# Múltiplos filtros
curl "http://localhost:8000/tickets?status=in_progress&channel=email&page=1&page_size=5"
```

**Códigos de Resposta:**
- `200 OK` - Sucesso
- `422 Unprocessable Entity` - Parâmetros inválidos

---

#### GET /tickets/{ticket_id}

Busca um ticket específico por ID.

**Path Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `ticket_id` | integer | ✅ | ID do ticket |

**Response Model:**
```json
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
```

**Exemplos:**

```bash
# Buscar ticket por ID
curl "http://localhost:8000/tickets/1"
curl "http://localhost:8000/tickets/42"
```

**Códigos de Resposta:**
- `200 OK` - Sucesso
- `404 Not Found` - Ticket não encontrado
- `422 Unprocessable Entity` - ID inválido

---

#### PATCH /tickets/{ticket_id}

Atualiza status e/ou prioridade de um ticket.

**Path Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `ticket_id` | integer | ✅ | ID do ticket |

**Request Body:**

```json
{
  "status": "in_progress",
  "priority": "medium"
}
```

**Campos do Body:**

| Campo | Tipo | Obrigatório | Valores Válidos |
|-------|------|-------------|-----------------|
| `status` | enum | ❌ | open, in_progress, on_hold, resolved, closed |
| `priority` | enum | ❌ | low, medium, high, urgent |

**Nota:** Pelo menos um dos campos (`status` ou `priority`) deve ser fornecido.

**Response Model:**
```json
{
  "id": 1,
  "status": "in_progress",
  "priority": "medium",
  "updated_at": "2025-09-20T14:30:00Z"
}
```

**Exemplos:**

```bash
# Atualizar apenas status
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'

# Atualizar apenas prioridade
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"priority": "urgent"}'

# Atualizar ambos
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "closed", "priority": "low"}'
```

**Códigos de Resposta:**
- `200 OK` - Sucesso
- `400 Bad Request` - Body vazio ou inválido
- `404 Not Found` - Ticket não encontrado
- `422 Unprocessable Entity` - Dados inválidos

---

### 3. Métricas

#### GET /metrics

Retorna métricas processadas do dataset Kaggle.

**Response Model:**
```json
{
  "tickets_by_day": [
    {"date": "2020-01-01", "count": 8},
    {"date": "2020-01-02", "count": 12}
  ],
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

**Campos da Resposta:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tickets_by_day` | array | Contagem de tickets por dia |
| `status_counts` | object | Distribuição por status |
| `priority_counts` | object | Distribuição por prioridade |
| `channel_counts` | object | Distribuição por canal |
| `top_products` | array | Top 10 produtos mais comuns |
| `total_tickets` | integer | Total de tickets processados |
| `avg_resolution_time_hours` | number | Tempo médio de resolução (pode ser null) |
| `avg_satisfaction_rating` | number | Avaliação média de satisfação (pode ser null) |
| `resolution_rate` | number | Taxa de resolução em percentual |

**Exemplos:**

```bash
# Buscar métricas
curl "http://localhost:8000/metrics"

# Com pretty print
curl "http://localhost:8000/metrics" | jq '.'
```

**Códigos de Resposta:**
- `200 OK` - Sucesso
- `404 Not Found` - Arquivo de métricas não encontrado

---

## Enums

### Ticket Status
- `open` - Ticket aberto
- `in_progress` - Em andamento
- `on_hold` - Em espera
- `resolved` - Resolvido
- `closed` - Fechado

### Ticket Priority
- `low` - Baixa
- `medium` - Média
- `high` - Alta
- `urgent` - Urgente

### Ticket Channel
- `email` - Email
- `slack` - Slack
- `whatsapp` - WhatsApp
- `web` - Web
- `phone` - Telefone

## Códigos de Erro

### 400 Bad Request
```json
{
  "detail": "At least one field (status or priority) must be provided"
}
```

### 404 Not Found
```json
{
  "detail": "Ticket 999 not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["query", "status"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

## Rate Limiting

Atualmente não há rate limiting implementado.

## CORS

CORS está configurado para permitir todas as origens em desenvolvimento:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Exemplos de Integração

### JavaScript/TypeScript

```typescript
// Buscar tickets
const response = await fetch('http://localhost:8000/tickets?status=open');
const data = await response.json();

// Atualizar ticket
const updateResponse = await fetch('http://localhost:8000/tickets/1', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    status: 'in_progress',
    priority: 'high'
  })
});

// Buscar métricas
const metricsResponse = await fetch('http://localhost:8000/metrics');
const metrics = await metricsResponse.json();
```

### Python

```python
import requests

# Buscar tickets
response = requests.get('http://localhost:8000/tickets', params={
    'status': 'open',
    'priority': 'high'
})
tickets = response.json()

# Atualizar ticket
update_response = requests.patch(
    'http://localhost:8000/tickets/1',
    json={
        'status': 'resolved',
        'priority': 'medium'
    }
)

# Buscar métricas
metrics_response = requests.get('http://localhost:8000/metrics')
metrics = metrics_response.json()
```

### cURL

```bash
# Lista completa de comandos de exemplo
curl "http://localhost:8000/"                           # Info da API
curl "http://localhost:8000/tickets"                     # Listar tickets
curl "http://localhost:8000/tickets/1"                   # Buscar ticket
curl "http://localhost:8000/tickets?status=open"         # Filtrar por status
curl "http://localhost:8000/tickets?q=erro"              # Buscar por texto
curl -X PATCH "http://localhost:8000/tickets/1" \        # Atualizar ticket
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
curl "http://localhost:8000/metrics"                     # Buscar métricas
```

## Validação de Dados

### Entrada
- Todos os enums são validados automaticamente pelo Pydantic
- IDs devem ser inteiros positivos
- Datas devem estar em formato ISO 8601
- Strings não podem estar vazias

### Saída
- Todos os campos de saída são validados pelo Pydantic
- Datas sempre em formato ISO 8601
- Números são tipados corretamente (int, float)
- Campos opcionais podem ser `null`

## Performance

### Otimizações
- **Índices SQLite**: created_at, status, priority
- **Paginação**: Limite máximo de 100 itens por página
- **Validação**: Pydantic para validação rápida
- **Cache**: Métricas em arquivo JSON (não recalculadas a cada request)

### Limites
- **page_size**: Máximo 100 itens por página
- **Busca**: Texto simples (sem regex ou busca avançada)
- **Filtros**: Aplicados em AND (todos devem ser verdadeiros)

---

**Versão**: 1.0  
**Última atualização**: 2025-01-11
