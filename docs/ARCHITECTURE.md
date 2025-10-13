# Arquitetura do Sistema - Support Ticket Management

Este documento descreve a arquitetura geral do sistema, incluindo componentes, fluxos de dados e decisões de design.

## Visão Geral da Arquitetura

O sistema é composto por 3 camadas principais:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Ticket List │  │ Ticket Detail│  │    Dashboard        │ │
│  │ (SQLite)    │  │ (SQLite)    │  │    (CSV Metrics)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Next.js BFF     │
                    │   (/api routes)   │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│   FastAPI      │   │   FastAPI       │   │   ETL Process  │
│   /tickets     │   │   /metrics      │   │   (pandas)     │
│   (SQLite)     │   │   (JSON file)   │   │   (CSV→JSON)   │
└────────────────┘   └─────────────────┘   └────────────────┘
        │                     │                     │
┌───────▼────────┐           │             ┌───────▼────────┐
│   SQLite DB    │           │             │   CSV Kaggle   │
│   (20+ tickets)│           │             │  (8.469 tickets)│
└────────────────┘           │             └────────────────┘
                             │
                    ┌────────▼────────┐
                    │  metrics.json   │
                    │  (processed)    │
                    └─────────────────┘
```

## Componentes Principais

### 1. Frontend (Next.js 15)

**Tecnologias:**
- Next.js 15 com App Router
- TypeScript
- Material Tailwind + Tailwind CSS
- React 18

**Páginas:**
- `/` - Home page com navegação
- `/tickets` - Lista de tickets (dados do SQLite)
- `/tickets/[id]` - Detalhes do ticket (dados do SQLite)
- `/dashboard` - Métricas e análises (dados do CSV)

**BFF (Backend for Frontend):**
- `/api/tickets` - Proxy para FastAPI `/tickets`
- `/api/tickets/[id]` - Proxy para FastAPI `/tickets/{id}`
- `/api/metrics` - Proxy para FastAPI `/metrics`

### 2. Backend (FastAPI)

**Tecnologias:**
- Python 3.8+
- FastAPI
- SQLite
- Pydantic para validação

**Endpoints:**
- `GET /` - Informações da API
- `GET /tickets` - Lista tickets com paginação e filtros
- `GET /tickets/{id}` - Busca ticket específico
- `PATCH /tickets/{id}` - Atualiza status/prioridade
- `GET /metrics` - Retorna métricas processadas

### 3. ETL Process (pandas)

**Tecnologias:**
- Python pandas
- JSON para saída

**Processo:**
1. **Extract**: Lê `data/raw/tickets.csv` (8.469 registros)
2. **Transform**: Calcula métricas analíticas
3. **Load**: Salva em `data/processed/metrics.json`

## Fluxos de Dados

### Fluxo 1: Operações CRUD (SQLite)

```mermaid
graph LR
    A[Frontend] --> B[Next.js BFF]
    B --> C[FastAPI]
    C --> D[SQLite]
    D --> C
    C --> B
    B --> A
```

**Características:**
- Dados operacionais (20+ tickets)
- Operações em tempo real
- Validação com Pydantic
- Paginação e filtros

### Fluxo 2: Métricas Analíticas (CSV)

```mermaid
graph LR
    A[CSV Kaggle] --> B[ETL Process]
    B --> C[JSON Metrics]
    C --> D[FastAPI /metrics]
    D --> E[Next.js BFF]
    E --> F[Frontend Dashboard]
```

**Características:**
- Dados históricos (8.469 tickets)
- Processamento batch
- Cache em arquivo JSON
- Atualização sob demanda

## Separação de Responsabilidades

### SQLite Database
- **Propósito**: Dados operacionais para CRUD
- **Volume**: 20+ tickets (pequeno)
- **Operações**: Create, Read, Update (sem Delete)
- **Performance**: Consultas rápidas com índices
- **Dados**: Tickets reais para demonstração

### CSV Dataset
- **Propósito**: Dados históricos para análise
- **Volume**: 8.469 tickets (grande)
- **Operações**: Read-only (análise)
- **Performance**: Processamento batch
- **Dados**: Dataset real do Kaggle (2020-2021)

## Decisões de Design

### 1. Separação SQLite/CSV

**Por que separar?**
- **Performance**: SQLite otimizado para CRUD, CSV para análise
- **Escalabilidade**: Operações vs. processamento batch
- **Manutenção**: Dados operacionais vs. dados históricos
- **Flexibilidade**: Permite diferentes estratégias de atualização

### 2. BFF Pattern

**Por que usar BFF?**
- **Segurança**: Frontend não acessa backend diretamente
- **Flexibilidade**: Pode agregar dados de múltiplas fontes
- **Cache**: Controle de cache no nível do BFF
- **Transformação**: Adaptar dados para o frontend

### 3. ETL vs. Real-time

**Por que ETL para métricas?**
- **Performance**: Processamento pesado feito uma vez
- **Consistência**: Dados históricos não mudam
- **Simplicidade**: API simples que lê arquivo JSON
- **Escalabilidade**: ETL pode rodar em background

### 4. Material Tailwind

**Por que Material Tailwind?**
- **Consistência**: Design system padronizado
- **Produtividade**: Componentes prontos
- **Acessibilidade**: Componentes acessíveis por padrão
- **Customização**: Fácil de customizar com Tailwind

## Estrutura de Arquivos

```
├─ backend/                 # FastAPI Backend
│  ├─ app.py               # Main application
│  ├─ models.py            # Pydantic models
│  ├─ repositories.py      # Database operations
│  ├─ db.py               # Database configuration
│  ├─ seed.py             # Data seeding
│  └─ requirements.txt    # Python dependencies
├─ frontend/              # Next.js Frontend
│  ├─ src/
│  │  ├─ app/             # App Router pages
│  │  ├─ components/      # React components
│  │  ├─ types/           # TypeScript types
│  │  └─ lib/             # Utilities
│  ├─ package.json        # Node dependencies
│  └─ tailwind.config.js  # Tailwind configuration
├─ data/                  # Data Layer
│  ├─ raw/                # Raw data sources
│  │  ├─ tickets.csv      # Kaggle dataset
│  │  └─ seed_tickets.json # SQLite seed data
│  ├─ processed/          # Processed data
│  │  └─ metrics.json     # ETL output
│  └─ etl_support.py      # ETL script
├─ docs/                  # Documentation
│  ├─ ARCHITECTURE.md     # This file
│  ├─ DATA_STRUCTURES.md  # Data schemas
│  └─ METRICAS.md         # Metrics guide
└─ Makefile              # Development commands
```

## Padrões e Convenções

### Naming Conventions
- **Arquivos**: snake_case para Python, kebab-case para frontend
- **Variáveis**: snake_case para Python, camelCase para TypeScript
- **APIs**: RESTful com recursos no plural (`/tickets`)
- **Banco**: snake_case para tabelas e colunas

### Error Handling
- **Backend**: HTTPException com status codes apropriados
- **Frontend**: Try/catch com mensagens de erro amigáveis
- **ETL**: Logs detalhados e tratamento de dados inconsistentes

### Validation
- **Backend**: Pydantic models para validação de entrada
- **Frontend**: Validação de formulários com feedback visual
- **Database**: Constraints SQLite para integridade

## Performance e Otimização

### Backend
- **Índices SQLite**: created_at, status, priority
- **Paginação**: Limite de 100 itens por página
- **Validação**: Pydantic para validação rápida

### Frontend
- **Next.js**: SSR/SSG para performance
- **Material Tailwind**: Componentes otimizados
- **Cache**: BFF pode implementar cache quando necessário

### ETL
- **pandas**: Processamento eficiente de dados
- **JSON**: Formato leve para métricas
- **Batch**: Processamento sob demanda

## Segurança

### Backend
- **CORS**: Configurado para desenvolvimento
- **Validação**: Pydantic previne injection
- **SQLite**: Previne SQL injection com queries parametrizadas

### Frontend
- **BFF**: Isola frontend do backend
- **Validação**: Validação client-side e server-side
- **HTTPS**: Recomendado para produção

## Monitoramento e Logs

### Logs
- **Backend**: FastAPI logs automáticos
- **ETL**: Prints detalhados do processo
- **Frontend**: Console logs para debug

### Métricas
- **Performance**: Tempo de resposta das APIs
- **Uso**: Contagem de requests por endpoint
- **Erros**: Taxa de erro por endpoint

## Extensibilidade

### Novas Funcionalidades
- **Backend**: Novos endpoints seguindo padrão REST
- **Frontend**: Novos componentes reutilizáveis
- **ETL**: Novas métricas seguindo padrão estabelecido

### Integrações
- **APIs**: Fácil adicionar novos endpoints
- **BFF**: Pode agregar dados de múltiplas fontes
- **ETL**: Pode processar múltiplos datasets

---

**Versão**: 1.0  
**Última atualização**: 2025-01-11
