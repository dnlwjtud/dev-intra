import docker

from apps.dockers.models import *
from apps.dockers.exceptions import *


class DockerManager:

    def __init__(self, auto_configure: bool = True, **kwargs):
        try:
            if auto_configure:
                self._client: docker.DockerClient = docker.from_env(**kwargs)
            else:
                self._client: docker.DockerClient = docker.DockerClient(**kwargs)
        except Exception:
            raise DockerEngineException()

    def __image_client(self):
        return self._client.images

    def __container_client(self):
        return self._client.containers

    def get_client(self):
        return self._client

    def pull_image(self, desc: PullingImageDescription) -> DockerImage:
        try:
            image = self.__image_client().pull(repository=desc.repository, tag=desc.tag)
            return DockerImage.of(attrs=image.attrs)
        except Exception:
            raise DockerImagePullingException()

    def inspect_image(self, image_name: str):
        pass

    def remove_image(self, image_name: str, is_force: bool = False):
        pass

    def images(self, repo: Optional[str] = None):
        pass


docker_manager = DockerManager()

