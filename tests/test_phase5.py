import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from app.main import app
from app.db.session import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test_phase5.db"
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

def test_insights_workflow(client):
    # 1. Create Athlete
    athlete_data = {"name": "Test Insight Athlete", "email": "insight@test.com", "age": 25}
    response = client.post("/api/v1/athletes/", json=athlete_data)
    athlete_id = response.json()["id"]
    
    # 2. Add some sessions to build load
    for i in range(5):
        client.post(f"/api/v1/sessions/", json={
            "athlete_id": athlete_id,
            "sport": "Running",
            "duration": 60,
            "intensity": 7,
            "date": (date.today() - timedelta(days=i)).isoformat()
        })
        
    # 3. Add sleep
    client.post(f"/api/v1/athletes/{athlete_id}/sleep", json={
        "athlete_id": athlete_id,
        "date": date.today().isoformat(),
        "sleep_hours": 8.5,
        "sleep_quality": 4
    })

    # 4. Get Insights
    response = client.get(f"/api/v1/athletes/{athlete_id}/insights/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "readiness_score" in data
    assert "readiness_band" in data
    assert "acute_load_7d" in data["signals"]
    assert len(data["top_reasons"]) > 0
    assert "self" in data["links"]

    # 5. Get Trends
    response = client.get(f"/api/v1/athletes/{athlete_id}/analytics/trends")
    assert response.status_code == 200
    assert len(response.json()["trends"]) == 15 # 0-14 days

    # 6. What-If Simulator
    what_if_data = {
        "planned_session_duration": 90,
        "planned_session_intensity": 8,
        "expected_sleep_hours": 9,
        "expected_sleep_quality": 5
    }
    response = client.post(f"/api/v1/athletes/{athlete_id}/whatif/readiness", json=what_if_data)
    assert response.status_code == 200
    assert "projected_readiness" in response.json()
    assert "change_description" in response.json()
