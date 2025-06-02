#!/bin/bash

# Check if the image name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <image_name> [additional_docker_args]"
  exit 1
fi

IMAGE_NAME=$1
shift  # Shift arguments to allow additional Docker arguments

# Run the container with the specified parameters
sudo docker run --runtime nvidia --network=host -it --rm "$IMAGE_NAME" "$@"