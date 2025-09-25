import json
import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# JSON File for Data
DATA_FILE = "data.json"


# -----------------------------
# Helper Functions
# -----------------------------
def load_students():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_students(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)


def calculate_grade(marks: float):
    if marks >= 80:
        return "A"
    elif marks >= 60:
        return "B"
    elif marks >= 40:
        return "C"
    else:
        return "Fail"


# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse("/students")


# List Students
@app.get("/students", response_class=HTMLResponse)
def list_students(request: Request):
    students = load_students()
    return templates.TemplateResponse(
        "list_students.html",
        {"request": request, "students": students, "calculate_grade": calculate_grade},
    )


# Add Student Page
@app.get("/students/add", response_class=HTMLResponse)
def add_student_form(request: Request):
    return templates.TemplateResponse(
        "add_student.html", {"request": request, "error": None}
    )


# Add Student Action
@app.post("/students/add", response_class=HTMLResponse)
def add_student(
    request: Request,
    roll_no: str = Form(...),
    name: str = Form(...),
    marks: str = Form(...),
):
    students = load_students()

    # Roll number validation
    if not roll_no.isdigit():
        return templates.TemplateResponse(
            "add_student.html",
            {"request": request, "error": "Roll No must be an integer!"},
        )

    roll_no = int(roll_no)
    if str(roll_no) in students:
        return templates.TemplateResponse(
            "add_student.html",
            {"request": request, "error": f"Roll No {roll_no} already exists!"},
        )

    # Name validation
    if not name.strip() or not name.replace(" ", "").isalpha():
        return templates.TemplateResponse(
            "add_student.html",
            {"request": request, "error": "Invalid name! Only alphabets allowed."},
        )

    # Marks validation
    try:
        marks_val = float(marks)
        if not (0 <= marks_val <= 100):
            return templates.TemplateResponse(
                "add_student.html",
                {"request": request, "error": "Marks must be between 0 and 100."},
            )
    except ValueError:
        return templates.TemplateResponse(
            "add_student.html",
            {"request": request, "error": "Invalid marks! Enter a number."},
        )

    # Save student
    students[str(roll_no)] = {"name": name.strip(), "marks": marks_val}
    save_students(students)

    return RedirectResponse("/students", status_code=303)


# Delete Student
@app.get("/students/delete/{roll_no}")
def delete_student(roll_no: int):
    students = load_students()
    students.pop(str(roll_no), None)
    save_students(students)
    return RedirectResponse("/students", status_code=303)


# Update Student Form
@app.get("/students/update/{roll_no}", response_class=HTMLResponse)
def update_student_form(request: Request, roll_no: int):
    students = load_students()
    student = students.get(str(roll_no))
    if not student:
        return RedirectResponse("/students", status_code=303)
    return templates.TemplateResponse(
        "update_student.html",
        {"request": request, "roll_no": roll_no, "student": student, "error": None},
    )


# Update Student Action
@app.post("/students/update/{roll_no}", response_class=HTMLResponse)
def update_student(
    request: Request, roll_no: int, name: str = Form(""), marks: str = Form("")
):
    students = load_students()

    if str(roll_no) not in students:
        return RedirectResponse("/students", status_code=303)

    # Name update
    if name.strip():
        if not name.replace(" ", "").isalpha():
            return templates.TemplateResponse(
                "update_student.html",
                {
                    "request": request,
                    "roll_no": roll_no,
                    "student": students[str(roll_no)],
                    "error": "Invalid name! Only alphabets allowed.",
                },
            )
        students[str(roll_no)]["name"] = name.strip()

    # Marks update
    if marks.strip():
        try:
            marks_val = float(marks)
            if 0 <= marks_val <= 100:
                students[str(roll_no)]["marks"] = marks_val
            else:
                return templates.TemplateResponse(
                    "update_student.html",
                    {
                        "request": request,
                        "roll_no": roll_no,
                        "student": students[str(roll_no)],
                        "error": "Marks must be between 0 and 100.",
                    },
                )
        except ValueError:
            return templates.TemplateResponse(
                "update_student.html",
                {
                    "request": request,
                    "roll_no": roll_no,
                    "student": students[str(roll_no)],
                    "error": "Invalid marks! Enter a number.",
                },
            )

    save_students(students)
    return RedirectResponse("/students", status_code=303)
