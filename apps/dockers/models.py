from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel

from apps.core.models import OutputModel


class TemplateTypes(Enum):
    Table: str = "TABLE"
    Json: str = "JSON"


class PullDockerImageRequest(BaseModel):
    name: str
    tag: str


@dataclass
class DockerCommandOutput(OutputModel):
    output: List[str] = field(default_factory=List)

    @staticmethod
    def of(origin: OutputModel):
        return DockerCommandOutput(
            status=origin.status,
            raw_cmd=origin.raw_cmd,
            raw_output=origin.raw_output,
            output=[]
        )

    def set_output(self, output: List[str]):
        self.output = output
        return self


@dataclass
class DockerTemplateCommandOutput(OutputModel):
    template_type: TemplateTypes

    @staticmethod
    def of(origin: DockerCommandOutput
           , template_type: TemplateTypes):
        if template_type == TemplateTypes.Json:
            return DockerCommandJsonOutput(
                status=origin.status,
                raw_cmd=origin.raw_cmd,
                raw_output=origin.raw_output,
                template_type=TemplateTypes.Json,
                output={}
            )
        elif template_type == TemplateTypes.Table:
            return DockerCommandTableOutput(
                status=origin.status,
                raw_cmd=origin.raw_cmd,
                raw_output=origin.raw_output,
                template_type=TemplateTypes.Table,
                output=[]
            )
        else:
            raise ValueError("Invalid template type")

@dataclass
class DockerCommandJsonOutput(DockerTemplateCommandOutput):
    output: Dict[str, Any] = field(default_factory=Dict)

    # @staticmethod
    # def of(origin: DockerCommandOutput):
    #     return DockerCommandJsonOutput(
    #         status=origin.status,
    #         raw_cmd=origin.raw_cmd,
    #         raw_output=origin.raw_output,
    #         template_type=TemplateTypes.Json,
    #         output={}
    #     )

    def set_output(self, output: Dict[str, Any]):
        self.output = output
        return self

@dataclass
class DockerCommandTableOutput(DockerTemplateCommandOutput):
    output: List[str] = field(default_factory=List)

    # @staticmethod
    # def of(origin: DockerCommandOutput):
    #     return DockerCommandTableOutput(
    #         status=origin.status,
    #         raw_cmd=origin.raw_cmd,
    #         raw_output=origin.raw_output,
    #         template_type=TemplateTypes.Json,
    #         output=[]
    #     )

    def set_output(self, output: List[str]):
        self.output = output
        return self


@dataclass
class DockerContainerListItem:
    container_id: str
    container_name: str
    is_available: bool
    ports: List[str] = field(default_factory=List)

    @staticmethod
    def of(values: List):
        return DockerContainerListItem(
            container_id=values[0].strip(),
            container_name=values[-1].strip(),
            is_available=True if values[4].__contains__('Up') else False,
            ports=values[5].strip().split(', ') if len(values) == 7 else []
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


@dataclass
class DockerImageListItem:
    image_id: str
    repository: str
    tag: str
    size: str

    @staticmethod
    def of(values: List):
        return DockerImageListItem(
            image_id=values[2].strip(),
            repository=values[0].strip(),
            tag=values[1].strip(),
            size=values[4].strip()
        )


@dataclass
class DockerImageDetail:
    image_id: str
    author: str
    repository: str
    created_at: str

    size: str

    raw_str: str

    config: Dict[str, Any] = field(default_factory=Dict)

    @staticmethod
    def of(data: Dict):
        import json
        return DockerImageDetail(
            image_id=data.get('Id'),
            author=data.get('Author'),
            repository=data.get('RepoTags'),
            created_at=data.get('Created').split('T')[0],
            size=data.get('Size'),
            config=data.get('Config'),
            raw_str=json.dumps(data, sort_keys=True, indent=2)
        )

