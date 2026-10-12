import os

import pytest
import redis
from fastapi.testclient import TestClient

import api

LONG_URL = "https://exemplu.ro/un/link/foarte/lung"


@pytest.fixture
def client(monkeypatch):
    test_redis = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=15,
        decode_responses=True,
    )
    test_redis.flushdb()
    monkeypatch.setattr(api, "r", test_redis)

    yield TestClient(api.app, follow_redirects=False)

    test_redis.flushdb()


def create_link(client, url=LONG_URL):
    res = client.post("/api/shorten", json={"url": url})
    assert res.status_code == 201
    return res.json()["code"]


def test_shorten_returns_six_char_code(client):
    code = create_link(client)
    assert len(code) == 6
    assert code.isalnum()


def test_redirect_existing_code(client):
    code = create_link(client)
    res = client.get(f"/r/{code}")
    assert res.status_code == 307
    assert res.headers["location"] == LONG_URL


def test_redirect_unknown_code(client):
    assert client.get("/r/nuexista").status_code == 404


def test_stats_counts_redirects(client):
    code = create_link(client)
    client.get(f"/r/{code}")
    client.get(f"/r/{code}")
    res = client.get(f"/api/stats/{code}")
    assert res.status_code == 200
    assert res.json()["clicks"] == 2


def test_stats_unknown_code(client):
    assert client.get("/api/stats/nuexista").status_code == 404


def test_health(client):
    assert client.get("/health").status_code == 200


def test_ready(client):
    assert client.get("/ready").status_code == 200