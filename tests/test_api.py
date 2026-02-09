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


# Phase 1: Basic Tests
def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["phase"] == "Phase 1: Basic Setup"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["phase"] == "1"


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
