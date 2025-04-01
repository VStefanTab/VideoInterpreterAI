import gradio as gr
from scripts.scripts import *

def processRequest(image, prompt):
    # TODO Add mechanism for getting n-th frame from video
    frame = getFrame(image)
    frameData = exctractFrameData(frame)
    
    response = generateResponse(prompt, frameData)
    return response

demo = gr.Interface(
    fn=processRequest,
    inputs=[
        gr.Image(sources=["webcam"], streaming=True, tool="select", type="pil"),
        gr.Textbox(label="Prompt", show_label=True),
    ],
    outputs=[gr.Textbox(label="Result")],
    title="AI Video Interpreter",
    live=True,
    flagging_mode="never",
)

demo.launch()
