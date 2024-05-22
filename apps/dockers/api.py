from fastapi import APIRouter

from apps.dockers.models import DockerContainer, DockerContainerDetail
from apps.dockers.app import docker_manager

router: APIRouter = APIRouter(
    prefix="/dockers"
)

@router.get("/{container_id}", response_model=DockerContainer)
async def get_container_by_id(container_id: str):
    return docker_manager.inspect_container_by_id(container_id)

