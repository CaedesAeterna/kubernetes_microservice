from fastapi import APIRouter, Request, Form, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from app.database import db, redis_client
from app.models import MediaItem
from app.kafka_producer import get_producer
from app.auth import get_current_user
from bson import ObjectId
from typing import Optional
import json
from datetime import datetime
from bson.errors import InvalidId

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

MEDIA_CACHE_KEY = "media_list:all"

@router.post("/media/{media_id}/release")
async def release_content(
    media_id: str,
    release_title: str = Form(...),
    season_number: Optional[int] = Form(None),
    episode_number: Optional[int] = Form(None),
    volume_number: Optional[int] = Form(None),
    chapter_number: Optional[int] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        oid = ObjectId(media_id)
    except InvalidId:
        return HTMLResponse(f"Invalid Media ID format", status_code=400)

    media = await db.media.find_one({"_id": oid})
    if not media:
        return HTMLResponse("Media not found", status_code=404)
    
    # Publish Kafka Event
    producer = await get_producer()
    event = {
        "event_type": "new_release",
        "media_id": media_id,
        "media_title": media["title"],
        "media_type": media.get("media_type", "unknown"),
        "release_title": release_title,
        "season": season_number,
        "episode": episode_number,
        "volume": volume_number,
        "chapter": chapter_number
    }
    await producer.send_and_wait("media-updates", event)
    
    # Invalidate Cache
    await redis_client.delete(MEDIA_CACHE_KEY)
    
    return RedirectResponse(url=f"/media", status_code=303)

@router.post("/media/{media_id}/delete")
async def delete_media(media_id: str, current_user: dict = Depends(get_current_user)):
    try:
        oid = ObjectId(media_id)
    except InvalidId:
        return HTMLResponse(f"Invalid Media ID", status_code=400)

    result = await db.media.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return HTMLResponse("Media not found", status_code=404)

    # Publish Event
    producer = await get_producer()
    event = {
        "event_type": "media_deleted",
        "media_id": media_id
    }
    await producer.send_and_wait("media-updates", event)
    
    # Invalidate Cache
    await redis_client.delete(MEDIA_CACHE_KEY)

    return RedirectResponse(url="/media", status_code=303)

@router.get("/api/recent")
async def get_recent_media():
    # Return last 5 added items as JSON
    media_list = []
    cursor = db.media.find({}).sort("_id", -1).limit(5)
    async for document in cursor:
        document["id"] = str(document["_id"])
        del document["_id"]
        # Convert datetime to string for JSON serialization
        if "created_at" in document and isinstance(document["created_at"], datetime):
            document["created_at"] = document["created_at"].isoformat()
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
            # Convert datetime to string for JSON serialization
            if "created_at" in document and isinstance(document["created_at"], datetime):
                document["created_at"] = document["created_at"].isoformat()
            media_list.append(document)
            
        # 4. Save to Cache (Expire in 60 seconds)
        await redis_client.setex(cache_key, 60, json.dumps(media_list))
        
    return templates.TemplateResponse("media_list.html", {
        "request": request, 
        "media_list": media_list, 
        "username": username,
        "search_query": q
    })

@router.post("/media", response_class=HTMLResponse)
async def create_media(
    request: Request,
    title: str = Form(...),
    media_type: str = Form(...),
    description: Optional[str] = Form(None),
    seasons_json: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        seasons_data = []
        if seasons_json and seasons_json.strip():
            import json
            seasons_data = json.loads(seasons_json)
        
        media_item = MediaItem(
            title=title, 
            media_type=media_type, 
            description=description,
            seasons=seasons_data
        )
        await db.media.insert_one(media_item.dict())
        
        # Invalidate Cache
        await redis_client.delete(MEDIA_CACHE_KEY)
        
        return RedirectResponse(url="/media", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("media_form.html", {"request": request, "error": str(e)})

@router.get("/media/new")
async def new_media_form(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("media_form.html", {"request": request})
