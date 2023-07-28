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

@app.get("/users", response_class=HTMLResponse)
async def users(request: Request):
    users = await Functions.get_users(functions)
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.get("/{user}/userprofile", response_class=HTMLResponse)
async def user_profile(request: Request, user: str):
    user_profile = await Functions.get_user_profile_properties(functions,user)
    update_urls = {property: app.url_path_for('update_user_property', user=user, property_name=property) for property
                   in user_profile}
    return templates.TemplateResponse("user_profile.html", {"request": request, "user_profile": user_profile, "update_urls": update_urls, "user": user})

@app.post("/{user}/userprofile/{property_name}")
async def update_user_property(request: Request, user: str, property_name: str):
    form_data = await request.form()
    property_value = form_data.get('property_value')
    await Functions.update_user_profile_properties(functions,property_name, property_value, user)
    return RedirectResponse(url=f'/{user}/userprofile', status_code=303)

@app.get("/view_groups", response_class=HTMLResponse)
async def view_groups(request: Request):
    groups = await Functions.get_groups(functions, config)
    return templates.TemplateResponse("view_groups.html", {"request": request, "groups": groups})

@app.get("/groups/{group}/viewusers", response_class=HTMLResponse)
async def view_users_in_a_group(request:Request, group:str):
    users = await Functions.view_users_in_a_group(functions,group)
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.post("/groups/{group}/addusers", response_class=HTMLResponse)
async def add_users(request:Request, group: str, users: List[str] = Form(...)):
    users = json.loads(users[0])
    for value in users:
        await Functions.add_user_to_group_singular(functions,value,group)

@app.get("/groups/{group}/groupprofile", response_class=HTMLResponse)
async def group_profile(request: Request, group: str):
    group_profile = await Functions.get_group_profile_properties(functions,group)
    update_urls = {property: app.url_path_for('update_group_property', group=group, property_name=property) for property
                   in group_profile}

    return templates.TemplateResponse("group_profile.html", {"request": request, "group_profile": group_profile, "update_urls": update_urls, "group": group})

@app.post("/groups/{group}/groupprofile/{property_name}")
async def update_group_property(request: Request, group: str, property_name: str):
    form_data = await request.form()
    property_value = form_data.get('property_value')
    await Functions.update_user_profile_properties(functions,property_name, property_value, group)
    return RedirectResponse(url=f'/groups/{group}/groupprofile', status_code=303)


@app.get("/template_user_properties", response_class=HTMLResponse)
async def template_user_properties(request: Request):
    template_user_properties = await Functions.show_template_user_properties(functions,config)
    return templates.TemplateResponse("template_user_properties.html", {"request": request, "template_user_properties": template_user_properties})
@app.post("/template_user_properties")
async def add_template_user_property(request:Request):
    form_data = await request.form()
    property_name = form_data.get('property_name')
    await Functions.add_template_user_property(functions,config,property_name)
    return RedirectResponse(url="/template_user_properties", status_code=303)
@app.post("/delete_template_user_property")
async def delete_user_property(request: Request):
    form_data = await request.form()
    property_value = form_data.get("property_value")
    await Functions.delete_user_property(functions,config, property_name=property_value)
    return RedirectResponse(url="/template_user_properties", status_code=303)

@app.get("/template_group_properties", response_class=HTMLResponse)
async def template_group_properties(request: Request):
    template_group_properties = await Functions.get_template_group_properties(functions,config)
    return templates.TemplateResponse("template_group_properties.html", {"request": request, "template_group_properties": template_group_properties})

@app.get("/groups/{group}/addusers", response_class=HTMLResponse)
async def add_users(request: Request):
    users = await Functions.get_users(functions)
    return templates.TemplateResponse("addusers.html", {"request": request, "users": users})


