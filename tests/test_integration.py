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

# API key used by the test suite — must match app/core/config.py
TEST_API_KEY = "ironmind_secret_2026"
AUTH_HEADERS = {"X-API-KEY": TEST_API_KEY}


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Provides a fresh isolated database and authenticated TestClient for every test case."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield TestClient(app, headers=AUTH_HEADERS)
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

    def test_validation_error_contains_field_details(self, client):
        """Error envelope must include per-field details for validation failures."""
        res = client.post("/api/v1/athletes/", json={"name": "NoEmail"})
        body = res.json()
        assert "details" in body["error"]
        assert len(body["error"]["details"]) > 0


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

    def test_athlete_list_pagination(self, client):
        """List endpoint must respect skip/limit query params."""
        for i in range(5):
            make_athlete(client, name=f"Athlete {i}", email=f"ath{i}@test.com")
        res = client.get("/api/v1/athletes/?skip=0&limit=3")
        assert res.status_code == 200
        assert len(res.json()) == 3


class TestAthleteInputValidation:
    """Edge-case validation tests for the Athlete schema."""

    def test_age_too_young_rejected(self, client):
        """Age below 10 must be rejected with 422."""
        res = client.post("/api/v1/athletes/", json={"name": "Baby", "email": "baby@test.com", "age": 5})
        assert res.status_code == 422

    def test_age_too_old_rejected(self, client):
        """Age above 120 must be rejected with 422."""
        res = client.post("/api/v1/athletes/", json={"name": "Old", "email": "old@test.com", "age": 150})
        assert res.status_code == 422

    def test_age_boundary_values_accepted(self, client):
        """Ages exactly at the boundaries (10, 120) must be accepted."""
        res10 = client.post("/api/v1/athletes/", json={"name": "Young", "email": "young@test.com", "age": 10})
        res120 = client.post("/api/v1/athletes/", json={"name": "Elder", "email": "elder@test.com", "age": 120})
        assert res10.status_code == 201
        assert res120.status_code == 201

    def test_blank_name_rejected(self, client):
        """A whitespace-only name must be rejected with 422."""
        res = client.post("/api/v1/athletes/", json={"name": "   ", "email": "blank@test.com"})
        assert res.status_code == 422

    def test_invalid_email_rejected(self, client):
        """A malformed email address must be rejected with 422."""
        res = client.post("/api/v1/athletes/", json={"name": "Test", "email": "not-an-email"})
        assert res.status_code == 422

    def test_missing_required_name_rejected(self, client):
        """Omitting name entirely must be rejected with 422."""
        res = client.post("/api/v1/athletes/", json={"email": "noname@test.com"})
        assert res.status_code == 422


class TestTrainingSessions:
    """Tests for session logging and validation."""

    def test_session_validation(self, client):
        ath = make_athlete(client)
        # Duration bounds – lower
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 0}).status_code == 422
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": -5}).status_code == 422
        # Duration upper bound
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 601}).status_code == 422
        # Intensity bounds
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30, "intensity": 0}).status_code == 422
        assert client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30, "intensity": 11}).status_code == 422

    def test_blank_sport_rejected(self, client):
        """Empty string sport must be rejected with 422."""
        ath = make_athlete(client)
        res = client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "   ", "duration": 30})
        assert res.status_code == 422

    def test_session_for_unknown_athlete_rejected(self, client):
        """Session for non-existent athlete_id must return 404."""
        res = client.post("/api/v1/sessions/", json={"athlete_id": 999999, "sport": "Run", "duration": 30})
        assert res.status_code == 404

    def test_session_full_crud(self, client):
        """Sessions support full CREATE → READ → UPDATE → DELETE lifecycle."""
        ath = make_athlete(client)
        sess = make_session(client, ath["id"])
        # Read
        res = client.get(f"/api/v1/sessions/{sess['id']}")
        assert res.status_code == 200
        # Update
        res = client.put(f"/api/v1/sessions/{sess['id']}", json={"intensity": 9})
        assert res.json()["intensity"] == 9
        # Delete
        client.delete(f"/api/v1/sessions/{sess['id']}")
        assert client.get(f"/api/v1/sessions/{sess['id']}").status_code == 404


class TestRecoveryTracking:
    """Tests for sleep and wellness check-ins."""

    def test_sleep_constraints(self, client):
        ath = make_athlete(client)
        # Uniqueness per day
        make_sleep(client, ath["id"], days_ago=0)
        assert client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 7, "date": date.today().isoformat()}).status_code == 409
        # Quality bounds
        assert client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 8, "sleep_quality": 6}).status_code == 422

    def test_sleep_negative_hours_rejected(self, client):
        """Negative sleep hours must be rejected with 422."""
        ath = make_athlete(client)
        res = client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": -1})
        assert res.status_code == 422

    def test_sleep_exceeds_24h_rejected(self, client):
        """Sleep hours above 24 must be rejected with 422."""
        ath = make_athlete(client)
        res = client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 25})
        assert res.status_code == 422

    def test_sleep_full_crud(self, client):
        """Sleep logs support full CREATE → READ → UPDATE → DELETE lifecycle."""
        ath = make_athlete(client)
        sl = make_sleep(client, ath["id"], days_ago=5)
        # Read
        assert client.get(f"/api/v1/sleep-logs/{sl['id']}").status_code == 200
        # Update
        res = client.put(f"/api/v1/sleep-logs/{sl['id']}", json={"sleep_hours": 9.0})
        assert res.json()["sleep_hours"] == 9.0
        # Delete
        client.delete(f"/api/v1/sleep-logs/{sl['id']}")
        assert client.get(f"/api/v1/sleep-logs/{sl['id']}").status_code == 404

    def test_checkin_constraints(self, client):
        ath = make_athlete(client)
        make_checkin(client, ath["id"], days_ago=0)
        res = client.post("/api/v1/checkins/", json={
            "athlete_id": ath["id"],
            "fatigue": 5, "stress": 5, "mood": 5, "soreness": 5,
            "date": date.today().isoformat()
        })
        assert res.status_code == 409

    def test_checkin_out_of_range_rejected(self, client):
        """Check-in values outside 1-10 must be rejected with 422."""
        ath = make_athlete(client)
        assert client.post("/api/v1/checkins/", json={
            "athlete_id": ath["id"], "fatigue": 0, "stress": 5, "mood": 5, "soreness": 5
        }).status_code == 422
        assert client.post("/api/v1/checkins/", json={
            "athlete_id": ath["id"], "fatigue": 5, "stress": 11, "mood": 5, "soreness": 5
        }).status_code == 422

    def test_checkin_full_crud(self, client):
        """Check-ins support full CREATE → READ → UPDATE → DELETE lifecycle."""
        ath = make_athlete(client)
        ci = make_checkin(client, ath["id"], days_ago=3)
        # Read
        assert client.get(f"/api/v1/checkins/{ci['id']}").status_code == 200
        # Update
        res = client.put(f"/api/v1/checkins/{ci['id']}", json={"mood": 9})
        assert res.json()["mood"] == 9
        # Delete
        client.delete(f"/api/v1/checkins/{ci['id']}")
        assert client.get(f"/api/v1/checkins/{ci['id']}").status_code == 404


class TestReadinessAnalytics:
    """Verifies sports science logic (ACWR and Score calculations)."""

    def test_readiness_signals(self, client):
        ath = make_athlete(client)
        for i in range(1, 15):
            make_session(client, ath["id"], duration=60, intensity=6, days_ago=i)
        
        res = client.get(f"/api/v1/athletes/{ath['id']}/insights/readiness")
        data = res.json()
        assert data["readiness_score"] > 0
        assert data["readiness_score"] <= 100
        assert "acwr" in data["signals"]
        assert "top_reasons" in data
        assert len(data["top_reasons"]) > 0
        assert data["readiness_band"] in ("Low", "Medium", "High")

    def test_readiness_hateoas_links(self, client):
        """Readiness response must include HATEOAS links."""
        ath = make_athlete(client)
        res = client.get(f"/api/v1/athletes/{ath['id']}/insights/readiness")
        assert "links" in res.json()
        assert "self" in res.json()["links"]

    def test_simulation_accuracy(self, client):
        ath = make_athlete(client)
        res = client.post(f"/api/v1/athletes/{ath['id']}/whatif/readiness", json={
            "planned_session_duration": 90, "planned_session_intensity": 9,
            "expected_sleep_hours": 9, "expected_sleep_quality": 5
        })
        assert res.status_code == 200
        body = res.json()
        assert "change_description" in body
        assert "original_readiness" in body
        assert "projected_readiness" in body

    def test_training_trends_structure(self, client):
        """Trends endpoint must return 15 data points and a load summary."""
        ath = make_athlete(client)
        res = client.get(f"/api/v1/athletes/{ath['id']}/analytics/trends")
        assert res.status_code == 200
        body = res.json()
        assert "trends" in body
        assert "load_summary" in body
        assert len(body["trends"]) == 15  # 0 to 14 days


class TestMCPEndpoint:
    """Verifies the MCP tool definitions are well-formed."""

    def test_mcp_returns_three_tools(self, client):
        res = client.get("/api/v1/mcp/tools")
        assert res.status_code == 200
        tools = res.json()
        assert len(tools) == 3

    def test_mcp_tool_names(self, client):
        res = client.get("/api/v1/mcp/tools")
        names = {t["name"] for t in res.json()}
        assert "get_athlete_readiness" in names
        assert "simulate_future_readiness" in names
        assert "get_training_trends" in names

    def test_mcp_tools_have_required_fields(self, client):
        """Every tool must have: name, description, parameters, returns."""
        tools = client.get("/api/v1/mcp/tools").json()
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "required" in tool["parameters"]
            assert "returns" in tool


def test_system_status(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "0.6.0"
