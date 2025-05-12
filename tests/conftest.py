import pytest
from fastapi.testclient import TestClient
from api.api import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def test_headers():
    """Create test headers for authenticated requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    } 