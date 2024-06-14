class DockerException(Exception):
    err_msg: str

    def __init__(self, msg, *args):
        super().__init__(*args)
        self.err_msg = msg


class DockerImageQueueFullException(DockerException):

    def __init__(self, *args):
        super().__init__("Image processing queue is full. Please try again later.", *args)


class DockerImageAlreadyPullingException(DockerException):

    def __init__(self, *args):
        super().__init__("This image is currently in progress.", *args)


