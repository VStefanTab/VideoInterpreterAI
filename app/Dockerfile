FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG NVIDIA_VISIBLE_DEVICES=all
ARG NVIDIA_DRIVER_CAPABILITIES=compute,utility

ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES}
ENV NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES}

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    cmake \
    curl \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /opt/app

COPY requirements.txt .

ENV CMAKE_ARGS="-DGGML_CUDA=ON -DLLAVA_BUILD=ON"
ENV FORCE_CMAKE=1
ENV LLAMA_CUDA=1

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu123

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]