import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from app.main import app
from app.db.session import Base, get_db

# Test Database configuration (isolated SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Provides a fresh database for every test case."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


# Test Helpers

def make_athlete(client, name="Test Athlete", email=None, age=25):
    email = email or f"{name.replace(' ', '_').lower()}@ironmind.com"
    res = client.post("/api/v1/athletes/", json={"name": name, "email": email, "age": age})
    assert res.status_code == 201
    return res.json()


def make_session(client, athlete_id, sport="Run", duration=60.0, intensity=7, days_ago=0, distance=10.0):
    d = (date.today() - timedelta(days=days_ago)).isoformat()
    res = client.post("/api/v1/sessions/", json={
        "athlete_id": athlete_id, "sport": sport,
        "duration": duration, "intensity": intensity,
        "distance": distance, "date": d,
    })
    assert res.status_code == 201
    return res.json()


def make_sleep(client, athlete_id, sleep_hours=8.0, sleep_quality=4, days_ago=0):
    d = (date.today() - timedelta(days=days_ago)).isoformat()
    res = client.post("/api/v1/sleep-logs/", json={
        "athlete_id": athlete_id, "sleep_hours": sleep_hours,
        "sleep_quality": sleep_quality, "date": d,
    })
    assert res.status_code == 201
    return res.json()


def make_checkin(client, athlete_id, fatigue=3, stress=2, mood=8, soreness=2, days_ago=0):
    d = (date.today() - timedelta(days=days_ago)).isoformat()
    res = client.post("/api/v1/checkins/", json={
        "athlete_id": athlete_id, "fatigue": fatigue, "stress": stress,
        "mood": mood, "soreness": soreness, "date": d,
    })
    assert res.status_code == 201
    return res.json()


# API Integration & Validation Tests

class TestErrorContract:
    """Verifies standard JSON error envelope responses."""
    
    def test_404_format(self, client):
        res = client.get("/api/v1/athletes/999999")
        assert res.status_code == 404
        assert res.json()["error"]["type"] == "not_found"

    def test_422_format(self, client):
        res = client.post("/api/v1/athletes/", json={"name": "MissingEmail"})
        assert res.status_code == 422
        assert res.json()["error"]["type"] == "validation_error"

    def test_400_format(self, client):
        make_athlete(client, email="taken@test.com")
        res = client.post("/api/v1/athletes/", json={"name": "X", "email": "taken@test.com"})
        assert res.status_code == 400
        assert res.json()["error"]["type"] == "bad_request"


class TestAthleteManagement:
    """Full lifecycle tests for athlete profiles."""

    def test_athlete_crud(self, client):
        # Create
        ath = make_athlete(client, name="Alice", email="alice@test.com")
        # Update
        res = client.put(f"/api/v1/athletes/{ath['id']}", json={"name": "Alice Smith"})
        assert res.json()["name"] == "Alice Smith"
        # Delete
        client.delete(f"/api/v1/athletes/{ath['id']}")
        assert client.get(f"/api/v1/athletes/{ath['id']}").status_code == 404


class TestTrainingSessions:
    """Tests for session logging and validation."""

    def test_session_validation(self, client):
        ath = make_athlete(client)
        # Duration bounds
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 0}).status_code == 422
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": -5}).status_code == 422
        # Intensity bounds
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30, "intensity": 0}).status_code == 422
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30, "intensity": 11}).status_code == 422


class TestRecoveryTracking:
    """Tests for sleep and wellness check-ins."""

    def test_sleep_constraints(self, client):
        ath = make_athlete(client)
        # Uniqueness per day
        make_sleep(client, ath["id"], days_ago=0)
        assert client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 7, "date": date.today().isoformat()}).status_code == 409
        # Quality bounds
        assert client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 8, "sleep_quality": 6}).status_code == 422

    def test_checkin_constraints(self, client):
        ath = make_athlete(client)
        make_checkin(client, ath["id"], days_ago=0)
        res = client.post("/api/v1/checkins/", json={
            "athlete_id": ath["id"], 
            "fatigue": 5, "stress": 5, "mood": 5, "soreness": 5,
            "date": date.today().isoformat()
        })
        assert res.status_code == 409


class TestReadinessAnalytics:
    """Verifies sports science logic (ACWR and Score calculations)."""

    def test_readiness_signals(self, client):
        ath = make_athlete(client)
        for i in range(1, 15):
            make_session(client, ath["id"], duration=60, intensity=6, days_ago=i)
        
        res = client.get(f"/api/v1/athletes/{ath['id']}/insights/readiness")
        data = res.json()
        assert data["readiness_score"] > 0
        assert "acwr" in data["signals"]
        assert "top_reasons" in data
        assert len(data["top_reasons"]) > 0

    def test_simulation_accuracy(self, client):
        ath = make_athlete(client)
        res = client.post(f"/api/v1/athletes/{ath['id']}/whatif/readiness", json={
            "planned_session_duration": 90, "planned_session_intensity": 9,
            "expected_sleep_hours": 9, "expected_sleep_quality": 5
        })
        assert res.status_code == 200
        assert "change_description" in res.json()


def test_system_status(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "0.6.0"
