from dataclasses import dataclass, field
from typing import Optional, List, Dict

from datetime import datetime

from pydantic import BaseModel


@dataclass
class PullingImageDescription:

    repository: str
    tag: Optional[str] = None

@dataclass
class DockerImage:

    image_id: str
    tag: str
    created_at: datetime

    container_name: str

    comment: Optional[str]
    size: int
    is_used: bool

    config: Dict = field(default_factory=Dict)


    @staticmethod
    def of(attrs: Dict) -> 'DockerImage':
        return DockerImage(
            image_id=attrs.get('Id')
            , tag=attrs.get('RepoTags')[0]
            , created_at=attrs.get('Created')
            , comment=attrs.get('Comment')
            , size=attrs.get('Size')
            , config=attrs.get('Config')
            , container_name="None"
            , is_used=False
        )

@dataclass
class DockerContainer:

    container_id: str
    container_name: str
    image_id: str

    created_at: str

    state: Dict = field(default_factory=Dict)
    args: List = field(default_factory=List)

    host_config: Dict = field(default_factory=Dict)

    mount: List = field(default_factory=List)

    config: Dict = field(default_factory=Dict)
    network: Dict = field(default_factory=Dict)

    @staticmethod
    def of(attrs: Dict) -> 'DockerContainer':
        return DockerContainer(
            container_id=attrs.get('Id'),
            container_name=attrs.get('Name')[1:],
            image_id=attrs.get('Image'),
            created_at=attrs.get('Created'),
            state=attrs.get('State'),
            args=attrs.get('Args'),
            host_config=attrs.get('HostConfig'),
            mount=attrs.get('Mounts'),
            config=attrs.get('Config'),
            network=attrs.get('NetworkSettings')
        )

class DockerContainerStatusRequest(BaseModel):
    act_type: str

class DockerContainerRemoveRequest(BaseModel):
    force: bool

@dataclass
class DockerNetwork:

    network_id: str
    network_name: str

    driver: str

    is_dangling: bool

    config: List = field(default_factory=List)
    containers: List = field(default_factory=List)

    @staticmethod
    def of(attrs: Dict) -> 'DockerNetwork':
        return DockerNetwork(
            network_id=attrs.get('Id'),
            network_name=attrs.get('Name'),
            driver=attrs.get('Driver'),
            is_dangling=True,
            config=attrs.get('IPAM')['Config'],
            containers=[]
        )

