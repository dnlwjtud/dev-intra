import docker
from docker.api import container

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
            raise DockerProcessingException()


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


class DockerContainerMixin:

    def __init__(self, client: docker.DockerClient):
        self._client = client

    def __container_client(self):
        return self._client.containers

    def docker_containers(self, is_all: bool = False) -> List[DockerContainer]:
        containers = self.__container_client().list(all=is_all)
        return [DockerContainer.of(attrs=con.attrs) for con in containers]

    def get_container(self, container_id: str) -> DockerContainer:
        try:
            con = self.__container_client().get(container_id=container_id)
            return DockerContainer.of(attrs=con.attrs)
        except docker.errors.NotFound:
            raise NoSuchDockerContainerException()
        except Exception as e:
            raise DockerProcessingException()

    def remove_container(self, container_id: str) -> None:
        pass

    def control_container(self, options: Dict[str, str]) -> DockerContainer:
        pass

    def container(self, **kwargs) -> DockerContainer:
        pass


class DockerManager(DockerConnector, DockerImageMixin, DockerContainerMixin):

    def __init__(self, auto_configure: bool = True, **kwargs):
        DockerConnector.__init__(self, auto_configure=auto_configure, **kwargs)
        DockerImageMixin.__init__(self, self._client)
        DockerContainerMixin.__init__(self, self._client)

    def get_client(self):
        return self._client




docker_manager = DockerManager()

