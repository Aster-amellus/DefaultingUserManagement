from datetime import datetime
from fastapi.testclient import TestClient


def _login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(t: str):
    return {"Authorization": f"Bearer {t}"}


def test_rebirth_on_non_default_fails(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    # reasons
    r = client.post(
        "/reasons/",
        json={"type": "REBIRTH", "description": "BackToNormal", "enabled": True, "sort_order": 10},
        headers=_auth(admin),
    )
    assert r.status_code == 200
    rebirth_reason = r.json()["id"]
    # customer non-default
    r = client.post(
        "/customers/",
        json={"name": "NonDefaultX", "industry": "T", "region": "N"},
        headers=_auth(admin),
    )
    cust = r.json()["id"]
    # try REBIRTH -> 400
    r = client.post(
        "/applications/",
        json={"type": "REBIRTH", "customer_id": cust, "reason_id": rebirth_reason},
        headers=_auth(admin),
    )
    assert r.status_code == 400


def test_rebirth_approve_unsets_default(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    # prepare reasons
    r = client.post(
        "/reasons/",
        json={"type": "REBIRTH", "description": "PassRebirth", "enabled": True, "sort_order": 11},
        headers=_auth(admin),
    )
    rebirth_reason = r.json()["id"]
    # make a default customer by approving a DEFAULT app first
    r = client.post(
        "/reasons/",
        json={"type": "DEFAULT", "description": "TempDef", "enabled": True, "sort_order": 12},
        headers=_auth(admin),
    )
    default_reason = r.json()["id"]
    r = client.post(
        "/users/",
        json={"email": "rev4@example.com", "password": "rev4", "role": "Reviewer"},
        headers=_auth(admin),
    )
    reviewer = _login(client, "rev4@example.com", "rev4")
    r = client.post(
        "/customers/",
        json={"name": "ToRebirth", "industry": "I", "region": "R"},
        headers=_auth(admin),
    )
    cust = r.json()["id"]
    # create DEFAULT app and approve (needs attachment)
    r = client.post(
        "/applications/",
        json={"type": "DEFAULT", "customer_id": cust, "reason_id": default_reason},
        headers=_auth(admin),
    )
    app_def = r.json()["id"]
    files = {"file": ("e.txt", b"x", "text/plain")}
    r = client.post(f"/applications/{app_def}/attachments", files=files, headers=_auth(admin))
    assert r.status_code == 200
    r = client.post(f"/applications/{app_def}/review", json={"decision": "APPROVED"}, headers=_auth(reviewer))
    assert r.status_code == 200

    # now REBIRTH application and approve, expect customer is_default False
    r = client.post(
        "/applications/",
        json={"type": "REBIRTH", "customer_id": cust, "reason_id": rebirth_reason},
        headers=_auth(admin),
    )
    app_re = r.json()["id"]
    r = client.post(f"/applications/{app_re}/review", json={"decision": "APPROVED"}, headers=_auth(reviewer))
    assert r.status_code == 200
    r = client.get(f"/customers/{cust}", headers=_auth(admin))
    assert r.status_code == 200
    assert r.json()["is_default"] is False


def test_applications_search_returns_rich_fields(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    r = client.get("/applications/search", headers=_auth(admin))
    assert r.status_code == 200
    arr = r.json()
    # shape check if any
    if arr:
        a = arr[0]
        for key in (
            "customer_name",
            "reason_description",
            "created_by_name",
            "reviewed_by_name",
        ):
            assert key in a


def test_stats_region_detailed(client: TestClient):
    admin = _login(client, "admin@example.com", "admin123")
    year = datetime.utcnow().year
    r = client.get("/stats/region", params={"year": year, "detailed": True}, headers=_auth(admin))
    assert r.status_code == 200
    data = r.json()
    for item in data:
        assert "default_share" in item
        assert "rebirth_share" in item
        assert "default_trend" in item and len(item["default_trend"]) == 12
        assert "rebirth_trend" in item and len(item["rebirth_trend"]) == 12
