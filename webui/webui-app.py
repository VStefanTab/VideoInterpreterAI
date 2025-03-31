import gradio as gr
import numpy as np


def main(img, prompt):
    return prompt
    
demo = gr.Interface(
    fn = main,
    inputs = [gr.Image(sources=["webcam"], streaming=True), gr.Textbox(label= "Prompt", show_label=True)],
    outputs = [gr.Textbox(label="Result", show_label=True)],
    live=True,
    flagging_mode="never"
)

demo.launch()
