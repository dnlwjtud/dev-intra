from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from apps.inspector.app import docker_container_manager as docker_manager
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "container_list": docker_manager.inspect_all_container()
        }
    )

