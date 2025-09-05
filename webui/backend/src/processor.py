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
        # Remove data URI prefix if present, leaving only the base64 string
        if imageBytes.startswith("data:image"):
            base64_string = imageBytes.split(",")[1]
        else:
            base64_string = imageBytes

        # Convert base64 string to bytes
        image_data = base64.b64decode(base64_string)

        # Attempt to open and validate image
        image = Image.open(BytesIO(image_data))

        max_size = 800
        if image.width > max_size or image.height > max_size:
            ratio = min(max_size / image.width, max_size / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            # Using LANCZOS for high-quality resampling
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Ensure proper image mode for JPEG (RGB)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background for transparency
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            # Convert to RGB if not already
            image = image.convert('RGB')

        # Convert back to base64 with higher quality JPEG compression
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=95, optimize=True)
        processed_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Add the required data URI prefix
        final_image_string = f"data:image/jpeg;base64,{processed_base64_string}"

    except Exception as e:
        return None, f"Error processing image: {str(e)}"

    request_id = send_request(prompt, final_image_string)
    if request_id is None:
        return None, "Failed to send request"

    # Return request_id immediately without polling
    return request_id, None
