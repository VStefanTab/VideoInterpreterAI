import os
import base64
import re
from queue import Queue
import threading
import time
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from huggingface_hub import hf_hub_download
from PIL import Image
from io import BytesIO

inference_queue = Queue()
results = {}
results_lock = threading.Lock()

model_cache = {}
model_path = None

app = Flask(__name__)
CORS(app)


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
            n_ctx=3072,
            chat_handler=chat_handler,
            n_threads=6, 
            n_gpu_layers=-1,
            verbose=True,
        )
    return model_cache[modelpath]


def process_image(img64):
    try:
        # Remove data URL prefix if present
        if img64.startswith('data:'):
            img64 = img64.split(',', 1)[1]
        
        # Decode base64
        image_data = base64.b64decode(img64)
        
        # Validate it's a proper image
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (LLaVA works better with smaller images)
        max_size = 512
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert back to base64
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        processed_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{processed_b64}"
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def inference_worker():
    while True:
        task_id, prompt, img64 = inference_queue.get()
        try:
            result = generate_response(prompt, img64)
        except Exception as e:
            result = f"Error: {str(e)}"
            print(f"Inference error: {e}")

        with results_lock:
            results[task_id] = result
        inference_queue.task_done()


def generate_response(prompt, img64):
    global model_path
    
    # Process the image first
    processed_image = process_image(img64)
    if not processed_image:
        return "Error: Could not process the provided image."
    
    llm = get_model(model_path)

    try:
        # Use a more specific system prompt for LLaVA
        system_prompt = """You are an AI assistant that can see and analyze images. When given an image and a question, provide a clear, accurate, and helpful response based on what you observe in the image. Be specific and descriptive in your analysis."""
        
        # Create the chat completion with proper parameters
        result = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": processed_image}},
                    ],
                },
            ],
            temperature=0.7,
            top_k=40,
            top_p=0.9,
            max_tokens=512,  # Increased max tokens
            stop=["\n\n\n", "###"],  # Add stop sequences to prevent repetition
            repeat_penalty=1.1,  # Prevent repetitive outputs
        )
        
        response_text = result["choices"][0]["message"]["content"].strip()
        
        # Clean up common issues
        if not response_text or response_text.count("#") > len(response_text) * 0.5:
            return "I'm having trouble processing this image. Could you please try with a different image or rephrase your question?"
        
        return response_text

    except Exception as e:
        print(f"Error in generate_response: {e}")
        return f"Error generating response: {str(e)}"


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

        print(f"Processing request - ID: {id}, Prompt length: {len(prompt)}, Image length: {len(image64)}")

        task_id = str(uuid.uuid4())
        with results_lock:
            results[task_id] = None

        inference_queue.put((task_id, prompt, image64))

        # Wait for result with timeout
        timeout = 120  # 2 minutes timeout
        start_time = time.time()
        
        while True:
            with results_lock:
                result = results.get(task_id)
            if result is not None:
                break
            if time.time() - start_time > timeout:
                return jsonify({"error": "Request timeout"}), 500
            time.sleep(0.1)

        # Clean up result from memory
        with results_lock:
            del results[task_id]

        send_request(id, result)
        return jsonify({"status": "success", "id": id}), 200

    except Exception as e:
        print(f"Error in /end: {e}")
        return jsonify({"error": "Internal server error"}), 500


def send_request(id, response):
    url = "http://processing:5000/request"
    payload = {
        "id": id,
        "response": response,
    }

    try:
        response_req = requests.post(url, json=payload, timeout=30)
        response_req.raise_for_status()
        return response_req.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None


# Add health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "model_loaded": model_path is not None}), 200


if __name__ == "__main__":
    try:
        print("Downloading and initializing model...")
        model_path = download_model()
        get_model(model_path)  # Pre-load the model
        print("Model loaded successfully!")
        
        # Start the inference worker
        threading.Thread(target=inference_worker, daemon=True).start()
        
        print("Starting server...")
        app.run(host="0.0.0.0", port=8080, debug=False)
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        exit(1)