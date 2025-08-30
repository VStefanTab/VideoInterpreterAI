# VideoInterpreterAI - Alex's branch

Project for AI Video Interpretation on Jetson Orin Nano

## Setup

First, set up **Docker** and **Docker Compose**, which are essential. In the project's root directory, create a `.env` file containing the following line:

`HOST_IP=localhost`

Replace **localhost** with public IP adress of the machine this application will run on, or leave it as is if you don't need to connect to the application from outside your machine.

## Start the application

You can run script `start-app.sh` with `sudo` previleges to start the Docker compose application. User entrypoint will be at the adress set in `.env` file and port **3000**.

The **Llama container** may take longer to start, so connect only when it's ready. You can check it's status by executing `sudo docker compose logs llama`, which will display logs from that container.
Wait until it says `Running on http://someaddress:8080`, then you're good to go.

## Stop the application

Stop application with `sudo docker compose stop`. If you want to stop **and** remove the containers, use `sudo docker compose down`.

### Project components

- **WebUI** built with **Next.js React**
- Fully containerized application with **Docker compose**
- **FastAPI** and **Flask** connectors for container communication
- **llava-v1.5-7b LLava** model
