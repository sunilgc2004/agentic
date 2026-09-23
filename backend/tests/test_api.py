import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_playground_endpoint():
    response = client.get("/api/v1/playground")
    assert response.status_code == 200
    assert "LexArbitrate Enterprise Portal" in response.text


def test_projects_crud():
    # Create project
    create_res = client.post("/api/v1/projects", json={
        "name": "Integration Test Project",
        "description": "Test suite project"
    })
    assert create_res.status_code == 200
    project_data = create_res.json()
    project_id = project_data["id"]

    # List projects
    list_res = client.get("/api/v1/projects")
    assert list_res.status_code == 200
    assert any(p["id"] == project_id for p in list_res.json())


def test_applications_crud():
    # First get or create project
    projects = client.get("/api/v1/projects").json()
    project_id = projects[0]["id"]

    # Create application
    app_res = client.post("/api/v1/applications", json={
        "project_id": project_id,
        "name": "Test Application",
        "base_url": "http://localhost:8000/api/v1/playground",
        "default_environment": "qa"
    })
    assert app_res.status_code == 200
    app_data = app_res.json()
    assert app_data["name"] == "Test Application"


def test_settings_api():
    get_res = client.get("/api/v1/settings")
    assert get_res.status_code == 200
    settings_data = get_res.json()
    assert "llm_provider" in settings_data

    update_res = client.post("/api/v1/settings", json={"confidence_threshold": 0.75})
    assert update_res.status_code == 200
    assert update_res.json()["settings"]["confidence_threshold"] == 0.75
