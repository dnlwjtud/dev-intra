from apps.dockers.modules import DockerCommandExecuteMixin

if __name__ == '__main__':
    t = DockerCommandExecuteMixin()

    result = t.docker_inspect(container_id='999')
    print(result)
    print(1)

