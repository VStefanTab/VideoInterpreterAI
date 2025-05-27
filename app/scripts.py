import torch
from PIL import Image
from transformers.models.blip import (
    BlipProcessor,
    BlipForConditionalGeneration,
    BlipForQuestionAnswering
)

# === Device setup ===
device = "cuda" if torch.cuda.is_available() else "cpu"

# === Load BLIP captioning (auto description) model ===
caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# === Load BLIP VQA (question answering) model ===
vqa_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
vqa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base").to(device)

# === Optional preprocessing for image/frame ===
def getFrame(image):
    return image

# === Functionality 1: Continuous captioning ===
def describeScene(image):
    with torch.no_grad():
        inputs = caption_processor(images=image, return_tensors="pt").to(device)
        out = caption_model.generate(**inputs, max_new_tokens=50)
        caption = caption_processor.decode(out[0], skip_special_tokens=True)
    return caption

# === Functionality 2: Answer arbitrary prompts ===
def answerPrompt(prompt, image):
    with torch.no_grad():
        if not prompt.strip().endswith("?"):
            prompt = prompt.strip() + "?"
        inputs = vqa_processor(image, prompt, return_tensors="pt").to(device)
        out = vqa_model.generate(**inputs, max_new_tokens=50)
        answer = vqa_processor.decode(out[0], skip_special_tokens=True)
    return answer

# === Combined example ===
def generateResponse(prompt, image):
    caption = describeScene(image)
    answer = answerPrompt(prompt, image)
    return (
        f"📸 Scene description: {caption}\n"
        f"🧠 Prompt: {prompt}\n"
        f"🤖 Answer: {answer}"
    )
