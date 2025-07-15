from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import uuid
import threading
from webui.processor import process_RTSP

app = FastAPI()
templates = Jinja2Templates(directory="webui/templates")
app.mount("/static", StaticFiles(directory="webui/static"), name="static")
responses = {}
lock = threading.Lock()
rtsp_link = None


class LinkData(BaseModel):
    link: str


class Payload(BaseModel):
    prompt: str
    image64: str


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/")
def set_rtsp(link_data: LinkData):
    global rtsp_link
    rtsp_link = link_data.link
    return JSONResponse(content={"success": True, "redirect_url": "/interpreter"})


@app.get("/interpreter", response_class=HTMLResponse)
def interpreter_view(request: Request):
    return templates.TemplateResponse(request=request, name="interpreterView.html")


@app.post("/interpreter")
def start_interpreter(data: Payload):
    # Tempory. Show prompt and image64
    print(f"Prompt: {data.prompt}")
    print(f"Image64: {data.image64[:30]}...")
    return {"status": "Interpreter started"}


@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(
        process_RTSP(rtsp_link), media_type="multipart/x-mixed-replace; boundary=frame"
    )


# POST endpoint to receive a response
@app.post("/request")
async def receive_response(request: Request):
    data = await request.json()
    request_id = data.get("id")
    response_text = data.get("response")

    if not request_id or not response_text:
        return JSONResponse(status_code=400, content={"error": "Invalid format"})

    with lock:
        responses[request_id] = response_text

    return {"status": "OK"}


# GET endpoint to return a stored response
@app.get("/result")
def get_response(id: str = None):
    if not id:
        return {"response": None}

    with lock:
        response = responses.get(id)

    return {"response": response}


# Function to send requests to an external service
def send_request(prompt, image64):
    url = "http://127.0.0.1:8080/end"
    request_id = str(uuid.uuid4())

    payload = {"id": request_id, "prompt": prompt, "image64": image64}

    try:
        requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None

    return request_id
