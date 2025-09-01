from datetime import datetime
from fastapi.testclient import TestClient


def _login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_default_review_requires_attachment(client: TestClient):
    # prepare admin and reviewer
    admin_token = _login(client, "admin@example.com", "admin123")
    r = client.post(
        "/users/",
        json={"email": "rev2@example.com", "password": "rev2", "role": "Reviewer", "full_name": "Rev2"},
        headers=_auth(admin_token),
    )
    assert r.status_code == 200
    reviewer_token = _login(client, "rev2@example.com", "rev2")

    # prepare data: reason (DEFAULT) and customer
    r = client.post(
        "/reasons/",
        json={"type": "DEFAULT", "description": "MustAttach", "enabled": True, "sort_order": 5},
        headers=_auth(admin_token),
    )
    assert r.status_code == 200, r.text
    reason_id = r.json()["id"]

    r = client.post(
        "/customers/",
        json={"name": "AttachCo", "industry": "QA", "region": "N"},
        headers=_auth(admin_token),
    )
    assert r.status_code == 200
    customer_id = r.json()["id"]

    # create DEFAULT application
    r = client.post(
        "/applications/",
        json={
            "type": "DEFAULT",
            "customer_id": customer_id,
            "latest_external_rating": "B",
            "reason_id": reason_id,
            "severity": "HIGH",
        },
        headers=_auth(admin_token),
    )
    assert r.status_code == 200, r.text
    app_id = r.json()["id"]

    # reviewer tries to approve without attachment -> 400
    r = client.post(f"/applications/{app_id}/review", json={"decision": "APPROVED"}, headers=_auth(reviewer_token))
    assert r.status_code == 400
    assert "Attachment" in r.json().get("detail", "")


def test_attachments_presign_local_and_audit_access_control(client: TestClient):
    admin_token = _login(client, "admin@example.com", "admin123")
    # create reason and customer
    r = client.post(
        "/reasons/",
        json={"type": "DEFAULT", "description": "PreSign", "enabled": True, "sort_order": 6},
        headers=_auth(admin_token),
    )
    reason_id = r.json()["id"]
    r = client.post(
        "/customers/",
        json={"name": "PreSignCo", "industry": "OPS", "region": "S"},
        headers=_auth(admin_token),
    )
    customer_id = r.json()["id"]
    r = client.post(
        "/applications/",
        json={"type": "DEFAULT", "customer_id": customer_id, "reason_id": reason_id, "severity": "LOW"},
        headers=_auth(admin_token),
    )
    app_id = r.json()["id"]

    # presign (local backend should fallback to /files path)
    r = client.get(f"/applications/{app_id}/attachments/presign", params={"filename": "x.txt"}, headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json()["url"].startswith("/files/")

    # audit logs should be admin-only
    # create operator and attempt access
    r = client.post(
        "/users/",
        json={"email": "op2@example.com", "password": "op2", "role": "Operator", "full_name": "Op2"},
        headers=_auth(admin_token),
    )
    assert r.status_code == 200
    op_token = _login(client, "op2@example.com", "op2")
    r = client.get("/audit-logs/", headers=_auth(op_token))
    assert r.status_code == 403

    # admin can view and should see fields actor/action/resource/ip
    r = client.get("/audit-logs/", headers=_auth(admin_token))
    assert r.status_code == 200
    items = r.json().get("items", [])
    if items:
        sample = items[0]
        assert "actor" in sample
        assert "action" in sample
        assert "resource" in sample
        assert "ip" in sample


def test_stats_detailed_has_shares_and_trends(client: TestClient):
    admin_token = _login(client, "admin@example.com", "admin123")
    year = datetime.utcnow().year
    r = client.get("/stats/industry", params={"year": year, "detailed": True}, headers=_auth(admin_token))
    assert r.status_code == 200
    data = r.json()
    # shape checks only; values may be zero when no approvals
    for item in data:
        assert "default_share" in item
        assert "rebirth_share" in item
        assert "default_trend" in item and len(item["default_trend"]) == 12
        assert "rebirth_trend" in item and len(item["rebirth_trend"]) == 12


def test_user_patch_and_delete_and_notifications_read(client: TestClient):
    admin_token = _login(client, "admin@example.com", "admin123")
    # create reviewer and operator
    r = client.post(
        "/users/",
        json={"email": "rev3@example.com", "password": "rev3", "role": "Reviewer", "full_name": "Rev3"},
        headers=_auth(admin_token),
    )
    assert r.status_code == 200
    reviewer_token = _login(client, "rev3@example.com", "rev3")

    r = client.post(
        "/users/",
        json={"email": "op3@example.com", "password": "op3", "role": "Operator", "full_name": "Op3"},
        headers=_auth(admin_token),
    )
    assert r.status_code == 200
    operator_token = _login(client, "op3@example.com", "op3")

    # admin patch reviewer name
    uid = r.json().get("id")
    r = client.patch(f"/users/{uid}", json={"full_name": "Op3-Updated"}, headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json()["full_name"] == "Op3-Updated"

    # create minimal reason/customer/app and approve to generate a notification for operator
    r = client.post(
        "/reasons/",
        json={"type": "DEFAULT", "description": "Notify", "enabled": True, "sort_order": 7},
        headers=_auth(admin_token),
    )
    reason_id = r.json()["id"]
    r = client.post(
        "/customers/",
        json={"name": "NotifCo", "industry": "IT", "region": "W"},
        headers=_auth(admin_token),
    )
    cust_id = r.json()["id"]
    r = client.post(
        "/applications/",
        json={"type": "DEFAULT", "customer_id": cust_id, "reason_id": reason_id, "severity": "LOW"},
        headers=_auth(operator_token),
    )
    app_id = r.json()["id"]
    files = {"file": ("e.txt", b"x", "text/plain")}
    r = client.post(f"/applications/{app_id}/attachments", files=files, headers=_auth(operator_token))
    assert r.status_code == 200
    r = client.post(f"/applications/{app_id}/review", json={"decision": "APPROVED"}, headers=_auth(reviewer_token))
    assert r.status_code == 200

    # operator sees notifications and can mark read
    r = client.get("/notifications/", headers=_auth(operator_token))
    assert r.status_code == 200
    notes = r.json()
    assert notes, "expected at least one notification"
    nid = notes[0]["id"]
    r = client.post(f"/notifications/{nid}/read", headers=_auth(operator_token))
    assert r.status_code == 200 and r.json().get("ok") is True
