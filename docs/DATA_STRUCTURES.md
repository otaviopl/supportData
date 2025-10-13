# Estruturas de Dados - Sistema de Tickets

Este documento descreve as estruturas de dados utilizadas no sistema, incluindo os formatos do SQLite, CSV e APIs.

## Visão Geral

O sistema utiliza **duas fontes de dados completamente separadas**:

1. **SQLite Database** - Dados operacionais para CRUD (20+ tickets)
2. **CSV Dataset** - Dados históricos do Kaggle para métricas (8.469 tickets)

### ⚠️ Separação Importante

- **SQLite**: Usado para listar e editar tickets (`/tickets`)
- **CSV**: Usado para gerar métricas analíticas (`/metrics`)
- **ETL**: Processa APENAS o CSV → JSON (não toca no SQLite)
- **Frontend**: Lista tickets do SQLite + Dashboard com métricas do CSV

## 1. Estrutura SQLite (Backend)

### Tabela: `tickets`

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

### Campos Detalhados

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| `id` | INTEGER | ✅ | Chave primária auto-incremento | `1` |
| `created_at` | TEXT | ✅ | Data/hora de criação (ISO 8601) | `"2025-09-20T13:22:00Z"` |
| `updated_at` | TEXT | ✅ | Data/hora da última atualização | `"2025-09-20T13:22:00Z"` |
| `customer_name` | TEXT | ✅ | Nome da empresa/cliente | `"Acme Ltd"` |
| `channel` | TEXT | ✅ | Canal de comunicação | `"email"` |
| `subject` | TEXT | ✅ | Assunto do ticket | `"Erro ao finalizar pedido"` |
| `description` | TEXT | ❌ | Descrição detalhada | `"Checkout retorna 500..."` |
| `status` | TEXT | ✅ | Status atual do ticket | `"open"` |
| `priority` | TEXT | ✅ | Prioridade do ticket | `"high"` |

### Enums SQLite

#### Status
- `open` - Ticket aberto
- `in_progress` - Em andamento
- `on_hold` - Em espera
- `resolved` - Resolvido
- `closed` - Fechado

#### Prioridade
- `low` - Baixa
- `medium` - Média
- `high` - Alta
- `urgent` - Urgente

#### Canal
- `email` - Email
- `slack` - Slack
- `whatsapp` - WhatsApp
- `web` - Web
- `phone` - Telefone

### Índices
```sql
CREATE INDEX idx_tickets_created ON tickets(created_at);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
```

## 2. Estrutura CSV (Dataset Kaggle)

### Campos do CSV

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `Ticket ID` | INTEGER | ID único do ticket | `1` |
| `Customer Name` | TEXT | Nome do cliente | `"Marisa Obrien"` |
| `Customer Email` | TEXT | Email do cliente | `"carrollallison@example.com"` |
| `Customer Age` | INTEGER | Idade do cliente | `32` |
| `Customer Gender` | TEXT | Gênero do cliente | `"Other"` |
| `Product Purchased` | TEXT | Produto comprado | `"GoPro Hero"` |
| `Date of Purchase` | DATE | Data da compra | `"2021-03-22"` |
| `Ticket Type` | TEXT | Tipo do ticket | `"Technical issue"` |
| `Ticket Subject` | TEXT | Assunto do ticket | `"Product setup"` |
| `Ticket Description` | TEXT | Descrição detalhada | `"I'm having an issue..."` |
| `Ticket Status` | TEXT | Status do ticket | `"Pending Customer Response"` |
| `Resolution` | TEXT | Resolução do ticket | `null` |
| `Ticket Priority` | TEXT | Prioridade | `"Critical"` |
| `Ticket Channel` | TEXT | Canal de comunicação | `"Social media"` |
| `First Response Time` | DATETIME | Primeira resposta | `"2023-06-01 12:15:36"` |
| `Time to Resolution` | DATETIME | Tempo de resolução | `null` |
| `Customer Satisfaction Rating` | FLOAT | Avaliação (1-5) | `null` |

### Processamento ETL (CSV → JSON)

O ETL (`data/etl_support.py`) processa **APENAS** o CSV do Kaggle e gera métricas em JSON:

| Campo CSV | Processamento ETL | Métrica Gerada |
|-----------|------------------|----------------|
| `Ticket ID` | Contagem total | `total_tickets` |
| `Customer Name` | Análise de clientes | (usado em análises) |
| `Ticket Subject` | Análise de texto | (usado em análises) |
| `Ticket Description` | Análise de conteúdo | (usado em análises) |
| `Ticket Status` | Contagem por status | `status_counts` |
| `Ticket Priority` | Contagem por prioridade | `priority_counts` |
| `Ticket Channel` | Contagem por canal | `channel_counts` |
| `Date of Purchase` | Agrupamento temporal | `tickets_by_day` |
| `Product Purchased` | Top produtos | `top_products` |
| `First Response Time` | Cálculo de tempo | `avg_resolution_time_hours` |
| `Time to Resolution` | Cálculo de tempo | `avg_resolution_time_hours` |
| `Customer Satisfaction Rating` | Média de satisfação | `avg_satisfaction_rating` |

**IMPORTANTE**: O ETL **NÃO** escreve no SQLite. Os dados do CSV e SQLite são **completamente independentes**.

## 3. APIs e Schemas

### Models Pydantic

#### TicketBase
```python
class TicketBase(BaseModel):
    customer_name: str
    channel: TicketChannel
    subject: str
    description: Optional[str] = None
    status: TicketStatus
    priority: TicketPriority
```

#### TicketResponse
```python
class TicketResponse(TicketBase):
    id: int
    created_at: str
    updated_at: str
```

#### TicketUpdate
```python
class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
```

### Endpoints API

#### GET /tickets
**Query Parameters:**
- `page` (int): Número da página (default: 1)
- `page_size` (int): Itens por página (default: 20, max: 100)
- `q` (string): Busca em subject/customer_name
- `status` (enum): Filtrar por status
- `priority` (enum): Filtrar por prioridade
- `channel` (enum): Filtrar por canal

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
  "page_size": 20,
  "total": 1
}
```

#### PATCH /tickets/{id}
**Request Body:**
```json
{
  "status": "in_progress",
  "priority": "medium"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "in_progress",
  "priority": "medium",
  "updated_at": "2025-09-20T14:30:00Z"
}
```

#### GET /metrics
**Response:**
```json
{
  "tickets_by_day": [
    {"date": "2020-01-01", "count": 8}
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
    {"product": "Canon EOS", "count": 240}
  ],
  "total_tickets": 8469,
  "avg_resolution_time_hours": -0.06,
  "avg_satisfaction_rating": 2.99,
  "resolution_rate": 0.0
}
```

## 4. Dados de Seed

### Estrutura seed_tickets.json

```json
[
  {
    "created_at": "2025-09-20T13:22:00Z",
    "customer_name": "Acme Ltd",
    "channel": "email",
    "subject": "Erro ao finalizar pedido",
    "description": "Checkout retorna 500 em cartões AMEX",
    "status": "open",
    "priority": "high"
  }
]
```

### Características dos Seeds

- **20 registros** inseridos automaticamente no SQLite
- **IDs 1-20** reservados para dados de seed
- **Formato JSON** com campos compatíveis com TicketCreate
- **Dados realistas** para demonstração

## 5. Identificação de Origem

### Frontend (Flags Visuais)

O frontend diferencia os dados usando o campo `id`:

```typescript
// SQLite Seed (IDs 1-20)
ticket.id <= 20 ? "SQLite (Seed)" : "SQLite (Manual)"

// Exibição no componente
<Chip 
  value={ticket.id <= 20 ? "SQLite" : "SQLite"} 
  color={ticket.id <= 20 ? "blue" : "gray"}
/>
```

### Lógica de Identificação

| ID Range | Origem | Flag | Cor | Descrição |
|----------|--------|------|-----|-----------|
| 1-20 | SQLite Seed | "SQLite" | Azul | Dados inseridos automaticamente |
| 21+ | SQLite Manual | "SQLite" | Cinza | Dados inseridos manualmente |

**NOTA**: Todos os dados da lista de tickets vêm do SQLite. O CSV é usado **APENAS** para métricas no dashboard.

## 6. Validações e Constraints

### SQLite Constraints
- `id`: PRIMARY KEY, AUTOINCREMENT
- `created_at`: NOT NULL
- `updated_at`: NOT NULL  
- `customer_name`: NOT NULL
- `channel`: NOT NULL, deve ser enum válido
- `subject`: NOT NULL
- `status`: NOT NULL, deve ser enum válido
- `priority`: NOT NULL, deve ser enum válido

### Pydantic Validations
- Todos os enums são validados automaticamente
- Campos opcionais podem ser `null`
- Datas devem estar em formato ISO 8601
- Strings têm validação de tamanho mínimo

## 7. Performance e Otimizações

### Índices SQLite
- `created_at`: Para ordenação temporal
- `status`: Para filtros de status
- `priority`: Para filtros de prioridade

### Paginação
- Limite máximo de 100 itens por página
- Offset calculado: `(page - 1) * page_size`
- Contagem total para navegação

### Cache de Métricas
- Arquivo JSON gerado pelo ETL
- Atualizado apenas quando necessário
- Leitura rápida via endpoint `/metrics`

---

**Versão**: 1.0  
**Última atualização**: 2025-01-11
