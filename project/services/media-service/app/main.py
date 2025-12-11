from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.routers import media
from app.kafka_consumer import consume
import asyncio

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.include_router(media.router)
# No special change needed if router defines the path

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Media Service"})
