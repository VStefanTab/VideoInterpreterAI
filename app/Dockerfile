FROM dustynv/llama_cpp:b5283-r36.4-cu128-24.04

WORKDIR /opt/app
# Filename for copying is temporary
COPY . /opt/app 
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5050
# Filename is temporary. Replace with the actual filename
CMD ["python3", "app.py"]