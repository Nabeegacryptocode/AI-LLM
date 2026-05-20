# Testing Guide - IBM Docs LLM

Comprehensive guide for testing the IBM Documentation LLM system.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

## Overview

The testing suite provides comprehensive coverage of:
- API endpoints
- Service layer components
- Integration workflows
- Performance characteristics
- Security features
- WordPress integration

### Test Framework

- **pytest**: Main testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **httpx**: HTTP client for API testing
- **unittest.mock**: Mocking external services

## Test Structure

```
backend/tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_api_endpoints.py    # API endpoint tests
├── test_services.py         # Service layer tests
└── test_integration.py      # End-to-end integration tests
```

### Key Files

**conftest.py**: Shared test fixtures
- `client`: FastAPI test client
- `auth_headers`: Authentication headers
- `mock_openai`: Mocked OpenAI API
- `mock_pinecone`: Mocked Pinecone API
- `sample_documents`: Test documents
- `sample_questions`: Test questions

**pytest.ini**: Pytest configuration
- Test discovery patterns
- Markers for test categorization
- Async test configuration

## Running Tests

### Prerequisites

```bash
# Install test dependencies
cd backend
pip install -r requirements-test.txt

# Set up test environment
cp .env.example .env.test
# Edit .env.test with test credentials
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with very verbose output
pytest -vv

# Run specific test file
pytest tests/test_api_endpoints.py

# Run specific test class
pytest tests/test_api_endpoints.py::TestChatEndpoint

# Run specific test
pytest tests/test_api_endpoints.py::TestChatEndpoint::test_chat_success
```

### Using the Test Runner Script

```bash
# Run all tests
python scripts/run_tests.py

# Run with coverage
python scripts/run_tests.py --coverage

# Run specific marker
python scripts/run_tests.py -m unit
python scripts/run_tests.py -m integration

# Run tests matching pattern
python scripts/run_tests.py -k "test_chat"

# Run specific file
python scripts/run_tests.py -f tests/test_api_endpoints.py

# Fail fast (stop on first failure)
python scripts/run_tests.py -x

# Show print statements
python scripts/run_tests.py -s

# Run in parallel (requires pytest-xdist)
python scripts/run_tests.py -n 4
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=app --cov=services --cov=scraper --cov-report=html --cov-report=term-missing

# View HTML report
# Open htmlcov/index.html in browser

# Generate XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

## Test Categories

### Unit Tests

Test individual components in isolation.

```bash
# Run unit tests only
pytest -m unit
```

**Examples:**
- Service initialization
- Data validation
- Utility functions
- Configuration loading

### Integration Tests

Test interactions between components.

```bash
# Run integration tests only
pytest -m integration
```

**Examples:**
- Complete RAG pipeline
- Multi-turn conversations
- Error recovery
- WordPress integration

### API Tests

Test HTTP endpoints.

```bash
# Run API tests
pytest tests/test_api_endpoints.py
```

**Coverage:**
- Health check endpoint
- Chat endpoint (with/without auth)
- Ingest endpoint
- Metrics endpoints
- CORS headers
- Rate limiting
- Error handling

### Service Tests

Test service layer components.

```bash
# Run service tests
pytest tests/test_services.py
```

**Coverage:**
- Vector service (Pinecone)
- Embedding service (OpenAI)
- RAG service
- Monitoring service
- Document processor

### Performance Tests

Test performance characteristics.

```bash
# Run performance tests
pytest -m slow tests/test_integration.py::TestPerformance
```

**Coverage:**
- Response time
- Concurrent requests
- Large document ingestion
- Memory usage

## Writing Tests

### Basic Test Structure

```python
import pytest
from fastapi import status


class TestMyFeature:
    """Test my feature"""
    
    def test_basic_functionality(self, client, auth_headers):
        """Test basic functionality"""
        response = client.post(
            "/api/endpoint",
            json={"data": "value"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "expected_key" in response.json()
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function(self, mock_openai, mock_pinecone):
    """Test async function"""
    from services.rag_service import RAGService
    
    service = RAGService()
    result = await service.generate_answer("Test question")
    
    assert "answer" in result
```

### Using Fixtures

```python
def test_with_fixtures(self, client, auth_headers, sample_documents):
    """Test using multiple fixtures"""
    response = client.post(
        "/api/ingest",
        json={"documents": sample_documents},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

def test_with_mock(self):
    """Test with custom mock"""
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))]
        )
        
        # Your test code here
```

### Parametrized Tests

```python
@pytest.mark.parametrize("question,expected", [
    ("What is IBM Cloud?", "cloud platform"),
    ("How to deploy?", "deployment"),
    ("Pricing info?", "pricing"),
])
def test_multiple_questions(self, client, auth_headers, question, expected):
    """Test multiple questions"""
    response = client.post(
        "/api/chat",
        json={"question": question},
        headers=auth_headers
    )
    
    assert expected.lower() in response.json()["answer"].lower()
```

### Test Markers

```python
@pytest.mark.unit
def test_unit_function():
    """Unit test"""
    pass

@pytest.mark.integration
def test_integration_workflow():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test"""
    pass
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
        API_KEY: ${{ secrets.API_KEY }}
      run: |
        cd backend
        pytest --cov=app --cov=services --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.11
  stage: test
  script:
    - cd backend
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
    - pytest --cov=app --cov=services --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running tests before commit..."

cd backend
pytest -x -q

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Tests passed. Proceeding with commit."
```

```bash
# Make executable
chmod +x .git/hooks/pre-commit
```

## Test Data Management

### Sample Data

```python
# In conftest.py
@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "id": "doc1",
            "text": "IBM Cloud provides infrastructure services.",
            "metadata": {
                "source": "https://cloud.ibm.com/docs",
                "title": "IBM Cloud Overview"
            }
        }
    ]
```

### Test Database

For integration tests requiring real data:

```python
@pytest.fixture(scope="session")
def test_vector_db():
    """Set up test vector database"""
    # Create test index
    # Populate with test data
    yield
    # Clean up
```

## Best Practices

### 1. Test Isolation

Each test should be independent:

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test"""
    # Reset metrics
    # Clear caches
    yield
    # Cleanup
```

### 2. Descriptive Names

```python
def test_chat_endpoint_returns_error_when_question_is_empty():
    """Clear, descriptive test name"""
    pass
```

### 3. Arrange-Act-Assert

```python
def test_example(self, client, auth_headers):
    # Arrange
    data = {"question": "Test"}
    
    # Act
    response = client.post("/api/chat", json=data, headers=auth_headers)
    
    # Assert
    assert response.status_code == 200
```

### 4. Test Edge Cases

```python
def test_empty_input(self):
    """Test with empty input"""
    pass

def test_very_long_input(self):
    """Test with very long input"""
    pass

def test_special_characters(self):
    """Test with special characters"""
    pass
```

### 5. Mock External Services

Always mock external API calls:

```python
@pytest.fixture
def mock_openai():
    """Mock OpenAI to avoid real API calls"""
    with patch('openai.OpenAI') as mock:
        # Configure mock
        yield mock
```

## Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Ensure backend directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Or use pytest's pythonpath
pytest --pythonpath=backend
```

**2. Async Test Failures**

```python
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Use asyncio marker
@pytest.mark.asyncio
async def test_async():
    pass
```

**3. Fixture Not Found**

```python
# Ensure conftest.py is in tests directory
# Check fixture scope
@pytest.fixture(scope="function")  # or "session", "module"
def my_fixture():
    pass
```

**4. Mock Not Working**

```python
# Use correct import path
with patch('app.services.openai_service.OpenAI') as mock:
    # Not 'openai.OpenAI' if imported differently
    pass
```

**5. Tests Pass Locally But Fail in CI**

- Check environment variables
- Verify Python version
- Check dependency versions
- Review CI logs carefully

### Debug Mode

```bash
# Run with debug output
pytest -vv -s --log-cli-level=DEBUG

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Verbose Output

```bash
# Show all output
pytest -vv -s

# Show only failures
pytest --tb=short

# Show full traceback
pytest --tb=long
```

## Performance Testing

### Load Testing

```python
import concurrent.futures

def test_concurrent_load(self, client, auth_headers):
    """Test system under load"""
    def make_request():
        return client.post("/api/chat", json={"question": "Test"}, headers=auth_headers)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in futures]
    
    success_count = sum(1 for r in results if r.status_code == 200)
    assert success_count >= 95  # 95% success rate
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run with memory profiling
pytest --memprof tests/test_integration.py
```

## Continuous Improvement

### Coverage Goals

- **Overall**: 80%+ coverage
- **Critical paths**: 95%+ coverage
- **API endpoints**: 100% coverage

### Regular Reviews

- Review test failures weekly
- Update tests with new features
- Remove obsolete tests
- Refactor slow tests

### Metrics to Track

- Test execution time
- Coverage percentage
- Flaky test rate
- Test maintenance burden

---

**Happy Testing!** 🧪

For questions or issues, refer to the main documentation or open an issue.