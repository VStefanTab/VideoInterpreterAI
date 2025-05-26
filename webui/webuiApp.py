import base64
from io import BytesIO
import time
import gradio as gr
from conn import *


def processRequest(image, prompt):
    if image is None:
        return "No frame captured"

    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    image64 = base64.b64encode(image_bytes).decode("utf-8")

    request_id = send_request(prompt, image64)
    if request_id is None:
        return "Failed to send request"

    # Poll for response
    for _ in range(30): 
        try:
            resp = requests.get(
                "http://localhost:5000/result", params={"id": request_id}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("response"):
                    return data["response"]
        except Exception as e:
            print(f"Polling error: {e}")

        time.sleep(0.3)  # Wait before polling again

    return "Timed out waiting for response"


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(
                label="Input", sources="webcam", streaming=True, type="pil"
            )
            input_prompt = gr.Textbox(label="Prompt", show_label=True)
        with gr.Column():
            output_prompt = gr.Textbox(label="Result")

        input_img.stream(
            fn=processRequest,
            inputs=[input_img, input_prompt],
            outputs=output_prompt,
            time_limit=15,
            stream_every=10,
            concurrency_limit=None,
        )
