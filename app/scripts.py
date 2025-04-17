import cv2
import numpy as np
from PIL import Image


def getFrame(image):
    if image is None:
        return "No frame captured"

    try:
        # Convert frame to format suitable for processing
        if isinstance(image, np.ndarray):
            # Convert BGR to RGB if necessary
            frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
        else:
            pil_image = image

        return pil_image

    except Exception as e:
        return None, f"Error processing frame: {str(e)}"


def generateResponse(prompt, image):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image,
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]

    # text = processor.apply_chat_template(
    #    messages, tokenize=False, add_generation_prompt=True
    # )

    # inputs = processor(
    #    text=[text],
    #    images=[image],
    #    padding=True,
    #    return_tensors="pt",
    # )
    # inputs = inputs.to("cuda")

    ## INFO: Relies on torchvision and torch+cuda, but current torch+cu version conflicts with torchvision
    #  generated_ids = model.generate(
    #    **inputs,
    #    max_new_tokens=128,
    #    do_sample=True,
    #    temperature=0.7,
    #    top_p=0.9,
    # )

    ## Decode the entire output
    # raw_output = processor.batch_decode(
    #    generated_ids,
    #    skip_special_tokens=True,
    #    clean_up_tokenization_spaces=True,
    # )

    ## Extract the actual response (usually after the prompt)
    # response = raw_output[0].split("Assistant:")[-1].strip()
    #
    # return response
