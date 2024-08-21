from pydantic import BaseModel

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResultCode(Enum):
    SUCCESS: int = 200
    BAD: int = 400
    ERROR: int = 500


@dataclass
class OutputModel:
    status: Any
    raw_cmd: str
    raw_output: str


class DefaultResponseModel(BaseModel):
    status: Any
    msg: str
    data: Any

