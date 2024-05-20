from fastapi import APIRouter

from apps.inspector.models import DockerContainer
from apps.inspector.app import docker_container_manager as docker_manager

router: APIRouter = APIRouter(
    prefix="/containers"
)

@router.get("/{container_id}", response_model=DockerContainer)
async def get_container_by_id(container_id: str):
    return docker_manager.inspect_container_by_id(container_id)

