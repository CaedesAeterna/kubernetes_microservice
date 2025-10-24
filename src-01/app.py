# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI in Docker!"}

@app.get("/health")
def health():
    return {"status": "ok"}

