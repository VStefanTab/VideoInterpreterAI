FROM dustynv/llama_cpp:b5283-r36.4-cu128-24.04

ARG PIP_URL=https://pypi.org/simple/
ARG CUDA_ARCH=87 

RUN FORCE_CMAKE=1 \
    CMAKE_ARGS="-DGGML_CUDA=ON -DLLAVA_BUILD=ON -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCH}" \
    pip install llama-cpp-python==0.3.10 --force-reinstall --upgrade --index-url ${PIP_URL}

WORKDIR /
RUN rm -rf /tmp/llama-cpp-python

WORKDIR /opt/app
COPY . /opt/app 
RUN pip install --no-cache-dir --index-url ${PIP_URL} -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py"]