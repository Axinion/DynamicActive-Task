"""
Test health and version endpoints for K12 LMS API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthAndVersion:
    """Test health check and version endpoints."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns OK status."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "API is running"
    
    def test_version_endpoint(self):
        """Test that the version endpoint returns version information."""
        response = client.get("/api/version")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "version" in data
        assert "buildTime" in data
        assert "environment" in data
        
        # Check version format
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
        
        # Check build time format (should be ISO format or "unknown")
        assert isinstance(data["buildTime"], str)
        assert len(data["buildTime"]) > 0
        
        # Check environment
        assert data["environment"] in ["development", "production", "testing"]
    
    def test_root_endpoint(self):
        """Test that the root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome to K12 LMS API" in data["message"]
    
    def test_health_endpoint_response_time(self):
        """Test that health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/api/health")
        end_time = time.time()
        
        assert response.status_code == 200
        # Should respond within 1 second
        assert (end_time - start_time) < 1.0
    
    def test_version_endpoint_response_time(self):
        """Test that version endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/api/version")
        end_time = time.time()
        
        assert response.status_code == 200
        # Should respond within 1 second
        assert (end_time - start_time) < 1.0
    
    def test_health_endpoint_headers(self):
        """Test that health endpoint returns proper headers."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    def test_version_endpoint_headers(self):
        """Test that version endpoint returns proper headers."""
        response = client.get("/api/version")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    def test_health_endpoint_methods(self):
        """Test that health endpoint only accepts GET requests."""
        # GET should work
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # POST should not work
        response = client.post("/api/health")
        assert response.status_code == 405  # Method Not Allowed
        
        # PUT should not work
        response = client.put("/api/health")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_version_endpoint_methods(self):
        """Test that version endpoint only accepts GET requests."""
        # GET should work
        response = client.get("/api/version")
        assert response.status_code == 200
        
        # POST should not work
        response = client.post("/api/version")
        assert response.status_code == 405  # Method Not Allowed
        
        # PUT should not work
        response = client.put("/api/version")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_health_endpoint_concurrent_requests(self):
        """Test that health endpoint handles concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/api/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(e)
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(status == 200 for status in results)
    
    def test_version_endpoint_concurrent_requests(self):
        """Test that version endpoint handles concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/api/version")
                results.append(response.status_code)
            except Exception as e:
                errors.append(e)
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(status == 200 for status in results)
