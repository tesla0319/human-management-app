import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_employees(reset_employee_table):
    pass


@pytest.fixture
def employees(client):
    client.post("/api/employees", json={
        "name": "田中太郎",
        "department": "営業部",
        "role": "営業",
        "skill_summary": "Python, 顧客対応, 営業スキル",
        "joined_date": "2024-01-01",
    })
    client.post("/api/employees", json={
        "name": "鈴木次郎",
        "department": "開発部",
        "role": "エンジニア",
        "skill_summary": "Python, FastAPI, Docker",
        "joined_date": "2024-02-01",
    })
    client.post("/api/employees", json={
        "name": "佐藤三郎",
        "department": "開発部",
        "role": "エンジニア",
        "skill_summary": "Java, Spring, Docker",
        "joined_date": "2024-03-01",
    })


class TestEmployeeMatch:
    def test_match_by_skill(self, client, employees):
        response = client.get("/api/employees/match?skill=Python")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "田中太郎" in names
        assert "鈴木次郎" in names
        assert "佐藤三郎" not in names

    def test_match_by_experience(self, client, employees):
        response = client.get("/api/employees/match?experience=Docker")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" in names
        assert "佐藤三郎" in names
        assert "田中太郎" not in names

    def test_match_by_role(self, client, employees):
        response = client.get("/api/employees/match?role=エンジニア")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" in names
        assert "佐藤三郎" in names
        assert "田中太郎" not in names

    def test_match_and_condition(self, client, employees):
        response = client.get("/api/employees/match?skill=Python&role=エンジニア")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" in names
        assert "田中太郎" not in names
        assert "佐藤三郎" not in names

    def test_match_no_params_returns_all(self, client, employees):
        response = client.get("/api/employees/match")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_match_no_result_returns_empty(self, client, employees):
        response = client.get("/api/employees/match?skill=COBOL")

        assert response.status_code == 200
        assert response.json() == []
