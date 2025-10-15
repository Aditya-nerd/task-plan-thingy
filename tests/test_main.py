import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Smart Task Planner API"
    assert data["version"] == "0.1.0"


def test_create_task_plan():
    """Test creating a task plan."""
    goal_data = {
        "goal": "Launch a simple blog website in 2 weeks"
    }
    
    response = client.post("/plan", json=goal_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["goal"] == goal_data["goal"]
    assert "title" in data
    assert "tasks" in data
    assert len(data["tasks"]) > 0
    assert "id" in data


def test_get_task_plan():
    """Test retrieving a task plan."""
    # First create a plan
    goal_data = {"goal": "Create a mobile app"}
    create_response = client.post("/plan", json=goal_data)
    plan_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/plans/{plan_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == plan_id
    assert data["goal"] == goal_data["goal"]


def test_list_task_plans():
    """Test listing all task plans."""
    response = client.get("/plans")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_update_task_status():
    """Test updating task status."""
    # First create a plan
    goal_data = {"goal": "Write a book"}
    create_response = client.post("/plan", json=goal_data)
    plan_data = create_response.json()
    
    if plan_data["tasks"]:
        task_id = plan_data["tasks"][0]["id"]
        
        # Update task status
        response = client.put(f"/tasks/{task_id}/status?status=in_progress")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "in_progress"


def test_invalid_task_plan():
    """Test retrieving non-existent task plan."""
    response = client.get("/plans/99999")
    assert response.status_code == 404