import pytest
from fastapi import status

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

def test_get_customers(client):
    """Test the customers endpoint."""
    response = client.get("/customers")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

def test_get_operators(client):
    """Test the operators endpoint."""
    response = client.get("/operators")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

def test_get_medicines(client):
    """Test the medicines endpoint."""
    response = client.get("/medicines")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

def test_get_purchases(client):
    """Test the purchases endpoint."""
    response = client.get("/purchases")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"] 