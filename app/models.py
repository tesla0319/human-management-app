from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, nullable=False)
    skill_summary = Column(String, nullable=False)
    joined_date = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False, default=True)


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint("employee_id", "skill_name", name="uq_employee_skill"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    years = Column(Integer, nullable=False, default=0)
