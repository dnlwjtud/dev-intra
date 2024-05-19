from dataclasses import dataclass, field
from typing import List

@dataclass
class ContainerStatus:
    container_id: str
    image: str
    command: str
    created: str
    status: str
    names: str
    ports: List[str] = field(default_factory=List)


@dataclass
class Container:
    container_id: str
    container_name: str
    is_available: bool

    ports: List[str] = field(default_factory=List)
