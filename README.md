# VideoInterpreterAI - Alex's branch

Project for AI Video Interpretation on Jetson Orin Nano

## Setup

First, set up **Docker** and **Docker Compose**, which are essential. In the project's root directory, create a `.env` file containing the following line:

`HOST_IP=localhost`

Replace **localhost** with public IP adress of the machine this application will run on, or leave it as is if you don't need to connect to the application from outside your machine.

## Start the application

You can run script `start-app.sh` with `sudo` previleges to start the Docker compose application. User entrypoint will be at the adress set in `.env` file and port **3000**.

*Be aware* that the application is quite large. To run it without problem, you might need **20GB+** of space. This is due to complex dependencies of the llama container.

## Stop the application

Stop application with `sudo docker compose stop`. If you want to stop **and** remove the containers, use `sudo docker compose down`.

### Project components

- **WebUI** built with **Next.js React**
- Fully containerized application with **Docker compose**
- **FastAPI** and **Flask** connectors for container communication
- **llava-v1.5-7b LLava** model
