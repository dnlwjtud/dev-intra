from enum import Enum
from typing import List, Dict, Optional, Literal

from .constants import *
from apps.core.modules import CommandExecuteMixin, StdOutParseMixin

class TemplateTypes(Enum):
    Table: str = "TABLE"
    Json: str = "JSON"

class DockerCommandExecuteMixin(CommandExecuteMixin, StdOutParseMixin):

    def _execute_docker_command(self
                                , command: List[str]
                                , options: Optional[Dict[str, str]] = None
                                , line_split: bool = True) -> List[str] | str:
        if options:
            for k, v in options.items():
                command.append(k)
                if v.strip() != '':
                    command.append(v)
        std_out = self._execute_command(command)
        return std_out.split('\n') if line_split else std_out

    def execute_cmd(self, command: str):
        return self._execute_docker_command(command=command.split(" "))

    def _execute_template(self
                          , command: List[str]
                          , options: Optional[Dict[str, str]] = None
                          , template_type: TemplateTypes = TemplateTypes.Json) -> Optional[List[List[str]] | Dict]:
        try:
            if template_type == TemplateTypes.Json:
                std_out = self._execute_docker_command(command=command, line_split=False)
                return self.parse_json(std_out)
            elif template_type == TemplateTypes.Table:
                lines = self._execute_docker_command(command=command, options=options)
                return self.parse_table(lines=lines)
        except Exception as e:
            print(f'[ERROR] Error while inspecting {e}')
            return None

    def docker_ps(self, options: Optional[Dict[str, str]] = None) -> List[List[str]]:
        return self._execute_template(command=[DOCKER, PS], options=options, template_type=TemplateTypes.Table)

    def docker_images(self, options: Optional[Dict[str, str]] = None) -> List[List[str]]:
        return self._execute_template(command=[DOCKER, IMAGES], options=options, template_type=TemplateTypes.Table)

    def docker_network_ls(self, options: Optional[Dict[str, str]] = None) -> List[List[str]]:
        return self._execute_template(command=[DOCKER, NETWORK, LS], options=options, template_type=TemplateTypes.Table)

    def docker_inspect(self
                       , target: Literal['container', 'image', 'network']
                       , target_id: str
                       , options: Optional[Dict[str, str]] = None
                       ) -> Optional[Dict]:
        return self._execute_template(command=[DOCKER, target, INSPECT, target_id]
                                      , options=options
                                      , template_type=TemplateTypes.Json)

