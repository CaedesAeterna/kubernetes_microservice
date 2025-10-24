from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI behind Nginx"}


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "message": "this is a v2 version of the app 2025-10-23"}

