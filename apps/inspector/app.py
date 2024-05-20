from typing import List, Optional

from apps.inspector.modules import DockerCommandExecuteMixin
from apps.inspector.models import DockerContainer, ContainerStatus

class DockerContainerManager(DockerCommandExecuteMixin):

    def inspect_all_container(self) -> List[DockerContainer]:

        container_list = []
        status_list: List[ContainerStatus] = self.docker_ps(options={'-a': ''})

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
        status_list: List[ContainerStatus] = self.docker_ps(options={'-a': '',
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


docker_container_manager = DockerContainerManager()

