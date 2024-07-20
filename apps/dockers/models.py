from dataclasses import dataclass, field
from typing import Optional, List, Dict

from datetime import datetime

@dataclass
class PullingImageDescription:

    repository: str
    tag: Optional[str] = None

@dataclass
class DockerImage:

    image_id: str
    tag: str
    created_at: datetime

    comment: Optional[str]
    size: int

    # env_var: List[str] = field(default_factory=List)
    # cmd: List[str] = field(default_factory=List)
    #
    # volumes: Optional[Dict[str, Dict]] = field(default_factory=dict)

    @staticmethod
    def of(attrs: Dict) -> 'DockerImage':
        return DockerImage(
            image_id=attrs.get('Id')
            , tag=attrs.get('RepoTags')[0]
            , created_at=attrs.get('Created')
            , comment=attrs.get('Comment')
            , size=attrs.get('Size')
        )


