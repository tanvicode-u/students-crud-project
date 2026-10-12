from contextlib import asynccontextmanager
from datetime import date
import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "students.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT,
                CHECK (email IS NOT NULL OR phone IS NOT NULL)
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Students Database CRUD API",
    description="A simple student records API built with FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None

    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email address or phone number.")


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    name: str
    date_of_birth: date
    email: Optional[str]
    phone: Optional[str]
    course: Optional[str]
    address: Optional[str]
    enrollment_date: Optional[date]


def row_to_student(row: sqlite3.Row) -> dict:
    item = dict(row)
    for field in ("date_of_birth", "enrollment_date"):
        if item.get(field):
            item[field] = date.fromisoformat(item[field])
    return item


@app.get("/")
def home():
    return {
        "message": "Students Database CRUD API is running.",
        "docs": "/docs",
        "operations": ["Create", "Read", "Update", "Delete"],
    }


@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate):
    if not student.email and not student.phone:
        raise HTTPException(
            status_code=422,
            detail="Provide at least an email address or phone number.",
        )
    values = student.model_dump(mode="json")
    columns = [
        "name", "date_of_birth", "email", "phone",
        "course", "address", "enrollment_date"
    ]
    with get_connection() as connection:
        cursor = connection.execute(
            f"INSERT INTO students ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
            [values.get(column) for column in columns],
        )
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (cursor.lastrowid,)
        ).fetchone()
    return row_to_student(row)


@app.get("/students", response_model=list[StudentOut])
def list_students(
    name: Optional[str] = Query(default=None, description="Filter by part of a student's name"),
    course: Optional[str] = Query(default=None, description="Filter by course"),
):
    sql = "SELECT * FROM students WHERE 1=1"
    params = []
    if name:
        sql += " AND name LIKE ?"
        params.append(f"%{name}%")
    if course:
        sql += " AND course LIKE ?"
        params.append(f"%{course}%")
    sql += " ORDER BY student_id"
    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()
    return [row_to_student(row) for row in rows]


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return row_to_student(row)


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student: StudentUpdate):
    updates = student.model_dump(exclude_unset=True, mode="json")
    if not updates:
        raise HTTPException(status_code=400, detail="No update fields provided")

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Student not found")

        merged_email = updates.get("email", existing["email"])
        merged_phone = updates.get("phone", existing["phone"])
        if not merged_email and not merged_phone:
            raise HTTPException(
                status_code=422,
                detail="A student must have at least an email address or phone number.",
            )

        allowed = {
            "name", "date_of_birth", "email", "phone",
            "course", "address", "enrollment_date"
        }
        fields = [(key, value) for key, value in updates.items() if key in allowed]
        if fields:
            assignments = ", ".join(f"{key} = ?" for key, _ in fields)
            values = [value for _, value in fields]
            values.append(student_id)
            connection.execute(
                f"UPDATE students SET {assignments} WHERE student_id = ?", values
            )
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    return row_to_student(row)


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,)
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully", "student_id": student_id}
