import docker

from apps.dockers.models import *
from apps.dockers.exceptions import *


class DockerConnector:
    def __init__(self, auto_configure: bool = True, **kwargs):
        try:
            if auto_configure:
                self._client: docker.DockerClient = docker.from_env(**kwargs)
            else:
                self._client: docker.DockerClient = docker.DockerClient(**kwargs)
        except Exception:
            raise DockerEngineException()


class DockerImageMixin:

    def __init__(self, client: docker.DockerClient):
        self._client = client

    def __image_client(self):
        return self._client.images

    def pull_image(self, desc: PullingImageDescription) -> DockerImage:
        try:
            image = self.__image_client().pull(repository=desc.repository, tag=desc.tag)
            return DockerImage.of(attrs=image.attrs)
        except Exception:
            raise DockerImagePullingException()

    def inspect_image(self, image_name: str) -> DockerImage:
        try:
            image = self.__image_client().get(name=image_name)
            return DockerImage.of(attrs=image.attrs)
        except docker.errors.ImageNotFound:
            raise NoSuchDockerImageException()
        except Exception:
            raise DockerImageProcessingException()


    def has_image(self, image_name: str) -> bool:
        try:
            self.inspect_image(image_name=image_name)
            return True
        except Exception:
            return False

    def remove_image(self, image_name: Optional[str] = None, is_force: bool = False):
        if not self.has_image(image_name=image_name):
            raise NoSuchDockerImageException()

        self.__image_client().remove(image=image_name, force=is_force)

    def images(self, image_name: Optional[str] = None) -> List[DockerImage]:
        images = self.__image_client().list(all=True if image_name is None else False, name=image_name)
        return [DockerImage.of(attrs=image.attrs) for image in images]



class DockerManager(DockerConnector, DockerImageMixin):

    def __init__(self, auto_configure: bool = True, **kwargs):
        DockerConnector.__init__(self, auto_configure=auto_configure, **kwargs)
        DockerImageMixin.__init__(self, self._client)

    def __container_client(self):
        return self._client.containers

    def get_client(self):
        return self._client


docker_manager = DockerManager()

