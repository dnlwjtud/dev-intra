import docker

from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from apps.dockers.app import DockerManager
from apps.dockers.models import DockerImage, PullingImageDescription
from apps.dockers.exceptions import DockerImagePullingException, NoSuchDockerImageException


if __name__ == '__main__':
    main()

class DockerManagerTest(TestCase):

    def setUp(self):
        self.instance = DockerManager()

    def __get_test_attrs(self):
        return {'Id': "sha:256:test_id_value"
            , 'RepoTags': ['test:latest']
            , 'Created': '2024-07-20T23:55:55Z'
            , 'Comment': ''
            , 'Size': 139168068}

    @patch('docker.from_env')
    def test_create_auto_configured_instance(self, mock_from_env):
        mock_client = MagicMock(spec=docker.DockerClient)
        mock_from_env.return_value = mock_client

        instance = DockerManager()

        self.assertIsInstance(instance, DockerManager)
        self.assertIsInstance(instance.get_client(), docker.DockerClient)

        mock_from_env.assert_called_once()

    @patch('docker.DockerClient')
    def test_create_manual_configured_instance(self, mock_docker_client):
        mock_client = MagicMock(spec=docker.DockerClient)
        mock_docker_client.return_value = mock_client

        instance = DockerManager(auto_configure=False)

        self.assertIsInstance(instance, DockerManager)

        mock_docker_client.assert_called_once()

    @patch('docker.models.images.ImageCollection.pull')
    def test_pull_image(self, mock_pull):
        mock_image_result = MagicMock()
        mock_image_result.attrs = self.__get_test_attrs()
        mock_pull.return_value = mock_image_result

        # given
        desc = PullingImageDescription(repository='test')

        # when
        image = self.instance.pull_image(desc=desc)

        # then
        mock_pull.assert_called_once_with(repository='test', tag=None)

        self.assertIsInstance(image, DockerImage)

        self.assertEqual(image.image_id, mock_image_result.attrs.get('Id'))
        self.assertEqual(image.tag, mock_image_result.attrs.get('RepoTags')[0])
        self.assertEqual(image.created_at, mock_image_result.attrs.get('Created'))
        self.assertEqual(image.comment, mock_image_result.attrs.get('Comment'))
        self.assertEqual(image.size, mock_image_result.attrs.get('Size'))

    @patch('docker.models.images.ImageCollection.pull', side_effect=Exception)
    def test_pull_not_exists_image(self, mock_pull):
        # given
        desc = PullingImageDescription(repository='unavailable_repo_name', tag='unavailable_tag')

        # when, then
        with self.assertRaises(DockerImagePullingException) as err:
            self.instance.pull_image(desc)

            self.assertEqual(err.err_msg
             , "Could not pull image. It may be due to an incorrect repository or tag. Please check it again")

    @patch('docker.models.images.ImageCollection.list')
    def test_image_list(self, mock_list):
        mock_list_result = MagicMock()
        mock_list_result.attrs = self.__get_test_attrs()
        mock_list.return_value = [mock_list_result]

        # when
        image_list = self.instance.images()

        # then
        mock_list.assert_called_once_with(all=True, name=None)

        self.assertEqual(len(image_list), 1)
        self.assertIsInstance(image_list[0], DockerImage)

    @patch('docker.models.images.ImageCollection.list')
    def test_image_search_from_list(self, mock_list):
        mock_list_result = MagicMock()
        mock_list_result.attrs = self.__get_test_attrs()
        mock_list.return_value = [mock_list_result]

        # when
        image_list = self.instance.images(image_name='test')

        # then
        mock_list.assert_called_once_with(all=False, name='test')

        self.assertEqual(len(image_list), 1)
        self.assertIsInstance(image_list[0], DockerImage)

    @patch('docker.models.images.ImageCollection.get')
    def test_get_image(self, mock_get):
        mock_image_result = MagicMock()
        mock_image_result.attrs = self.__get_test_attrs()
        mock_get.return_value = mock_image_result

        # given
        available_image_name = 'test'

        # when
        image = self.instance.inspect_image(image_name=available_image_name)

        # then
        mock_get.assert_called_once_with(name=available_image_name)

        self.assertIsInstance(image, DockerImage)

        self.assertEqual(image.image_id, mock_image_result.attrs.get('Id'))
        self.assertEqual(image.tag, mock_image_result.attrs.get('RepoTags')[0])
        self.assertEqual(image.created_at, mock_image_result.attrs.get('Created'))
        self.assertEqual(image.comment, mock_image_result.attrs.get('Comment'))
        self.assertEqual(image.size, mock_image_result.attrs.get('Size'))

    @patch('docker.models.images.ImageCollection.get'
        , side_effect=docker.errors.ImageNotFound("No Such Docker Image"))
    def test_get_not_exist_image(self, mock_get):
        # given
        invalid_image_name = 'invalid_image_name'

        # when
        with self.assertRaises(NoSuchDockerImageException) as e:
            self.instance.inspect_image(image_name=invalid_image_name)

        # then
        mock_get.assert_called_once_with(name=invalid_image_name)

    @patch('apps.dockers.app.DockerManager.inspect_image')
    def test_has_image(self, mock_inspect_image):
        mock_inspect_image.return_value = DockerImage.of(self.__get_test_attrs())

        # given
        image_name = 'valid_image_name'

        # when
        result = self.instance.has_image(image_name=image_name)

        # then
        mock_inspect_image.assert_called_once_with(image_name=image_name)
        self.assertTrue(result)

    @patch('apps.dockers.app.DockerManager.inspect_image', side_effect=NoSuchDockerImageException)
    def test_has_not_image(self, mock_inspect_image):
        # given
        image_name = 'invalid_image_name'

        # when
        result = self.instance.has_image(image_name=image_name)

        # then
        mock_inspect_image.assert_called_once_with(image_name=image_name)
        self.assertFalse(result)

    @patch('apps.dockers.app.DockerManager.has_image')
    @patch('docker.models.images.ImageCollection.remove')
    def test_removing_valid_image(self, mock_remove, mock_has_image):
        mock_has_image.return_value = True

        # given
        image_name = 'valid_image_name'

        # when
        self.instance.remove_image(image_name=image_name)

        # then
        mock_has_image.assert_called_once_with(image_name=image_name)
        mock_remove.assert_called_once_with(image=image_name, force=False)


    @patch('apps.dockers.app.DockerManager.has_image')
    def test_removing_invalid_image(self, mock_has_image):
        mock_has_image.return_value = False

        # given
        image_name = 'invalid_image_name'

        # when, then
        with self.assertRaises(NoSuchDockerImageException) as e:
            self.instance.remove_image(image_name=image_name)

        mock_has_image.assert_called_once_with(image_name=image_name)

