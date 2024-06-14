from typing import List, Dict, Optional, Literal

from celery import shared_task

from apps.core.config import PULL_IMAGE_TASK_NAME
from apps.core.modules import CommandExecuteMixin, StdOutParseMixin, task_queue
from apps.core.models import ResultCode

from .constants import *
from .models import DockerCommandOutput, TemplateTypes, DockerTemplateCommandOutput


class DockerCommandExecuteMixin(CommandExecuteMixin, StdOutParseMixin):

    def _execute_docker_command(self
                                , command: List[str]
                                , options: Optional[Dict[str, str]] = None
                                , line_split: bool = True) -> DockerCommandOutput:
        if options:
            for k, v in options.items():
                command.append(k)
                if v.strip() != '':
                    command.append(v)

        result = self._execute_command(command)
        output = DockerCommandOutput.of(origin=result)

        if line_split and result.status == ResultCode.SUCCESS:
            output.set_output(result.raw_output.strip().split('\n'))

        return output

    def execute_cmd(self, command: str) -> DockerCommandOutput:
        return self._execute_docker_command(command=command.split(" "))

    def _execute_template(self
                          , command: List[str]
                          , options: Optional[Dict[str, str]] = None
                          , template_type: TemplateTypes = TemplateTypes.Json) -> DockerTemplateCommandOutput:
        try:
            if template_type == TemplateTypes.Json:
                result = self._execute_docker_command(command=command, line_split=False)
                return DockerTemplateCommandOutput.of(
                    origin=result,
                    template_type=TemplateTypes.Json
                ).set_output(self.parse_json(result.raw_output))
            elif template_type == TemplateTypes.Table:
                result = self._execute_docker_command(command=command, options=options)
                return DockerTemplateCommandOutput.of(
                    origin=result,
                    template_type=TemplateTypes.Json
                ).set_output(self.parse_table(lines=result.output))
        except Exception as e:
            print(f'[ERROR] Error while inspecting {e}')
            result = self._execute_docker_command(command=command, options=options)
            return DockerTemplateCommandOutput.of(origin=result, template_type=TemplateTypes.Json)

    def docker_ps(self, options: Optional[Dict[str, str]] = None) -> DockerTemplateCommandOutput:
        return self._execute_template(command=[DOCKER, PS], options=options, template_type=TemplateTypes.Table)

    def docker_images(self, options: Optional[Dict[str, str]] = None) -> DockerTemplateCommandOutput:
        return self._execute_template(command=[DOCKER, IMAGES], options=options, template_type=TemplateTypes.Table)

    def docker_network_ls(self, options: Optional[Dict[str, str]] = None) -> DockerTemplateCommandOutput:
        return self._execute_template(command=[DOCKER, NETWORK, LS], options=options, template_type=TemplateTypes.Table)

    def docker_inspect(self
                       , target: Literal['container', 'image', 'network']
                       , target_id: str
                       , options: Optional[Dict[str, str]] = None
                       ) -> DockerTemplateCommandOutput:
        return self._execute_template(command=[DOCKER, target, INSPECT, target_id]
                                      , options=options
                                      , template_type=TemplateTypes.Json)

    def docker_pull_image(self, name: str, tag: str) -> DockerTemplateCommandOutput:
        return self._execute_template(command=[DOCKER, PULL, f'{name}:{tag}'])
