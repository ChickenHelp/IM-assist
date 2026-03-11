"""Integration tests for the REST API."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "pitwall"


@pytest.mark.asyncio
async def test_auth_token(client):
    response = await client.post("/api/v1/auth/token?username=testuser&role=manager")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "manager"
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_me(client):
    # Get token
    response = await client.post("/api/v1/auth/token?username=testuser&role=strategist")
    token = response.json()["access_token"]

    # Use token
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "strategist"


@pytest.mark.asyncio
async def test_sessions_requires_auth(client):
    response = await client.get("/api/v1/sessions")
    # 401 Unauthorized — no token provided
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sessions_with_auth(client):
    # Get token with session:read permission
    response = await client.post("/api/v1/auth/token?username=testuser&role=manager")
    token = response.json()["access_token"]

    response = await client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_pit_window_calculation(client):
    # Get token
    response = await client.post("/api/v1/auth/token?username=testuser&role=strategist")
    token = response.json()["access_token"]

    response = await client.post(
        "/api/v1/strategy/pit-window",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_lap": 10,
            "total_laps": 50,
            "fuel_level": 25.0,
            "fuel_per_lap": 2.5,
            "tyre_wear_avg": 0.3,
            "tyre_wear_rate": 0.02,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "earliest_lap" in data
    assert "optimal_lap" in data
    assert "latest_lap" in data
    assert data["earliest_lap"] <= data["optimal_lap"] <= data["latest_lap"]


@pytest.mark.asyncio
async def test_undercut_simulation(client):
    # Get token
    response = await client.post("/api/v1/auth/token?username=testuser&role=strategist")
    token = response.json()["access_token"]

    response = await client.post(
        "/api/v1/strategy/undercut?gap_ahead=3.0",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_lap": 15,
            "total_laps": 50,
            "fuel_level": 50.0,
            "fuel_per_lap": 2.5,
            "tyre_wear_avg": 0.5,
            "tyre_wear_rate": 0.03,
            "pit_loss_seconds": 25.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "undercut"
    assert "risk_level" in data
    assert "time_delta" in data


@pytest.mark.asyncio
async def test_observer_cannot_write_strategy(client):
    # Observer should be able to read strategy but not in current implementation
    # they can only read telemetry and sessions
    response = await client.post("/api/v1/auth/token?username=observer&role=observer")
    token = response.json()["access_token"]

    response = await client.post(
        "/api/v1/strategy/pit-window",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_lap": 10,
            "total_laps": 50,
            "fuel_level": 25.0,
            "fuel_per_lap": 2.5,
            "tyre_wear_avg": 0.3,
            "tyre_wear_rate": 0.02,
        },
    )
    # Observer lacks strategy:read permission
    assert response.status_code == 403
