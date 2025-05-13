import gradio as gr
from app.scripts import *


def processRequest(image, prompt):
    if image is None:
        return "No frame captured"
    response = generateResponse(prompt, image)
    return response


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
