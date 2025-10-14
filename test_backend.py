#!/usr/bin/env python3
"""
Script completo para testar todos os endpoints do backend FastAPI
Executa testes em http://localhost:8080
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuração
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

class BackendTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.test_results = []
        
    def log(self, message: str, status: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_endpoint(self, method: str, endpoint: str, data: Dict[Any, Any] = None, 
                     expected_status: int = 200, description: str = ""):
        """Testa um endpoint e registra o resultado"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            success = response.status_code == expected_status
            status_icon = "✅" if success else "❌"
            
            self.log(f"{status_icon} {method} {endpoint} - Status: {response.status_code} (esperado: {expected_status})", 
                    "PASS" if success else "FAIL")
            
            if description:
                self.log(f"   {description}")
            
            # Tentar parsear JSON se possível
            try:
                json_data = response.json()
                if success and json_data:
                    self.log(f"   Resposta: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}...")
            except:
                self.log(f"   Resposta (texto): {response.text[:100]}...")
            
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "expected": expected_status,
                "success": success,
                "description": description
            })
            
            return response if success else None
            
        except requests.exceptions.ConnectionError:
            self.log(f"❌ {method} {endpoint} - ERRO: Não foi possível conectar ao servidor", "ERROR")
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status_code": None,
                "expected": expected_status,
                "success": False,
                "description": f"ERRO: {description}"
            })
            return None
        except Exception as e:
            self.log(f"❌ {method} {endpoint} - ERRO: {str(e)}", "ERROR")
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status_code": None,
                "expected": expected_status,
                "success": False,
                "description": f"ERRO: {description}"
            })
            return None

    def test_api_info(self):
        """Testa endpoint de informações da API"""
        self.log("🔍 Testando informações da API...")
        response = self.test_endpoint("GET", "/", description="Informações básicas da API")
        return response

    def test_tickets_list(self):
        """Testa listagem de tickets"""
        self.log("🎫 Testando listagem de tickets...")
        
        # Teste básico
        response = self.test_endpoint("GET", "/tickets", description="Listar todos os tickets")
        if not response:
            return None
            
        # Teste com paginação
        self.test_endpoint("GET", "/tickets?page=1&page_size=5", description="Listar com paginação")
        
        # Teste com filtros
        self.test_endpoint("GET", "/tickets?status=open", description="Filtrar por status")
        self.test_endpoint("GET", "/tickets?priority=high", description="Filtrar por prioridade")
        self.test_endpoint("GET", "/tickets?channel=email", description="Filtrar por canal")
        
        # Teste com busca
        self.test_endpoint("GET", "/tickets?q=erro", description="Buscar por texto")
        
        # Teste com múltiplos filtros
        self.test_endpoint("GET", "/tickets?status=open&priority=high&page=1&page_size=3", 
                          description="Múltiplos filtros")
        
        return response

    def test_ticket_detail(self):
        """Testa busca de ticket específico"""
        self.log("🔍 Testando busca de ticket específico...")
        
        # Teste com ID válido (assumindo que existe)
        response = self.test_endpoint("GET", "/tickets/1", description="Buscar ticket ID 1")
        
        # Teste com ID que não existe
        self.test_endpoint("GET", "/tickets/999", expected_status=404, description="Ticket inexistente")
        
        # Teste com ID inválido
        self.test_endpoint("GET", "/tickets/abc", expected_status=422, description="ID inválido")
        
        return response

    def test_ticket_update(self):
        """Testa atualização de tickets"""
        self.log("✏️ Testando atualização de tickets...")
        
        # Teste atualizar apenas status
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"status": "in_progress"}, 
                          description="Atualizar apenas status")
        
        # Teste atualizar apenas prioridade
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"priority": "urgent"}, 
                          description="Atualizar apenas prioridade")
        
        # Teste atualizar ambos
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"status": "resolved", "priority": "low"}, 
                          description="Atualizar status e prioridade")
        
        # Teste com dados inválidos
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"status": "invalid_status"}, 
                          expected_status=422, 
                          description="Status inválido")
        
        # Teste sem dados
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={}, 
                          expected_status=400, 
                          description="Body vazio")
        
        # Teste com ticket inexistente
        self.test_endpoint("PATCH", "/tickets/999", 
                          data={"status": "resolved"}, 
                          expected_status=404, 
                          description="Ticket inexistente")

    def test_metrics(self):
        """Testa endpoint de métricas"""
        self.log("📊 Testando métricas...")
        response = self.test_endpoint("GET", "/metrics", description="Buscar métricas processadas")
        return response

    def test_invalid_endpoints(self):
        """Testa endpoints que não existem"""
        self.log("🚫 Testando endpoints inválidos...")
        
        self.test_endpoint("GET", "/invalid", expected_status=404, description="Endpoint inexistente")
        self.test_endpoint("POST", "/tickets", expected_status=405, description="Método não permitido")
        self.test_endpoint("DELETE", "/tickets/1", expected_status=405, description="Método não permitido")

    def test_validation_errors(self):
        """Testa validações de parâmetros"""
        self.log("🔍 Testando validações...")
        
        # Parâmetros inválidos
        self.test_endpoint("GET", "/tickets?page=0", expected_status=422, description="Página inválida")
        self.test_endpoint("GET", "/tickets?page_size=200", expected_status=422, description="Page size muito grande")
        self.test_endpoint("GET", "/tickets?status=invalid", expected_status=422, description="Status inválido")
        self.test_endpoint("GET", "/tickets?priority=invalid", expected_status=422, description="Prioridade inválida")

    def run_all_tests(self):
        """Executa todos os testes"""
        self.log("🚀 Iniciando testes do backend FastAPI", "START")
        self.log(f"🌐 URL base: {self.base_url}")
        self.log("=" * 60)
        
        # Testes principais
        self.test_api_info()
        self.test_tickets_list()
        self.test_ticket_detail()
        self.test_ticket_update()
        self.test_metrics()
        
        # Testes de validação e erro
        self.test_invalid_endpoints()
        self.test_validation_errors()
        
        # Resumo
        self.print_summary()

    def print_summary(self):
        """Imprime resumo dos testes"""
        self.log("=" * 60)
        self.log("📋 RESUMO DOS TESTES", "SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total de testes: {total_tests}")
        self.log(f"✅ Passou: {passed_tests}")
        self.log(f"❌ Falhou: {failed_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        self.log(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if failed_tests > 0:
            self.log("\n❌ TESTES QUE FALHARAM:", "FAIL")
            for result in self.test_results:
                if not result["success"]:
                    self.log(f"   {result['method']} {result['endpoint']} - {result['description']}")
        
        self.log("=" * 60)
        
        if failed_tests == 0:
            self.log("🎉 Todos os testes passaram!", "SUCCESS")
            return True
        else:
            self.log(f"⚠️ {failed_tests} teste(s) falharam. Verifique o backend.", "WARNING")
            return False

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Testa todos os endpoints do backend FastAPI")
    parser.add_argument("--url", default=BASE_URL, help=f"URL base do backend (default: {BASE_URL})")
    parser.add_argument("--port", type=int, help="Porta do backend (sobrescreve URL)")
    
    args = parser.parse_args()
    
    # Se porta foi especificada, usar localhost com essa porta
    if args.port:
        base_url = f"http://localhost:{args.port}"
    else:
        base_url = args.url
    
    # Executar testes
    tester = BackendTester(base_url)
    success = tester.run_all_tests()
    
    # Exit code baseado no resultado
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
