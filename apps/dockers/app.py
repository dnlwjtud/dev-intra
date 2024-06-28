import asyncio

from fastapi import WebSocket
from subprocess import Popen

from typing import List, Literal

from apps.core.config import PULL_IMAGE_TASK_NAME, MAX_PULLING_TASK_SIZE
from apps.core.models import ResultCode
from apps.core.modules import task_queue

from apps.dockers.constants import CONTAINER, IMAGE, STOP, START, RESTART
from apps.dockers.exceptions import DockerException, DockerImageQueueFullException, \
    DockerImageAlreadyProcessingException, \
    DockerImageNotFoundException, DockerContainerNotFoundException
from apps.dockers.modules import DockerCommandExecuteMixin
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, DockerImageListItem, \
    DockerImageDetail, DockerTemplateCommandOutput, ImageTaskQueueList

class InteractiveCommunicateHelper:

    async def read_data_from_process(self, process: Popen, socket: WebSocket):
        evt_loop = asyncio.get_event_loop()
        while True:
            std_out = await evt_loop.run_in_executor(None, process.stdout.readline)
            if std_out == '' and process.poll() is not None:
                break
            await socket.send_text(std_out)

    async def send_data_from_socket(self, process: Popen, socket: WebSocket):
        while True:
            data = await socket.receive_text()
            process.stdin.write(data + '\n')
            process.stdin.flush()


class DockerContainerManageMixin(DockerCommandExecuteMixin, InteractiveCommunicateHelper):

    def inspect_all_container(self) -> List[DockerContainerListItem]:
        result: DockerTemplateCommandOutput = self.docker_ps(options={'-a': ''})

        if result.status == ResultCode.SUCCESS:
            return [DockerContainerListItem.of(_)for _ in result.output]
        else:
            raise DockerException(msg=result.raw_output)

    def _get_container_by_id(self, container_id: str) -> DockerTemplateCommandOutput:
        return self.docker_ps(options={'-a': '', '-f': f'id={container_id}'})

    def get_container_list_item(self, container_id: str) -> DockerContainerListItem:
        result: DockerTemplateCommandOutput = self._get_container_by_id(container_id=container_id)

        if result.status == ResultCode.SUCCESS:
            if len(result.output) > 0:
                return DockerContainerListItem.of(result.output[0])

        raise DockerException(msg=result.raw_output)

    def inspect_container_detail(self, container_id: str) -> DockerContainerDetail:
        result: DockerTemplateCommandOutput = self.docker_inspect(target=CONTAINER, target_id=container_id)

        if result.status == ResultCode.SUCCESS:
            return DockerContainerDetail.of(result.output)
        else:
            raise DockerException(msg=result.raw_output)

    def has_container(self, container_id: str) -> bool:
        result: DockerTemplateCommandOutput = self._get_container_by_id(container_id=container_id)

        if result.status == ResultCode.SUCCESS:
            if len(result.output) > 0:
                if container_id in result.output[0]:
                    return True

        return False

    def _ctrl_container(self, ctrl_type: Literal['start', 'stop', 'restart'], container_id: str) -> DockerTemplateCommandOutput:

        if ctrl_type not in ['start', 'stop', 'restart']:
            raise ValueError(f"Invalid ctrl_type {ctrl_type} is not supported. Must be 'start', 'stop', or 'restart'.")

        if not self.has_container(container_id=container_id):
            raise DockerContainerNotFoundException()

        control_method = {
            'start': self.docker_start
            , 'stop': self.docker_stop
            , 'restart': self.docker_restart
        }

        result: DockerTemplateCommandOutput = control_method[ctrl_type](container_id=container_id)

        if result.status == ResultCode.SUCCESS and container_id in result.raw_output:
            return result

        raise DockerException(msg=result.raw_output)

    def stop_container(self, container_id: str) -> DockerTemplateCommandOutput:
        return self._ctrl_container(ctrl_type=STOP, container_id=container_id)

    def start_container(self, container_id: str) -> DockerTemplateCommandOutput:
        return self._ctrl_container(ctrl_type=START, container_id=container_id)

    def restart_container(self, container_id: str) -> DockerTemplateCommandOutput:
        return self._ctrl_container(ctrl_type=RESTART, container_id=container_id)

    def access_container(self, socket: WebSocket, container_id: str) -> Popen:
        process = self.docker_exec_interactive(container_id=container_id)

        return process


class DockerImageManageMixin(DockerCommandExecuteMixin):

    def has_image(self, target_id: str) -> bool:

        image_ids: DockerTemplateCommandOutput = self.docker_images(options={'-q': ''})

        for image_id in image_ids.output:
            if target_id in image_id[0].strip():
                return True

        return False

    def inspect_all_image(self) -> List[DockerImageListItem]:
        result: DockerTemplateCommandOutput = self.docker_images()

        if result.status == ResultCode.SUCCESS:
            return [DockerImageListItem.of(_) for _ in result.output]
        else:
            raise DockerException(msg=result.raw_output)

    def inspect_image(self, image_id: str) -> DockerImageDetail:
        result: DockerTemplateCommandOutput = self.docker_inspect(target=IMAGE, target_id=image_id)

        if result.status == ResultCode.SUCCESS:
            return DockerImageDetail.of(result.output)
        else:
            raise DockerException(msg=result.raw_output)

    def pull_image(self, name: str, tag: str) -> DockerTemplateCommandOutput:
        task_id = f'image:{name}:{tag}'

        if task_queue.scard(PULL_IMAGE_TASK_NAME) >= MAX_PULLING_TASK_SIZE:
            raise DockerImageQueueFullException()

        if task_queue.sismember(PULL_IMAGE_TASK_NAME, task_id):
            raise DockerImageAlreadyProcessingException()

        task_queue.sadd(PULL_IMAGE_TASK_NAME, task_id)

        result = self.docker_pull_image(name=name, tag=tag)

        task_queue.srem(PULL_IMAGE_TASK_NAME, task_id)

        if result.status == ResultCode.ERROR:
            raise DockerException(msg=result.raw_output)

        return result

    def rmi(self, image_id: str) -> DockerTemplateCommandOutput:

        if not self.has_image(image_id):
            raise DockerImageNotFoundException()

        result = self.docker_rmi(image_id=image_id)

        if result.status == ResultCode.ERROR:
            raise DockerException(msg=result.raw_output)

        return result


class DockerManager(DockerContainerManageMixin, DockerImageManageMixin):

    def is_include_task_from_queue(self, name: str) -> bool:
        task_list = self.get_queue_tasks()

        for image_name in [_.split(':')[0] for _ in task_list.tasks]:
            if name in image_name:
                return True

        return False

    def has_task_from_queue(self, name: str, tag: str) -> bool:
        return task_queue.sismember(PULL_IMAGE_TASK_NAME, f'image:{name}:{tag}')

    def get_queue_tasks(self) -> ImageTaskQueueList:
        print(task_queue.smembers(PULL_IMAGE_TASK_NAME))
        return ImageTaskQueueList(
            tasks=[task.decode('utf-8').split('image:')[1] for task in task_queue.smembers(PULL_IMAGE_TASK_NAME)]
        )


docker_manager = DockerManager()

