import sys
import logging
from contextlib import asynccontextmanager

# 将当前目录添加到Python路径
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.api import plan_api, auth_api, llm_api, util_api
from app.db import engine

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接健康检查，带重试机制
@retry(
    retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=16),
    before_sleep=lambda retry_state: logger.warning(f"数据库连接健康检查失败，正在重试... 第{retry_state.attempt_number}次")
)
def check_database_connection():
    """检查数据库连接是否正常"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("数据库连接健康检查通过")
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        raise

# 应用启动时的生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理，包含启动和关闭逻辑"""
    # 启动时执行
    logger.info("正在启动 FastAPI 应用...")
    try:
        # 执行数据库连接检查
        check_database_connection()
        logger.info("应用启动完成，所有依赖服务连接正常")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭 FastAPI 应用...")
    try:
        # 关闭数据库连接
        engine.dispose()
        logger.info("应用关闭完成")
    except Exception as e:
        logger.error(f"应用关闭时出现错误: {str(e)}")

# 创建FastAPI应用，使用生命周期管理
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
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
app.include_router(util_api.router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API is running!"}

@app.get("/health")
@retry(
    retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    before_sleep=lambda retry_state: logger.warning(f"健康检查失败，正在重试... 第{retry_state.attempt_number}次")
)
def health_check():
    """健康检查端点，带重试机制"""
    try:
        # 检查数据库连接
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "服务运行正常",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"服务异常: {str(e)}",
            "database": "disconnected"
        }
