from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Literal
from datetime import date

from app import models
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1)  # 空文字を拒否
    department: str
    role: str
    skill_summary: str
    joined_date: date
    active: Optional[bool] = True


class Employee(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    department: str
    role: str
    skill_summary: str
    joined_date: date
    active: bool


class EmployeeSkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=1)
    years: int = Field(..., ge=0)


class EmployeeSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    skill_name: str
    years: int


@app.get("/api/skills/summary", response_model=Dict[str, int])
def get_skill_summary(db: Session = Depends(get_db)):
    counts: Dict[str, int] = {}
    for emp in db.query(models.Employee).all():
        skills = {s.strip() for s in emp.skill_summary.split(",") if s.strip()}
        for skill in skills:
            counts[skill] = counts.get(skill, 0) + 1
    return counts


@app.get("/api/employees", response_model=List[Employee])
def get_employees(department: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Employee)
    if department is not None:
        query = query.filter(models.Employee.department == department)
    return query.all()


@app.get("/api/employees/match", response_model=List[Employee])
def match_employees(
    skill: Optional[List[str]] = Query(None),
    skill_match: Literal["and", "or"] = "and",
    experience: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Employee)
    if role is not None:
        query = query.filter(models.Employee.role == role)
    result = query.all()
    if skill:
        if skill_match == "or":
            result = [emp for emp in result if any(s in emp.skill_summary for s in skill)]
        else:
            result = [emp for emp in result if all(s in emp.skill_summary for s in skill)]
    if experience is not None:
        result = [emp for emp in result if experience in emp.skill_summary]
    return result


@app.get("/api/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@app.put("/api/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in employee.model_dump().items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return emp


@app.delete("/api/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()


@app.post("/api/employees", status_code=201, response_model=Employee)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = models.Employee(**employee.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@app.post("/api/employees/{employee_id}/skills", status_code=201, response_model=EmployeeSkill)
def create_employee_skill(employee_id: int, skill: EmployeeSkillCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.skill_name == skill.skill_name,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Skill already registered")

    new_skill = models.EmployeeSkill(employee_id=employee_id, **skill.model_dump())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@app.get("/api/employees/{employee_id}/skills", response_model=List[EmployeeSkill])
def get_employee_skills(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return (
        db.query(models.EmployeeSkill)
        .filter(models.EmployeeSkill.employee_id == employee_id)
        .all()
    )


@app.put("/api/employees/{employee_id}/skills/{skill_id}", response_model=EmployeeSkill)
def update_employee_skill(employee_id: int, skill_id: int, skill: EmployeeSkillCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    target = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.id == skill_id,
            models.EmployeeSkill.employee_id == employee_id,
        )
        .first()
    )
    if target is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    duplicate = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.skill_name == skill.skill_name,
            models.EmployeeSkill.id != skill_id,
        )
        .first()
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="Skill already registered")

    target.skill_name = skill.skill_name
    target.years = skill.years
    db.commit()
    db.refresh(target)
    return target


@app.delete("/api/employees/{employee_id}/skills/{skill_id}", status_code=204)
def delete_employee_skill(employee_id: int, skill_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    target = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.id == skill_id,
            models.EmployeeSkill.employee_id == employee_id,
        )
        .first()
    )
    if target is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(target)
    db.commit()
