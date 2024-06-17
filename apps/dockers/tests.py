from unittest import TestCase, main

from apps.dockers.constants import *
from apps.dockers.exceptions import DockerImageNotFoundException
from apps.dockers.app import DockerManager
from apps.dockers.models import TemplateTypes

if __name__ == '__main__':
    main()


class DockerImageTests(TestCase):

    @classmethod
    def setUpClass(cls):
        manager = DockerManager()
        manager.docker_pull_image(name='hello-world', tag='latest')

        cls.manager = manager


    def test_pulling_image(self) -> None:
        test_image = 'hello-world'
        tag = 'latest'

        result = self.manager.docker_pull_image(name=test_image, tag=tag)

        self.assertEqual(result.status.value, 200)


    def test_has_image_ng(self) -> None:
        unavailable_image_id = 'unavailable_image_id'

        result = self.manager.has_image(unavailable_image_id)

        self.assertFalse(result)


    def test_has_image_g(self) -> None:
        available_id_part = 'ee301c921b8a'

        result = self.manager.has_image(available_id_part)

        self.assertTrue(result)


    def test_rmi_exception(self) -> None:
        unavailable_image_id = 'unavailable_image_id'

        with self.assertRaises(DockerImageNotFoundException) as context:
            self.manager.rmi(unavailable_image_id)
            self.assertEquals(context.exception.err_msg, 'Could not find such image.')


    def test_rmi(self) -> None:
        available_image_id = 'ee301c921b8a'

        result = self.manager.rmi(image_id=available_image_id)

        self.assertEqual(result.status.value, 200)
        self.assertEqual(result.template_type, TemplateTypes.Text)
        self.assertEqual(result.raw_cmd.split(' '), [DOCKER, RMI, available_image_id])

