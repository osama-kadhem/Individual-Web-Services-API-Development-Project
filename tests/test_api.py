import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client and database"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


# Phase 4: Sleep logs and daily check-ins (constraints)
def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["phase"] == "5"


def test_create_athlete(client):
    """Test creating an athlete"""
    response = client.post(
        "/api/v1/athletes/",
        json={"name": "John Doe", "email": "john@example.com", "age": 30}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data


def test_list_athletes(client):
    """Test listing athletes"""
    client.post(
        "/api/v1/athletes/",
        json={"name": "Jane Doe", "email": "jane@example.com"}
    )
    
    response = client.get("/api/v1/athletes/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_athlete(client):
    """Test getting a specific athlete"""
    create_response = client.post(
        "/api/v1/athletes/",
        json={"name": "Bob Smith", "email": "bob@example.com"}
    )
    athlete_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/athletes/{athlete_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "bob@example.com"


def test_update_athlete(client):
    """Test updating an athlete"""
    create_response = client.post(
        "/api/v1/athletes/",
        json={"name": "Old Name", "email": "old@example.com"}
    )
    athlete_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/v1/athletes/{athlete_id}",
        json={"name": "New Name", "email": "new@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["email"] == "new@example.com"


def test_delete_athlete(client):
    """Test deleting an athlete"""
    create_response = client.post(
        "/api/v1/athletes/",
        json={"name": "Delete Me", "email": "delete@example.com"}
    )
    athlete_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/athletes/{athlete_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/v1/athletes/{athlete_id}")
    assert get_response.status_code == 404


def test_create_session(client):
    """Test creating a session"""
    athlete_res = client.post("/api/v1/athletes/", json={"name": "Runner", "email": "run@example.com"})
    athlete_id = athlete_res.json()["id"]
    
    response = client.post(
        "/api/v1/sessions/",
        json={
            "athlete_id": athlete_id,
            "sport": "Running",
            "duration": 45.0,
            "distance": 8.5,
            "intensity": 7
        }
    )
    assert response.status_code == 201
    assert response.json()["sport"] == "Running"
    assert response.json()["athlete_id"] == athlete_id


def test_create_sleep_log(client):
    """Test creating a sleep log"""
    athlete_res = client.post("/api/v1/athletes/", json={"name": "Sleeper", "email": "sleep@example.com"})
    athlete_id = athlete_res.json()["id"]
    
    response = client.post(
        "/api/v1/sleep-logs/",
        json={
            "athlete_id": athlete_id,
            "sleep_hours": 8.5,
            "sleep_quality": 4,
            "date": "2026-02-18"
        }
    )
    assert response.status_code == 201
    assert response.json()["sleep_hours"] == 8.5
    assert response.json()["sleep_quality"] == 4


def test_create_checkin(client):
    """Test creating a check-in"""
    athlete_res = client.post("/api/v1/athletes/", json={"name": "Ready", "email": "ready@example.com"})
    athlete_id = athlete_res.json()["id"]
    
    response = client.post(
        "/api/v1/checkins/",
        json={
            "athlete_id": athlete_id,
            "fatigue": 3,
            "stress": 2,
            "mood": 5,
            "soreness": 1,
            "date": "2026-02-18"
        }
    )
    assert response.status_code == 201
    assert response.json()["mood"] == 5


def test_sleep_uniqueness(client):
    """Test 409 Conflict for duplicate sleep logs"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "unique@ex.com"}).json()
    id = ath["id"]
    
    # First post
    res1 = client.post("/api/v1/sleep-logs/", json={"athlete_id": id, "sleep_hours": 8, "date": "2026-02-18"})
    assert res1.status_code == 201
    
    # Second post (same day)
    res2 = client.post("/api/v1/sleep-logs/", json={"athlete_id": id, "sleep_hours": 7, "date": "2026-02-18"})
    assert res2.status_code == 409


def test_checkin_uniqueness(client):
    """Test 409 Conflict for duplicate check-ins"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "unique2@ex.com"}).json()
    id = ath["id"]
    
    # First post
    res1 = client.post("/api/v1/checkins/", json={"athlete_id": id, "fatigue": 5, "stress": 4, "mood": 6, "soreness": 2, "date": "2026-02-18"})
    assert res1.status_code == 201
    
    # Second post (same day)
    res2 = client.post("/api/v1/checkins/", json={"athlete_id": id, "fatigue": 1, "stress": 1, "mood": 1, "soreness": 1, "date": "2026-02-18"})
    assert res2.status_code == 409


def test_nested_endpoints(client):
    """Test Phase 4 nested endpoints /athletes/{id}/sleep and /checkins"""
    ath = client.post("/api/v1/athletes/", json={"name": "Nested", "email": "nested@ex.com"}).json()
    id = ath["id"]
    
    # POST /athletes/{id}/sleep
    res_sleep = client.post(f"/api/v1/athletes/{id}/sleep", json={"athlete_id": id, "sleep_hours": 9, "sleep_quality": 5, "date": "2026-02-18"})
    assert res_sleep.status_code == 201
    
    # POST /athletes/{id}/checkins
    res_ci = client.post(f"/api/v1/athletes/{id}/checkins", json={"athlete_id": id, "fatigue": 2, "stress": 2, "mood": 8, "soreness": 3, "date": "2026-02-18"})
    assert res_ci.status_code == 201


def test_list_sessions_filtered(client):
    """Test listing sessions filtered by athlete_id"""
    res1 = client.post("/api/v1/athletes/", json={"name": "A1", "email": "a1@example.com"})
    res2 = client.post("/api/v1/athletes/", json={"name": "A2", "email": "a2@example.com"})
    id1, id2 = res1.json()["id"], res2.json()["id"]
    
    client.post("/api/v1/sessions/", json={"athlete_id": id1, "sport": "Run", "duration": 30})
    client.post("/api/v1/sessions/", json={"athlete_id": id2, "sport": "Bike", "duration": 60})
    
    response = client.get(f"/api/v1/sessions/?athlete_id={id1}")
    assert len(response.json()) == 1
    assert response.json()[0]["sport"] == "Run"


def test_update_sleep_log(client):
    """Test updating a sleep log"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    log = client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 8, "sleep_quality": 4}).json()
    
    res = client.put(f"/api/v1/sleep-logs/{log['id']}", json={"sleep_hours": 9})
    assert res.status_code == 200
    assert res.json()["sleep_hours"] == 9


def test_athlete_pagination(client):
    """Test athlete pagination"""
    for i in range(15):
        client.post("/api/v1/athletes/", json={"name": f"Athlete {i}", "email": f"a{i}@test.com"})
    
    # Page 1
    response = client.get("/api/v1/athletes/?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 10
    
    # Page 2
    response = client.get("/api/v1/athletes/?skip=10&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_session_filtering_sport(client):
    """Test session filtering by sport"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30})
    client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Bike", "duration": 60})
    
    response = client.get("/api/v1/sessions/?sport=Run")
    assert len(response.json()) == 1
    assert response.json()[0]["sport"] == "Run"


def test_sleep_filtering_date(client):
    """Test sleep log filtering by date"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "filt@ex.com"}).json()
    client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 8, "date": "2026-01-01"})
    client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "sleep_hours": 7, "date": "2026-01-02"})
    
    # Test from_date
    res = client.get("/api/v1/sleep-logs/?from_date=2026-01-02")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["date"] == "2026-01-02"
