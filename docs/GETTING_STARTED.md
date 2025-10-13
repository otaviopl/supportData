# Guia de Início - Support Ticket Management

Este guia ajuda novos desenvolvedores a configurar e executar o sistema pela primeira vez.

## Pré-requisitos

### Software Necessário

- **Python 3.8+** - Para backend e ETL
- **Node.js 20.11.0** - Para frontend (use `.nvmrc`)
- **pnpm** - Gerenciador de pacotes Node.js
- **Git** - Controle de versão

### Verificar Instalações

```bash
# Verificar Python
python --version  # Deve ser 3.8+
pip --version

# Verificar Node.js (usar versão específica)
node --version    # Deve ser 20.11.0
pnpm --version

# Verificar Git
git --version
```

## Configuração Inicial

### 1. Clonar o Repositório

```bash
git clone <repository-url>
cd teste1-tecnico
```

### 2. Configurar Backend

```bash
# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r backend/requirements.txt
```

### 3. Configurar Frontend

```bash
# Instalar dependências Node.js
cd frontend
pnpm install
cd ..
```

### 4. Configurar ETL

```bash
# O ETL usa apenas pandas (já instalado com backend)
# Verificar se o CSV existe
ls -la data/raw/tickets.csv
```

## Executando o Sistema

### Opção 1: Usando Makefile (Recomendado)

```bash
# Instalar todas as dependências
make install

# Executar backend
make run-backend

# Em outro terminal, gerar métricas
make etl

# Em outro terminal, executar frontend
cd frontend && pnpm dev
```

### Opção 2: Manual

```bash
# Terminal 1: Backend
uvicorn backend.app:app --reload

# Terminal 2: ETL
python data/etl_support.py

# Terminal 3: Frontend
cd frontend && pnpm dev
```

## Verificar se Está Funcionando

### 1. Testar Backend

```bash
# Testar API
curl "http://localhost:8000/"

# Testar tickets
curl "http://localhost:8000/tickets"

# Testar métricas
curl "http://localhost:8000/metrics"
```

### 2. Testar Frontend

Acesse no navegador:
- **Home**: http://localhost:3000
- **Tickets**: http://localhost:3000/tickets
- **Dashboard**: http://localhost:3000/dashboard

### 3. Verificar Dados

```bash
# Verificar SQLite
sqlite3 app.db "SELECT COUNT(*) FROM tickets;"

# Verificar métricas
ls -la data/processed/metrics.json
```

## Estrutura do Projeto

```
teste1-tecnico/
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
│  └─ .nvmrc             # Node version
├─ data/                  # Data Layer
│  ├─ raw/                # Raw data sources
│  │  ├─ tickets.csv      # Kaggle dataset (8.469 tickets)
│  │  └─ seed_tickets.json # SQLite seed data (20 tickets)
│  ├─ processed/          # Processed data
│  │  └─ metrics.json     # ETL output
│  └─ etl_support.py      # ETL script
├─ docs/                  # Documentation
│  ├─ GETTING_STARTED.md  # This file
│  ├─ ARCHITECTURE.md     # System architecture
│  ├─ DATA_STRUCTURES.md  # Data schemas
│  ├─ API.md             # API documentation
│  └─ METRICAS.md        # Metrics guide
├─ app.db                # SQLite database (created automatically)
├─ Makefile             # Development commands
└─ README.md            # Project overview
```

## Comandos Úteis

### Makefile Commands

```bash
make help          # Mostrar todos os comandos disponíveis
make install       # Instalar todas as dependências
make run-backend   # Executar servidor FastAPI
make etl           # Processar métricas do CSV
make clean         # Limpar arquivos temporários
```

### Desenvolvimento

```bash
# Backend
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && pnpm dev

# ETL
python data/etl_support.py

# Testes da API
curl "http://localhost:8000/tickets"
curl -X PATCH "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

## Troubleshooting

### Problemas Comuns

#### 1. Porta 8000 em uso
```bash
# Verificar processo usando a porta
lsof -i :8000

# Matar processo
kill -9 <PID>

# Ou usar porta diferente
uvicorn backend.app:app --reload --port 8001
```

#### 2. Node.js versão errada
```bash
# Usar nvm para instalar versão correta
nvm install 20.11.0
nvm use 20.11.0

# Verificar versão
node --version
```

#### 3. Dependências Python não instaladas
```bash
# Reinstalar dependências
pip install -r backend/requirements.txt

# Ou usar pip-tools para lock de dependências
pip install pip-tools
pip-compile backend/requirements.in
pip-sync backend/requirements.txt
```

#### 4. Frontend não carrega
```bash
# Limpar cache do Next.js
cd frontend
rm -rf .next
pnpm dev

# Verificar se backend está rodando
curl http://localhost:8000/
```

#### 5. Métricas não aparecem
```bash
# Verificar se CSV existe
ls -la data/raw/tickets.csv

# Re-executar ETL
python data/etl_support.py

# Verificar se arquivo foi gerado
ls -la data/processed/metrics.json
```

#### 6. Banco de dados vazio
```bash
# Remover banco e recriar
rm app.db
uvicorn backend.app:app --reload

# Verificar dados
sqlite3 app.db "SELECT COUNT(*) FROM tickets;"
```

### Logs e Debug

```bash
# Backend logs
uvicorn backend.app:app --reload --log-level debug

# ETL logs
python data/etl_support.py 2>&1 | tee etl.log

# Frontend logs
cd frontend && pnpm dev --verbose
```

## Próximos Passos

### 1. Explorar o Sistema

- **Listar tickets**: http://localhost:3000/tickets
- **Ver detalhes**: Clique em qualquer ticket
- **Editar ticket**: Mude status ou prioridade
- **Ver métricas**: http://localhost:3000/dashboard

### 2. Entender a Arquitetura

Leia a documentação:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Visão geral da arquitetura
- **[DATA_STRUCTURES.md](DATA_STRUCTURES.md)** - Estruturas de dados
- **[API.md](API.md)** - Documentação da API

### 3. Desenvolver Novas Funcionalidades

- **[METRICAS.md](METRICAS.md)** - Como adicionar novas métricas
- **[API.md](API.md)** - Como criar novos endpoints
- **Frontend**: Criar novos componentes React

### 4. Contribuir

1. **Fork** o repositório
2. **Criar branch** para sua feature
3. **Implementar** mudanças
4. **Testar** localmente
5. **Criar Pull Request**

## Ambiente de Desenvolvimento

### IDE Recomendado

- **VS Code** com extensões:
  - Python
  - TypeScript/JavaScript
  - Tailwind CSS IntelliSense
  - Material Tailwind

### Configurações VS Code

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "tailwindCSS.experimental.classRegex": [
    ["classnames\\(([^)]*)\\)", "'([^']*)'"],
    ["clsx\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ]
}
```

### Git Hooks (Opcional)

```bash
# Instalar pre-commit
pip install pre-commit
pre-commit install

# Configurar .pre-commit-config.yaml
```

## Suporte

### Documentação
- **README.md** - Visão geral do projeto
- **docs/** - Documentação detalhada

### Problemas
1. Verificar **Troubleshooting** acima
2. Consultar **documentação** relevante
3. Criar **issue** no repositório

### Comunidade
- **Discord/Slack** - Canal de desenvolvimento
- **Code Review** - Peer review obrigatório
- **Documentação** - Manter docs atualizadas

---

**Versão**: 1.0  
**Última atualização**: 2025-01-11
