import pytest
from fastapi.testclient import TestClient
from typing import Generator
import pytest


def get_token(client: TestClient):
    r = client.post("/auth/token", data={"username": "admin@example.com", "password": "admin123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200


def test_flow(client: TestClient):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # create customer
    r = client.post("/customers/", json={"name": "ACME", "industry": "MFG", "region": "EAST"}, headers=headers)
    assert r.status_code == 200, r.text
    customer_id = r.json()["id"]

    # create default reason
    r = client.post("/reasons/", json={"type": "DEFAULT", "description": "Overdue", "enabled": True, "sort_order": 1}, headers=headers)
    assert r.status_code == 200, r.text
    reason_id = r.json()["id"]

    # create application DEFAULT
    r = client.post(
        "/applications/",
        json={
            "type": "DEFAULT",
            "customer_id": customer_id,
            "latest_external_rating": "B",
            "reason_id": reason_id,
            "severity": "HIGH",
            "remark": "Test",
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    app_id = r.json()["id"]

    # upload an attachment to satisfy approval requirement
    files = {"file": ("evidence.txt", b"dummy", "text/plain")}
    r = client.post(f"/applications/{app_id}/attachments", files=files, headers=headers)
    assert r.status_code == 200, r.text

    # review approve
    r = client.post(f"/applications/{app_id}/review", json={"decision": "APPROVED"}, headers=headers)
    assert r.status_code == 200, r.text
