from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import uuid
import threading

app = FastAPI()
responses = {}
lock = threading.Lock()


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
