from typing import List

from apps.core.config import PULL_IMAGE_TASK_NAME, MAX_PULLING_TASK_SIZE
from apps.core.models import ResultCode
from apps.core.modules import task_queue

from apps.dockers.constants import CONTAINER, IMAGE
from apps.dockers.exceptions import DockerException, DockerImageQueueFullException, DockerImageAlreadyPullingException, \
    DockerImageNotFoundException
from apps.dockers.modules import DockerCommandExecuteMixin
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, DockerImageListItem, \
    DockerImageDetail, DockerTemplateCommandOutput, ImageTaskQueueList


class DockerContainerManageMixin(DockerCommandExecuteMixin):

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
            raise DockerImageAlreadyPullingException()

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

    def has_task_from_queue(self, name: str, tag: str) -> bool:
        return task_queue.sismember(PULL_IMAGE_TASK_NAME, f'image:{name}:{tag}')

    def get_queue_tasks(self) -> ImageTaskQueueList:
        return ImageTaskQueueList(
            tasks=[task.decode('utf-8').split('image:')[1] for task in task_queue.smembers(PULL_IMAGE_TASK_NAME)]
        )


docker_manager = DockerManager()

