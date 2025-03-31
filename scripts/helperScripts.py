import cv2
import numpy as np
from PIL import Image


def processFrame(frame, prompt):
    if frame is None:
        return "No frame captured"

    # Convert frame to format suitable for processing
    if isinstance(frame, np.ndarray):
        # Convert BGR to RGB if necessary
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
    else:
        pil_image = frame

    # Here you would add your backend processing
    # For now, just return basic info about the capture
    result = f"Frame captured: {pil_image.size}px | Prompt: {prompt}"

    return result