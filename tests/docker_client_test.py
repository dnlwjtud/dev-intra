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

        exist_image = image_client.get('9249c72f04dc76e4e5054f7287386d1a54ab9e759e7d1827efac3e43f947ef0d')

        self.assertIsInstance(exist_image, docker.models.images.Image)
        print(exist_image.attrs)

        with self.assertRaises(docker.errors.ImageNotFound) as e:
        # with self.assertRaises(docker.errors.DockerException) as e:
            image_client.get('invalid-image-name')


    def test_print_containers(self):
        from typing import List, Dict
        container_client = self.docker_client.containers

        self.assertIsInstance(container_client, docker.client.ContainerCollection)

        # the default value of `all` is False.
        # it basically returns running containers.
        container_list = container_client.list(all=True)
        self.assertIsInstance(container_list, List)

        for container in container_list:
            print(container.name)
            self.assertIsInstance(container, docker.models.containers.Container)

        first_con = container_list[0]

        self.assertIsNotNone(first_con.attrs)
        self.assertIsInstance(first_con.attrs, Dict)


    def test_get_invalid_container(self):
        container_client = self.docker_client.containers

        invalid_container_id = 'invalid-container-id'

        # with self.assertRaises(docker.errors.DockerException) as e:
        with self.assertRaises(docker.errors.NotFound) as e:
            container_client.get(container_id=invalid_container_id)


    def test_remove_container(self):
        container_client = self.docker_client.containers

        container_client.run(image='hello-world', name='hello-world')

        con = container_client.get(container_id='hello-world')
        self.assertIsInstance(con, docker.models.containers.Container)

        con.remove()

        with self.assertRaises(docker.errors.NotFound):
            container_client.get(container_id='hello-world')

    def test_print_network_list(self):
        from typing import List
        network_client = self.docker_client.networks

        networks = network_client.list(greedy=True)
        self.assertIsInstance(networks, List)

        print(networks)

        for network in networks:
            # print(network)
            self.assertIsInstance(network, docker.models.networks.Network)
            self.assertIsNotNone(network.attrs)
            self.assertIsNotNone(network.containers)

    def test_print_network_details(self):
        network_client = self.docker_client.networks
        # network = network_client.get(network_id='7e985a0c89e25e34d0f7e95f300594620768f9539bd0fe746327ea5158138448')
        # print(network.containers)

    def test_create_network(self):

        BRIDGE = 'bridge'
        NETWORK_NAME = 'test-network'

        network_client = self.docker_client.networks

        created_network = network_client.create(name=NETWORK_NAME
                                                , driver=BRIDGE)

        self.assertIsInstance(created_network, docker.models.networks.Network)
        self.assertIsNotNone(created_network.attrs)

        self.assertEqual(created_network.attrs.get('Name'), NETWORK_NAME)

        # Remove Test
        created_network_id = created_network.attrs.get('Id')
        created_network.remove()

        with self.assertRaises(docker.errors.DockerException) as e:
            network_client.get(network_id=created_network_id)


