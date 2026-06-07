import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_employees(reset_employee_table):
    pass


class TestEmployeeSearch:
    def test_search_by_department(self, client):
        client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル",
            "joined_date": "2024-01-01",
        })
        client.post("/api/employees", json={
            "name": "鈴木次郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python",
            "joined_date": "2024-02-01",
        })

        response = client.get("/api/employees?department=営業部")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "田中太郎"

    def test_search_no_match_returns_empty(self, client):
        client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル",
            "joined_date": "2024-01-01",
        })

        response = client.get("/api/employees?department=存在しない部署")

        assert response.status_code == 200
        assert response.json() == []

    def test_search_without_department_returns_all(self, client):
        client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル",
            "joined_date": "2024-01-01",
        })
        client.post("/api/employees", json={
            "name": "鈴木次郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python",
            "joined_date": "2024-02-01",
        })

        response = client.get("/api/employees")

        assert response.status_code == 200
        assert len(response.json()) == 2
