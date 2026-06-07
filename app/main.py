from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date

from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# インメモリストレージ
employees_db = []
next_id = 1


class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1)  # 空文字を拒否
    department: str
    role: str
    skill_summary: str
    joined_date: date
    active: Optional[bool] = True


class Employee(BaseModel):
    id: int
    name: str
    department: str
    role: str
    skill_summary: str
    joined_date: date
    active: bool


@app.get("/api/skills/summary", response_model=Dict[str, int])
def get_skill_summary():
    counts: Dict[str, int] = {}
    for emp in employees_db:
        skills = {s.strip() for s in emp.skill_summary.split(",") if s.strip()}
        for skill in skills:
            counts[skill] = counts.get(skill, 0) + 1
    return counts


@app.get("/api/employees", response_model=List[Employee])
def get_employees(department: Optional[str] = None):
    if department is None:
        return employees_db
    return [emp for emp in employees_db if emp.department == department]


@app.get("/api/employees/match", response_model=List[Employee])
def match_employees(
    skill: Optional[str] = None,
    experience: Optional[str] = None,
    role: Optional[str] = None,
):
    result = employees_db
    if skill is not None:
        result = [emp for emp in result if skill in emp.skill_summary]
    if experience is not None:
        result = [emp for emp in result if experience in emp.skill_summary]
    if role is not None:
        result = [emp for emp in result if emp.role == role]
    return result


@app.get("/api/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int):
    for emp in employees_db:
        if emp.id == employee_id:
            return emp
    raise HTTPException(status_code=404, detail="Employee not found")


@app.put("/api/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee: EmployeeCreate):
    for i, emp in enumerate(employees_db):
        if emp.id == employee_id:
            updated = Employee(id=employee_id, **employee.model_dump())
            employees_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Employee not found")


@app.delete("/api/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: int):
    for i, emp in enumerate(employees_db):
        if emp.id == employee_id:
            employees_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Employee not found")


@app.post("/api/employees", status_code=201, response_model=Employee)
def create_employee(employee: EmployeeCreate):
    global next_id
    
    new_employee = Employee(
        id=next_id,
        name=employee.name,
        department=employee.department,
        role=employee.role,
        skill_summary=employee.skill_summary,
        joined_date=employee.joined_date,
        active=employee.active
    )
    
    employees_db.append(new_employee)
    next_id += 1
    
    return new_employee