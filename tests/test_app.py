from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect known activity keys
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # Use a unique email so tests are idempotent across runs
    email = f"testuser+{uuid4().hex}@example.com"
    activity_name = "Chess Club"

    # Ensure email not present initially
    before = client.get("/activities").json()
    assert email not in before[activity_name]["participants"]

    # Sign up (use params so plus signs are encoded correctly)
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email} for {activity_name}" in resp.json().get("message", "")

    # Verify signup is visible
    after = client.get("/activities").json()
    assert email in after[activity_name]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity_name}/participant", params={"email": email})
    assert resp.status_code == 200
    assert f"Unregistered {email} from {activity_name}" in resp.json().get("message", "")

    # Verify removal
    final = client.get("/activities").json()
    assert email not in final[activity_name]["participants"]


def test_unregister_nonexistent_returns_404():
    email = f"noone+{uuid4().hex}@example.com"
    activity_name = "Chess Club"
    resp = client.delete(f"/activities/{activity_name}/participant", params={"email": email})
    assert resp.status_code == 404