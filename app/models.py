from sqlalchemy import Boolean, Column, Date, Integer, String

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
