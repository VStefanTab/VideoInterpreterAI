import torch
from PIL import Image
from transformers.models.blip import BlipProcessor, BlipForQuestionAnswering
import clip  # Optional: can be replaced with open_clip for better quant support

# === Device setup ===
device = "cuda" if torch.cuda.is_available() else "cpu"

# === Load BLIP VQA Model ===
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
blip_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base").to(device)

# === Load CLIP ===
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

# === Concept list for CLIP matching ===
concepts = [
    "a person",
    "a fire",
    "a dog",
    "a car",
    "a laptop",
    "an empty street",
    "a crowd",
]
concept_tokens = clip.tokenize(concepts).to(device)

# === Optional preprocessing step ===
def getFrame(image):
    # Modify as needed for your camera input
    return image

# === Main function ===
def generateResponse(prompt, image):
    with torch.no_grad():
        # === Step 1: CLIP Matching (unchanged) ===
        image_clip = clip_preprocess(image).unsqueeze(0).to(device)
        image_features = clip_model.encode_image(image_clip)
        text_features = clip_model.encode_text(concept_tokens)
        similarity = (image_features @ text_features.T).softmax(dim=-1)
        best_idx = similarity[0].argmax().item()
        best_match = concepts[best_idx]
        confidence = similarity[0][best_idx].item()

        # === Step 2: Use BLIP VQA for actual question answering ===
        inputs = blip_processor(image, prompt, return_tensors="pt").to(device)
        out = blip_model.generate(**inputs)
        vqa_answer = blip_processor.decode(out[0], skip_special_tokens=True)

    result = (
        f"🧠 Prompt: {prompt}\n"
        f"🔎 CLIP Match: '{best_match}' ({confidence:.2f})\n"
        f"🤖 VQA Answer: {vqa_answer}"
    )
    return result
