import gradio as gr
from app.scripts import *

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(
                label="Input", sources="webcam", streaming=True, type="pil"
            )
            input_prompt = gr.Textbox(label="Prompt", show_label=True)
        with gr.Column():
            output_prompt = gr.Textbox(label="Result")

        def processRequest(image, prompt):
            frame = getFrame(image)

            response = generateResponse(prompt, frame)
            return response

        input_img.stream(
            fn=processRequest,
            inputs=[input_img, input_prompt],
            outputs=output_prompt,
            time_limit=15,
            stream_every=10,
            concurrency_limit=None,
        )
