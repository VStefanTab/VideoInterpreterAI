import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/end", methods=["POST"])
def test_endpoint():
    print("Received request at /end")

    try:
        data = request.get_json(force=True)
        print("Parsed JSON:", data)

        # Safely extract fields
        id = data.get("id")
        prompt = data.get("prompt")
        image64 = data.get("image64")

        if not id or not prompt or not image64:
            print("Missing one of: id, prompt, image64")
            return jsonify({"error": "Missing data fields"}), 400

        print(f"Received prompt: {prompt}")
        print(f"Received image64: {image64[:30]}...")
        print(f"Request ID: {id}")

        send_request(id, "This is a test response")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
