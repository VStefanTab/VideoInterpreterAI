import gradio as gr
from app.scripts import *

# === Unified function ===
def processRequest(image, prompt):
    frame = getFrame(image)
    scene_description = describeScene(frame)  # continuous description
    answer = answerPrompt(prompt, frame) if prompt.strip() else ""
    
    return scene_description, prompt, answer

css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #0f172a !important;
    min-height: 100vh;
}

.main-container {
    background: #1e293b !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    border: 1px solid #334155 !important;
    margin: 16px !important;
    padding: 24px !important;
}

.header-section {
    text-align: center !important;
    margin-bottom: 24px !important;
    padding-bottom: 16px !important;
    border-bottom: 1px solid #334155 !important;
}

.header-title {
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    color: #f1f5f9 !important;
    margin-bottom: 4px !important;
}

.header-subtitle {
    color: #94a3b8 !important;
    font-size: 0.95rem !important;
    font-weight: 400 !important;
}

.input-section, .output-section {
    background: #334155 !important;
    border-radius: 6px !important;
    padding: 20px !important;
    border: 1px solid #475569 !important;
}

.section-header {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    margin-bottom: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.webcam-container {
    border-radius: 6px !important;
    overflow: hidden !important;
    border: 1px solid #475569 !important;
    background: #1e293b !important;
}

.prompt-input {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 6px !important;
    color: #f1f5f9 !important;
    padding: 12px !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s ease !important;
}

.prompt-input:focus {
    border-color: #64748b !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(100, 116, 139, 0.2) !important;
}

.prompt-input::placeholder {
    color: #64748b !important;
}

.output-box {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 6px !important;
    padding: 16px !important;
    min-height: 100px !important;
    font-size: 0.9rem !important;
    line-height: 1.5 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', monospace !important;
}

.scene-output {
    border-left: 3px solid #10b981 !important;
}

.prompt-output {
    border-left: 3px solid #3b82f6 !important;
}

.answer-output {
    border-left: 3px solid #8b5cf6 !important;
}

.status-dot {
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    background: #10b981 !important;
    animation: pulse 2s infinite !important;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* Scrollbar styling */
.output-box::-webkit-scrollbar {
    width: 6px;
}

.output-box::-webkit-scrollbar-track {
    background: #1e293b;
}

.output-box::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 3px;
}

.output-box::-webkit-scrollbar-thumb:hover {
    background: #64748b;
}

/* Responsive design */
@media (max-width: 768px) {
    .main-container {
        margin: 8px !important;
        padding: 16px !important;
    }
    
    .input-section, .output-section {
        padding: 16px !important;
    }
    
    .header-title {
        font-size: 1.5rem !important;
    }
}
"""

# === Gradio interface ===
with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="slate",
        secondary_hue="gray",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter")
    ),
    css=professional_css,
    title="AI Video Interpreter"
) as demo:
    
    with gr.Column(elem_classes="main-container"):
        # Header Section
        with gr.Column(elem_classes="header-section"):
            gr.HTML("""
                <div class="header-title">🎥 AI Video Interpreter</div>
                <div class="header-subtitle">Real-time scene analysis and Q&A</div>
            """)
        
        # Main Content
        with gr.Row():
            # Input Section
            with gr.Column(scale=1, elem_classes="input-section"):
                gr.HTML('<div class="section-header">📹 Camera Input</div>')
                webcam = gr.Image(
                    sources="webcam",
                    streaming=True,
                    type="pil",
                    elem_classes="webcam-container",
                    show_label=False,
                    container=False
                )
                
                gr.HTML('<div class="section-header" style="margin-top: 20px;">💬 Question</div>')
                prompt_box = gr.Textbox(
                    placeholder="Ask about what you see in the video...",
                    elem_classes="prompt-input",
                    show_label=False,
                    container=False,
                    lines=2
                )
            
            # Output Section
            with gr.Column(scale=1, elem_classes="output-section"):
                gr.HTML('<div class="section-header">🔍 Scene Analysis <div class="status-dot"></div></div>')
                scene_box = gr.Textbox(
                    elem_classes="output-box scene-output",
                    interactive=False,
                    show_label=False,
                    container=False,
                    placeholder="Analyzing scene..."
                )
                
                gr.HTML('<div class="section-header" style="margin-top: 16px;">❓ Current Question</div>')
                prompt_display = gr.Textbox(
                    elem_classes="output-box prompt-output",
                    interactive=False,
                    show_label=False,
                    container=False,
                    placeholder="No question asked yet"
                )
                
                gr.HTML('<div class="section-header" style="margin-top: 16px;">🤖 AI Answer</div>')
                answer_box = gr.Textbox(
                    elem_classes="output-box answer-output",
                    interactive=False,
                    show_label=False,
                    container=False,
                    placeholder="Answer will appear here..."
                )

    # === Set up streaming ===
    webcam.stream(
        fn=processRequest,
        inputs=[webcam, prompt_box],
        outputs=[scene_box, prompt_display, answer_box],
        concurrency_limit=None,
        stream_every=1
    )

demo.launch()