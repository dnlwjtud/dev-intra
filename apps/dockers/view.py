from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from apps.core.handler import handle_err_page
from apps.core.settings import templates
from apps.dockers.app import docker_manager
from apps.dockers.exceptions import MessageException

router = APIRouter()

@router.get("/containers/{container_name}", response_class=HTMLResponse)
async def show_container_details_view(container_name: str, request: Request):
    try:
        find_container = docker_manager.docker_container(container_id=container_name)
        return templates.TemplateResponse(
            request=request,
            name="/docker/container_detail.html",
            context={
                "container": find_container
            }
        )
    except MessageException as e:
        return handle_err_page(request, templates, status.HTTP_404_NOT_FOUND, e.err_msg)


@router.get("/images", response_class=HTMLResponse)
async def show_image_list_view(request: Request):
    images = docker_manager.inspect_all_image()
    return templates.TemplateResponse(
        request=request,
        name="/docker/image_list.html",
        context={
            "images": images
        }
    )

@router.get("/images/{image_id}", response_class=HTMLResponse)
async def show_image_detail_view(image_id: str, request: Request):
    image = docker_manager.inspect_image(image_id=image_id)
    return templates.TemplateResponse(
        request=request,
        name="/docker/image_detail.html",
        context={
            "image": image
        }
    )

