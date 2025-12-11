from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import db, redis_client
from app.models import MediaItemCreate
from bson import ObjectId
from typing import Optional
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/api/recent")
async def get_recent_media():
    # Return last 5 added items as JSON
    media_list = []
    cursor = db.media.find({}).sort("_id", -1).limit(5)
    async for document in cursor:
        document["id"] = str(document["_id"])
        del document["_id"]
        media_list.append(document)
    return media_list

@router.get("/media")
async def list_media(request: Request, q: Optional[str] = None):
    username = request.cookies.get("username")
    
    # 1. Generate Cache Key based on query
    cache_key = f"media_list:{q if q else 'all'}"
    
    # 2. Check Cache
    cached_data = await redis_client.get(cache_key)
    
    media_list = []
    
    if cached_data:
        print(f"[Cache Hit] Serving {cache_key} from Redis")
        media_list = json.loads(cached_data)
    else:
        print(f"[Cache Miss] Querying MongoDB for {cache_key}")
        # 3. Query Database (Cache Miss)
        query = {}
        if q:
            query = {"title": {"$regex": q, "$options": "i"}}
            
        cursor = db.media.find(query)
        async for document in cursor:
            document["id"] = str(document["_id"])
            del document["_id"] # Remove ObjectId for JSON serialization
            media_list.append(document)
            
        # 4. Save to Cache (Expire in 60 seconds)
        await redis_client.setex(cache_key, 60, json.dumps(media_list))
        
    return templates.TemplateResponse("media_list.html", {
        "request": request, 
        "media_list": media_list, 
        "username": username,
        "search_query": q
    })

@router.post("/media")
async def create_media(title: str = Form(...), media_type: str = Form(...), description: str = Form(...)):
    new_media = {"title": title, "media_type": media_type, "description": description}
    await db.media.insert_one(new_media)
    
    # 5. Invalidate Cache on Write
    # We clear the 'all' list and any potential searches (simple invalidation)
    # A robust system might use specific keys or tags.
    print("[Cache Invalidate] Clearing media_list:all")
    await redis_client.delete("media_list:all")
    
    return RedirectResponse(url="/media", status_code=303)

@router.get("/media/new")
async def new_media_form(request: Request):
    return templates.TemplateResponse("media_form.html", {"request": request})
