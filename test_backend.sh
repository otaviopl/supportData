#!/bin/bash

PORT=${1:-8080}
HOST=${2:-localhost}
BASE_URL="http://$HOST:$PORT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing Backend FastAPI${NC}"
echo -e "${BLUE}URL: $BASE_URL${NC}"
echo "=================================="

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=${4:-200}
    local description=$5
    
    echo -e "\n${YELLOW}$method $endpoint${NC}"
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
    
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "   ${GREEN}PASS Status: $status_code${NC}"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "   Response: $(echo "$body" | head -c 100)..."
        fi
    else
        echo -e "   ${RED}FAIL Status: $status_code (expected: $expected_status)${NC}"
        if [ -n "$body" ]; then
            echo "   Error: $(echo "$body" | head -c 100)..."
        fi
    fi
}

check_server() {
    echo -e "${BLUE}Checking if server is running...${NC}"
    if curl -s "$BASE_URL/" > /dev/null; then
        echo -e "${GREEN}Server is running!${NC}"
        return 0
    else
        echo -e "${RED}Server not responding at $BASE_URL${NC}"
        echo -e "${YELLOW}Check if backend is running:${NC}"
        echo "   uvicorn backend.app:app --host 0.0.0.0 --port $PORT"
        return 1
    fi
}

if ! check_server; then
    exit 1
fi

echo -e "\n${BLUE}Running tests...${NC}"

test_endpoint "GET" "/" "" 200 "Basic API info"
test_endpoint "GET" "/tickets" "" 200 "List all tickets"
test_endpoint "GET" "/tickets?page=1&page_size=5" "" 200 "With pagination"
test_endpoint "GET" "/tickets?status=open" "" 200 "Filter by status"
test_endpoint "GET" "/tickets?priority=high" "" 200 "Filter by priority"
test_endpoint "GET" "/tickets?channel=email" "" 200 "Filter by channel"
test_endpoint "GET" "/tickets?q=erro" "" 200 "Search by text"
test_endpoint "GET" "/tickets/1" "" 200 "Get ticket ID 1"
test_endpoint "GET" "/tickets/999" "" 404 "Non-existent ticket"
test_endpoint "PATCH" "/tickets/1" '{"status": "in_progress"}' 200 "Update status"
test_endpoint "PATCH" "/tickets/1" '{"priority": "urgent"}' 200 "Update priority"
test_endpoint "PATCH" "/tickets/1" '{"status": "resolved", "priority": "low"}' 200 "Update both"
test_endpoint "PATCH" "/tickets/1" '{"status": "invalid"}' 422 "Invalid status"
test_endpoint "PATCH" "/tickets/1" '{}' 400 "Empty body"
test_endpoint "PATCH" "/tickets/999" '{"status": "resolved"}' 404 "Non-existent ticket"
test_endpoint "GET" "/metrics" "" 200 "Get metrics"
test_endpoint "GET" "/invalid" "" 404 "Non-existent endpoint"
test_endpoint "POST" "/tickets" '{}' 405 "Method not allowed"
test_endpoint "GET" "/tickets?page=0" "" 422 "Invalid page"
test_endpoint "GET" "/tickets?page_size=200" "" 422 "Page size too large"

echo -e "\n${BLUE}==================================${NC}"
echo -e "${GREEN}Tests completed!${NC}"
echo -e "${BLUE}For detailed tests, use: python test_backend.py${NC}"