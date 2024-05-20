from typing import List

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


docker_container_manager = DockerContainerManager()

