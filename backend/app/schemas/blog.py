from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.blog import BlogStatus

class BlogBase(BaseModel):
    topic: str
    content: Optional[str] = None

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[BlogStatus] = None
    feedback: Optional[str] = None

class BlogResponse(BlogBase):
    id: int
    status: BlogStatus
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    topic: str

class OptimizeRequest(BaseModel):
    blog_id: int
    feedback: str
