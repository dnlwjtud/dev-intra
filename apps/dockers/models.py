from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DockerContainerListItem:
    container_id: str
    container_name: str
    is_available: bool
    ports: List[str] = field(default_factory=List)

    @staticmethod
    def of(values: List):
        return DockerContainerListItem(
            container_id=values[0],
            container_name=values[6],
            is_available=True if values[4].__contains__('Up') else False,
            ports=values[5].strip().split(', ')
        )

@dataclass
class DockerContainerStatus:
    container_id: str
    image: str
    command: str
    created: str
    status: str
    names: str
    ports: List[str] = field(default_factory=List)


@dataclass
class DockerContainerDetail:
    container_id: str
    container_name: str

    created_at: str

    image_id: str

    raw_str: str

    args: List[str] = field(default_factory=List)
    state: Dict[str, str] = field(default_factory=Dict)
    binds: List[str] = field(default_factory=List)
    mounts: List[Any] = field(default_factory=List)
    networks: Dict[str, Any] = field(default_factory=Dict)

    @staticmethod
    def of(data: Dict):
        import json
        return DockerContainerDetail(
            container_id=data.get('Id'),
            container_name=data.get('Name'),
            created_at=data.get('Created'),
            image_id=data.get('Image').split(':')[1],
            args=data.get('Args'),
            state=data.get('State'),
            binds=data.get('HostConfig').get('Binds'),
            mounts=data.get('Mounts'),
            networks=data.get('NetworkSettings'),
            raw_str=json.dumps(data, sort_keys=True, indent=2)
        )
