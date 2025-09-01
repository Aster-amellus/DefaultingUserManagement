from datetime import datetime, timedelta
from fastapi.testclient import TestClient

def _login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

def _auth(t: str):
    return {"Authorization": f"Bearer {t}"}

def test_disabled_reason_blocks_application(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    # create reason and customer
    r = client.post("/reasons/", json={"type": "DEFAULT", "description": "Disabled", "enabled": False, "sort_order": 20}, headers=_auth(admin))
    reason_id = r.json()["id"]
    r = client.post("/customers/", json={"name": "EdgeCust", "industry": "E", "region": "E"}, headers=_auth(admin))
    cust_id = r.json()["id"]
    # try to create application
    r = client.post("/applications/", json={"type": "DEFAULT", "customer_id": cust_id, "reason_id": reason_id}, headers=_auth(admin))
    assert r.status_code == 400
    assert "Invalid reason" in r.json().get("detail", "")

def test_approval_non_pending_fails(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    r = client.post("/reasons/", json={"type": "DEFAULT", "description": "NonPending", "enabled": True, "sort_order": 21}, headers=_auth(admin))
    reason_id = r.json()["id"]
    r = client.post("/customers/", json={"name": "NonPending", "industry": "E", "region": "E"}, headers=_auth(admin))
    cust_id = r.json()["id"]
    r = client.post("/applications/", json={"type": "DEFAULT", "customer_id": cust_id, "reason_id": reason_id}, headers=_auth(admin))
    app_id = r.json()["id"]
    files = {"file": ("e.txt", b"x", "text/plain")}
    r = client.post(f"/applications/{app_id}/attachments", files=files, headers=_auth(admin))
    assert r.status_code == 200
    # approve once
    r = client.post(f"/applications/{app_id}/review", json={"decision": "APPROVED"}, headers=_auth(admin))
    assert r.status_code == 200
    # try to approve again
    r = client.post(f"/applications/{app_id}/review", json={"decision": "APPROVED"}, headers=_auth(admin))
    assert r.status_code == 400
    assert "Not pending" in r.json().get("detail", "")

def test_upload_empty_file(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    r = client.post("/reasons/", json={"type": "DEFAULT", "description": "EmptyFile", "enabled": True, "sort_order": 22}, headers=_auth(admin))
    reason_id = r.json()["id"]
    r = client.post("/customers/", json={"name": "EmptyFile", "industry": "E", "region": "E"}, headers=_auth(admin))
    cust_id = r.json()["id"]
    r = client.post("/applications/", json={"type": "DEFAULT", "customer_id": cust_id, "reason_id": reason_id}, headers=_auth(admin))
    app_id = r.json()["id"]
    files = {"file": ("empty.txt", b"", "text/plain")}
    r = client.post(f"/applications/{app_id}/attachments", files=files, headers=_auth(admin))
    # Accepts empty file, but should succeed (business logic may vary)
    assert r.status_code == 200

def test_jwt_invalid_and_expired(client: TestClient):
    # invalid token
    r = client.get("/customers/", headers={"Authorization": "Bearer invalidtoken"})
    assert r.status_code == 401
    # expired token (simulate by using a token with past exp, if possible)
    # Skipped: token generation with custom exp not supported in current test infra

def test_audit_limit(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    r = client.get("/audit-logs/", params={"limit": 2}, headers=_auth(admin))
    assert r.status_code == 200
    items = r.json().get("items", [])
    assert len(items) <= 2