# AI 博客系统 - 完整项目实施 Skill 文档
> **目标**：基于方案一（PWA 网页 + 微信机器人 + 后端 API），生成一个完整的 AI 驱动个人博客系统代码。  
> **使用方式**：将本文档交给 AI，要求其按照文档结构逐步生成所有代码。

---

## 一、项目概述
### 1.1 核心功能
- **电脑端（PWA 网页）**：输入主题、AI 生成博客、Markdown 预览、审核通过/提修改意见、查看历史文章
- **手机端（微信机器人）**：微信聊天输入主题、接收生成预览、回复「通过」推送、回复「修改：xxx」优化
- **后端**：API 接口、AI 搜索生成工作流、数据库管理、n8n 工作流触发
- **多渠道推送**：审核通过后自动推送到 Strapi 博客系统和微信公众号

### 1.2 项目结构
```
/my-blog-system
├── /pwa-web              # 电脑端 PWA 网页
│   ├── /src
│   │   ├── /components   # 通用组件
│   │   ├── /views        # 页面
│   │   ├── /router       # 路由
│   │   ├── /stores       # Pinia 状态管理
│   │   ├── /api          # API 封装
│   │   └── App.vue
│   ├── vite.config.js
│   └── package.json
├── /wechat-bot           # 手机端微信机器人
│   ├── bot.py            # 机器人主逻辑
│   ├── .env              # 环境变量
│   └── requirements.txt
├── /backend              # 后端 API + AI 工作流
│   ├── /app
│   │   ├── /api          # 路由
│   │   ├── /models       # 数据库模型
│   │   ├── /services     # 业务逻辑（AI 生成、推送）
│   │   ├── /schemas      # Pydantic 模型
│   │   └── main.py       # FastAPI 入口
│   ├── .env
│   ├── requirements.txt
│   └── docker-compose.yml
└── /n8n                  # n8n 工作流配置（可选）
    └── workflows.json
```

---

## 二、技术栈总览
| 模块 | 技术选型 | 版本要求 |
|------|----------|----------|
| **PWA 网页** | Vue 3 + Vite + Naive UI + Vue Router + Pinia + Axios + vite-plugin-pwa | 最新稳定版 |
| **微信机器人** | Python 3.10+ + wechaty + requests + python-dotenv | 最新稳定版 |
| **后端 API** | Python 3.10+ + FastAPI + Uvicorn + SQLAlchemy + PostgreSQL + LangChain | 最新稳定版 |
| **AI 服务** | 通义千问 API（dashscope） + SerpAPI | 最新稳定版 |
| **部署** | Docker + Docker Compose + Vercel | 最新稳定版 |

---

## 三、分模块详细需求

---

### 模块 1：后端 API（`/backend`）
**优先级：最高**，必须先生成后端代码。

#### 3.1.1 环境变量（`.env`）
```env
# 数据库
DATABASE_URL=postgresql://user:password@db:5432/my_blog_db

# 通义千问 API
DASHSCOPE_API_KEY=your_dashscope_api_key

# SerpAPI（搜索）
SERPAPI_API_KEY=your_serpapi_api_key

# 微信公众号（可选）
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# n8n Webhook（可选）
N8N_WEBHOOK_URL=http://n8n:5678/webhook/approve
```

#### 3.1.2 依赖（`requirements.txt`）
```txt
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
python-dotenv==1.0.0
langchain==0.1.4
langchain-community==0.0.16
dashscope==1.14.1
serpapi==0.1.5
requests==2.31.0
pydantic==2.5.3
```

#### 3.1.3 Docker Compose（`docker-compose.yml`）
一键启动后端 + PostgreSQL + Redis
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/my_blog_db
    volumes:
      - ./app:/app/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=my_blog_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

#### 3.1.4 数据库模型（`/app/models/blog.py`）
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class BlogStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PUBLISHED = "published"

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(SQLEnum(BlogStatus), default=BlogStatus.DRAFT)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3.1.5 Pydantic 模式（`/app/schemas/blog.py`）
```python
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
```

#### 3.1.6 AI 生成服务（`/app/services/ai_service.py`）
**核心逻辑**：LangChain + SerpAPI 搜索 + 通义千问生成
```python
import os
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
from langchain_community.llms import Tongyi
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# 初始化通义千问
llm = Tongyi(
    model="qwen-max",
    dashscope_api_key=DASHSCOPE_API_KEY,
    temperature=0.7
)

# 初始化搜索工具
search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="用于搜索最新的相关信息，当需要实时数据或背景知识时使用"
    )
]

# 初始化 Agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 生成博客的 Prompt
BLOG_GENERATE_PROMPT = """
你是一个专业的技术博客作者。请根据以下主题和搜索到的信息，生成一篇高质量的技术博客。

要求：
1. 结构清晰，包含标题、引言、正文、总结
2. 语言专业但易懂，适合技术读者
3. 包含代码示例（如果适用）
4. 字数在 1500-2500 字之间
5. 输出格式为 Markdown

主题：{topic}
搜索信息：{search_info}

请开始生成博客：
"""

# 优化博客的 Prompt
BLOG_OPTIMIZE_PROMPT = """
你是一个专业的技术编辑。请根据以下反馈意见，优化这篇博客。

原始博客：
{content}

反馈意见：
{feedback}

请输出优化后的博客（Markdown 格式）：
"""

class AIService:
    @staticmethod
    async def generate_blog(topic: str) -> str:
        # 1. 先搜索相关信息
        search_result = search.run(f"最新 {topic} 技术信息 最佳实践")
        
        # 2. 构建 Prompt
        prompt = PromptTemplate(
            input_variables=["topic", "search_info"],
            template=BLOG_GENERATE_PROMPT
        )
        
        # 3. 调用 LLM 生成
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(topic=topic, search_info=search_result)
        
        return result

    @staticmethod
    async def optimize_blog(content: str, feedback: str) -> str:
        prompt = PromptTemplate(
            input_variables=["content", "feedback"],
            template=BLOG_OPTIMIZE_PROMPT
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(content=content, feedback=feedback)
        return result
```

#### 3.1.7 业务逻辑（`/app/services/blog_service.py`）
```python
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
        # 1. 调用 AI 生成内容
        content = await AIService.generate_blog(topic)
        
        # 2. 保存到数据库
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
        
        # 调用 AI 优化
        optimized_content = await AIService.optimize_blog(blog.content, feedback)
        
        # 更新数据库
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
        
        # 触发 n8n 工作流（推送到博客和公众号）
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
```

#### 3.1.8 API 路由（`/app/api/blogs.py`）
```python
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
```

#### 3.1.9 FastAPI 入口（`/app/main.py`）
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import blogs

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 博客系统 API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(blogs.router)

@app.get("/")
def read_root():
    return {"message": "AI 博客系统 API 运行中"}
```

#### 3.1.10 数据库连接（`/app/database.py`）
```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 模块 2：PWA 网页（`/pwa-web`）
**优先级：高**，后端完成后生成。

#### 3.2.1 依赖（`package.json`）
```json
{
  "name": "my-blog-pwa",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "naive-ui": "^2.38.1",
    "axios": "^1.6.5",
    "@vicons/ionicons5": "^0.12.0",
    "marked": "^11.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "vite-plugin-pwa": "^0.17.4"
  }
}
```

#### 3.2.2 Vite 配置（`vite.config.js`）
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: 'AI 博客助手',
        short_name: 'AI 博客',
        description: 'AI 驱动的个人博客生成系统',
        theme_color: '#18a058',
        icons: [
          {
            src: 'icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

#### 3.2.3 API 封装（`/src/api/index.js`）
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 60000
})

// 博客相关 API
export const blogApi = {
  // 生成博客
  generate: (topic) => api.post('/blogs/generate', { topic }),
  
  // 获取博客详情
  get: (id) => api.get(`/blogs/${id}`),
  
  // 获取博客列表
  list: (params) => api.get('/blogs', { params }),
  
  // 优化博客
  optimize: (id, feedback) => api.post(`/blogs/${id}/optimize`, { blog_id: id, feedback }),
  
  // 审核通过
  approve: (id) => api.post(`/blogs/${id}/approve`)
}

export default api
```

#### 3.2.4 Pinia 状态管理（`/src/stores/blog.js`）
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { blogApi } from '@/api'

export const useBlogStore = defineStore('blog', () => {
  const currentBlog = ref(null)
  const blogList = ref([])
  const loading = ref(false)

  // 生成博客
  const generateBlog = async (topic) => {
    loading.value = true
    try {
      const res = await blogApi.generate(topic)
      currentBlog.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  // 获取博客列表
  const fetchBlogList = async () => {
    loading.value = true
    try {
      const res = await blogApi.list()
      blogList.value = res.data
    } finally {
      loading.value = false
    }
  }

  // 优化博客
  const optimizeBlog = async (id, feedback) => {
    loading.value = true
    try {
      const res = await blogApi.optimize(id, feedback)
      currentBlog.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  // 审核通过
  const approveBlog = async (id) => {
    loading.value = true
    try {
      const res = await blogApi.approve(id)
      currentBlog.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  return {
    currentBlog,
    blogList,
    loading,
    generateBlog,
    fetchBlogList,
    optimizeBlog,
    approveBlog
  }
})
```

#### 3.2.5 路由配置（`/src/router/index.js`）
```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Generate',
    component: () => import('@/views/GenerateView.vue')
  },
  {
    path: '/blogs',
    name: 'BlogList',
    component: () => import('@/views/BlogListView.vue')
  },
  {
    path: '/blogs/:id',
    name: 'BlogDetail',
    component: () => import('@/views/BlogDetailView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

#### 3.2.6 主入口（`/src/main.js`）
```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(naive)

app.mount('#app')
```

#### 3.2.7 生成博客页面（`/src/views/GenerateView.vue`）
```vue
<template>
  <n-layout content-style="padding: 24px; max-width: 900px; margin: 0 auto">
    <n-page-header title="AI 生成博客" subtitle="输入主题，AI 帮你写" />
    
    <n-card style="margin-top: 24px">
      <n-form :model="form">
        <n-form-item label="博客主题">
          <n-input
            v-model:value="form.topic"
            placeholder="例如：Vue3 组合式 API 最佳实践、Docker 部署 FastAPI 完整指南"
            size="large"
          />
        </n-form-item>
        <n-form-item>
          <n-button
            type="primary"
            size="large"
            @click="handleGenerate"
            :loading="store.loading"
          >
            <template #icon>
              <n-icon><SparklesOutline /></n-icon>
            </template>
            生成博客
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 生成结果 -->
    <n-card v-if="store.currentBlog" title="生成结果" style="margin-top: 24px">
      <n-tabs type="line">
        <n-tab-pane name="preview" tab="预览">
          <div class="markdown-preview" v-html="renderedMarkdown"></div>
        </n-tab-pane>
        <n-tab-pane name="raw" tab="原始 Markdown">
          <n-input
            type="textarea"
            :value="store.currentBlog.content"
            readonly
            style="min-height: 400px"
          />
        </n-tab-pane>
      </n-tabs>

      <n-space style="margin-top: 24px; justify-content: flex-end">
        <n-button @click="showFeedbackModal = true">
          <template #icon>
            <n-icon><CreateOutline /></n-icon>
          </template>
          提修改意见
        </n-button>
        <n-button type="success" @click="handleApprove" :loading="store.loading">
          <template #icon>
            <n-icon><CheckmarkOutline /></n-icon>
          </template>
          审核通过
        </n-button>
      </n-space>
    </n-card>

    <!-- 修改意见弹窗 -->
    <n-modal v-model:show="showFeedbackModal" preset="card" title="提修改意见" style="width: 600px">
      <n-form :model="feedbackForm">
        <n-form-item label="修改意见">
          <n-input
            type="textarea"
            v-model:value="feedbackForm.feedback"
            placeholder="例如：这里加个代码示例、语言更口语化一点、增加最新的 2024 年数据"
            style="min-height: 150px"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showFeedbackModal = false">取消</n-button>
          <n-button type="primary" @click="handleOptimize" :loading="store.loading">
            提交优化
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </n-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBlogStore } from '@/stores/blog'
import { SparklesOutline, CreateOutline, CheckmarkOutline } from '@vicons/ionicons5'
import { marked } from 'marked'
import { useMessage } from 'naive-ui'

const router = useRouter()
const store = useBlogStore()
const message = useMessage()

const form = ref({ topic: '' })
const feedbackForm = ref({ feedback: '' })
const showFeedbackModal = ref(false)

const renderedMarkdown = computed(() => {
  if (!store.currentBlog) return ''
  return marked.parse(store.currentBlog.content)
})

const handleGenerate = async () => {
  if (!form.value.topic.trim()) {
    message.warning('请输入博客主题')
    return
  }
  try {
    await store.generateBlog(form.value.topic)
    message.success('生成成功！')
  } catch (error) {
    message.error('生成失败：' + error.message)
  }
}

const handleOptimize = async () => {
  if (!feedbackForm.value.feedback.trim()) {
    message.warning('请输入修改意见')
    return
  }
  try {
    await store.optimizeBlog(store.currentBlog.id, feedbackForm.value.feedback)
    showFeedbackModal.value = false
    feedbackForm.value.feedback = ''
    message.success('优化成功！')
  } catch (error) {
    message.error('优化失败：' + error.message)
  }
}

const handleApprove = async () => {
  try {
    await store.approveBlog(store.currentBlog.id)
    message.success('审核通过！已推送到博客和公众号')
    router.push('/blogs')
  } catch (error) {
    message.error('审核失败：' + error.message)
  }
}
</script>

<style scoped>
.markdown-preview {
  line-height: 1.8;
}
.markdown-preview h1 { font-size: 2em; margin: 0.67em 0; }
.markdown-preview h2 { font-size: 1.5em; margin: 0.83em 0; }
.markdown-preview h3 { font-size: 1.17em; margin: 1em 0; }
.markdown-preview p { margin: 1em 0; }
.markdown-preview code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
.markdown-preview pre { background: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 8px; overflow-x: auto; }
.markdown-preview pre code { background: none; padding: 0; }
</style>
```

#### 3.2.8 博客列表页面（`/src/views/BlogListView.vue`）
```vue
<template>
  <n-layout content-style="padding: 24px; max-width: 1000px; margin: 0 auto">
    <n-page-header title="博客列表">
      <template #extra>
        <n-button type="primary" @click="$router.push('/')">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          生成新博客
        </n-button>
      </template>
    </n-page-header>

    <n-card style="margin-top: 24px">
      <n-spin :show="store.loading">
        <n-list>
          <n-list-item v-for="blog in store.blogList" :key="blog.id" clickable @click="$router.push(`/blogs/${blog.id}`)">
            <n-thing>
              <template #header>
                <n-text depth="3" style="margin-right: 12px">{{ formatDate(blog.created_at) }}</n-text>
                <n-tag :type="getStatusType(blog.status)">{{ getStatusText(blog.status) }}</n-tag>
              </template>
              <template #header-extra>
                <n-icon><ChevronForwardOutline /></n-icon>
              </template>
              <template #title>{{ blog.topic }}</template>
              <template #description>{{ truncateContent(blog.content) }}</template>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-empty v-if="store.blogList.length === 0 && !store.loading" description="暂无博客，去生成一篇吧！" />
      </n-spin>
    </n-card>
  </n-layout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useBlogStore } from '@/stores/blog'
import { AddOutline, ChevronForwardOutline } from '@vicons/ionicons5'

const store = useBlogStore()

onMounted(() => {
  store.fetchBlogList()
})

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const map = {
    draft: 'default',
    pending: 'warning',
    approved: 'info',
    published: 'success'
  }
  return map[status] || 'default'
}

const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    pending: '待审核',
    approved: '已审核',
    published: '已发布'
  }
  return map[status] || status
}

const truncateContent = (content) => {
  return content.replace(/[#*`]/g, '').substring(0, 100) + '...'
}
</script>
```

#### 3.2.9 博客详情页面（`/src/views/BlogDetailView.vue`）
```vue
<template>
  <n-layout content-style="padding: 24px; max-width: 900px; margin: 0 auto">
    <n-page-header @back-click="$router.back()">
      <template #header>
        <n-breadcrumb>
          <n-breadcrumb-item @click="$router.push('/blogs')">博客列表</n-breadcrumb-item>
          <n-breadcrumb-item>详情</n-breadcrumb-item>
        </n-breadcrumb>
      </template>
      <template #avatar>
        <n-avatar round>
          <template #icon>
            <n-icon><DocumentTextOutline /></n-icon>
          </template>
        </n-avatar>
      </template>
      <template #title>{{ blog?.topic }}</template>
      <template #subtitle>
        <n-text depth="3">{{ formatDate(blog?.created_at) }}</n-text>
        <n-tag :type="getStatusType(blog?.status)" style="margin-left: 12px">{{ getStatusText(blog?.status) }}</n-tag>
      </template>
      <template #extra>
        <n-space>
          <n-button v-if="blog?.status === 'pending'" @click="showFeedbackModal = true">
            提修改意见
          </n-button>
          <n-button v-if="blog?.status === 'pending'" type="success" @click="handleApprove" :loading="store.loading">
            审核通过
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-card style="margin-top: 24px">
      <div class="markdown-preview" v-html="renderedMarkdown"></div>
    </n-card>

    <!-- 修改意见弹窗（同 GenerateView.vue，省略重复代码） -->
  </n-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBlogStore } from '@/stores/blog'
import { DocumentTextOutline } from '@vicons/ionicons5'
import { marked } from 'marked'
import { useMessage } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const store = useBlogStore()
const message = useMessage()

const blog = computed(() => store.currentBlog)
const showFeedbackModal = ref(false)
const feedbackForm = ref({ feedback: '' })

const renderedMarkdown = computed(() => {
  if (!blog.value) return ''
  return marked.parse(blog.value.content)
})

onMounted(async () => {
  const id = parseInt(route.params.id)
  const existing = store.blogList.find(b => b.id === id)
  if (existing) {
    store.currentBlog = existing
  } else {
    try {
      const res = await blogApi.get(id)
      store.currentBlog = res.data
    } catch (error) {
      message.error('获取博客失败')
      router.push('/blogs')
    }
  }
})

// 省略 formatDate, getStatusType, getStatusText, handleOptimize, handleApprove（同 GenerateView.vue）
</script>
```

---

### 模块 3：微信机器人（`/wechat-bot`）
**优先级：中**，前两个模块完成后生成。

#### 3.3.1 依赖（`requirements.txt`）
```txt
wechaty==1.20.2
wechaty-puppet-wechat==1.18.4
requests==2.31.0
python-dotenv==1.0.0
```

#### 3.3.2 环境变量（`.env`）
```env
BACKEND_URL=http://localhost:8000/api
```

#### 3.3.3 机器人主逻辑（`bot.py`）
```python
import os
import re
import requests
from dotenv import load_dotenv
from wechaty import Wechaty, Contact, Message
from wechaty_puppet import FileBox

# 加载环境变量
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

# 存储当前待审核的博客 ID（简单内存存储，重启丢失）
current_blog_id = None

class MyBlogBot(Wechaty):
    async def on_message(self, msg: Message):
        global current_blog_id
        
        # 只处理文本消息，且是自己发送的（避免群消息干扰）
        if msg.type() != Message.Type.MESSAGE_TYPE_TEXT:
            return
        
        talker = msg.talker()
        text = msg.text().strip()
        
        # 1. 生成博客：输入「生成：xxx」或「生成 xxx」
        generate_match = re.match(r'^生成[：:]\s*(.+)$', text) or re.match(r'^生成\s+(.+)$', text)
        if generate_match:
            topic = generate_match.group(1).strip()
            await talker.say(f'收到！正在为你生成关于「{topic}」的博客，请稍候...')
            
            try:
                # 调用后端 API
                res = requests.post(f'{BACKEND_URL}/blogs/generate', json={'topic': topic})
                res.raise_for_status()
                blog = res.json()
                current_blog_id = blog['id']
                
                # 截取前 800 字预览
                content = blog['content']
                preview = content[:800] + ('...\n\n' if len(content) > 800 else '\n\n')
                
                await talker.say(f'✅ 生成完成！\n\n主题：{blog["topic"]}\n\n预览：\n{preview}')
                await talker.say('请回复：\n- 「通过」直接推送\n- 「修改：xxx」提优化意见')
                
            except requests.exceptions.RequestException as e:
                await talker.say(f'❌ 生成失败：{str(e)}')
            except Exception as e:
                await talker.say(f'❌ 发生错误：{str(e)}')
        
        # 2. 审核通过：输入「通过」
        elif text == '通过' or text == '通过了':
            if not current_blog_id:
                await talker.say('没有待审核的博客，请先发送「生成：xxx」生成一篇')
                return
            
            await talker.say('正在推送...')
            try:
                res = requests.post(f'{BACKEND_URL}/blogs/{current_blog_id}/approve')
                res.raise_for_status()
                await talker.say('✅ 推送成功！博客和公众号已更新')
                current_blog_id = None
            except requests.exceptions.RequestException as e:
                await talker.say(f'❌ 推送失败：{str(e)}')
        
        # 3. 提修改意见：输入「修改：xxx」或「修改 xxx」
        elif text.startswith('修改'):
            if not current_blog_id:
                await talker.say('没有待优化的博客，请先发送「生成：xxx」生成一篇')
                return
            
            feedback_match = re.match(r'^修改[：:]\s*(.+)$', text) or re.match(r'^修改\s+(.+)$', text)
            if not feedback_match:
                await talker.say('请输入修改意见，格式：「修改：这里加个代码示例」')
                return
            
            feedback = feedback_match.group(1).strip()
            await talker.say(f'收到修改意见，正在优化...')
            
            try:
                res = requests.post(
                    f'{BACKEND_URL}/blogs/{current_blog_id}/optimize',
                    json={'blog_id': current_blog_id, 'feedback': feedback}
                )
                res.raise_for_status()
                blog = res.json()
                
                # 截取预览
                content = blog['content']
                preview = content[:800] + ('...\n\n' if len(content) > 800 else '\n\n')
                
                await talker.say(f'✅ 优化完成！\n\n预览：\n{preview}')
                await talker.say('请回复：\n- 「通过」直接推送\n- 「修改：xxx」继续提意见')
                
            except requests.exceptions.RequestException as e:
                await talker.say(f'❌ 优化失败：{str(e)}')
        
        # 4. 帮助
        elif text == '帮助' or text == 'help':
            help_text = """
🤖 AI 博客助手使用说明：

1️⃣ 生成博客
发送：「生成：Vue3 最佳实践」

2️⃣ 审核通过
发送：「通过」

3️⃣ 提修改意见
发送：「修改：这里加个代码示例」

4️⃣ 查看帮助
发送：「帮助」
            """.strip()
            await talker.say(help_text)

if __name__ == '__main__':
    print('🤖 AI 博客助手正在启动...')
    print('请扫描下方二维码登录微信：')
    bot = MyBlogBot()
    bot.run()
```

---

## 四、部署方案
### 4.1 后端部署
1. 在服务器上安装 Docker 和 Docker Compose
2. 上传 `/backend` 目录到服务器
3. 修改 `.env` 中的 API Key
4. 运行：`docker-compose up -d --build`
5. 访问 `http://your-server-ip:8000/docs` 查看 API 文档

### 4.2 PWA 网页部署
1. 把 `/pwa-web` 代码推送到 GitHub
2. 打开 [Vercel](sslocal://flow/file_open?url=https%3A%2F%2Fvercel.com&flow_extra=eyJsaW5rX3R5cGUiOiJjb2RlX2ludGVycHJldGVyIn0=)，导入仓库
3. 在 Vercel 项目设置中添加环境变量 `VITE_API_URL` = `http://your-server-ip:8000/api`
4. 点击「Deploy」，完成后分配域名

### 4.3 微信机器人部署
1. 在服务器上安装 Python 3.10+
2. 上传 `/wechat-bot` 目录到服务器
3. 修改 `.env` 中的 `BACKEND_URL`
4. 运行：`pip install -r requirements.txt && python bot.py`
5. 扫描二维码登录微信（建议使用小号）

---

## 五、AI 生成代码的执行顺序
请严格按照以下顺序要求 AI 生成代码：
1. **第一步**：生成 `/backend` 模块的所有代码（从 `database.py` 开始，到 `main.py` 结束）
2. **第二步**：生成 `/pwa-web` 模块的所有代码（从 `package.json` 开始，到页面组件结束）
3. **第三步**：生成 `/wechat-bot` 模块的所有代码
4. **第四步**：生成 `docker-compose.yml` 和部署说明

---

## 六、注意事项
1. **API Key 安全**：不要将 `.env` 文件提交到 Git
2. **CORS 配置**：后端 `main.py` 中的 `allow_origins` 生产环境请改为具体域名
3. **微信机器人**：建议使用微信小号，避免封号风险
4. **n8n 集成**：如果需要推送到 Strapi 和公众号，请自行配置 n8n 工作流并修改 `N8N_WEBHOOK_URL`
5. **数据库备份**：生产环境请定期备份 PostgreSQL 数据

---
