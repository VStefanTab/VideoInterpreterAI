import cv2
import numpy as np
from PIL import Image
from llama_cpp import Llama
from transformers import CLIPProcessor, CLIPModel
import torch

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
llama_model = Llama(model_path="")  # TODO Add model path

def getFrame(image):
    if image is None:
        return "No frame captured"

    # Convert frame to format suitable for processing
    if isinstance(image, np.ndarray):
        # Convert BGR to RGB if necessary
        frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
    else:
        pil_image = image

    return image

def exctractFrameData(frame):
    image = Image.open(frame).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    return image_features.squeeze().tolist()

def generateResponse(prompt, imageData):
    # TODO Add prompt and image details, test it
    response = llama_model.generate(prompt, imageData=imageData)
    return response