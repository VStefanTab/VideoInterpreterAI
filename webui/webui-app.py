import gradio as gr
import numpy as np
import scripts.helperScripts as hs


demo = gr.Interface(
    fn=hs.processFrame,
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
