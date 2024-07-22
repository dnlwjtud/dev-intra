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
        image_client = self.docker_client.images
        hello_world_image = image_client.pull(repository='hello-world')
        print(hello_world_image)

        self.assertIsInstance(hello_world_image, docker.models.images.Image)

        # Removing Test Image
        # images.remove(image='hello-world')

    def test_removing_image(self):
        image_client = self.docker_client.images

        target_image = 'hello-world'

        hello_world_image = image_client.pull(repository=target_image)
        print(hello_world_image)

        self.assertIsInstance(hello_world_image, docker.models.images.Image)

        # returning nothing
        image_client.remove(image=target_image)

        # recover image
        image_client.pull(repository=target_image)

    def test_removing_invaild_image(self):
        image_client = self.docker_client.images

        target_image = 'invalid-image'

        with self.assertRaises(docker.errors.DockerException) as e:
            image_client.remove(image=target_image)


    def test_print_image_list(self):

        image_client = self.docker_client.images

        self.assertIsInstance(image_client, docker.client.ImageCollection)

        # Including dangling image
        image_list = image_client.list(all=True)

        for image in image_list:
            print(image)

    def test_print_search_from_image_list(self):

        image_client = self.docker_client.images

        # search by name
        search_result1 = image_client.list(name='hello-world')

        print("result 1")
        print(search_result1)
        for result in search_result1:
            self.assertIsInstance(result, docker.models.images.Image)
            print(result)

        # search including dangling
        search_result2 = image_client.list(filters={
            "dangling": True
        })

        print("result 2")
        print(search_result2)
        for result in search_result2:
            print(result)

        # invalid image name
        search_result3 = image_client.list(name='invalid-image-name')

        print("result 3")
        print(search_result3)
        for result in search_result3:
            print(result)


    def test_print_image(self):

        image_client = self.docker_client.images

        exist_image = image_client.get('hello-world')

        self.assertIsInstance(exist_image, docker.models.images.Image)
        print(exist_image.attrs)

        with self.assertRaises(docker.errors.ImageNotFound) as e:
        # with self.assertRaises(docker.errors.DockerException) as e:
            image_client.get('invalid-image-name')



    def test_print_containers(self):
        containers = self.docker_client.containers

        self.assertIsInstance(containers, docker.client.ContainerCollection)

        # the default value of `all` is False.
        # it basically returns running containers.
        container_list = containers.list(all=True)

        for container in container_list:
            print(container.name)


