import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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


# Phase 2: Expanded Tests
def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["phase"] == "Phase 2: Complete CRUD & Core Entities"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["phase"] == "2"


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
            "hours": 8.5,
            "quality": 9
        }
    )
    assert response.status_code == 201
    assert response.json()["hours"] == 8.5
    assert response.json()["athlete_id"] == athlete_id


def test_create_checkin(client):
    """Test creating a check-in"""
    athlete_res = client.post("/api/v1/athletes/", json={"name": "Ready", "email": "ready@example.com"})
    athlete_id = athlete_res.json()["id"]
    
    response = client.post(
        "/api/v1/checkins/",
        json={
            "athlete_id": athlete_id,
            "readiness_score": 85,
            "fatigue": 3,
            "stress": 2,
            "soreness": 1
        }
    )
    assert response.status_code == 201
    assert response.json()["readiness_score"] == 85
    assert response.json()["athlete_id"] == athlete_id


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


def test_update_session(client):
    """Test updating a session"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    sess = client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30}).json()
    
    res = client.put(f"/api/v1/sessions/{sess['id']}", json={"duration": 45})
    assert res.status_code == 200
    assert res.json()["duration"] == 45


def test_delete_session(client):
    """Test deleting a session"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    sess = client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30}).json()
    
    res = client.delete(f"/api/v1/sessions/{sess['id']}")
    assert res.status_code == 204


def test_update_sleep_log(client):
    """Test updating a sleep log"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    log = client.post("/api/v1/sleep-logs/", json={"athlete_id": ath["id"], "hours": 8}).json()
    
    res = client.put(f"/api/v1/sleep-logs/{log['id']}", json={"hours": 9})
    assert res.status_code == 200
    assert res.json()["hours"] == 9


def test_update_checkin(client):
    """Test updating a check-in"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    ci = client.post("/api/v1/checkins/", json={"athlete_id": ath["id"], "fatigue": 5}).json()
    
    res = client.put(f"/api/v1/checkins/{ci['id']}", json={"fatigue": 2})
    assert res.status_code == 200
    assert res.json()["fatigue"] == 2


def test_athlete_cascade_delete(client):
    """Test that deleting an athlete deletes their associated data"""
    ath = client.post("/api/v1/athletes/", json={"name": "A", "email": "a@ex.com"}).json()
    client.post("/api/v1/sessions/", json={"athlete_id": ath["id"], "sport": "Run", "duration": 30})
    
    client.delete(f"/api/v1/athletes/{ath['id']}")
    
    res = client.get(f"/api/v1/sessions/?athlete_id={ath['id']}")
    assert len(res.json()) == 0
