# Support Tickets Frontend

Frontend Next.js com Material Tailwind para sistema de gerenciamento de tickets.

## Tecnologias

- Next.js 15.0.3 (App Router)
- TypeScript
- Material Tailwind
- Tailwind CSS
- Node.js 20.11.0

## Setup

### 1. Instalar dependências

```bash
pnpm install
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Executar em desenvolvimento

```bash
pnpm dev
```

Frontend disponível em: http://localhost:3000

## Estrutura

```
src/
├── app/
│   ├── api/                 # BFF - Backend for Frontend
│   │   ├── tickets/         # Proxy para /tickets do FastAPI
│   │   └── metrics/         # Proxy para /metrics do FastAPI
│   ├── tickets/             # Páginas de tickets
│   ├── dashboard/           # Dashboard com métricas
│   ├── layout.tsx           # Layout principal
│   └── page.tsx             # Home
├── components/              # Componentes React
├── lib/                     # Utilitários
│   ├── api.ts              # Cliente HTTP
│   └── material-tailwind.tsx
└── types/                   # Types TypeScript
```

## Páginas

- `/` - Home
- `/tickets` - Lista de tickets com filtros
- `/tickets/[id]` - Detalhes e edição de ticket
- `/dashboard` - Dashboard com métricas

## BFF Pattern

O frontend usa rotas API do Next.js (`/app/api/`) como Backend for Frontend:
- Encapsula chamadas ao FastAPI
- Permite transformação de dados
- Evita problemas de CORS
- Cache e otimizações do lado do servidor

## Comandos

```bash
pnpm dev          # Desenvolvimento
pnpm build        # Build de produção
pnpm start        # Servidor de produção
pnpm lint         # Linter
```

## Cores

O tema usa escala de cinza (branco, cinza, preto):
- Background: Branco/Preto
- Primary: Escala de cinza (50-950)
- Componentes: Material Tailwind

