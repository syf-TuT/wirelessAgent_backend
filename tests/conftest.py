"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_user_request():
    """Sample user request data."""
    return {
        "user_id": "test-001",
        "location": {"x": 75.64, "y": 182.46, "z": 1.5},
        "request_text": "I need to stream 4K video",
        "cqi": 12,
        "ground_truth": "eMBB"
    }


@pytest.fixture
def sample_allocation_result():
    """Sample allocation result."""
    return {
        "user_id": "test-001",
        "request_id": "req-001",
        "slice_type": "eMBB",
        "status": "success",
        "resources": {
            "bandwidth": 15.0,
            "rate": 129.58,
            "latency": 50.0
        }
    }
