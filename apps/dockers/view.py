from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from apps.core.handler import handle_err_page
from apps.core.settings import templates
from apps.dockers.app import docker_manager
from apps.dockers.exceptions import MessageException

router = APIRouter()


@router.get("/images/new")
def show_dockerfile_edit_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/docker/dockerfile.html",
        context={
        }
    )
@router.get("/containers/new")
def show_run_container_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/docker/container_run.html",
        context={
            "images": docker_manager.images(),
            "networks": docker_manager.docker_networks()
        }
    )

@router.get("/networks/new")
def show_create_network_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/docker/network_create.html",
        context={
        }
    )

@router.get("/containers/{container_id}/connect", response_class=HTMLResponse)
def show_run_container_view(request: Request, container_id: str):
    return templates.TemplateResponse(
        request=request,
        name="/docker/container_connect.html",
        context={
            "container_id": container_id
        }
    )

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
    images = docker_manager.images()
    return templates.TemplateResponse(
        request=request,
        name="/docker/image_list.html",
        context={
            "images": images
        }
    )

@router.get("/images/{image_id}", response_class=HTMLResponse)
async def show_image_detail_view(image_id: str, request: Request):
    image = docker_manager.inspect_image(image_name=image_id)
    return templates.TemplateResponse(
        request=request,
        name="/docker/image_detail.html",
        context={
            "image": image
        }
    )

@router.get("/networks", response_class=HTMLResponse)
async def show_network_list_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/docker/network_list.html",
        context={
            "networks": docker_manager.docker_networks()
        }
    )

@router.get("/networks/{network_id}", response_class=HTMLResponse)
async def show_network_list_view(network_id: str, request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/docker/network_detail.html",
        context={
            "network": docker_manager.docker_network(network_id=network_id)
        }
    )
