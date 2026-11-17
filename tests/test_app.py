import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Test activity",
            "schedule": "Mondays",
            "max_participants": 3,
            "participants": ["existing@mergington.edu"],
        },
        "Art Club": {
            "description": "Another test activity",
            "schedule": "Tuesdays",
            "max_participants": 4,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data_without_caching(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["Chess Club"]["participants"] == ["existing@mergington.edu"]
    assert response.json()["Art Club"]["participants"] == []


def test_signup_adds_participant_to_activity(client):
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@mergington.edu for Art Club"}
    activities_response = client.get("/activities")
    assert activities_response.json()["Art Club"]["participants"] == ["new@mergington.edu"]


def test_unregister_removes_participant_from_activity(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed existing@mergington.edu from Chess Club"}
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == []
