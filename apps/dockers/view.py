from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from apps.core.handler import handle_err_page
from apps.core.settings import templates
from apps.dockers.app import docker_manager

router = APIRouter()

@router.get("/{container_id}", response_class=HTMLResponse)
async def show_container_details(container_id: str, request: Request):
    detail = docker_manager.inspect_container_detail(container_id=container_id)
    return templates.TemplateResponse(
        request=request,
        name="/docker/container_detail.html",
        context={
            "container": detail
        }
    ) if detail else handle_err_page(request, templates, status.HTTP_404_NOT_FOUND, "Container could not find")

