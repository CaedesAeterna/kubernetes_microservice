from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Service URLs (Internal K8s DNS)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service.app.svc.cluster.local:80")
MEDIA_SERVICE_URL = os.getenv("MEDIA_SERVICE_URL", "http://media-service.app.svc.cluster.local:80")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    username = request.cookies.get("username")
    if not username:
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Please login first"})

    user_data = None
    media_data = []

    async with httpx.AsyncClient() as client:
        # Aggregation Pattern: Call both services
        # Circuit Breaker Logic (Simplified): If call fails, return default/empty data instead of crashing.
        
        # 1. Call User Service (JSON API)
        try:
            user_resp = await client.get(f"{USER_SERVICE_URL}/api/data?username={username}", timeout=2.0)
            if user_resp.status_code == 200:
                user_data = user_resp.json()
        except Exception as e:
            print(f"[Dashboard] User Service Unreachable: {e}")
            user_data = {"error": "User Service unavailable"}

        # 2. Call Media Service (JSON API)
        try:
            media_resp = await client.get(f"{MEDIA_SERVICE_URL}/api/recent", timeout=2.0)
            if media_resp.status_code == 200:
                media_data = media_resp.json()
        except Exception as e:
            print(f"[Dashboard] Media Service Unreachable: {e}")
            
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "username": username,
        "user_data": user_data,
        "media_data": media_data
    })
