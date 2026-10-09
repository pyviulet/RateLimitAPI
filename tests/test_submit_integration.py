
import time
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
    ) as client:
        yield client


@pytest.fixture(autouse=True)
def clear_rate_limits():
    redis_client.delete("rate_limit:192.0.2.1")
    yield
    redis_client.delete("rate_limit:192.0.2.1")


def test_submit_rate_limit(client):
    for i in range(5):
        response = client.post("/api/submit")

        assert response.status_code == 200
        assert response.json()["request_count"] == i + 1

    response = client.post("/api/submit")

    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"


def test_submit_sliding_window(client):
    old_timestamp = time.time() - 61

    for i in range(5):
        redis_client.zadd(
            "rate_limit:192.0.2.1",
            {f"old-request-{i}": old_timestamp},
        )

    response = client.post("/api/submit")

    assert response.status_code == 200
    assert response.json()["request_count"] == 1


def test_submit_seprate_ip_limits(client):

    # First IP makes 5 request
    for _ in range (5):
        response = client.post("/api/submit")
        assert response.status_code == 200

    # The first IP has reached its limit
    response = client.post("/api/submit")
    assert response.status_code == 429

    with TestClient(
        app,
        client=("192.0.2.2", 12345),

    ) as another_client:
        response = another_client .post("/api/submit")

        # The second IP should have its own limit
        assert response.status_code == 200
        assert response.json()["request_count"] == 1

