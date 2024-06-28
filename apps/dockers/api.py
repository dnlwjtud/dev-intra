import os
import pty
import subprocess

from typing import Callable

from fastapi import APIRouter, status, Response, WebSocket, WebSocketDisconnect

from apps.core.models import DefaultResponseModel, ResultCode
from apps.dockers.exceptions import DockerException, DockerContainerNotFoundException
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, PullDockerImageRequest, \
    RemoveDockerImageRequest
from apps.dockers.app import docker_manager

router: APIRouter = APIRouter(
    prefix="/dockers"
)

def ctrl_container(func: Callable, container_id: str, response: Response) -> DefaultResponseModel:
    try:
        result = func(container_id=container_id)
        return DefaultResponseModel(
            status=result.status,
            msg=f"Successfully performed action on container {container_id}",
            data={
                "target_id": result.raw_output
            }
        )
    except DockerContainerNotFoundException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DefaultResponseModel(
            status=ResultCode.BAD,
            msg=e.err_msg,
            data=None
        )
    except DockerException as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DefaultResponseModel(
            status=ResultCode.BAD,
            msg=e.err_msg,
            data=None
        )

@router.get("/containers/{container_id}", response_model=DockerContainerListItem)
async def get_container_by_id(container_id: str):
    return docker_manager.get_container_list_item(container_id)

@router.put("/containers/{container_id}/stop", response_model=DefaultResponseModel)
def stop_container(container_id: str, response: Response):
    return ctrl_container(func=docker_manager.stop_container
                          , container_id=container_id
                          , response=response)

@router.put("/containers/{container_id}/start", response_model=DefaultResponseModel)
def start_container(container_id: str, response: Response):
    return ctrl_container(func=docker_manager.start_container
                          , container_id=container_id
                          , response=response)

@router.put("/containers/{container_id}/restart", response_model=DefaultResponseModel)
def start_container(container_id: str, response: Response):
    return ctrl_container(func=docker_manager.restart_container
                          , container_id=container_id
                          , response=response)

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


@router.websocket("/containers/{container_id}/ws")
async def access_container(socket: WebSocket, container_id: str):
    await socket.accept()
    try:

        main_fd, sub_fd = pty.openpty()
        subprocess.Popen(
            ['docker', 'exec', '-it', container_id, 'sh']
            , stdin=sub_fd
            , stdout=sub_fd
            , stderr=sub_fd
            , close_fds=True
        )

        os.close(sub_fd)

        while True:
            try:
                req_cmd = await socket.receive_text()
                os.write(main_fd, f'{req_cmd}\n'.encode())
            except WebSocketDisconnect:
                print("Client disconnected")
                break

            try:
                output = os.read(main_fd, 1024).decode()
                await socket.send_text(output)
            except Exception as e:
                print("Error reading from pty:", e)
                break

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("err")
        print(e)


