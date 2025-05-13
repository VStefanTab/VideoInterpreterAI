from nano_llm import NanoLLM, ChatHistory
from PIL import Image

model_cache = {}  # Cache for models


def get_model(model):
    # TODO: Check if model loaded correctly
    if model not in model_cache:
        chat_history = ChatHistory(
            model, system_prompt="You are an assistant who perfectly describes images."
        )
        model_cache[model] = NanoLLM.from_pretrained(
            model=model,
            chat_history=chat_history,
            max_context_len=2048,
            max_new_tokens=512,
        )
    return model_cache[model]


def generateResponse(prompt, image):
    # TODO: Tweak model response argumets
    model = get_model("Efficient-Large-Model/VILA-7b")
    response = model.chat(
        prompt,
        image=image,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        num_beams=1,
    )
    return response
