from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import blogs

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 博客系统 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blogs.router)

@app.get("/")
def read_root():
    return {"message": "AI 博客系统 API 运行中"}
