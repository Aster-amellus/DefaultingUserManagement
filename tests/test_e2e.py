from datetime import datetime
from fastapi.testclient import TestClient


def login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_end_to_end(client: TestClient):
    # 1) admin login (auto-created on first login)
    admin_token = login(client, "admin@example.com", "admin123")

    # 2) admin creates reviewer and operator users
    r = client.post(
        "/users/",
        json={"email": "reviewer@example.com", "password": "rev123", "full_name": "Rev", "role": "Reviewer"},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200, r.text

    r = client.post(
        "/users/",
        json={"email": "operator@example.com", "password": "op123", "full_name": "Op", "role": "Operator"},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200, r.text

    reviewer_token = login(client, "reviewer@example.com", "rev123")
    operator_token = login(client, "operator@example.com", "op123")

    # 3) admin creates reasons
    r = client.post(
        "/reasons/",
        json={"type": "DEFAULT", "description": "Overdue 90d", "enabled": True, "sort_order": 1},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200, r.text
    default_reason_id = r.json()["id"]

    r = client.post(
        "/reasons/",
    json={"type": "REBIRTH", "description": "Debt Cleared", "enabled": True, "sort_order": 2},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200, r.text
    rebirth_reason_id = r.json()["id"]

    # 4) operator creates a customer
    r = client.post(
        "/customers/",
        json={"name": "Contoso", "industry": "Tech", "region": "North"},
        headers=auth_header(operator_token),
    )
    assert r.status_code == 200, r.text
    customer_id = r.json()["id"]

    # 5) operator submits a DEFAULT application
    r = client.post(
        "/applications/",
        json={
            "type": "DEFAULT",
            "customer_id": customer_id,
            "latest_external_rating": "CCC",
            "reason_id": default_reason_id,
            "severity": "HIGH",
            "remark": "Serious overdue",
        },
        headers=auth_header(operator_token),
    )
    assert r.status_code == 200, r.text
    app_id = r.json()["id"]

    # 6) RBAC: operator cannot review -> 403
    r = client.post(
        f"/applications/{app_id}/review",
        json={"decision": "APPROVED"},
        headers=auth_header(operator_token),
    )
    assert r.status_code == 403

    # 7) reviewer approves
    r = client.post(
        f"/applications/{app_id}/review",
        json={"decision": "APPROVED", "remark": "OK"},
        headers=auth_header(reviewer_token),
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "APPROVED"

    # 8) customer should now be default
    r = client.get(f"/customers/{customer_id}", headers=auth_header(admin_token))
    assert r.status_code == 200
    assert r.json()["is_default"] is True

    # 9) business rule: cannot submit another DEFAULT for already default customer
    r = client.post(
        "/applications/",
        json={
            "type": "DEFAULT",
            "customer_id": customer_id,
            "latest_external_rating": "CCC",
            "reason_id": default_reason_id,
            "severity": "LOW",
        },
        headers=auth_header(operator_token),
    )
    assert r.status_code == 400

    # 10) operator submits a REBIRTH application
    r = client.post(
        "/applications/",
        json={
            "type": "REBIRTH",
            "customer_id": customer_id,
            "reason_id": rebirth_reason_id,
            "remark": "Cleared debt",
        },
        headers=auth_header(operator_token),
    )
    assert r.status_code == 200, r.text
    rebirth_app_id = r.json()["id"]

    # 11) reviewer rejects once
    r = client.post(
        f"/applications/{rebirth_app_id}/review",
        json={"decision": "REJECTED"},
        headers=auth_header(reviewer_token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "REJECTED"

    # 12) notifications for operator should exist
    r = client.get("/notifications/", headers=auth_header(operator_token))
    assert r.status_code == 200
    notes = r.json()
    assert any("Application #" in n["content"] for n in notes)

    # 13) search applications by name and status
    r = client.get("/applications/", params={"customer_name": "Contoso"}, headers=auth_header(admin_token))
    assert r.status_code == 200
    assert len(r.json()) >= 2

    # 14) stats for current year should reflect at least one APPROVED default
    year = datetime.utcnow().year
    r = client.get("/stats/industry", params={"year": year}, headers=auth_header(admin_token))
    assert r.status_code == 200
    # ensure our industry shows up
    items = r.json()
    assert any(i["industry"] == "Tech" and i["default_count"] >= 1 for i in items)

    r = client.get("/stats/region", params={"year": year}, headers=auth_header(admin_token))
    assert r.status_code == 200
    items = r.json()
    assert any(i["region"] == "North" and i["default_count"] >= 1 for i in items)

    # 15) disabled reason should block new application
    r = client.patch(
        f"/reasons/{default_reason_id}",
        json={"type": "DEFAULT", "description": "Overdue 90d", "enabled": False, "sort_order": 1},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200

    r = client.post(
        "/applications/",
        json={
            "type": "DEFAULT",
            "customer_id": customer_id,
            "latest_external_rating": "C",
            "reason_id": default_reason_id,
        },
        headers=auth_header(operator_token),
    )
    assert r.status_code == 400

    # 16) stats handle empty industry/region gracefully
    r = client.post(
        "/customers/",
        json={"name": "NoMeta", "industry": None, "region": None},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200
