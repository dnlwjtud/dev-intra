from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DockerContainer:
    container_id: str
    container_name: str
    is_available: bool
    ports: List[str] = field(default_factory=List)


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

    args: List[str] = field(default_factory=List)
    state: Dict[str, str] = field(default_factory=Dict)
    binds: List[str] = field(default_factory=List)
    mounts: List[Any] = field(default_factory=List)
    networks: Dict[str, Any] = field(default_factory=Dict)

