from fastapi import FastAPI
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