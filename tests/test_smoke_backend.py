#!/usr/bin/env python3
"""
Smoke tests for the K12 LMS backend API.
These tests verify that the basic API endpoints are working.
"""

import sys
import os
import pytest
import httpx
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the health endpoint returns 200 with correct status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data


def test_root_endpoint():
    """Test that the root endpoint returns a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "K12 LMS" in data["message"]


def test_auth_login_endpoint_exists():
    """Test that the login endpoint exists and accepts POST requests."""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    # Should return 401 for invalid credentials, not 404
    assert response.status_code == 401


def test_classes_endpoint_requires_auth():
    """Test that the classes endpoint requires authentication."""
    response = client.get("/api/classes")
    assert response.status_code == 401


def test_lessons_endpoint_requires_auth():
    """Test that the lessons endpoint requires authentication."""
    response = client.get("/api/lessons")
    assert response.status_code == 401


def test_assignments_endpoint_requires_auth():
    """Test that the assignments endpoint requires authentication."""
    response = client.get("/api/assignments")
    assert response.status_code == 401


def test_grading_endpoint_requires_auth():
    """Test that the grading endpoint requires authentication."""
    response = client.post("/api/grading/short-answer", json={
        "question_id": 1,
        "student_answer": "test answer"
    })
    assert response.status_code == 401


def test_recommendations_endpoint_requires_auth():
    """Test that the recommendations endpoint requires authentication."""
    response = client.get("/api/recommendations")
    assert response.status_code == 401


def test_cors_headers():
    """Test that CORS headers are properly set."""
    response = client.options("/api/health")
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


def test_api_documentation_accessible():
    """Test that the API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema_accessible():
    """Test that the OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "K12 LMS API"
    assert data["info"]["version"] == "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
