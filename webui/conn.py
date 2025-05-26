from flask import Flask, request, jsonify
import requests
from threading import Lock
import uuid

app = Flask(__name__)
responses = {}
lock = Lock()


@app.route("/request", methods=["POST"])
def receive_response():
    data = request.get_json()
    request_id = data.get("id")
    response_text = data.get("response")

    if not request_id or not response_text:
        return "Invalid format", 400

    with lock:
        responses[request_id] = response_text

    return "OK", 200


@app.route("/result", methods=["GET"])
def get_response():
    request_id = request.args.get("id")
    if not request_id:
        return jsonify({"response": None})

    with lock:
        response = responses.pop(request_id, None)

    return jsonify({"response": response})


def send_request(prompt, image64):
    url = "http:/?"  # TODO: Replace with actual URL
    request_id = str(uuid.uuid4())

    payload = {
        "id": request_id,
        "prompt": prompt,
        "image64": image64,
        "flags": [],  # Add flags if needed
    }

    try:
        requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None

    return request_id
