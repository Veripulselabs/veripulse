"""
Integration tests for VeriPulse FastAPI endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.anyio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.anyio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "VeriPulse API"
    assert "endpoints" in data

@pytest.mark.anyio
async def test_verify_disposable_email():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/v1/verify?email=spammer@10minutemail.com")
    assert response.status_code == 200
    data = response.json()
    assert data["is_disposable"] is True
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert data["recommended_action"] == "BLOCK"

@pytest.mark.anyio
async def test_verify_invalid_syntax():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/v1/verify?email=invalid-address")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["is_syntax_valid"] is False
    assert data["risk_score"] == 100

@pytest.mark.anyio
async def test_verify_batch():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/v1/verify-batch",
            json={"emails": ["test@google.com", "fake@10minutemail.com"]}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2
