from typing import List

from apps.core.config import PULL_IMAGE_TASK_NAME, MAX_PULLING_TASK_SIZE
from apps.core.models import ResultCode
from apps.core.modules import task_queue

from apps.dockers.constants import CONTAINER, IMAGE
from apps.dockers.exceptions import DockerException, DockerImageQueueFullException, DockerImageAlreadyPullingException
from apps.dockers.modules import DockerCommandExecuteMixin
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, DockerImageListItem, DockerImageDetail, \
    DockerTemplateCommandOutput


class DockerContainerManager(DockerCommandExecuteMixin):

    def inspect_all_container(self) -> List[DockerContainerListItem]:
        result: DockerTemplateCommandOutput = self.docker_ps(options={'-a': ''})

        if result.status == ResultCode.SUCCESS:
            return [DockerContainerListItem.of(_)for _ in result.output]
        else:
            raise DockerException(msg=result.raw_output)

    def inspect_container_by_id(self, container_id: str) -> DockerContainerListItem:
        result: DockerTemplateCommandOutput = self.docker_ps(options={'-a': '', '-f': f'id={container_id}'})

        if result.status == ResultCode.SUCCESS:
            return DockerContainerListItem.of(result.output[0])
        else:
            raise DockerException(msg=result.raw_output)

    def inspect_container_detail(self, container_id: str) -> DockerContainerDetail:
        result: DockerTemplateCommandOutput = self.docker_inspect(target=CONTAINER, target_id=container_id)

        if result.status == ResultCode.SUCCESS:
            return DockerContainerDetail.of(result.output)
        else:
            raise DockerException(msg=result.raw_output)

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

    def pull_image(self, name: str, tag: str):
        task_id = f'image:{name}:{tag}'

        if task_queue.scard(PULL_IMAGE_TASK_NAME) >= MAX_PULLING_TASK_SIZE:
            raise DockerImageQueueFullException()

        if task_queue.sismember(PULL_IMAGE_TASK_NAME, task_id):
            raise DockerImageAlreadyPullingException()

        task_queue.sadd(PULL_IMAGE_TASK_NAME, task_id)
        # result = self.pull_image_helper(self.pull_image, name=name, tag=tag)
        result = self.docker_pull_image(name=name, tag=tag)

        # task_queue.scard(task_id)
        # task_queue.spop(name=task_id)
        task_queue.srem(PULL_IMAGE_TASK_NAME, task_id)

        if result.status == ResultCode.ERROR:
            raise DockerException(msg=result.raw_output)

        return result


docker_manager = DockerContainerManager()


