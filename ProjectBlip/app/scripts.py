import torch
from PIL import Image
import cv2
from transformers import BitsAndBytesConfig
from transformers.models.blip import (
    BlipProcessor,
    BlipForConditionalGeneration,
    BlipForQuestionAnswering
)

# === Device setup ===
device = "cuda" if torch.cuda.is_available() else "cpu"
CUDA = torch.cuda.is_available()
dtype  = torch.float16 if CUDA else torch.float32

# --------------------------- 8-bit quantisation -------------------------
bnb_cfg = None
if CUDA:
    try:                               # bitsandbytes present?
        bnb_cfg = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0,    # keep ∼99 % accuracy
        )
    except Exception:
        pass                           # silently fall back to full precision

# === Load BLIP captioning (auto description) model ===
caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device).eval()

# === Load BLIP VQA (question answering) model ===
vqa_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
vqa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base").to(device).eval()

# === Preprocessing for image/frame ===
def getFrame(src):
    from PIL import Image
    import numpy as np

    # Webcam (PIL Image)
    if isinstance(src, Image.Image):
        return src

    # Uploaded video file (file-like object)
    if hasattr(src, "name"):  # TempFile or similar from Gradio
        video_path = src.name
    elif isinstance(src, str):  # Sometimes it's just a file path
        video_path = src
    else:
        raise ValueError(f"Unsupported input type for getFrame: {type(src)}")

    # Try to extract first frame
    cap = cv2.VideoCapture(video_path)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise ValueError("Could not read frame from video!")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame)

    

# === Captioning ===
@torch.inference_mode()
def describeScene(image: Image.Image) -> str:
    image = image.resize((384, 384)) 
    inputs = caption_processor(images=image, return_tensors="pt").to(device, dtype)
    out = caption_model.generate(**inputs, max_new_tokens=50)
    return caption_processor.decode(out[0], skip_special_tokens=True).strip()

# === Answer prompts ===
@torch.inference_mode()
def answerPrompt(prompt: str, image: Image.Image) -> str:
    if not prompt.strip().endswith("?"):
        prompt = prompt.strip() + "?"
    image = image.resize((384, 384))
    inputs = vqa_processor(image, prompt, return_tensors="pt").to(device, dtype)
    out = vqa_model.generate(**inputs, max_new_tokens=50)
    return vqa_processor.decode(out[0], skip_special_tokens=True).strip()
    

# === Generate response ===
@torch.inference_mode()
def processRequest(media, prompt):
    prompt = prompt or ""

    frame = getFrame(media)
    caption = describeScene(frame)
    answer = answerPrompt(prompt, frame) if prompt.strip() else ""
    return caption, prompt, answer
    
@torch.inference_mode()
def processVideoRequest(video_file, prompt):
    import math
    prompt = prompt or ""

    if video_file is None:
        return "No video file provided.", prompt, ""

    # Extract path
    if hasattr(video_file, "name"):
        video_path = video_file.name
    elif isinstance(video_file, str):
        video_path = video_file
    else:
        raise ValueError(f"Unsupported input type for processVideoRequest: {type(video_file)}")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps else 0

    interval_sec = 1
    sample_frames = [int(i * fps) for i in range(0, math.ceil(duration), interval_sec)]

    captions = []
    last_frame_img = None

    for fno in sample_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
        ok, frame = cap.read()
        if not ok:
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        last_frame_img = pil_img
        desc = describeScene(pil_img)
        captions.append(f"t={fno/fps:.1f}s: {desc}")

    cap.release()

    # === Logic change here ===
    if prompt.strip() and last_frame_img:
        # Display the answer in the scene analysis box
        answer = answerPrompt(prompt, last_frame_img)
        return answer, prompt, ""
    else:
        # No question -> fallback to captioning summary
        final_caption = "\n".join(captions) if captions else "No frames could be analyzed."
        return final_caption, prompt, ""