import base64
from io import BytesIO
import time
import uuid
from PIL import Image
from fastapi import requests
from webui.backend.conn import *


# Function to send requests to an external service
def send_request(prompt, image64):
    url = "http://127.0.0.1:8080/end"
    request_id = str(uuid.uuid4())

    payload = {"id": request_id, "prompt": prompt, "image64": image64}

    try:
        requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None

    return request_id


def processRequest(imageBytes, prompt):
    if imageBytes is None:
        return "No frame captured"

    # Decode the image bytes
    image = Image.open(BytesIO(base64.b64decode(imageBytes.split(",")[1])))

    # Resize the image
    image = image.resize((1344, 336), Image.Resampling.LANCZOS)

    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    image64 = f"data:image/png;base64,{base64_data}"

    request_id = send_request(prompt, image64)
    if request_id is None:
        return "Failed to send request"

    # Poll for response
    for _ in range(30):
        try:
            resp = requests.get(
                "http://localhost:5000/result", params={"id": request_id}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("response"):
                    return data["response"]
        except Exception as e:
            print(f"Polling error: {e}")

        time.sleep(0.3)  # Wait before polling again

    return "Timed out waiting for response"

