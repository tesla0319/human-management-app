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


class TestEmployeeGet:
    def test_get_employee_by_id(self, client):
        payload = {
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル、顧客対応",
            "joined_date": "2024-01-01",
            "active": True,
        }
        created = client.post("/api/employees", json=payload)
        employee_id = created.json()["id"]

        response = client.get(f"/api/employees/{employee_id}")

        assert response.status_code == 200
        assert response.json()["id"] == employee_id
        assert response.json()["name"] == "田中太郎"

    def test_get_employee_not_found(self, client):
        response = client.get("/api/employees/999")

        assert response.status_code == 404
