import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestEmployeeList:
    def test_get_employees_empty(self, client):
        response = client.get("/api/employees")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_employees_after_create(self, client):
        payload = {
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル、顧客対応",
            "joined_date": "2024-01-01",
            "active": True,
        }

        create_response = client.post("/api/employees", json=payload)
        response = client.get("/api/employees")

        assert create_response.status_code == 201
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "田中太郎"


@pytest.fixture(autouse=True)
def reset_employees():
    import app.main as main

    main.employees_db.clear()
    main.next_id = 1