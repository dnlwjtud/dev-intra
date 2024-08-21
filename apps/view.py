from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from apps.dockers.app import docker_manager as docker_manager
from apps.core.settings import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "container_list": docker_manager.docker_containers(is_all=True)
        }
    )

