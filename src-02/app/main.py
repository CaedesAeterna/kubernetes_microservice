from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone


app = FastAPI(title="Minimal FastAPI")


class Echo(BaseModel):
  message: str


@app.get("/health")
async def health():
  return {"status": "ok"}


@app.post("/echo")
async def echo(payload: Echo):
  return {"echo": payload.message}


@app.get("/time")
async def time():
  return {"utc": datetime.now(timezone.utc).isoformat()}