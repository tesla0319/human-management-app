import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_employees(reset_employee_skill_table, reset_employee_table):
    pass


@pytest.fixture
def employee_id(client):
    created = client.post("/api/employees", json={
        "name": "田中太郎",
        "department": "開発部",
        "role": "エンジニア",
        "skill_summary": "Python, FastAPI",
        "joined_date": "2024-01-01",
    })
    return created.json()["id"]


class TestEmployeeSkillCreate:
    def test_create_employee_skill(self, client, employee_id):
        response = client.post(f"/api/employees/{employee_id}/skills", json={
            "skill_name": "Python",
            "years": 3,
        })

        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["skill_name"] == "Python"
        assert data["years"] == 3
        assert "id" in data

    def test_create_employee_skill_not_found(self, client):
        response = client.post("/api/employees/999/skills", json={
            "skill_name": "Python",
            "years": 3,
        })

        assert response.status_code == 404

    def test_create_employee_skill_name_empty_error(self, client, employee_id):
        response = client.post(f"/api/employees/{employee_id}/skills", json={
            "skill_name": "",
            "years": 3,
        })

        assert response.status_code == 422

    def test_create_employee_skill_years_negative_error(self, client, employee_id):
        response = client.post(f"/api/employees/{employee_id}/skills", json={
            "skill_name": "Python",
            "years": -1,
        })

        assert response.status_code == 422

    def test_create_employee_skill_duplicate_error(self, client, employee_id):
        client.post(f"/api/employees/{employee_id}/skills", json={
            "skill_name": "Python",
            "years": 3,
        })

        response = client.post(f"/api/employees/{employee_id}/skills", json={
            "skill_name": "Python",
            "years": 5,
        })

        assert response.status_code == 409


class TestEmployeeSkillList:
    def test_get_employee_skills(self, client, employee_id):
        client.post(f"/api/employees/{employee_id}/skills", json={"skill_name": "Python", "years": 3})
        client.post(f"/api/employees/{employee_id}/skills", json={"skill_name": "FastAPI", "years": 2})

        response = client.get(f"/api/employees/{employee_id}/skills")

        assert response.status_code == 200
        names = [s["skill_name"] for s in response.json()]
        assert "Python" in names
        assert "FastAPI" in names

    def test_get_employee_skills_empty(self, client, employee_id):
        response = client.get(f"/api/employees/{employee_id}/skills")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_employee_skills_not_found(self, client):
        response = client.get("/api/employees/999/skills")

        assert response.status_code == 404

    def test_get_employee_skills_only_returns_specified_employee(self, client, employee_id):
        other = client.post("/api/employees", json={
            "name": "鈴木次郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Java, Spring",
            "joined_date": "2024-02-01",
        })
        other_id = other.json()["id"]

        client.post(f"/api/employees/{employee_id}/skills", json={"skill_name": "Python", "years": 3})
        client.post(f"/api/employees/{other_id}/skills", json={"skill_name": "Java", "years": 4})

        response = client.get(f"/api/employees/{employee_id}/skills")

        assert response.status_code == 200
        names = [s["skill_name"] for s in response.json()]
        assert names == ["Python"]
