# VideoInterpreterAI - Alex's branch

Project for AI Video Interpretation on Jetson Orin Nano

## Setup

Create venv and install requirements via pip. Build llama_cpp container with `docker build -t [Container name] ./app`.
WebUI and container are ran async, for that there are two scripts: `run-webui.sh` and `run-container.sh`. `run-container.sh` needs container name passed to run it.

## Known issues

Generated output sometimes may not consider question and only consider picture description. The longer application runs, the less intelligent responses are produced.

### Project components

- WebUI built with Gradio.
- Docker container with Llama.cpp
- FastAPI and Flask connectors for container communication
- llava-v1.5-7b LLava model
