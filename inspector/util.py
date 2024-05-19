from typing import List

from .models import ContainerStatus


class DockerControlMixin:

    __BASE: str = 'docker'
    __ENCODE_TYPE: str = 'utf-8'

    def get_all_container_status(self) -> List[List[str]]:
        import subprocess as cmd

        std_out = cmd.check_output([self.__BASE, 'ps', '-a'])
        lines = std_out.decode(self.__ENCODE_TYPE).split('\n')

        result = []

        for line in lines:
            line_split = line.split('  ')
            line_result = [_ for _ in line_split if _ != '']
            if len(line_result) > 0:
                result.append([_ for _ in line_split if _ != ''])

        return result[1:]

    def get_container_status(self, container_id: str) -> List[str]:
        import subprocess as cmd

        std_out = cmd.check_output([self.__BASE, 'ps', '-a', '-f', f'id={container_id}'])
        lines = std_out.decode(self.__ENCODE_TYPE).split('\n')

        return [_.strip() for _ in lines[1].split('  ')]


class StdOutParseMixin:
    def parse_container_list_status(self, std_str_list: list | str) -> List[ContainerStatus]:
        result = []

        for std_str in std_str_list:
            result.append(ContainerStatus(
                container_id=std_str[0],
                image=std_str[1],
                command=std_str[2],
                created=std_str[3],
                status=std_str[4],
                names=std_str[6],
                ports=std_str[5].strip().split(', ')
            ))

        return result

    def parse_container_status(self, std_str: str) -> ContainerStatus:
        return ContainerStatus(
            container_id=std_str[0],
            image=std_str[1],
            command=std_str[2],
            created=std_str[3],
            status=std_str[4],
            names=std_str[6],
            ports=std_str[5].strip().split(', ')
        )

