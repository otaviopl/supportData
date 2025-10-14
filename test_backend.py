#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

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
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            success = response.status_code == expected_status
            status_icon = "PASS" if success else "FAIL"
            
            self.log(f"{status_icon} {method} {endpoint} - Status: {response.status_code} (expected: {expected_status})", 
                    "PASS" if success else "FAIL")
            
            if description:
                self.log(f"   {description}")
            
            try:
                json_data = response.json()
                if success and json_data:
                    self.log(f"   Response: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}...")
            except:
                self.log(f"   Response (text): {response.text[:100]}...")
            
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
            self.log(f"FAIL {method} {endpoint} - ERROR: Cannot connect to server", "ERROR")
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status_code": None,
                "expected": expected_status,
                "success": False,
                "description": f"ERROR: {description}"
            })
            return None
        except Exception as e:
            self.log(f"FAIL {method} {endpoint} - ERROR: {str(e)}", "ERROR")
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status_code": None,
                "expected": expected_status,
                "success": False,
                "description": f"ERROR: {description}"
            })
            return None

    def test_api_info(self):
        self.log("Testing API info...")
        response = self.test_endpoint("GET", "/", description="Basic API info")
        return response

    def test_tickets_list(self):
        self.log("Testing ticket listing...")
        
        response = self.test_endpoint("GET", "/tickets", description="List all tickets")
        if not response:
            return None
            
        self.test_endpoint("GET", "/tickets?page=1&page_size=5", description="With pagination")
        self.test_endpoint("GET", "/tickets?status=open", description="Filter by status")
        self.test_endpoint("GET", "/tickets?priority=high", description="Filter by priority")
        self.test_endpoint("GET", "/tickets?channel=email", description="Filter by channel")
        self.test_endpoint("GET", "/tickets?q=erro", description="Search by text")
        self.test_endpoint("GET", "/tickets?status=open&priority=high&page=1&page_size=3", 
                          description="Multiple filters")
        
        return response

    def test_ticket_detail(self):
        self.log("Testing specific ticket search...")
        
        response = self.test_endpoint("GET", "/tickets/1", description="Get ticket ID 1")
        self.test_endpoint("GET", "/tickets/999", expected_status=404, description="Non-existent ticket")
        self.test_endpoint("GET", "/tickets/abc", expected_status=422, description="Invalid ID")
        
        return response

    def test_ticket_update(self):
        self.log("Testing ticket updates...")
        
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"status": "in_progress"}, 
                          description="Update status only")
        
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"priority": "urgent"}, 
                          description="Update priority only")
        
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"status": "resolved", "priority": "low"}, 
                          description="Update both")
        
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={"status": "invalid_status"}, 
                          expected_status=422, 
                          description="Invalid status")
        
        self.test_endpoint("PATCH", "/tickets/1", 
                          data={}, 
                          expected_status=400, 
                          description="Empty body")
        
        self.test_endpoint("PATCH", "/tickets/999", 
                          data={"status": "resolved"}, 
                          expected_status=404, 
                          description="Non-existent ticket")

    def test_metrics(self):
        self.log("Testing metrics...")
        response = self.test_endpoint("GET", "/metrics", description="Get processed metrics")
        return response

    def test_invalid_endpoints(self):
        self.log("Testing invalid endpoints...")
        
        self.test_endpoint("GET", "/invalid", expected_status=404, description="Non-existent endpoint")
        self.test_endpoint("POST", "/tickets", expected_status=405, description="Method not allowed")
        self.test_endpoint("DELETE", "/tickets/1", expected_status=405, description="Method not allowed")

    def test_validation_errors(self):
        self.log("Testing validation...")
        
        self.test_endpoint("GET", "/tickets?page=0", expected_status=422, description="Invalid page")
        self.test_endpoint("GET", "/tickets?page_size=200", expected_status=422, description="Page size too large")
        self.test_endpoint("GET", "/tickets?status=invalid", expected_status=422, description="Invalid status")
        self.test_endpoint("GET", "/tickets?priority=invalid", expected_status=422, description="Invalid priority")

    def run_all_tests(self):
        self.log("Starting FastAPI backend tests", "START")
        self.log(f"Base URL: {self.base_url}")
        self.log("=" * 60)
        
        self.test_api_info()
        self.test_tickets_list()
        self.test_ticket_detail()
        self.test_ticket_update()
        self.test_metrics()
        self.test_invalid_endpoints()
        self.test_validation_errors()
        self.print_summary()

    def print_summary(self):
        self.log("=" * 60)
        self.log("TEST SUMMARY", "SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total tests: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {failed_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        self.log(f"Success rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            self.log("\nFAILED TESTS:", "FAIL")
            for result in self.test_results:
                if not result["success"]:
                    self.log(f"   {result['method']} {result['endpoint']} - {result['description']}")
        
        self.log("=" * 60)
        
        if failed_tests == 0:
            self.log("All tests passed!", "SUCCESS")
            return True
        else:
            self.log(f"{failed_tests} test(s) failed. Check backend.", "WARNING")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test all FastAPI backend endpoints")
    parser.add_argument("--url", default=BASE_URL, help=f"Backend base URL (default: {BASE_URL})")
    parser.add_argument("--port", type=int, help="Backend port (overrides URL)")
    
    args = parser.parse_args()
    
    if args.port:
        base_url = f"http://localhost:{args.port}"
    else:
        base_url = args.url
    
    tester = BackendTester(base_url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()