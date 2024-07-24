from apps.core.exception import MessageException

class DockerEngineException(MessageException):

    def __init__(self, *args):
        super().__init__("Could not create an instance of the Docker client. This may be due to the absence of the Docker Engine. Please check it again.", *args)

class DockerProcessingException(MessageException):
    def __init__(self, *args):
        super().__init__("An unexpected exception occurred while processing. Please check again.", *args)

class DockerImagePullingException(MessageException):

    def __init__(self, *args):
        super().__init__("Could not pull image. It may be due to an incorrect repository or tag. Please check it again", *args)

class NoSuchDockerImageException(MessageException):
    def __init__(self, *args):
        super().__init__("Could not find such image. Please check it again.", *args)

class NoSuchDockerContainerException(MessageException):
    def __init__(self, *args):
        super().__init__("Could not find such container. Please check it again.", *args)


class DockerImageQueueFullException(MessageException):

    def __init__(self, *args):
        super().__init__("Image processing queue is full. Please try again later.", *args)


class DockerImageAlreadyProcessingException(MessageException):

    def __init__(self, *args):
        super().__init__("This image is currently in progress.", *args)

class DockerImageNotFoundException(MessageException):

    def __init__(self, *args):
        super().__init__("Could not find such image.", *args)


