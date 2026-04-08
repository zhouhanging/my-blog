import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.blog import Blog

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

class BlogService:
    @staticmethod
    async def create_blog(db: Session, topic: str) -> dict:
        if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "your_deepseek_api_key":
            try:
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的中文技术博客作家。请根据用户提供的主题，生成一篇结构完整、内容丰富的技术博客文章。使用 Markdown 格式输出，包含标题、引言、正文、代码示例和���结。"
                        },
                        {
                            "role": "user",
                            "content": f"请生成一篇关于「{topic}」的技术博客，要求：\n1. 使用中文\n2. 结构清晰，包含引言、正文、代码示例、总结\n3. 代码示例使用 Python\n4. 字数在 800-1500 字之间"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                else:
                    content = f"# {topic}\n\n抱歉，AI 服务暂时不可用。请稍后重试。"
            except Exception as e:
                content = f"# {topic}\n\n生成失败: {str(e)}"
        else:
            content = f"""# {topic}

## 引言

这是一篇关于 **{topic}** 的技术博客。

## 正文

本文将深入探讨 {topic} 的核心概念和实践方法。

### 什么是 {topic}？

{topic} 是现代软件开发中的重要组成部分。它帮助开发者更高效地构建应用程序，提升代码质量和可维护性。

### 核心特性

1. **简洁易用** - API 设计直观，学习曲线平缓
2. **高性能** - 优化了内部实现，处理速度快
3. **可扩展** - 支持插件系统和自定义扩展

### 代码示例

```python
# 示例代码
def hello_world():
    print("Hello, {topic}!")
    return True

# 调用示例
result = hello_world()
print(f"结果: {{result}}")
```

## 总结

通过本文，我们了解了 {topic} 的基本概念和使用方法。希望对你有所帮助！

---
*由 AI 博客助手自动生成*
"""

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