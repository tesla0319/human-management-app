import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """テスト用のAPIクライアントを作成"""
    from app.main import app
    
    return TestClient(app)


class TestEmployeeCreate:
    """社員登録機能のテストクラス"""
    
    def test_create_employee_with_name(self, client):
        """nameがある場合に登録できる"""
        payload = {
            "name": "田中太郎",
            "department": "営業部",
            "role": "営業",
            "skill_summary": "営業スキル、顧客対応",
            "joined_date": "2024-01-01",
            "active": True
        }
        
        response = client.post("/api/employees", json=payload)
        
        assert response.status_code == 201
        assert response.json()["name"] == "田中太郎"
        assert response.json()["department"] == "営業部"
    
    def test_create_employee_auto_increment_id(self, client):
        """idが自動採番される"""
        payload = {
            "name": "鈴木次郎",
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python, FastAPI",
            "joined_date": "2024-02-01",
            "active": True
        }
        
        response1 = client.post("/api/employees", json=payload)
        response2 = client.post("/api/employees", json=payload)
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        
        assert id1 is not None
        assert id2 is not None
        assert id1 != id2
        assert id2 > id1
    
    def test_create_employee_active_default_true(self, client):
        """active未指定時はTrue"""
        payload = {
            "name": "佐藤三郎",
            "department": "企画部",
            "role": "企画",
            "skill_summary": "企画、分析",
            "joined_date": "2024-03-01"
            # active は指定しない
        }
        
        response = client.post("/api/employees", json=payload)
        
        assert response.status_code == 201
        assert response.json()["active"] is True
    
    def test_create_employee_name_empty_error(self, client):
        """nameが空の場合エラー"""
        payload = {
            "name": "",  # 空文字列
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python",
            "joined_date": "2024-04-01",
            "active": True
        }
        
        response = client.post("/api/employees", json=payload)
        
        assert response.status_code == 422
    
    def test_create_employee_name_missing_error(self, client):
        """nameが未指定の場合エラー"""
        payload = {
            # name がない
            "department": "開発部",
            "role": "エンジニア",
            "skill_summary": "Python",
            "joined_date": "2024-04-01",
            "active": True
        }
        
        response = client.post("/api/employees", json=payload)
        
        assert response.status_code == 422  # バリデーションエラー
