from typing import List, Dict, Optional

from .models import DockerContainerStatus, DockerContainerDetail
from apps.core.modules import CommandExecuteMixin, StdOutParseMixin

class ContainerModelMixin:

    def container_status(self, values: List[str]) -> DockerContainerStatus:
        return DockerContainerStatus(
            container_id=values[0],
            image=values[1],
            command=values[2],
            created=values[3],
            status=values[4],
            names=values[6],
            ports=values[5].strip().split(', ')
        )

    def container_detail(self, values: Dict) -> DockerContainerDetail:
        import json
        return DockerContainerDetail(
            container_id=values.get('Id'),
            container_name=values.get('Name'),
            created_at=values.get('Created'),
            image_id=values.get('Image').split(':')[1],
            args=values.get('Args'),
            state=values.get('State'),
            binds=values.get('HostConfig').get('Binds'),
            mounts=values.get('Mounts'),
            networks=values.get('NetworkSettings'),
            raw_str=json.dumps(values, sort_keys=True, indent=2)
        )

class DockerCommandExecuteMixin(CommandExecuteMixin, StdOutParseMixin, ContainerModelMixin):

    __BASE: str = 'docker'
    __ENCODE_TYPE: str = 'utf-8'

    def _execute_docker_command(self, command: str, line_split: bool = True) -> List[str] | str:
        std_out = self._execute_command(command)
        return std_out.split('\n') if line_split else std_out

    def docker_ps(self, options: Optional[Dict[str, str]] = None) -> List[DockerContainerStatus]:
        cmd = f'{self.__BASE} ps'

        if options:
            for k, v in options.items():
                if v.strip() != '':
                    cmd += f' {k} {v}'
                else:
                    cmd += f' {k}'

        lines = self._execute_docker_command(cmd)
        parsed = self.parse_table(lines=lines)

        return [self.container_status(_) for _ in parsed] if len(parsed) > 0 else parsed

    def docker_inspect(self, container_id: str):
        try:
            cmd = f'{self.__BASE} inspect {container_id}'
            std_out = self._execute_docker_command(cmd, line_split=False)

            return self.parse_json(std_out)
        except Exception as e:
            print(f'[ERROR] Error while inspecting {e}')
            return None
