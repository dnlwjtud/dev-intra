import docker

from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from apps.dockers.app import DockerManager

if __name__ == '__main__':
    main()

class DockerManagerTest(TestCase):

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
        from apps.dockers.models import PullingImageDescription, DockerImage

        instance = DockerManager()

        mock_image_result = MagicMock()
        mock_image_result.attrs = {'Id': "sha:256:test_id_value"
                                    , 'RepoTags': ['test:latest']
                                    , 'Created': '2024-07-20T23:55:55Z'
                                    , 'Comment': ''
                                    , 'Size': 139168068}
        mock_pull.return_value = mock_image_result

        # given
        desc = PullingImageDescription(repository='test')

        # when
        image = instance.pull_image(desc=desc)

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
        from apps.dockers.models import PullingImageDescription
        from apps.dockers.exceptions import DockerImagePullingException

        instance = DockerManager()

        # given
        desc = PullingImageDescription(repository='unavailable_repo_name', tag='unavailable_tag')

        # when, then
        with self.assertRaises(DockerImagePullingException) as err:
            instance.pull_image(desc)

            self.assertEqual(err.err_msg
             , "Could not pull image. It may be due to an incorrect repository or tag. Please check it again")


