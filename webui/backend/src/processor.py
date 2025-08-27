from io import BytesIO
import time
import uuid
from PIL import Image
import requests
from src.conn import *


# Function to send requests to an external service
def send_request(prompt, image64):
    url = "http://llama:8080/end"
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

    imageBytes = f"data:image/jpeg;base64,{imageBytes}"

    request_id = send_request(prompt, imageBytes)
    if request_id is None:
        return None, "Failed to send request"

    # Return request_id immediately without polling
    return request_id, None
