from typing import List

from apps.core.models import ResultCode
from apps.dockers.constants import CONTAINER, IMAGE
from apps.dockers.exceptions import DockerException
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


docker_manager = DockerContainerManager()

