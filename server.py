import json

from fastapi import FastAPI, Request, Form
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from functions import Functions
import configparser

app = FastAPI()
templates = Jinja2Templates(directory="templates")
config = configparser.ConfigParser()
config.read(['config.dev.cfg'])
azure_settings = config['azure']
functions = Functions(azure_settings)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/documentation", response_class=HTMLResponse)
async def documentation(request: Request):
    return templates.TemplateResponse("documentation.html", {"request": request})

@app.get("/students", response_class=HTMLResponse)
async def students(request: Request):
    students = await Functions.get_students(functions)
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

@app.get("/{student}/studentprofile", response_class=HTMLResponse)
async def student_profile(request: Request, student: str):
    student_profile = await Functions.get_student_profile_properties(functions,student)
    update_urls = {property: app.url_path_for('update_student_property', student=student, property_name=property) for property
                   in student_profile}
    return templates.TemplateResponse("student_profile.html", {"request": request, "student_profile": student_profile, "update_urls": update_urls, "student": student})

@app.post("/{student}/studentprofile/{property_name}")
async def update_student_property(request: Request, student: str, property_name: str):
    form_data = await request.form()
    property_value = form_data.get('property_value')
    await Functions.update_student_profile_properties(functions,property_name, property_value, student)
    return RedirectResponse(url=f'/{student}/studentprofile', status_code=303)

@app.get("/view_courses", response_class=HTMLResponse)
async def view_courses(request: Request):
    courses = await Functions.get_courses(functions, config)
    return templates.TemplateResponse("view_courses.html", {"request": request, "courses": courses})

@app.get("/courses/{course}/viewstudents", response_class=HTMLResponse)
async def view_students_in_a_course(request:Request, course:str):
    students = await Functions.view_students_in_a_course(functions,course)
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

@app.post("/courses/{course}/addstudents", response_class=HTMLResponse)
async def add_students(request:Request, course: str, students: List[str] = Form(...)):
    students = json.loads(students[0])
    for value in students:
        await Functions.add_student_to_course_singular(functions,value,course)

@app.get("/courses/{course}/courseprofile", response_class=HTMLResponse)
async def course_profile(request: Request, course: str):
    course_profile = await Functions.get_course_profile_properties(functions,course)
    update_urls = {property: app.url_path_for('update_course_property', course=course, property_name=property) for property
                   in course_profile}

    return templates.TemplateResponse("course_profile.html", {"request": request, "course_profile": course_profile, "update_urls": update_urls, "course": course})

@app.post("/courses/{course}/courseprofile/{property_name}")
async def update_course_property(request: Request, course: str, property_name: str):
    form_data = await request.form()
    property_value = form_data.get('property_value')
    await Functions.update_student_profile_properties(functions,property_name, property_value, course)
    return RedirectResponse(url=f'/courses/{course}/courseprofile', status_code=303)


@app.get("/template_student_properties", response_class=HTMLResponse)
async def template_student_properties(request: Request):
    template_student_properties = await Functions.show_template_student_properties(functions,config)
    return templates.TemplateResponse("template_student_properties.html", {"request": request, "template_student_properties": template_student_properties})
@app.post("/template_student_properties")
async def add_template_student_property(request:Request):
    form_data = await request.form()
    property_name = form_data.get('property_name')
    await Functions.add_template_student_property(functions,config,property_name)
    return RedirectResponse(url="/template_student_properties", status_code=303)
@app.post("/delete_template_student_property")
async def delete_student_property(request: Request):
    form_data = await request.form()
    property_value = form_data.get("property_value")
    await Functions.delete_student_property(functions,config, property_name=property_value)
    return RedirectResponse(url="/template_student_properties", status_code=303)

@app.get("/template_course_properties", response_class=HTMLResponse)
async def template_course_properties(request: Request):
    template_course_properties = await Functions.get_template_course_properties(functions,config)
    return templates.TemplateResponse("template_course_properties.html", {"request": request, "template_course_properties": template_course_properties})

@app.get("/courses/{course}/addstudents", response_class=HTMLResponse)
async def add_students(request: Request):
    students = await Functions.get_students(functions)
    return templates.TemplateResponse("addstudents.html", {"request": request, "students": students})


