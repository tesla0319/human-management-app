from datetime import date

from app import models
from app.database import SessionLocal


class TestEmployeeModel:
    def test_insert_and_select(self, reset_employee_table):
        db = SessionLocal()
        try:
            employee = models.Employee(
                name="田中太郎",
                department="開発部",
                role="エンジニア",
                skill_summary="Python, FastAPI",
                joined_date=date(2024, 1, 1),
                active=True,
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)

            assert employee.id is not None

            fetched = (
                db.query(models.Employee)
                .filter(models.Employee.id == employee.id)
                .first()
            )

            assert fetched is not None
            assert fetched.name == "田中太郎"
            assert fetched.department == "開発部"
            assert fetched.role == "エンジニア"
            assert fetched.skill_summary == "Python, FastAPI"
            assert fetched.joined_date == date(2024, 1, 1)
            assert fetched.active is True
        finally:
            db.close()

    def test_select_returns_none_when_not_found(self, reset_employee_table):
        db = SessionLocal()
        try:
            fetched = (
                db.query(models.Employee).filter(models.Employee.id == 999).first()
            )

            assert fetched is None
        finally:
            db.close()
