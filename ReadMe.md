# Simple Docker Helper

Simple Docker Helper is a lightweight web tool designed to efficiently manage Docker containers in environments with restricted network access. This project helps team members who may not be familiar with Docker CLI to easily manage Docker-based operational processes on physical servers.  

Key features include image creation and deletion, container management, an interactive shell for executing commands, and network management. All of these functions are provided through an intuitive web interface, allowing for easy management of the Docker environment without requiring a connection to external networks.  

This project does not use a traditional database and is designed with lightweight operation and quick deployment in mind. As a result, it can be used in real-time production environments with minimal overhead.  

The project was developed in response to the situation of former colleagues at a previous company. If only one person can access the deployed physical server computer and most team members are somewhat unfamiliar with CLI-based Docker management, this tool is intended to be helpful.

## Description

This project operates by executing Docker commands on behalf of the user.  

### Image Management

![removeImage](https://github.com/user-attachments/assets/88d8cbd1-7b0c-42b6-b345-64a2305d86fb)  

Images can be easily managed through the web interface. If an image is currently being used by any running container, a blue dot will appear in the upper-right corner, indicating that the image cannot be deleted.      

By hovering over an image and right-clicking, you can choose to either delete or inspect the image.     

Image inspection provides general information about the image.  

Deleting an image is irreversible. The image is not only removed from the web interface but is also deleted from Docker itself.   

#### Dockerfile
Right-clicking on an empty space in the image list page will take you to a page where you can create an image using a Dockerfile. On this page, you can write the Dockerfile according to its syntax to generate an image.

![buildDockerfile](https://github.com/user-attachments/assets/992f829f-cc9c-404d-b50b-0c246556347c)  

Since the project is intended to be lightweight for use in production environments, Dockerfiles are not saved. They are temporarily created in the project’s root directory and automatically removed after the build is complete.    

After completing the Dockerfile, you can right-click to build it, or you can exit if you wish to stop writing.    

### Container Management
Container management can be easily performed through the web interface. Running containers are indicated with a green dot in the upper-right corner of the container icon, containers with issues are marked with a yellow dot, and stopped containers are marked with a red dot.    

Just like with images, you can interact with containers by hovering over the container icon and right-clicking.  

![containerManaging](https://github.com/user-attachments/assets/33c7aaed-ac59-4cef-aa99-723b1c6f0bb3)  

You can start, restart, stop, unstop, update, or inspect containers. The inspection of a container provides general information about it.    

#### Interactive Shell

![containerTerminal](https://github.com/user-attachments/assets/80e3d3b9-5ab0-4fbd-8cf1-23852b202f19)

The connect button is enabled only for running containers. Clicking this button initiates socket communication with the container, allowing you to access its internal shell. This function operates the same way as the docker exec -it sh command.    

Since the connection is made via socket communication, it is strongly recommended to close the connection manually. You can exit the connection using the 'exit' command.    

#### Staring a Container

![CreateContainer](https://github.com/user-attachments/assets/dd8653e2-9e5f-408a-8154-7218291e5777)  

You can easily start a container based on an image that has been downloaded or built locally. Right-click on an empty space in the container list and go to the container execution page to start a new container.      

After selecting the image and network, you can configure the container by entering ports, environment variables, and command-line options, then click the create button to start the container.   

### Network Management

![NetworkCreate](https://github.com/user-attachments/assets/f94a836c-e2a8-4002-a58d-2585e3a32f6e)

Networks can be easily managed. Active networks are indicated with a blue dot in the upper-right corner of the network icon, similar to images. If no container is connected to the network or if the connected containers are not running, there will be no indicator.    

Only unused networks can be deleted, and these changes are reflected in Docker.    

## Getting Started

This project is built with FastAPI in Python. Therefore, Python must be installed beforehand.  

### Executing program

You can run the FastAPI application using the following commands: 

- Linux based OS
```shell
sh start.sh
```

- Windows OS
```shell
start.bat
```

## License

This project is licensed under the MIT License.