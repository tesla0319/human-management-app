import pytest

from app import models
from app.database import SessionLocal, engine

# テーブルが存在しない状態でreset_employee_tableが呼ばれないようにする
models.Base.metadata.create_all(bind=engine)


@pytest.fixture
def reset_employee_table():
    """SQLiteのemployeesテーブルを空の状態にする"""
    db = SessionLocal()
    try:
        db.query(models.Employee).delete()
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def reset_employee_skill_table():
    """SQLiteのemployee_skillsテーブルを空の状態にする"""
    db = SessionLocal()
    try:
        db.query(models.EmployeeSkill).delete()
        db.commit()
    finally:
        db.close()
    yield
