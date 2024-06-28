from unittest import TestCase, main
from unittest.mock import patch

from apps.core.config import PULL_IMAGE_TASK_NAME
from apps.core.models import ResultCode

from apps.dockers.constants import *
from apps.dockers.exceptions import DockerImageNotFoundException, DockerContainerNotFoundException
from apps.dockers.app import DockerManager
from apps.dockers.models import TemplateTypes, ImageTaskQueueList, DockerCommandTableOutput, DockerTemplateCommandOutput

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


class DockerContainerTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.manager = DockerManager()

    def setUp(self) -> None:
        self.test_container_id = 'test-container-id'
        self.ng_container_id = 'test-ng-container-id'

    def has_container_helper(self
                             , mock_has_container
                             , mock_container_method
                             , is_exists: bool = True) -> None:
        mock_has_container.return_value = is_exists
        if is_exists:
            mock_container_method.return_value = DockerTemplateCommandOutput(
                status=ResultCode.SUCCESS,
                raw_cmd=f'docker {mock_container_method._mock_name.split("_")[1]} {self.test_container_id}',
                raw_output=f'{self.test_container_id}',
                template_type=TemplateTypes.Text
            )


    @patch('apps.dockers.app.DockerContainerManageMixin._get_container_by_id')
    def test_has_container(self, mock_get_container_id) -> None:
        mock_get_container_id.return_value = DockerCommandTableOutput(
            status=ResultCode.SUCCESS
            , raw_cmd='docker ps -a -f id=test'
            , raw_output=f"""
                CONTAINER ID   IMAGE         COMMAND    CREATED       STATUS                   PORTS     NAMES\n
                {self.test_container_id}   test-image   "/test-cmd"   1 hours ago   Exited (0) 0 hours ago             test_container_name
                """
            , template_type=TemplateTypes.Table
            , output=[
                [self.test_container_id, 'test-image', '"/test-cmd"', '1 hours ago', 'Exited (0) 0 hours ago',
                 'test_container_name']
            ]
        )

        result = self.manager.has_container(container_id=self.test_container_id)

        mock_get_container_id.assert_called_with(container_id=self.test_container_id)
        self.assertTrue(result)

        result = self.manager.has_container(container_id=self.ng_container_id)
        mock_get_container_id.assert_called_with(container_id=self.ng_container_id)
        self.assertFalse(result)

    @patch('apps.dockers.app.DockerManager.docker_stop')  # 1
    @patch('apps.dockers.app.DockerContainerManageMixin.has_container')  # 0
    def test_stop_container(self, mock_has_container, mock_docker_stop) -> None:
        self.has_container_helper(mock_has_container=mock_has_container
                                  , mock_container_method=mock_docker_stop
                                  , is_exists=True)

        result = self.manager.stop_container(container_id=self.test_container_id)

        mock_docker_stop.assert_called_with(container_id=self.test_container_id)
        mock_has_container.assert_called_with(container_id=self.test_container_id)

        self.assertEqual(result.status, ResultCode.SUCCESS)
        self.assertEqual(result.raw_output, self.test_container_id)

    @patch('apps.dockers.app.DockerManager.docker_stop')
    @patch('apps.dockers.app.DockerContainerManageMixin.has_container')
    def test_stop_container_ng(self, mock_has_container, mock_docker_stop) -> None:
        self.has_container_helper(mock_has_container=mock_has_container
                                  , mock_container_method=mock_docker_stop
                                  , is_exists=False)

        with self.assertRaises(DockerContainerNotFoundException):
            self.manager.stop_container(container_id=self.ng_container_id)

    @patch('apps.dockers.app.DockerManager.docker_start')
    @patch('apps.dockers.app.DockerContainerManageMixin.has_container')
    def test_start_container(self, mock_has_container, mock_docker_start) -> None:
        self.has_container_helper(mock_has_container=mock_has_container
                                  , mock_container_method=mock_docker_start
                                  , is_exists=True)

        result = self.manager.start_container(container_id=self.test_container_id)

        mock_docker_start.assert_called_with(container_id=self.test_container_id)
        mock_has_container.assert_called_with(container_id=self.test_container_id)

        self.assertEqual(result.status, ResultCode.SUCCESS)
        self.assertEqual(result.raw_output, self.test_container_id)

    @patch('apps.dockers.app.DockerManager.docker_start')
    @patch('apps.dockers.app.DockerContainerManageMixin.has_container')
    def test_start_container_ng(self, mock_has_container, mock_docker_start) -> None:
        self.has_container_helper(mock_has_container=mock_has_container
                                  , mock_container_method=mock_docker_start
                                  , is_exists=False)

        with self.assertRaises(DockerContainerNotFoundException):
            self.manager.start_container(container_id=self.ng_container_id)

    @patch('apps.dockers.app.DockerManager.docker_restart')
    @patch('apps.dockers.app.DockerContainerManageMixin.has_container')
    def test_restart_container(self, mock_has_container, mock_docker_restart) -> None:
        self.has_container_helper(mock_has_container=mock_has_container
                                  , mock_container_method=mock_docker_restart
                                  , is_exists=True)

        result = self.manager.restart_container(container_id=self.test_container_id)

        mock_docker_restart.assert_called_with(container_id=self.test_container_id)
        mock_has_container.assert_called_with(container_id=self.test_container_id)

        self.assertEqual(result.status, ResultCode.SUCCESS)
        self.assertEqual(result.raw_output, self.test_container_id)

    @patch('apps.dockers.app.DockerManager.docker_restart')
    @patch('apps.dockers.app.DockerContainerManageMixin.has_container')
    def test_restart_container_ng(self, mock_has_container, mock_docker_restart) -> None:
        self.has_container_helper(mock_has_container=mock_has_container
                                  , mock_container_method=mock_docker_restart
                                  , is_exists=False)

        with self.assertRaises(DockerContainerNotFoundException):
            self.manager.restart_container(container_id=self.ng_container_id)


class DockerContainerShellTests(TestCase):

    def test_open_shell(self):
        pass

