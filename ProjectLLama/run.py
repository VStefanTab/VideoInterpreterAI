import threading
import uvicorn
import webui.webuiApp as webui
import webui.conn as conn


def run_gradio():
    webui.demo.launch()


def run_fastapi():
    uvicorn.run(conn.app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    run_gradio()
