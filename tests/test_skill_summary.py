import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_employees():
    import app.main as main

    main.employees_db.clear()
    main.next_id = 1


class TestSkillSummary:
    def test_skill_count(self, client):
        client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python, FastAPI, Docker",
            "joined_date": "2024-01-01",
        })
        client.post("/api/employees", json={
            "name": "鈴木次郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python, AWS",
            "joined_date": "2024-02-01",
        })

        response = client.get("/api/skills/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["Python"] == 2
        assert data["FastAPI"] == 1
        assert data["Docker"] == 1
        assert data["AWS"] == 1

    def test_whitespace_stripped(self, client):
        client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python,  FastAPI ,Docker",
            "joined_date": "2024-01-01",
        })

        response = client.get("/api/skills/summary")

        assert response.status_code == 200
        data = response.json()
        assert "Python" in data
        assert "FastAPI" in data
        assert "Docker" in data

    def test_duplicate_within_same_employee_counted_once(self, client):
        client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python, Python, FastAPI",
            "joined_date": "2024-01-01",
        })

        response = client.get("/api/skills/summary")

        assert response.status_code == 200
        assert response.json()["Python"] == 1

    def test_empty_returns_empty_dict(self, client):
        response = client.get("/api/skills/summary")

        assert response.status_code == 200
        assert response.json() == {}
