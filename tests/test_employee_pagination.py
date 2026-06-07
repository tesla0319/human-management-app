import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_employees(reset_employee_table):
    pass


def _create_employee(client, name, department="開発部"):
    return client.post("/api/employees", json={
        "name": name,
        "department": department,
        "role": "エンジニア",
        "skill_summary": "Python",
        "joined_date": "2024-01-01",
    })


class TestEmployeePagination:
    def test_limit_returns_specified_count(self, client):
        """limit=2 を指定すると2件だけ返る"""
        _create_employee(client, "社員1")
        _create_employee(client, "社員2")
        _create_employee(client, "社員3")

        response = client.get("/api/employees?limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_page_returns_second_page(self, client):
        """page=2&limit=2 を指定すると2ページ目（3件目以降）が返る"""
        _create_employee(client, "社員1")
        _create_employee(client, "社員2")
        _create_employee(client, "社員3")

        response = client.get("/api/employees?page=2&limit=2")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert names == ["社員3"]

    def test_department_and_pagination_combined(self, client):
        """departmentで絞り込んだ結果に対してpage/limitが適用される"""
        _create_employee(client, "開発1", department="開発部")
        _create_employee(client, "開発2", department="開発部")
        _create_employee(client, "開発3", department="開発部")
        _create_employee(client, "営業1", department="営業部")

        response = client.get("/api/employees?department=開発部&page=2&limit=2")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert names == ["開発3"]

    def test_page_zero_returns_422(self, client):
        """page=0 はバリデーションエラーになる"""
        response = client.get("/api/employees?page=0")

        assert response.status_code == 422

    def test_limit_zero_returns_422(self, client):
        """limit=0 はバリデーションエラーになる"""
        response = client.get("/api/employees?limit=0")

        assert response.status_code == 422

    def test_limit_over_max_returns_422(self, client):
        """limit=101 はバリデーションエラーになる"""
        response = client.get("/api/employees?limit=101")

        assert response.status_code == 422

    def test_page_beyond_data_returns_empty(self, client):
        """データ件数を超えるpageを指定すると空配列が返る"""
        _create_employee(client, "社員1")
        _create_employee(client, "社員2")

        response = client.get("/api/employees?page=5&limit=20")

        assert response.status_code == 200
        assert response.json() == []
