import time
from unittest.mock import AsyncMock, patch

import redis
import pytest
from fastapi.testclient import TestClient

from app.main import app


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(
        app,
        client=("192.0.2.1", 12345),
    ) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_rate_limits():
    redis_client.delete(
        "rate_limit:token_bucket:192.0.2.1"
    )
    yield
    redis_client.delete(
        "rate_limit:token_bucket:192.0.2.1"
    )


def test_submit_rate_limit(client):
    for i in range(5):
        response = client.post("/api/submit")

        assert response.status_code == 200
        assert response.json()["tokens_remaining"] == 4 - i

    response = client.post("/api/submit")

    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"


def test_token_bucket_refills(client):
    key = "rate_limit:token_bucket:192.0.2.1"
    old_timestamp = time.time() - 61

    redis_client.hset(
        key,
        mapping={
            "tokens": 0,
            "timestamp": old_timestamp,
        },
    )

    response = client.post("/api/submit")

    assert response.status_code == 200
    assert response.json()["tokens_remaining"] == 4


def test_submit_separate_ip_limits(client):
    for _ in range(5):
        response = client.post("/api/submit")
        assert response.status_code == 200

    response = client.post("/api/submit")
    assert response.status_code == 429

    with TestClient(
        app,
        client=("192.0.2.2", 12345),
    ) as another_client:
        response = another_client.post("/api/submit")

        assert response.status_code == 200
        assert response.json()["tokens_remaining"] == 4


def test_unprotected_endpoint_bypasses_rate_limit(client):
    for _ in range(5):
        response = client.post("/api/submit")
        assert response.status_code == 200

    response = client.post("/api/submit")
    assert response.status_code == 429

    response = client.post(
        "/api/redis",
        json={"username": "test_user"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "test_user"


def test_fail_open_when_redis_unavailable(client):
    redis_instance = app.state.redis

    with patch.object(
        redis_instance,
        "eval",
        new_callable=AsyncMock,
        side_effect=redis.ConnectionError(
            "Redis is unavailable"
        ),
        create=True,
    ):
        response = client.post("/api/submit")

    assert response.status_code == 200
    assert response.json()["message"] == "Request allowed"
    assert response.json()["tokens_remaining"] is None


def test_fail_open_logs_redis_error(client, caplog):
    with caplog.at_level("ERROR", logger="app.main"):
        with patch.object(
            app.state.redis,
            "eval",
            new_callable=AsyncMock,
            side_effect=redis.ConnectionError(
                "Redis is unavailable"
            ),
            create=True,
        ):
            response = client.post("/api/submit")

    assert response.status_code == 200
    assert "rate_limiter_failure" in caplog.text
    assert "Redis is unavailable" in caplog.text