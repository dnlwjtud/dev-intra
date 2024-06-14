from fastapi import APIRouter, status, Response

from apps.core.models import DefaultResponseModel, ResultCode
from apps.dockers.exceptions import DockerException
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, PullDockerImageRequest
from apps.dockers.app import docker_manager

router: APIRouter = APIRouter(
    prefix="/dockers"
)

@router.get("/containers/{container_id}", response_model=DockerContainerListItem)
async def get_container_by_id(container_id: str):
    return docker_manager.inspect_container_by_id(container_id)

@router.post("/images", status_code=status.HTTP_201_CREATED, response_model=DefaultResponseModel)
def pull_image(req: PullDockerImageRequest, response: Response):
    try:
        result = docker_manager.pull_image(
            name=req.name,
            tag=req.tag
        )
        return DefaultResponseModel(
            status=result.status,
            msg=result.raw_output,
            data=result.output
        )
    except DockerException as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DefaultResponseModel(
            status=ResultCode.BAD,
            msg=e.err_msg,
            data=None
        )


