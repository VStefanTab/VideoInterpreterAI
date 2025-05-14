from nano_llm import NanoLLM, ChatHistory
from PIL import Image

model_cache = {}  # Cache for models


def get_model(model):
    # TODO: Check if model loaded correctly
    if model not in model_cache:
        model_cache[model] = NanoLLM.from_pretrained(model=model)
    return model_cache[model]


def generateResponse(prompt, image):
    # TODO: Tweak model response argumets
    model = get_model("Efficient-Large-Model/VILA-7b")

    inputs = {
        "user": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image", "image": image},
        ],
    }
    response = model.generate(
        inputs=inputs,
        streaming=False,
    )
    return response
