# VideoInterpreterAI - Alex's branch

Project for AI Video Interpretation on Jetson Orin Nano

## Description

A LLama version of the video Interpreter. Differs from BLIP version by using LLama framework inside container made specifically for jetson machine. Average response time ~15-20 seconds.

## Setup

1. Create virtual enviroment using python inside this folder and install requirements via pip.
2. Build llama_cpp docker image with `docker build -t [Image name] ./app`. It may take around 10 minutes to build image and will use ~10GB of space.

## Running project

WebUI and LLama container are ran separately from each other, for that there are two scripts: `run-webui.sh` and `run-container.sh`.
`run-webui.sh` is responsible for starting WebUI. It automatically detects virtual enviroment and starts WebUI from it.

`run-container.sh` needs image name passed to run it. Run this script like this `./run-container.sh [Image name]` and container will be created by docker. Container may need some time to start because it downloads LLaVa model for inference and starts LLama. When finished startup, in the console will be shown URL for connection to container, do not access it manually, it is for WebUI to send requests.

## Known issues

Generated output sometimes may not consider question and only consider picture description. The longer application runs, the less intelligent responses are produced.

### Project components

- WebUI built with Gradio.
- Docker container with Llama.cpp
- FastAPI and Flask connectors for container communication
- llava-v1.5-7b Q4_K LLava model
