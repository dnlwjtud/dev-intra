from typing import List, Optional

from apps.dockers.constants import CONTAINER, IMAGE
from apps.dockers.modules import DockerCommandExecuteMixin
from apps.dockers.models import DockerContainerListItem, DockerContainerDetail, DockerImageListItem, DockerImageDetail


class DockerContainerManager(DockerCommandExecuteMixin):

    def inspect_all_container(self) -> List[DockerContainerListItem]:
        status_list: List[List[str]] = self.docker_ps(options={'-a': ''})
        if status_list:
            return [DockerContainerListItem.of(_) for _ in status_list]
        else:
            return []

    def inspect_container_by_id(self, container_id: str) -> Optional[DockerContainerListItem]:
        status_list: List[List[str]] = self.docker_ps(options={'-a': '', '-f': f'id={container_id}'})

        if len(status_list) == 0:
            return None

        return DockerContainerListItem.of(status_list[0])

    def inspect_container_detail(self, container_id: str) -> Optional[DockerContainerDetail]:
        obj = self.docker_inspect(target=CONTAINER, target_id=container_id)
        return DockerContainerDetail.of(obj) if obj else None

    def inspect_all_image(self) -> List[DockerImageListItem]:
        result = self.docker_images()
        if len(result) == 0:
            return []
        return [DockerImageListItem.of(_) for _ in result]

    def inspect_image(self, image_id: str) -> Optional[DockerImageDetail]:
        obj = self.docker_inspect(target=IMAGE, target_id=image_id)
        return DockerImageDetail.of(obj) if obj else None



docker_manager = DockerContainerManager()

