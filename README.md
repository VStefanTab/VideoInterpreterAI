# VideoInterpreterAI - Alex's branch

Project for AI Video Interpretation on Jetson Orin Nano

## Setup

Create venv and install requirements via pip. Build llama_cpp container with `docker build -t [Container name] ./app`.
WebUI and container are ran async, for that there are two scripts: `run-webui.sh` and `run-container.sh`. `run-container.sh` needs container name passed to run it.

## Known issues

When WebUI sends a request to container, it catches it, sends to llama_cpp, but at the end of inference (or after sending back response) causes severe lag and unresponsivness of system.