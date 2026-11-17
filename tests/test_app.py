import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    # Arrange
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
    # Arrange
    expected_chess_participants = ["existing@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["Chess Club"]["participants"] == expected_chess_participants
    assert response.json()["Art Club"]["participants"] == []


def test_signup_adds_participant_to_activity(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert activities_response.json()["Art Club"]["participants"] == [email]


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert activities_response.json()["Chess Club"]["participants"] == []
