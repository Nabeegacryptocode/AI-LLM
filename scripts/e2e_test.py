"""
End-to-end test script for Fahm Faris system
Tests the complete workflow from deployment to query
"""
import requests
import time
import sys
from typing import Dict, List
import json


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


class E2ETest:
    """End-to-end test runner"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.results = []
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")
    
    def print_test(self, name: str, passed: bool, message: str = ""):
        """Print test result"""
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {name}")
        if message:
            print(f"  {Colors.YELLOW}{message}{Colors.END}")
        self.results.append({"name": name, "passed": passed, "message": message})
    
    def test_health_check(self) -> bool:
        """Test 1: Health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.print_test("Health Check", False, f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("status") != "healthy":
                self.print_test("Health Check", False, f"Status: {data.get('status')}")
                return False
            
            self.print_test("Health Check", True, "API is healthy")
            return True
            
        except Exception as e:
            self.print_test("Health Check", False, str(e))
            return False
    
    def test_authentication(self) -> bool:
        """Test 2: Authentication"""
        try:
            # Test without auth
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={"question": "Test"},
                timeout=10
            )
            
            if response.status_code != 401:
                self.print_test("Authentication - No Auth", False, "Should return 401")
                return False
            
            # Test with invalid auth
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={"question": "Test"},
                headers={"Authorization": "Bearer invalid"},
                timeout=10
            )
            
            if response.status_code != 401:
                self.print_test("Authentication - Invalid Auth", False, "Should return 401")
                return False
            
            self.print_test("Authentication", True, "Auth validation working")
            return True
            
        except Exception as e:
            self.print_test("Authentication", False, str(e))
            return False
    
    def test_document_ingestion(self) -> bool:
        """Test 3: Document ingestion"""
        try:
            documents = [
                {
                    "id": "test-doc-1",
                    "text": "IBM Cloud is a comprehensive cloud computing platform that provides infrastructure, platform, and software services.",
                    "metadata": {
                        "source": "https://cloud.ibm.com/docs",
                        "title": "IBM Cloud Overview",
                        "section": "overview"
                    }
                },
                {
                    "id": "test-doc-2",
                    "text": "Kubernetes on IBM Cloud provides a managed container orchestration service for deploying containerized applications.",
                    "metadata": {
                        "source": "https://cloud.ibm.com/docs/containers",
                        "title": "Kubernetes Service",
                        "section": "containers"
                    }
                }
            ]
            
            response = requests.post(
                f"{self.api_url}/api/ingest",
                json={"documents": documents},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self.print_test("Document Ingestion", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("ingested_count") != len(documents):
                self.print_test("Document Ingestion", False, f"Expected {len(documents)}, got {data.get('ingested_count')}")
                return False
            
            self.print_test("Document Ingestion", True, f"Ingested {len(documents)} documents")
            return True
            
        except Exception as e:
            self.print_test("Document Ingestion", False, str(e))
            return False
    
    def test_chat_query(self) -> bool:
        """Test 4: Chat query"""
        try:
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={"question": "What is IBM Cloud?"},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self.print_test("Chat Query", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            
            required_fields = ["answer", "sources", "metadata"]
            for field in required_fields:
                if field not in data:
                    self.print_test("Chat Query", False, f"Missing field: {field}")
                    return False
            
            if not data["answer"]:
                self.print_test("Chat Query", False, "Empty answer")
                return False
            
            self.print_test("Chat Query", True, f"Answer length: {len(data['answer'])} chars")
            return True
            
        except Exception as e:
            self.print_test("Chat Query", False, str(e))
            return False
    
    def test_source_attribution(self) -> bool:
        """Test 5: Source attribution"""
        try:
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={"question": "Tell me about Kubernetes on IBM Cloud"},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self.print_test("Source Attribution", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            sources = data.get("sources", [])
            
            if not sources:
                self.print_test("Source Attribution", False, "No sources returned")
                return False
            
            # Check source structure
            for source in sources:
                required = ["url", "title", "relevance_score"]
                if not all(field in source for field in required):
                    self.print_test("Source Attribution", False, "Invalid source structure")
                    return False
            
            self.print_test("Source Attribution", True, f"Found {len(sources)} sources")
            return True
            
        except Exception as e:
            self.print_test("Source Attribution", False, str(e))
            return False
    
    def test_conversation_context(self) -> bool:
        """Test 6: Conversation context"""
        try:
            conversation_id = "e2e-test-conv"
            
            # First question
            response1 = requests.post(
                f"{self.api_url}/api/chat",
                json={
                    "question": "What is IBM Cloud?",
                    "conversation_id": conversation_id
                },
                headers=self.headers,
                timeout=30
            )
            
            if response1.status_code != 200:
                self.print_test("Conversation Context", False, "First query failed")
                return False
            
            # Follow-up question
            response2 = requests.post(
                f"{self.api_url}/api/chat",
                json={
                    "question": "What services does it provide?",
                    "conversation_id": conversation_id
                },
                headers=self.headers,
                timeout=30
            )
            
            if response2.status_code != 200:
                self.print_test("Conversation Context", False, "Follow-up query failed")
                return False
            
            data1 = response1.json()
            data2 = response2.json()
            
            if data1["metadata"]["conversation_id"] != data2["metadata"]["conversation_id"]:
                self.print_test("Conversation Context", False, "Conversation ID mismatch")
                return False
            
            self.print_test("Conversation Context", True, "Multi-turn conversation working")
            return True
            
        except Exception as e:
            self.print_test("Conversation Context", False, str(e))
            return False
    
    def test_metrics_tracking(self) -> bool:
        """Test 7: Metrics tracking"""
        try:
            response = requests.get(
                f"{self.api_url}/api/metrics/summary",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                self.print_test("Metrics Tracking", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            
            required_fields = ["total_queries", "success_rate"]
            for field in required_fields:
                if field not in data:
                    self.print_test("Metrics Tracking", False, f"Missing field: {field}")
                    return False
            
            self.print_test("Metrics Tracking", True, f"Queries: {data['total_queries']}, Success: {data['success_rate']:.1%}")
            return True
            
        except Exception as e:
            self.print_test("Metrics Tracking", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Test 8: Error handling"""
        try:
            # Test with empty question
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={"question": ""},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code not in [400, 422]:
                self.print_test("Error Handling - Empty Question", False, f"Status: {response.status_code}")
                return False
            
            # Test with missing question
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code not in [400, 422]:
                self.print_test("Error Handling - Missing Question", False, f"Status: {response.status_code}")
                return False
            
            self.print_test("Error Handling", True, "Validation working correctly")
            return True
            
        except Exception as e:
            self.print_test("Error Handling", False, str(e))
            return False
    
    def test_performance(self) -> bool:
        """Test 9: Performance"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={"question": "What is IBM Cloud?"},
                headers=self.headers,
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code != 200:
                self.print_test("Performance", False, f"Status: {response.status_code}")
                return False
            
            if response_time > 10.0:
                self.print_test("Performance", False, f"Too slow: {response_time:.2f}s")
                return False
            
            self.print_test("Performance", True, f"Response time: {response_time:.2f}s")
            return True
            
        except Exception as e:
            self.print_test("Performance", False, str(e))
            return False
    
    def test_cors_headers(self) -> bool:
        """Test 10: CORS headers"""
        try:
            response = requests.options(
                f"{self.api_url}/api/health",
                headers={"Origin": "https://example.com"},
                timeout=10
            )
            
            if "access-control-allow-origin" not in response.headers:
                self.print_test("CORS Headers", False, "Missing CORS headers")
                return False
            
            self.print_test("CORS Headers", True, "CORS configured correctly")
            return True
            
        except Exception as e:
            self.print_test("CORS Headers", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("Fahm Faris - End-to-End Test Suite")
        
        print(f"API URL: {self.api_url}")
        print(f"Testing started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Document Ingestion", self.test_document_ingestion),
            ("Chat Query", self.test_chat_query),
            ("Source Attribution", self.test_source_attribution),
            ("Conversation Context", self.test_conversation_context),
            ("Metrics Tracking", self.test_metrics_tracking),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("CORS Headers", self.test_cors_headers),
        ]
        
        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.print_test(name, False, f"Unexpected error: {str(e)}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        print(f"Success Rate: {(passed/total)*100:.1f}%\n")
        
        if failed > 0:
            print(f"{Colors.RED}Failed Tests:{Colors.END}")
            for result in self.results:
                if not result["passed"]:
                    print(f"  - {result['name']}: {result['message']}")
            print()
        
        if passed == total:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! System is ready for production.{Colors.END}\n")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Some tests failed. Please review and fix issues.{Colors.END}\n")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run end-to-end tests for Fahm Faris")
    parser.add_argument("--api-url", required=True, help="API URL (e.g., https://api.example.com)")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    
    args = parser.parse_args()
    
    tester = E2ETest(args.api_url, args.api_key)
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

# Made with Bob
