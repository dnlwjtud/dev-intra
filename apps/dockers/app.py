from typing import List, Optional

from apps.dockers.modules import DockerCommandExecuteMixin
from apps.dockers.models import DockerContainer, DockerContainerStatus, DockerContainerDetail


class DockerContainerManager(DockerCommandExecuteMixin):

    def inspect_all_container(self) -> List[DockerContainer]:

        container_list = []
        status_list: List[DockerContainerStatus] = self.docker_ps(options={'-a': ''})

        for status in status_list:
            if status:
                container_list.append(
                    DockerContainer(
                        container_id=status.container_id,
                        container_name=status.names,
                        is_available=True if status.status.__contains__('Up') else False,
                        ports=status.ports
                    )
                )

        return container_list

    def inspect_container_by_id(self, container_id: str) -> Optional[DockerContainer]:
        status_list: List[DockerContainerStatus] = self.docker_ps(options={'-a': '',
                                                                     '-f': f'id={container_id}'})

        if len(status_list) == 0:
            return None

        status = status_list[0]

        return DockerContainer(
            container_id=status.container_id,
            container_name=status.names,
            is_available=True if status.status.__contains__('Up') else False,
            ports=status.ports
        )

    def inspect_container_detail(self, container_id: str) -> Optional[DockerContainerDetail]:
        obj = self.docker_inspect(container_id=container_id)
        return self.container_detail(
            values=obj
        ) if obj else None


docker_manager = DockerContainerManager()

