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
    assert "VeriPulse" in data["service"]
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
async def test_phone_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/v1/phone/validate?phone=+14155552671")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert "carrier" in data

@pytest.mark.anyio
async def test_unified_trust_score_disposable_and_voip():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/v1/trust-score",
            json={"email": "bot@10minutemail.com", "phone": "+14155552671"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "trust_score" in data
    assert "risk_score" in data
    assert data["risk_level"] in ["HIGH", "MEDIUM"]
    assert data["email_intelligence"] is not None
    assert data["phone_intelligence"] is not None

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
