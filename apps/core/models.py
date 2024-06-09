from dataclasses import dataclass
from enum import Enum
from typing import List


class ResultCode(Enum):
    SUCCESS: int = 200
    ERROR: int = 500


@dataclass
class OutputModel:
    status: ResultCode
    raw_cmd: str
    raw_output: str

