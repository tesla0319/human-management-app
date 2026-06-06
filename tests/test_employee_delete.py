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


class TestEmployeeDelete:
    def test_delete_employee(self, client):
        created = client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル",
            "joined_date": "2024-01-01",
            "active": True,
        })
        employee_id = created.json()["id"]

        response = client.delete(f"/api/employees/{employee_id}")

        assert response.status_code == 204

    def test_delete_employee_not_found(self, client):
        response = client.delete("/api/employees/999")

        assert response.status_code == 404

    def test_delete_employee_removed_from_list(self, client):
        created = client.post("/api/employees", json={
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル",
            "joined_date": "2024-01-01",
            "active": True,
        })
        employee_id = created.json()["id"]

        client.delete(f"/api/employees/{employee_id}")
        response = client.get("/api/employees")

        assert response.status_code == 200
        assert response.json() == []
