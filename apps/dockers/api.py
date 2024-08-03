from fastapi import APIRouter, status, Response

from apps.core.models import DefaultResponseModel, ResultCode
from apps.dockers.exceptions import MessageException

from apps.dockers.app import docker_manager
from apps.dockers.models import DockerContainerStatusRequest, DockerContainerRemoveRequest, DockerNetworkCreateRequest, \
    DockerContainerRunRequest

router: APIRouter = APIRouter(
    prefix="/dockers"
)

@router.get("/containers", response_model=DefaultResponseModel)
async def get_containers():
    return DefaultResponseModel(
        status=status.HTTP_200_OK,
        msg='The list of all docker containers.',
        data=docker_manager.images()
    )

@router.post("/containers/run"
            , response_model=DefaultResponseModel
            , status_code=status.HTTP_201_CREATED)
async def get_containers(req: DockerContainerRunRequest):
    return DefaultResponseModel(
        status=status.HTTP_200_OK,
        msg='Container was successfully run.',
        data=docker_manager.compact_run(**req.dict())
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


@router.post("/networks/new", status_code=status.HTTP_201_CREATED)
def create_network(req: DockerNetworkCreateRequest):
    network = docker_manager.compact_create_network(req=req)
    return DefaultResponseModel(
        status=status.HTTP_201_CREATED,
        msg='Network was successfully created',
        data=network
    )


@router.delete("/networks/{network_id}"
                , status_code=status.HTTP_204_NO_CONTENT)
def remove_network(network_id: str, resp: Response):
    result = docker_manager.remove_network(network_id=network_id)

    if not result:
        resp.status_code = status.HTTP_400_BAD_REQUEST
        return DefaultResponseModel(
            status=status.HTTP_400_BAD_REQUEST
            , msg='Network was not successfully removed. Please try again.'
            , data=None
        )

    return None


