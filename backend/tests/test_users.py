import uuid

import pytest
from fastapi.testclient import TestClient

from db.models import User
from db.postgres import SessionLocal
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    db = SessionLocal()
    for u in db.query(User).filter(User.email.like("test_%@testmail.com")).all():
        db.delete(u)
    db.commit()
    db.close()


def new_user(**overrides):
    data = {
        "name": "Test User",
        "email": f"test_{uuid.uuid4().hex[:8]}@testmail.com",
        "password": "Password123",
    }
    data.update(overrides)
    return data


def test_database_connections(client):
    r = client.get("/api/health/db")
    assert r.status_code == 200
    assert r.json()["postgres"] is True
    assert r.json()["influxdb"] is True


def test_register_valid_user(client):
    payload = new_user()
    r = client.post("/api/users/register", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == payload["email"]
    assert "password" not in body
    assert "password_hash" not in body
    assert body["profile"]["alert_threshold"] == 150


def test_asthma_user_gets_lower_threshold(client):
    r = client.post("/api/users/register", json=new_user(profile={"has_asthma": True}))
    assert r.status_code == 201
    assert r.json()["profile"]["alert_threshold"] == 100


def test_child_and_elderly_thresholds(client):
    r = client.post(
        "/api/users/register",
        json=new_user(profile={"is_child": True, "is_elderly": True}),
    )
    assert r.status_code == 201
    assert r.json()["profile"]["alert_threshold"] == 100


def test_custom_threshold_is_used(client):
    r = client.post(
        "/api/users/register",
        json=new_user(profile={"has_asthma": True, "alert_threshold": 80}),
    )
    assert r.status_code == 201
    assert r.json()["profile"]["alert_threshold"] == 80


def test_duplicate_email_rejected(client):
    payload = new_user()
    assert client.post("/api/users/register", json=payload).status_code == 201
    assert client.post("/api/users/register", json=payload).status_code == 409


def test_invalid_email_rejected(client):
    r = client.post("/api/users/register", json=new_user(email="not-an-email"))
    assert r.status_code == 422


def test_missing_fields_rejected(client):
    r = client.post("/api/users/register", json={"name": "No Email"})
    assert r.status_code == 422


def test_short_password_rejected(client):
    r = client.post("/api/users/register", json=new_user(password="abc1"))
    assert r.status_code == 422


def test_password_without_number_rejected(client):
    r = client.post("/api/users/register", json=new_user(password="onlyletters"))
    assert r.status_code == 422


def test_threshold_out_of_range_rejected(client):
    r = client.post(
        "/api/users/register", json=new_user(profile={"alert_threshold": 999})
    )
    assert r.status_code == 422


def test_get_user_and_profile(client):
    created = client.post("/api/users/register", json=new_user()).json()

    r = client.get(f"/api/users/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == created["email"]

    r = client.get(f"/api/users/{created['id']}/profile")
    assert r.status_code == 200
    assert r.json()["alert_threshold"] == 150


def test_get_unknown_user_returns_404(client):
    assert client.get("/api/users/999999").status_code == 404
    assert client.get("/api/users/999999/profile").status_code == 404