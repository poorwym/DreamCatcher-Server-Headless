import sys
import os

# 将当前目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api import plans, media_ws
from db import create_tables

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(plans.router, prefix=f"{settings.API_V1_STR}")
app.include_router(media_ws.router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API is running!"}
@app.on_event("startup")
def startup_event():
    # 创建数据库表
    create_tables()
