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

    def test_match_single_skill_backward_compatible(self, client, employees):
        """skillを1件だけ指定した場合は従来と同じ結果になる"""
        response = client.get("/api/employees/match?skill=Python")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "田中太郎" in names
        assert "鈴木次郎" in names
        assert "佐藤三郎" not in names

    def test_match_multiple_skills_and(self, client, employees):
        """複数skill + skill_match=and: 全スキルを保有する社員のみ"""
        response = client.get("/api/employees/match?skill=Python&skill=FastAPI&skill_match=and")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert names == ["鈴木次郎"]

    def test_match_multiple_skills_or(self, client, employees):
        """複数skill + skill_match=or: いずれかのスキルを保有する社員"""
        response = client.get("/api/employees/match?skill=FastAPI&skill=Java&skill_match=or")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" in names
        assert "佐藤三郎" in names
        assert "田中太郎" not in names

    def test_match_multiple_skills_default_is_and(self, client, employees):
        """skill_match省略時はAND条件として扱われる"""
        response = client.get("/api/employees/match?skill=Python&skill=FastAPI")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert names == ["鈴木次郎"]

    def test_match_multiple_skills_or_with_role(self, client, employees):
        """複数skill(OR)とroleを組み合わせた場合、role側はAND結合される"""
        response = client.get(
            "/api/employees/match?skill=Python&skill=Docker&skill_match=or&role=エンジニア"
        )

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" in names
        assert "佐藤三郎" in names
        assert "田中太郎" not in names

    def test_match_multiple_skills_no_result_returns_empty(self, client, employees):
        response = client.get("/api/employees/match?skill=COBOL&skill=Fortran&skill_match=and")

        assert response.status_code == 200
        assert response.json() == []

    def test_match_skill_match_invalid_value_returns_422(self, client, employees):
        """skill_matchに and/or 以外の値を渡すとバリデーションエラーになる"""
        response = client.get("/api/employees/match?skill=Python&skill_match=invalid")

        assert response.status_code == 422


@pytest.fixture
def employees_with_skill_years(client):
    """employee_skillsに経験年数を登録済みの社員2名を作成する
    田中太郎: Python=5年, FastAPI=4年（両方ともmin_years=3を満たす）
    鈴木次郎: Python=2年, FastAPI=5年（Pythonのみmin_years=3を満たさない）
    """
    tanaka = client.post("/api/employees", json={
        "name": "田中太郎",
        "department": "開発部",
        "role": "エンジニア",
        "skill_summary": "Python, FastAPI",
        "joined_date": "2024-01-01",
    }).json()
    suzuki = client.post("/api/employees", json={
        "name": "鈴木次郎",
        "department": "開発部",
        "role": "エンジニア",
        "skill_summary": "Python, FastAPI",
        "joined_date": "2024-02-01",
    }).json()

    client.post(f"/api/employees/{tanaka['id']}/skills", json={"skill_name": "Python", "years": 5})
    client.post(f"/api/employees/{tanaka['id']}/skills", json={"skill_name": "FastAPI", "years": 4})
    client.post(f"/api/employees/{suzuki['id']}/skills", json={"skill_name": "Python", "years": 2})
    client.post(f"/api/employees/{suzuki['id']}/skills", json={"skill_name": "FastAPI", "years": 5})


class TestEmployeeMatchByExperienceYears:
    def test_single_skill_meets_min_years_is_included(self, client, employees_with_skill_years):
        """単一スキルでmin_years以上なら結果に含まれる"""
        response = client.get("/api/employees/match?skill=Python&min_years=3")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "田中太郎" in names

    def test_single_skill_below_min_years_is_excluded(self, client, employees_with_skill_years):
        """単一スキルでmin_years未満なら結果に含まれない"""
        response = client.get("/api/employees/match?skill=Python&min_years=3")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" not in names

    def test_multiple_skills_and_all_meet_min_years_is_included(self, client, employees_with_skill_years):
        """複数スキル+skill_match=andで全スキルがmin_years以上なら結果に含まれる"""
        response = client.get("/api/employees/match?skill=Python&skill=FastAPI&skill_match=and&min_years=3")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "田中太郎" in names

    def test_multiple_skills_and_one_below_min_years_is_excluded(self, client, employees_with_skill_years):
        """複数スキル+skill_match=andで一部スキルがmin_years未満なら結果に含まれない"""
        response = client.get("/api/employees/match?skill=Python&skill=FastAPI&skill_match=and&min_years=3")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" not in names

    def test_multiple_skills_or_one_meets_min_years_is_included(self, client, employees_with_skill_years):
        """複数スキル+skill_match=orでいずれかのスキルがmin_years以上なら結果に含まれる"""
        response = client.get("/api/employees/match?skill=Python&skill=FastAPI&skill_match=or&min_years=3")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "鈴木次郎" in names

    def test_min_years_not_specified_keeps_existing_behavior(self, client, employees_with_skill_years):
        """min_years未指定時はskill_summaryへの部分一致という既存仕様のまま動作する"""
        response = client.get("/api/employees/match?skill=Python")

        assert response.status_code == 200
        names = [e["name"] for e in response.json()]
        assert "田中太郎" in names
        assert "鈴木次郎" in names

    def test_min_years_negative_returns_422(self, client, employees_with_skill_years):
        """min_yearsに負の値を渡すとバリデーションエラーになる"""
        response = client.get("/api/employees/match?skill=Python&min_years=-1")

        assert response.status_code == 422
