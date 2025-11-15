"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestJobEndpoints:
    """Test cases for job analysis endpoints."""
    
    def test_analyze_job_with_description(self, client: TestClient, sample_job_description):
        """Test job analysis with description."""
        response = client.post(
            "/api/v1/jobs/analyze",
            json={"job_description": sample_job_description}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "processing_time" in data
        assert data["data"]["title"] is not None
        assert len(data["data"]["requirements"]["skills"]) > 0
    
    def test_analyze_job_with_url(self, client: TestClient, sample_job_url):
        """Test job analysis with URL."""
        response = client.post(
            "/api/v1/jobs/analyze",
            json={"job_url": sample_job_url}
        )
        
        # This might fail due to web scraping, but should not return 500
        assert response.status_code in [200, 400, 422]
    
    def test_analyze_job_no_input(self, client: TestClient):
        """Test job analysis with no input."""
        response = client.post("/api/v1/jobs/analyze", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_get_job_analysis_not_found(self, client: TestClient):
        """Test getting non-existent job analysis."""
        response = client.get("/api/v1/jobs/non_existent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "JOB_NOT_FOUND"
    
    def test_list_job_analyses(self, client: TestClient):
        """Test listing job analyses."""
        response = client.get("/api/v1/jobs/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCVEndpoints:
    """Test cases for CV analysis endpoints."""
    
    def test_analyze_cv_success(self, client: TestClient, sample_cv_content):
        """Test successful CV analysis."""
        files = {"file": ("test_cv.pdf", sample_cv_content, "application/pdf")}
        
        response = client.post("/api/v1/cv/analyze", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "processing_time" in data
        assert data["data"]["cv_id"] is not None
        assert len(data["data"]["skills"]["technical"]) > 0
    
    def test_analyze_cv_no_file(self, client: TestClient):
        """Test CV analysis with no file."""
        response = client.post("/api/v1/cv/analyze")
        
        assert response.status_code == 422
    
    def test_analyze_cv_invalid_file_type(self, client: TestClient):
        """Test CV analysis with invalid file type."""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        
        response = client.post("/api/v1/cv/analyze", files=files)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "Unsupported file type" in data["error"]["message"]
    
    def test_optimize_cv(self, client: TestClient, mock_cv_analysis, mock_job_analysis):
        """Test CV optimization."""
        request_data = {
            "cv_analysis": mock_cv_analysis,
            "job_requirements": mock_job_analysis["requirements"]
        }
        
        response = client.post("/api/v1/cv/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "job_match_score" in data
        assert "strengths" in data
        assert "improvements" in data
        assert "missing_requirements" in data
    
    def test_get_cv_analysis_not_found(self, client: TestClient):
        """Test getting non-existent CV analysis."""
        response = client.get("/api/v1/cv/non_existent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "CV_NOT_FOUND"
    
    def test_list_cv_analyses(self, client: TestClient):
        """Test listing CV analyses."""
        response = client.get("/api/v1/cv/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestDiscordEndpoints:
    """Test cases for Discord integration endpoints."""
    
    def test_send_discord_webhook(self, client: TestClient, sample_discord_webhook_url):
        """Test sending Discord webhook."""
        request_data = {
            "webhook_url": sample_discord_webhook_url,
            "message": {
                "content": "Test message",
                "username": "Test Bot"
            }
        }
        
        response = client.post("/api/v1/discord/webhook", json=request_data)
        
        # This might fail due to network, but should not return 500
        assert response.status_code in [200, 400, 422]
    
    def test_send_discord_webhook_invalid_url(self, client: TestClient):
        """Test sending Discord webhook with invalid URL."""
        request_data = {
            "webhook_url": "https://invalid-url.com",
            "message": {
                "content": "Test message",
                "username": "Test Bot"
            }
        }
        
        response = client.post("/api/v1/discord/webhook", json=request_data)
        
        assert response.status_code in [400, 422]
    
    def test_send_job_analysis_to_discord(self, client: TestClient, sample_discord_webhook_url, mock_job_analysis):
        """Test sending job analysis to Discord."""
        request_data = {
            "webhook_url": sample_discord_webhook_url,
            "job_analysis_data": mock_job_analysis
        }
        
        response = client.post("/api/v1/discord/job-analysis", json=request_data)
        
        # This might fail due to network, but should not return 500
        assert response.status_code in [200, 400, 422]
    
    def test_send_cv_optimization_to_discord(self, client: TestClient, sample_discord_webhook_url, mock_cv_optimization):
        """Test sending CV optimization to Discord."""
        request_data = {
            "webhook_url": sample_discord_webhook_url,
            "cv_optimization_data": mock_cv_optimization
        }
        
        response = client.post("/api/v1/discord/cv-optimization", json=request_data)
        
        # This might fail due to network, but should not return 500
        assert response.status_code in [200, 400, 422]


class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime" in data
    
    def test_readiness_check(self, client: TestClient):
        """Test readiness check endpoint."""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
    
    def test_liveness_check(self, client: TestClient):
        """Test liveness check endpoint."""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_metrics(self, client: TestClient):
        """Test metrics endpoint."""
        response = client.get("/api/v1/health/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "timestamp" in data
        assert "total_requests" in data["metrics"]
        assert "successful_requests" in data["metrics"]


class TestRootEndpoints:
    """Test cases for root endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
        assert "health_url" in data
    
    def test_simple_health_check(self, client: TestClient):
        """Test simple health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client: TestClient):
        """Test 404 error handling."""
        response = client.get("/api/v1/non_existent_endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test method not allowed error."""
        response = client.delete("/api/v1/health/")
        
        assert response.status_code == 405
    
    def test_rate_limiting(self, client: TestClient, sample_job_description):
        """Test rate limiting."""
        # Make multiple requests quickly
        for _ in range(15):  # Exceed the rate limit
            response = client.post(
                "/api/v1/jobs/analyze",
                json={"job_description": sample_job_description}
            )
            
            if response.status_code == 429:
                break
        
        # At least one request should be rate limited
        assert response.status_code == 429
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "RATE_LIMIT_ERROR"