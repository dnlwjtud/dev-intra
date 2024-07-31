from fastapi import APIRouter, status, Response

from apps.core.models import DefaultResponseModel, ResultCode
from apps.dockers.exceptions import MessageException

from apps.dockers.app import docker_manager
from apps.dockers.models import DockerContainerStatusRequest, DockerContainerRemoveRequest

router: APIRouter = APIRouter(
    prefix="/dockers"
)

@router.patch("/containers/{container_id}"
                , response_model=DefaultResponseModel
                , status_code=status.HTTP_202_ACCEPTED)
async def update_container_status(req: DockerContainerStatusRequest
                                  , container_id: str
                                  , resp: Response):
    result = docker_manager.compact_container_action(
        container_id=container_id
        , act_type=req.act_type
    )

    if not result:
        resp.status_code = status.HTTP_400_BAD_REQUEST

    return DefaultResponseModel(
        status=status.HTTP_202_ACCEPTED,
        msg='Container status was successfully updated.',
        data=None
    )

@router.delete("/containers/{container_id}"
               , status_code=status.HTTP_204_NO_CONTENT)
async def remove_container(req: DockerContainerRemoveRequest
                           , container_id: str
                           , resp: Response):
    result = docker_manager.remove_container(
        container_id=container_id
        , is_force=req.force
    )

    if not result:
        resp.status_code = status.HTTP_400_BAD_REQUEST

    return None

@router.delete("/images/{image_id}"
                , status_code=status.HTTP_204_NO_CONTENT)
def remove_image(image_id: str, response: Response):
    try:
        docker_manager.remove_image(image_name=image_id)
        return None
    except MessageException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponseModel(
            status=status.HTTP_404_NOT_FOUND,
            msg=e.err_msg,
            data=None
        )


