from .modules import DockerControlMixin, StdOutParseMixin
from .models import Container


class ContainerManager(DockerControlMixin, StdOutParseMixin):

    def get_container_status_list(self):
        status_str = self.get_all_container_status()
        std_str_list = self.parse_container_list_status(status_str)

        result = []

        for std_str in std_str_list:
            result.append(
                Container(
                    container_id=std_str.container_id,
                    container_name=std_str.names,
                    is_available=self.__validate_status(std_str.status),
                    ports=std_str.ports
                )
            )

        return result

    def __validate_status(self, val) -> bool:
        return val.strip().startswith('Up')
