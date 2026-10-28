"""
Automated Pytest Suite: Flask Web Routes, Templates, and REST Endpoints.
"""
import pytest
from app import app

@pytest.fixture
def client():
    """Provides Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_page_routes_render(client):
    """Ensures all 8 required web pages render successfully with HTTP 200."""
    routes = [
        "/",
        "/dashboard",
        "/manufacturers",
        "/battery-analysis",
        "/geography",
        "/story",
        "/methodology",
        "/about"
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Route {route} failed with status {response.status_code}"
        assert b"EVMarket" in response.data or b"Electric Vehicle" in response.data

def test_api_endpoints_return_json(client):
    """Verifies that all AJAX/REST endpoints return valid JSON structures."""
    endpoints = [
        "/api/kpis?year=2024",
        "/api/sales-trend",
        "/api/manufacturer-ranking?year=2024&limit=5",
        "/api/category-breakdown?year=2024",
        "/api/battery-tech",
        "/api/scatter-battery-range",
        "/api/geography-data",
        "/api/customer-ratings",
        "/api/vehicles?category=SUV"
    ]
    for ep in endpoints:
        response = client.get(ep)
        assert response.status_code == 200, f"API {ep} returned {response.status_code}"
        assert response.is_json

def test_404_error_handler(client):
    """Verifies custom 404 handler for nonexistent URLs."""
    response = client.get("/nonexistent-page-url")
    assert response.status_code == 404
    assert b"404" in response.data
