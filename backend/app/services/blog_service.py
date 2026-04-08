import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.blog import Blog

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def generate_blog_content(topic: str) -> str:
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    content = f"""# {topic}

## 引言

在当今快速发展的技术领域，**{topic}** 已成为开发者必须掌握的核心技能之一。本文将深入探讨 {topic} 的原理、实现方式以及最佳实践。

## 什么是 {topic}？

{topic} 是现代软件开发中的关键技术，它能够帮助我们构建更高效、更可维护的应用程序。无论是前端开发还是后端服务，{topic} 都发挥着重要作用。

## 核心概念

### 1. 基本原理

{topic} 的核心原理涉及几个关键概念：
- **概念一**：理解基础概念是掌握 {topic} 的第一步
- **概念二**：实践出真知，多动手才能真正理解
- **概念三**：与现有技术结合，发挥最大价值

### 2. 优势与特点

{topic} 具有以下显著优势：

| 特性 | 说明 |
|------|------|
| 高性能 | 优化处理流程，提升响应速度 |
| 易用性 | API 设计友好，上手简单 |
| 可扩展 | 支持插件和自定义功能 |

## 代码示例

以下是 {topic} 的基本使用示例：

```python
# {topic} 基础示例
import requests
from typing import Dict, Any

class {topic.replace(" ", "")}Client:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.example.com"
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{{self.base_url}}/process",
            json=data,
            headers={{"Authorization": f"Bearer {{self.api_key}}"}}
        )
        return response.json()

# 使用示例
client = {topic.replace(" ", "")}Client("your-api-key")
result = client.process({{"input": "example"}})
print(result)
```

## 实际应用场景

{topic} 在以下场景中特别有用：
1. **Web 开发** - 构建高性能的 Web 应用
2. **数据处理** - 大规模数据清洗和转换
3. **自动化任务** - 减少重复性工作

## 总结

通过本文的学习，我们了解到：

1. {topic} 是现代开发中不可或缺的技能
2. 掌握核心概念和最佳实践非常重要
3. 多实践、多思考才能真正精通

希望这篇教程能帮助你更好地理解和应用 {topic}！

---
*由 AI 博客助手自动生成 | 生成时间：{timestamp}*
"""
    return content

class BlogService:
    @staticmethod
    async def create_blog(db: Session, topic: str) -> dict:
        content = generate_blog_content(topic)

        blog = Blog(
            topic=topic,
            content=content,
            status="pending"
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
        
        feedback_lower = feedback.lower()
        
        if any(word in feedback_lower for word in ['代码', '示例']):
            blog.content = blog.content + """

### 补充代码示例

```python
# 扩展示例
def advanced_usage():
    # 高级用法示例
    data = [1, 2, 3, 4, 5]
    result = [x * 2 for x in data if x > 2]
    return result
```
"""
        
        if any(word in feedback_lower for word in ['最新', '2024', '2025', '2026']):
            blog.content = blog.content + """

> **更新日期**: 2026 年 4 月
"""
        
        blog.feedback = feedback
        blog.status = "pending"
        blog.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(blog)
        
        return blog

    @staticmethod
    async def approve_blog(db: Session, blog_id: int) -> Blog:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise ValueError("Blog not found")
        
        blog.status = "approved"
        db.commit()
        db.refresh(blog)
        
        if N8N_WEBHOOK_URL:
            try:
                import requests as req
                req.post(N8N_WEBHOOK_URL, json={
                    "blog_id": blog.id,
                    "topic": blog.topic,
                    "content": blog.content
                }, timeout=5)
            except Exception as e:
                print(f"Failed to trigger n8n: {e}")
        
        return blog

    @staticmethod
    def get_blog(db: Session, blog_id: int) -> Blog:
        return db.query(Blog).filter(Blog.id == blog_id).first()

    @staticmethod
    def list_blogs(db: Session, skip: int = 0, limit: int = 100) -> list[Blog]:
        return db.query(Blog).order_by(Blog.created_at.desc()).offset(skip).limit(limit).all()