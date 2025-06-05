import sys

# 将当前目录添加到Python路径
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api import plan_api, auth_api, llm_api

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
app.include_router(plan_api.router, prefix=f"{settings.API_V1_STR}")
app.include_router(auth_api.router, prefix=f"{settings.API_V1_STR}")
app.include_router(llm_api.router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API is running!"}
