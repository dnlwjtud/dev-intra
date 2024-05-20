from typing import List, Dict, Optional
import subprocess

from .models import ContainerStatus

class CommandExecuteMixin:

    __ENCODE_TYPE: str = 'utf-8'

    def _execute_command(self, command: str) -> str:
        try:
            std_out = subprocess.check_output(command.split(' '))
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

        # return [line.strip() for line in lines[1].split('  ')]
        return parsed[1:] if not contain_col_names else parsed


class ContainerModelMixin:

    def container_status(self, values: List[str]) -> ContainerStatus:
        return ContainerStatus(
            container_id=values[0],
            image=values[1],
            command=values[2],
            created=values[3],
            status=values[4],
            names=values[6],
            ports=values[5].strip().split(', ')
        )


class DockerCommandExecuteMixin(CommandExecuteMixin, StdOutParseMixin, ContainerModelMixin):

    __ENCODE_TYPE: str = 'utf-8'

    def _execute_docker_command(self, command: str) -> List[str]:
        return self._execute_command(command).split('\n')

    def docker_ps(self, options: Optional[Dict[str, str]] = None) -> List[ContainerStatus]:
        cmd = 'docker ps'

        if options:
            for k, v in options.items():
                if v.strip() != '':
                    cmd += f' {k} {v}'
                else:
                    cmd += f' {k}'

        lines = self._execute_docker_command(cmd)
        parsed = self.parse_table(lines=lines)

        return [self.container_status(_) for _ in parsed] if len(parsed) > 1 else parsed

