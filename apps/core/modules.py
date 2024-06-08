import json
import subprocess
from typing import List, Dict


class CommandExecuteMixin:

    __ENCODE_TYPE: str = 'utf-8'

    def _execute_command(self, command: List[str]) -> str:
        try:
            std_out = subprocess.check_output(command)
            return std_out.decode(self.__ENCODE_TYPE)
        except subprocess.CalledProcessError as e:
            print(f'[ERROR] Command is not available: {command}, error: {e.output}')
            return ''


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
