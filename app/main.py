from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

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


@app.get("/api/employees", response_model=List[Employee])
def get_employees():
    return employees_db


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