FROM dustynv/llama_cpp:b5283-r36.4-cu128-24.04

ARG LLAMA_CPP_REPO=https://github.com/abetlen/llama-cpp-python.git
ARG LLAMA_CPP_BRANCH=main
ARG CUDA_ARCH=87 

WORKDIR /tmp/llama-cpp-python
RUN git clone --recursive --branch=${LLAMA_CPP_BRANCH} ${LLAMA_CPP_REPO} .

RUN FORCE_CMAKE=1 \
    CMAKE_ARGS="-DGGML_CUDA=ON -DLLAVA_BUILD=ON -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCH}" \
    pip install . --force-reinstall --upgrade

WORKDIR /
RUN rm -rf /tmp/llama-cpp-python

WORKDIR /opt/app
COPY . /opt/app 
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py"]