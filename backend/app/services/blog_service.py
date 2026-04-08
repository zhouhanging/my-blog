from sqlalchemy.orm import Session
from app.models.blog import Blog, BlogStatus
from app.schemas.blog import BlogCreate, BlogUpdate
from app.services.ai_service import AIService
import requests
import os

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

class BlogService:
    @staticmethod
    async def create_blog(db: Session, topic: str) -> Blog:
        content = await AIService.generate_blog(topic)
        
        blog = Blog(
            topic=topic,
            content=content,
            status=BlogStatus.PENDING
        )
        db.add(blog)
        db.commit()
        db.refresh(blog)
        
        return blog

    @staticmethod
    async def optimize_blog(db: Session, blog_id: int, feedback: str) -> Blog:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise ValueError("Blog not found")
        
        optimized_content = await AIService.optimize_blog(blog.content, feedback)
        
        blog.content = optimized_content
        blog.feedback = feedback
        blog.status = BlogStatus.PENDING
        db.commit()
        db.refresh(blog)
        
        return blog

    @staticmethod
    async def approve_blog(db: Session, blog_id: int) -> Blog:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise ValueError("Blog not found")
        
        blog.status = BlogStatus.APPROVED
        db.commit()
        db.refresh(blog)
        
        if N8N_WEBHOOK_URL:
            try:
                requests.post(N8N_WEBHOOK_URL, json={
                    "blog_id": blog.id,
                    "topic": blog.topic,
                    "content": blog.content
                })
            except Exception as e:
                print(f"Failed to trigger n8n: {e}")
        
        return blog

    @staticmethod
    def get_blog(db: Session, blog_id: int) -> Blog:
        return db.query(Blog).filter(Blog.id == blog_id).first()

    @staticmethod
    def list_blogs(db: Session, skip: int = 0, limit: int = 100) -> list[Blog]:
        return db.query(Blog).order_by(Blog.created_at.desc()).offset(skip).limit(limit).all()
