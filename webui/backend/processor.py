import base64
from io import BytesIO
import time
import uuid
from PIL import Image
import requests
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
        return None, "No frame captured"

    # # Decode the image bytes
    # image = Image.open(BytesIO(base64.b64decode(imageBytes.split(",")[1])))

    # # Resize the image
    # image = image.resize((1344, 336), Image.Resampling.LANCZOS)

    # # Convert image to base64
    # buffered = BytesIO()
    # image.save(buffered, format="JPEG")
    # image_bytes = buffered.getvalue()
    # base64_data = base64.b64encode(image_bytes).decode("utf-8")
    imageBytes = f"data:image/jpeg;base64,{imageBytes}"

    request_id = send_request(prompt, imageBytes)
    if request_id is None:
        return None, "Failed to send request"

    # Return request_id immediately without polling
    return request_id, None
