FROM dustynv/llama_cpp:b5283-r36.4-cu128-24.04

ARG LLAMA_CPP_REPO=https://github.com/abetlen/llama-cpp-python.git
ARG LLAMA_CPP_BRANCH=main
ARG LLAMA_CPP_SHA=c37132bac860fcc333255c36313f89c4f49d4c8d
ARG PIP_URL=https://pypi.org/simple/
ARG CUDA_ARCH=87 

WORKDIR /tmp/llama-cpp-python
RUN git clone --recursive --branch=${LLAMA_CPP_BRANCH} ${LLAMA_CPP_REPO} .
RUN git checkout ${LLAMA_CPP_SHA}

RUN FORCE_CMAKE=1 \
    CMAKE_ARGS="-DGGML_CUDA=ON -DLLAVA_BUILD=ON -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCH}" \
    pip install . --force-reinstall --upgrade --index-url ${PIP_URL}

WORKDIR /
RUN rm -rf /tmp/llama-cpp-python

WORKDIR /opt/app
COPY . /opt/app 
RUN pip install --no-cache-dir --index-url ${PIP_URL} -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py"]