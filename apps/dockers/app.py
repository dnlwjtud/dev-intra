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

    def get_client(self):
        return self._client

class DockerImageMixin:

    def __init__(self, client: docker.DockerClient):
        self._image_client = client.images

    def get_image_client(self):
        return self._image_client

    def pull_image(self, desc: PullingImageDescription) -> DockerImage:
        try:
            image = self._image_client.pull(repository=desc.repository, tag=desc.tag)
            return DockerImage.of(attrs=image.attrs)
        except Exception:
            raise DockerImagePullingException()

    def inspect_image(self, image_name: str) -> DockerImage:
        try:
            image = self._image_client.get(name=image_name)
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

        self._image_client.remove(image=image_name, force=is_force)

    def images(self, image_name: Optional[str] = None) -> List[DockerImage]:
        images = self._image_client.list(all=True if image_name is None else False, name=image_name)
        return [DockerImage.of(attrs=image.attrs) for image in images]

    def write_and_build_docker_file(self, contents: str) -> bool:
        import os
        from uuid import uuid4
        from pathlib import Path

        ROOT_DIR = Path(__file__).parent.parent.parent
        target_dir = f'{ROOT_DIR}/{uuid4()}'

        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            else:
                return False

            dockerfile_dir = f'{target_dir}/Dockerfile'

            with open(dockerfile_dir, 'wt', encoding='utf-8') as dockerfile:
                dockerfile.write(contents)

            print("Started building Dockerfile")
            image = self._image_client.build(path=target_dir)
            print("Finished building Dockerfile")

            os.remove(dockerfile_dir)
            os.rmdir(target_dir)

            if image is not None:
                return True

        except Exception as e:
            print(e)
            return False

        return False

class DockerContainerMixin:

    def __init__(self, client: docker.DockerClient):
        self._container_client = client.containers

    def __container_client(self):
        return self._container_client

    def docker_containers(self, is_all: bool = False) -> List[DockerContainer]:
        containers = self._container_client.list(all=is_all)
        return [DockerContainer.of(attrs=con.attrs) for con in containers]

    def docker_container(self, container_id: str) -> DockerContainer:
        con = self.container(container_id=container_id)
        return DockerContainer.of(attrs=con.attrs)

    def container(self, container_id: str) -> docker.models.containers.Container:
        try:
            con = self._container_client.get(container_id=container_id)
            return con
        except docker.errors.NotFound:
            raise NoSuchDockerContainerException()
        except Exception as e:
            raise DockerProcessingException()

    def containers(self) -> List:
        return self._container_client.list(all=True)

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
                    , environment: Optional[Dict[str, str]] = None
                    , entrypoint: Optional[str | List[str]] = None
                    , volumes: Optional[Dict[str, Dict[str, str]]] = None
                    , command: Optional[str] = None
                    , name: Optional[str] = None
                    , network: Optional[str] = None) -> DockerContainer:
        try:
            con = self._container_client.run(image=image
                                   , ports=ports
                                   , environment=environment if environment is not None else {}
                                   , entrypoint=entrypoint if entrypoint is not None else []
                                   , volumes=volumes if volumes is not None else {}
                                   , command=command if command is not None else ''
                                   , name=name if name is not None else ''
                                   , network=network if network is not None else {}
                                   , detach=True)
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


class DockerNetworkMixin:
    def __init__(self, client: docker.DockerClient):
        self._network_client = client.networks

    def __network_client(self):
        return self._network_client

    def networks(self, **kwargs) -> List:
        return self._network_client.list(**kwargs)

    def network(self, network_id: str):
        return self._network_client.get(network_id=network_id)

    def create_network(self, **kwargs) -> DockerNetwork:
        network = self.__network_client().create(**kwargs)
        return DockerNetwork.of(network.attrs)

    # def compact_create_network(self, name: str, driver: str):
    def compact_create_network(self, req: DockerNetworkCreateRequest):
        network = self._network_client.create(name=req.name, driver=req.driver)
        return DockerNetwork.of(network.attrs)

    def remove_network(self, network_id: str) -> True:
        try:
            find_network = self._network_client.get(network_id=network_id)
            find_network.remove()
            return True
        except Exception as e:
            return False


class DockerManager(DockerConnector, DockerImageMixin, DockerContainerMixin, DockerNetworkMixin):

    def __init__(self, auto_configure: bool = True, **kwargs):
        DockerConnector.__init__(self, auto_configure=auto_configure, **kwargs)
        DockerImageMixin.__init__(self, self._client)
        DockerContainerMixin.__init__(self, self._client)
        DockerNetworkMixin.__init__(self, self._client)

    def _get_image_container_name_pair(self):
        result = {}
        for container in super().docker_containers(is_all=True):
            result[container.image_id] = container.container_name
        return result

    def images(self, image_name: Optional[str] = None) -> List[DockerImage]:
        used_images = [_.image_id for _ in super().docker_containers(is_all=True)]
        image_list = super().images(image_name=image_name)

        for image in image_list:
            if image.image_id in used_images:
                image.is_used = True

        return image_list

    def inspect_image(self, image_name: str) -> DockerImage:
        find_image = super().inspect_image(image_name=image_name)
        name_pair = self._get_image_container_name_pair()

        if find_image.image_id in list(name_pair.keys()):
            find_image.is_used = True
            find_image.container_name = name_pair[find_image.image_id]

        return find_image

    def docker_networks(self) -> List:

        network_obj_list = super().networks(greedy=True)
        docker_networks = []

        for network_obj in network_obj_list:
            docker_network = DockerNetwork.of(network_obj.attrs)

            if network_obj.containers:
                docker_network.is_dangling = False
                # docker_network.containers = [DockerContainer.of(container.attrs) for container in network_obj.containers]
            docker_networks.append(docker_network)

        return docker_networks

    def docker_network(self, network_id: str) -> DockerNetwork:

        network = super().network(network_id=network_id)

        docker_network = DockerNetwork.of(network.attrs)

        if network.containers:
            containers = []
            docker_network.is_dangling = False

            for container in network.containers:
                docker_container = DockerContainer.of(container.attrs)
                docker_container.network = network.attrs['Containers'][docker_container.container_id]
                containers.append(docker_container)

            docker_network.containers = containers

        return docker_network


docker_manager = DockerManager()

