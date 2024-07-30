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
        self._client = client.containers

    def __container_client(self):
        return self._client

    def docker_containers(self, is_all: bool = False) -> List[DockerContainer]:
        containers = self._client.list(all=is_all)
        return [DockerContainer.of(attrs=con.attrs) for con in containers]

    def docker_container(self, container_id: str) -> DockerContainer:
        con = self.container(container_id=container_id)
        return DockerContainer.of(attrs=con.attrs)

    def container(self, container_id: str) -> docker.models.containers.Container:
        try:
            con = self._client.get(container_id=container_id)
            return con
        except docker.errors.NotFound:
            raise NoSuchDockerContainerException()
        except Exception as e:
            raise DockerProcessingException()

    def remove_container(self, container_id: str, is_force: bool = False) -> bool:
        try:
            con = self.container(container_id=container_id)
            con.remove(force=is_force)
            return True
        except Exception as e:
            return False

    def has_container(self, container_id: str) -> bool:
        try:
            self.container(container_id=container_id)
            return True
        except Exception as e:
            return False

    def compact_run(self, image: str
                    , ports: dict
                    , env: Optional[Dict[str, str]] = None
                    , entrypoint: Optional[str | List[str]] = None
                    , volumes: Optional[Dict[str, Dict[str, str]]] = None
                    , command: Optional[str] = None
                    , name: Optional[str] = None
                    , network: Optional[str] = None) -> DockerContainer:
        try:
            con = self._client.run(image=image
                                   , ports=ports
                                   , env=env if env is not None else {}
                                   , entrypoint=entrypoint if entrypoint is not None else []
                                   , volumes=volumes if volumes is not None else {}
                                   , command=command if command is not None else ''
                                   , name=name if name is not None else ''
                                   , network=network if network is not None else {})

            return DockerContainer.of(con.attrs)
        except Exception as e:
            raise e

    def compact_container_action(self, container_id: str, act_type: str) -> bool:
        try:
            act_type = act_type.upper()
            con = self.container(container_id=container_id)

            if act_type == "PAUSE":
                con.pause()
            elif act_type == "UNPAUSE":
                con.unpause()
            elif act_type == "START":
                con.start()
            elif act_type == "RESTART":
                con.restart()
            elif act_type == "STOP":
                con.stop()
            else:
                return False
            return True
        except Exception as e:
            return False


class DockerManager(DockerConnector, DockerImageMixin, DockerContainerMixin):

    def __init__(self, auto_configure: bool = True, **kwargs):
        DockerConnector.__init__(self, auto_configure=auto_configure, **kwargs)
        DockerImageMixin.__init__(self, self._client)
        DockerContainerMixin.__init__(self, self._client)

    def get_client(self):
        return self._client


docker_manager = DockerManager()
