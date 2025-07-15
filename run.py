import threading
import uvicorn
import webui.conn as conn


def run_fastapi():
    uvicorn.run(conn.app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    api_thread.join()
