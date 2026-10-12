# Students Database CRUD Application

**Internship Project Assignment — Python Backend Development**

A simple REST API for managing student records using Python, FastAPI, and SQLite. It supports Create, Read, Update, and Delete (CRUD) operations.

## Features

- Add student records
- List all students
- Filter students by name or course
- Retrieve one student by ID
- Update student details
- Delete a student
- SQLite database persistence
- Input validation and 404 errors for missing students
- Interactive API documentation

## Requirements

- Python 3.10 or newer
- Internet connection for installing dependencies the first time

## Setup

Open a terminal in the project folder and run:

### Windows
```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs in your browser to test the API.

The `students.db` SQLite file is created automatically the first time the application starts.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List/filter students |
| GET | `/students/{student_id}` | Get one student |
| PUT | `/students/{student_id}` | Update a student |
| DELETE | `/students/{student_id}` | Delete a student |

## Sample request

Use `POST /students` with this JSON body:

```json
{
  "name": "Aarav Patil",
  "date_of_birth": "2006-05-14",
  "email": "aarav@example.com",
  "phone": "9876543210",
  "course": "Engineering",
  "address": "Loni",
  "enrollment_date": "2026-08-01"
}
```

This is fictional sample data. Do not use real students' personal information for testing.

## Filtering examples

- `/students?name=Aarav`
- `/students?course=Engineering`
- `/students?name=Aarav&course=Engineering`

## Error handling

- `404 Student not found` when a requested ID does not exist
- `422` for invalid data, invalid email, or missing both email and phone
- `400` if an update request contains no fields

## Project structure

```text
students_crud_project/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## GitHub upload

1. Create a new GitHub repository.
2. Upload the project files (do not upload `.venv/` or `students.db`).
3. Add this README and `requirements.txt`.
4. Copy the repository URL and submit it through the channel announced by your trainer.

## Security notes

- Use fictional/sample data only.
- Do not commit passwords, API keys, or real student personal data.
- This project does not include the optional Ollama AI extension; the assignment says the AI extension is optional.
