#!/bin/bash

# Script simples para testar endpoints do backend FastAPI
# Uso: ./test_backend.sh [porta] [host]

# Configuração
PORT=${1:-8080}
HOST=${2:-localhost}
BASE_URL="http://$HOST:$PORT"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Testando Backend FastAPI${NC}"
echo -e "${BLUE}URL: $BASE_URL${NC}"
echo "=================================="

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=${4:-200}
    local description=$5
    
    echo -e "\n${YELLOW}🔍 $method $endpoint${NC}"
    echo "   $description"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "PATCH" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PATCH \
            -H "Content-Type: application/json" \
            -d "$data" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" "$BASE_URL$endpoint")
    fi
    
    # Separar body e status code
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "   ${GREEN}✅ Status: $status_code${NC}"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "   Resposta: $(echo "$body" | head -c 100)..."
        fi
    else
        echo -e "   ${RED}❌ Status: $status_code (esperado: $expected_status)${NC}"
        if [ -n "$body" ]; then
            echo "   Erro: $(echo "$body" | head -c 100)..."
        fi
    fi
}

# Função para verificar se servidor está rodando
check_server() {
    echo -e "${BLUE}🔍 Verificando se servidor está rodando...${NC}"
    if curl -s "$BASE_URL/" > /dev/null; then
        echo -e "${GREEN}✅ Servidor está rodando!${NC}"
        return 0
    else
        echo -e "${RED}❌ Servidor não está respondendo em $BASE_URL${NC}"
        echo -e "${YELLOW}💡 Verifique se o backend está rodando:${NC}"
        echo "   uvicorn backend.app:app --host 0.0.0.0 --port $PORT"
        return 1
    fi
}

# Verificar servidor
if ! check_server; then
    exit 1
fi

echo -e "\n${BLUE}📋 Executando testes...${NC}"

# 1. Informações da API
test_endpoint "GET" "/" "" 200 "Informações básicas da API"

# 2. Listar tickets
test_endpoint "GET" "/tickets" "" 200 "Listar todos os tickets"
test_endpoint "GET" "/tickets?page=1&page_size=5" "" 200 "Listar com paginação"
test_endpoint "GET" "/tickets?status=open" "" 200 "Filtrar por status"
test_endpoint "GET" "/tickets?priority=high" "" 200 "Filtrar por prioridade"
test_endpoint "GET" "/tickets?channel=email" "" 200 "Filtrar por canal"
test_endpoint "GET" "/tickets?q=erro" "" 200 "Buscar por texto"

# 3. Buscar ticket específico
test_endpoint "GET" "/tickets/1" "" 200 "Buscar ticket ID 1"
test_endpoint "GET" "/tickets/999" "" 404 "Ticket inexistente"

# 4. Atualizar tickets
test_endpoint "PATCH" "/tickets/1" '{"status": "in_progress"}' 200 "Atualizar status"
test_endpoint "PATCH" "/tickets/1" '{"priority": "urgent"}' 200 "Atualizar prioridade"
test_endpoint "PATCH" "/tickets/1" '{"status": "resolved", "priority": "low"}' 200 "Atualizar ambos"
test_endpoint "PATCH" "/tickets/1" '{"status": "invalid"}' 422 "Status inválido"
test_endpoint "PATCH" "/tickets/1" '{}' 400 "Body vazio"
test_endpoint "PATCH" "/tickets/999" '{"status": "resolved"}' 404 "Ticket inexistente"

# 5. Métricas
test_endpoint "GET" "/metrics" "" 200 "Buscar métricas"

# 6. Endpoints inválidos
test_endpoint "GET" "/invalid" "" 404 "Endpoint inexistente"
test_endpoint "POST" "/tickets" '{}' 405 "Método não permitido"

# 7. Validações
test_endpoint "GET" "/tickets?page=0" "" 422 "Página inválida"
test_endpoint "GET" "/tickets?page_size=200" "" 422 "Page size muito grande"

echo -e "\n${BLUE}==================================${NC}"
echo -e "${GREEN}🎉 Testes concluídos!${NC}"
echo -e "${BLUE}Para testes mais detalhados, use: python test_backend.py${NC}"
