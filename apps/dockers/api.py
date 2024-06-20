from fastapi import APIRouter, status, Response

from apps.core.models import DefaultResponseModel, ResultCode
from apps.dockers.exceptions import DockerException
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, PullDockerImageRequest, \
    RemoveDockerImageRequest
from apps.dockers.app import docker_manager

router: APIRouter = APIRouter(
    prefix="/dockers"
)

@router.get("/containers/{container_id}", response_model=DockerContainerListItem)
async def get_container_by_id(container_id: str):
    return docker_manager.get_container_list_item(container_id)


@router.get("/queue/images", response_model=DefaultResponseModel)
async def get_task_queue():
    return DefaultResponseModel(
        status=ResultCode.SUCCESS,
        msg='',
        data=docker_manager.get_queue_tasks()
    )

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

@router.delete("/images/{image_id}")
def remove_image(image_id: str, response: Response):
    try:
        if not docker_manager.has_image(image_id):
            response.status_code = status.HTTP_404_NOT_FOUND
            return DefaultResponseModel(
                status=ResultCode.BAD,
                msg='Could not find such image.',
                data=None
            )
        docker_manager.rmi(image_id=image_id)
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    except DockerException as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DefaultResponseModel(
            status=ResultCode.BAD,
            msg=e.err_msg,
            data=None
        )


