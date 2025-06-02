import os
from queue import Queue
import threading
import time
import uuid
import requests
from flask import Flask, request, jsonify
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from huggingface_hub import hf_hub_download

inference_queue = Queue()
results = {}
results_lock = threading.Lock()

model_cache = {}
model_path = None

app = Flask(__name__)


def download_model():
    model_name = "ggml-model-q4_k.gguf"
    repo_id = "mys/ggml_llava-v1.5-7b"
    local_dir = "models"
    local_path = os.path.join(local_dir, model_name)

    if not os.path.exists(local_path):
        print(f"Downloading {model_name} from Huggingface...")
        os.makedirs(local_dir, exist_ok=True)
        local_path = hf_hub_download(
            repo_id=repo_id, filename=model_name, local_dir=local_dir
        )
    return local_path


def get_model(modelpath):
    if modelpath not in model_cache:
        print("Initializing model...")
        chat_handler = Llava15ChatHandler.from_pretrained(
            repo_id="mys/ggml_llava-v1.5-7b",
            filename="*mmproj*",
        )
        model_cache[modelpath] = Llama(
            model_path=modelpath,
            n_ctx=2048,
            chat_handler=chat_handler,
            threads=6,
            n_gpu_layers=-1,
            temperature=0.8,
            top_k=40,
            top_p=0.90,
            max_tokens=128,
            logits_all=False,
            verbose=True,
        )
    return model_cache[modelpath]


def inference_worker():
    while True:
        task_id, prompt, img64 = inference_queue.get()
        try:
            result = generate_response(prompt, img64)
        except Exception as e:
            result = f"Error: {str(e)}"

        with results_lock:
            results[task_id] = result
        inference_queue.task_done()


def generate_response(prompt, img64):
    global model_path
    llm = get_model(model_path)

    result = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You are a vision-language assistant. Your task is to first understand the user's question, then carefully analyze the attached image and provide an accurate, relevant, and detailed answer. Always respond to the user's specific question — do not just describe the image.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": img64}},
                ],
            }
        ]
    )["choices"][0]["message"]["content"]
    
    print(f"Generated response: {result}")

    return result


@app.route("/end", methods=["POST"])
def process_package():
    print("Received request at /end")

    try:
        data = request.get_json(force=True)

        id = data.get("id")
        prompt = data.get("prompt")
        image64 = data.get("image64")

        if not id or not prompt or not image64:
            print("Missing one of: id, prompt, image64")
            return jsonify({"error": "Missing data fields"}), 400

        task_id = str(uuid.uuid4())
        with results_lock:
            results[task_id] = None

        inference_queue.put((task_id, prompt, image64))

        while True:
            with results_lock:
                result = results.get(task_id)
            if result is not None:
                break
            time.sleep(0.1)

        send_request(id, result)
        return jsonify({"status": "success", "id": id}), 200

    except Exception as e:
        print(f"Error in /end: {e}")
        return jsonify({"error": "Internal server error"}), 500


def send_request(id, response):
    url = "http://localhost:5000/request"
    payload = {
        "id": id,
        "response": response,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None


model_path = download_model()
get_model(model_path)

if __name__ == "__main__":
    threading.Thread(target=inference_worker, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, debug=False)
