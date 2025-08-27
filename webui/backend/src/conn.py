from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import threading
from src.processor import processRequest

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

responses = {}
lock = threading.Lock()
rtsp_link = None


class Payload(BaseModel):
    prompt: str
    image64: str


@app.post("/interpreter")
def start_interpreter(data: Payload):
    request_id, error = processRequest(data.image64, data.prompt)
    if error:
        return JSONResponse(content={"success": False, "error": error})
    return JSONResponse(content={"success": True, "request_id": request_id})


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
