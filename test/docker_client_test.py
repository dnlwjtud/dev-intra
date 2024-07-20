import docker

from unittest import TestCase, main

if __name__ == '__main__':
    main()


class DockerClientTests(TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.docker_client = docker.from_env()
            if not cls.docker_client.ping():
                cls.docker_client = None
        except Exception:
            cls.docker_client = None

    def setUp(self):
        if self.docker_client is None:
            self.skipTest('Docker client is not available')

    def test_pulling_image(self):

        # Pulling Test Image
        images = self.docker_client.images
        hello_world_image = images.pull(repository='hello-world')
        print(hello_world_image)

        # Removing Test Image
        # images.remove(image='hello-world')

    def test_get_images(self):

        images = self.docker_client.images

        self.assertIsInstance(images, docker.client.ImageCollection)

        # Including dangling image
        image_list = images.list(all=True)

        for image in image_list:
            print(image)

    def test_print_specific_image(self):

        images = self.docker_client.images

        searched_images = images.list(name='hello-world')

        for image in searched_images:
            print(image)
            print(image.attrs)


    def test_get_containers(self):
        containers = self.docker_client.containers

        self.assertIsInstance(containers, docker.client.ContainerCollection)

        # the default value of `all` is False.
        # it basically returns running containers.
        container_list = containers.list(all=True)

        for container in container_list:
            print(container.name)


