from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MediaItem(BaseModel):
    title: str
    media_type: str # movie, series, book, etc.
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MediaItemCreate(MediaItem):
    pass

class MediaItemDB(MediaItem):
    id: str
