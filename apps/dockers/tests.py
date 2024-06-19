from unittest import TestCase, main
from unittest.mock import patch

from apps.core.config import PULL_IMAGE_TASK_NAME

from apps.dockers.constants import *
from apps.dockers.exceptions import DockerImageNotFoundException
from apps.dockers.app import DockerManager
from apps.dockers.models import TemplateTypes, ImageTaskQueueList

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


@patch('apps.dockers.app.task_queue')
class DockerTaskQueueTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manager = DockerManager()


    def test_has_task_from_queue(self, mock_task_queue) -> None:

        test_image_name = 'test'
        test_image_tag = 'latest'

        mock_task_queue.sismember.return_value = True

        result = self.manager.has_task_from_queue(name=test_image_name, tag=test_image_tag)

        self.assertTrue(result)
        mock_task_queue.sismember.assert_called_with(
            PULL_IMAGE_TASK_NAME, f'image:{test_image_name}:{test_image_tag}'
        )


    def test_get_queue_tasks(self, mock_task_queue) -> None:

        mock_task_queue.smembers.return_value = [
            b'image:test1:latest',
            b'image:test2:latest',
            b'image:test3:latest'
        ]

        result = self.manager.get_queue_tasks()

        self.assertIsInstance(result, ImageTaskQueueList)
        self.assertEqual(len(result.tasks), 3)

        self.assertIn('test1:latest', result.tasks)
        self.assertIn('test2:latest', result.tasks)
        self.assertIn('test3:latest', result.tasks)

        mock_task_queue.smembers.assert_called_with(PULL_IMAGE_TASK_NAME)

    def test_is_include_task_from_queue(self, mock_task_queue) -> None:

        mock_task_queue.smembers.return_value = [
            b'image:test1:latest',
            b'image:test2:latest',
            b'image:test3:latest'
        ]

        target_image_name = 'test1'

        result = self.manager.is_include_task_from_queue(target_image_name)

        self.assertTrue(result)
        mock_task_queue.smembers.assert_called_with(PULL_IMAGE_TASK_NAME)


