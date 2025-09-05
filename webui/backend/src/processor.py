import base64
from io import BytesIO
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

    try:
        # Attempt to open and validate image
        image = Image.open(BytesIO(imageBytes))

        # Calculate new dimensions while maintaining aspect ratio
        max_size = 800
        ratio = min(max_size / image.width, max_size / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))

        # Resize image if it's larger than max_size
        if image.width > max_size or image.height > max_size:
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Convert back to base64
        buffered = BytesIO()
        image.save(buffered, format=image.format or "JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Add data URI prefix if not present
        if not image_base64.startswith("data:image"):
            image_base64 = f"data:image/jpeg;base64,{image_base64}"
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

    request_id = send_request(prompt, imageBytes)
    if request_id is None:
        return None, "Failed to send request"

    # Return request_id immediately without polling
    return request_id, None
