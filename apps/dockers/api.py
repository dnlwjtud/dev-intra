from fastapi import APIRouter

from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, PullDockerImageRequest
from apps.dockers.app import docker_manager

router: APIRouter = APIRouter(
    prefix="/dockers"
)

@router.get("/containers/{container_id}", response_model=DockerContainerListItem)
async def get_container_by_id(container_id: str):
    return docker_manager.inspect_container_by_id(container_id)

@router.post("/images")
def pull_image(req: PullDockerImageRequest):
    result = docker_manager.docker_pull_image(
        name=req.name,
        tag=req.tag
    )
    print(f'result: {result}')
    return {
        "status": "success"
    }


