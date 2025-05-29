import base64
from io import BytesIO
import time
from PIL import Image
import gradio as gr
from webui.conn import *


def processRequest(image, prompt):
    if image is None:
        return "No frame captured"
    
    image = image.resize((1344, 336), Image.Resampling.LANCZOS)

    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    image64 = f"data:image/png;base64,{base64_data}"

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
