import os
import requests
from flask import Flask, request, jsonify
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from huggingface_hub import hf_hub_download

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
            n_gpu_layers=-1,
            logits_all=False,
            verbose=True,
        )
    return model_cache[modelpath]


def generate_response(prompt, img64):
    global model_path

    llm = get_model(model_path)

    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You are an assistant who perfectly describes images. Carefully analyze the image and provide a detailed and correct answer to the user's question.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": img64}},
                ],
            },
        ]
    )

    return output["choices"][0]["message"]["content"]


@app.route("/end", methods=["POST"])
def test_endpoint():
    print("Received request at /end")

    try:
        data = request.get_json(force=True)

        id = data.get("id")
        prompt = data.get("prompt")
        image64 = data.get("image64")

        if not id or not prompt or not image64:
            print("Missing one of: id, prompt, image64")
            return jsonify({"error": "Missing data fields"}), 400

        print(f"Received prompt: {prompt}")
        print(f"Received image64: {image64[:30]}...")
        print(f"Request ID: {id}")
        
        response = generate_response(prompt, image64)

        send_request(id, response)
        return jsonify({"status": "success", "id": id}), 200

    except Exception as e:
        print(f"Error in /end: {e}")
        return jsonify({"error": "Internal server error"}), 500


def send_request(id, response):
    url = "http://host.docker.internal:5000/request"
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
    app.run(host="0.0.0.0", port=8080, debug=False)
