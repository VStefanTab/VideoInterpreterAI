import clip
import torch
from PIL import Image
from transformers.models.blip import (BlipForConditionalGeneration,
                                      BlipProcessor)

# === Device setup ===
device = "cuda" if torch.cuda.is_available() else "cpu"

# === Load BLIP ===
blip_processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
blip_model_used = blip_model.to(device)

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


# Optional preprocessing step
def getFrame(image):
    # Here you can resize or normalize if needed
    return image


# Main function to handle processing
def generateResponse(prompt, image):
    # === Run BLIP for caption ===
    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    out = blip_model.generate(**inputs)
    caption = blip_processor.decode(out[0], skip_special_tokens=True)

    # === Run CLIP for matching predefined concepts ===
    image_clip = clip_preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = clip_model.encode_image(image_clip)
        text_features = clip_model.encode_text(concept_tokens)
        similarity = (image_features @ text_features.T).softmax(dim=-1)
        best_idx = similarity[0].argmax().item()
        best_match = concepts[best_idx]
        confidence = similarity[0][best_idx].item()

    # === Combine response ===
    result = (
        f"🧠 Prompt: {prompt}\n"
        f"📸 Caption: {caption}\n"
        f"🔎 Best CLIP Match: '{best_match}' ({confidence:.2f})"
    )
    return result
