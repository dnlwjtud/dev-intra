import json
import subprocess

from redis import Redis
from typing import List, Dict

from apps.core.config import REDIS_PORT, REDIS_HOST
from apps.core.models import OutputModel, ResultCode

task_queue = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

class CommandExecuteMixin:

    __ENCODE_TYPE: str = 'utf-8'

    def _execute_command(self, command: List[str]) -> OutputModel:
        try:
            std_out = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
            return OutputModel(
                status=ResultCode.SUCCESS,
                raw_cmd=' '.join(command),
                raw_output=std_out
            )
        except subprocess.CalledProcessError as e:
            print(f'[ERROR] Command is not available: {command}, error: {e.output}')
            return OutputModel(
                status=ResultCode.ERROR,
                raw_cmd=' '.join(command),
                raw_output=e.output
            )
        except Exception as e:
            print(f'[ERROR] Unexpected error occurred: {e}, command: {command}')
            return OutputModel(
                status=ResultCode.ERROR,
                raw_cmd=' '.join(command),
                raw_output=str(e)
            )

class StdOutParseMixin:

    def parse_table(self, lines: List[str], contain_col_names: bool = False) -> List[List[str]]:
        parsed = []
        if len(lines) == 0:
            return []

        for line in lines:
            split_line = [_ for _ in line.split('  ') if _ != '']
            if len(split_line) > 0:
                parsed.append(split_line)

        return parsed[1:] if not contain_col_names else parsed

    def parse_json(self, string: str) -> Dict:
        parsed = json.loads(string)

        if isinstance(parsed, List):
            return parsed[0]
        else:
            return parsed
