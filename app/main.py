import json

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class SubmitRequest(BaseModel):
    username: str
    email: str

@app.get("/api/data")
async def get_data():
    with open("app/data/data.json", "r") as file:
        data = json.load(file)

    return data


@app.post("/api/submit")
async def submit(request: SubmitRequest):
    return {
        "message": "submitted successfully",
        "data": {
            "username": request.username,
            "email": request.email,
        }
    }

