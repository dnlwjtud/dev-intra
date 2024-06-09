class DockerException(Exception):
    err_msg: str

    def __init__(self, msg, *args):
        super().__init__(*args)
        self.err_msg = msg


