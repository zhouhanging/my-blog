from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.blog import (
    BlogResponse, BlogCreate, GenerateRequest, OptimizeRequest
)
from app.services.blog_service import BlogService

router = APIRouter(prefix="/api/blogs", tags=["blogs"])

@router.post("/generate", response_model=BlogResponse)
async def generate_blog(request: GenerateRequest, db: Session = Depends(get_db)):
    try:
        blog = await BlogService.create_blog(db, request.topic)
        return blog
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{blog_id}/optimize", response_model=BlogResponse)
async def optimize_blog(blog_id: int, request: OptimizeRequest, db: Session = Depends(get_db)):
    try:
        blog = await BlogService.optimize_blog(db, blog_id, request.feedback)
        return blog
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{blog_id}/approve", response_model=BlogResponse)
async def approve_blog(blog_id: int, db: Session = Depends(get_db)):
    try:
        blog = await BlogService.approve_blog(db, blog_id)
        return blog
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = BlogService.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.get("", response_model=list[BlogResponse])
def list_blogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return BlogService.list_blogs(db, skip=skip, limit=limit)
