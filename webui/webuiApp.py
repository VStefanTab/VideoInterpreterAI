import gradio as gr
from app.scripts import *

# Main processing function: runs whenever the webcam stream is active

def processRequest(image, prompt):
    frame = getFrame(image)
    response = generateResponse(prompt, frame)
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

    # Stream frames continuously and process each as long as the user has activated the webcam
    input_img.stream(
        fn=processRequest,
        inputs=[input_img, input_prompt],
        outputs=[output_prompt],
        time_limit=None,
        stream_every=1,
        concurrency_limit=None,
    )

# Launch the demo application
demo.launch()

