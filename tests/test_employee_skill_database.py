from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import models
from app.database import SessionLocal


class TestEmployeeSkillModel:
    # employee_skills は employees の子テーブルのため、リセット時は
    # employee_skills → employees の順に削除されるようフィクスチャを並べる
    def test_insert_and_select(self, reset_employee_skill_table, reset_employee_table):
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

            skill = models.EmployeeSkill(
                employee_id=employee.id,
                skill_name="Python",
                years=3,
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)

            assert skill.id is not None

            fetched = (
                db.query(models.EmployeeSkill)
                .filter(models.EmployeeSkill.id == skill.id)
                .first()
            )

            assert fetched is not None
            assert fetched.employee_id == employee.id
            assert fetched.skill_name == "Python"
            assert fetched.years == 3
        finally:
            db.close()

    def test_select_returns_none_when_not_found(self, reset_employee_skill_table, reset_employee_table):
        db = SessionLocal()
        try:
            fetched = (
                db.query(models.EmployeeSkill)
                .filter(models.EmployeeSkill.id == 999)
                .first()
            )

            assert fetched is None
        finally:
            db.close()

    def test_unique_constraint_prevents_duplicate_skill_name(self, reset_employee_skill_table, reset_employee_table):
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

            db.add(models.EmployeeSkill(employee_id=employee.id, skill_name="Python", years=3))
            db.commit()

            db.add(models.EmployeeSkill(employee_id=employee.id, skill_name="Python", years=5))
            with pytest.raises(IntegrityError):
                db.commit()
            db.rollback()
        finally:
            db.close()
