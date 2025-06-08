from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DisconnectionError
from app.core.config import settings
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 设置日志
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 添加重试装饰器的数据库引擎创建
@retry(
    retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=lambda retry_state: logger.info(f"数据库连接失败，正在重试... 第{retry_state.attempt_number}次")
)
def create_db_engine():
    """创建数据库引擎，带重试机制"""
    logger.info("正在创建数据库引擎...")
    return create_engine(SQLALCHEMY_DATABASE_URL)

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖项 - 添加重试机制的数据库会话获取
def get_db():
    """获取数据库会话，带重试机制"""
    db = SessionLocal()
    try:
        # 测试连接是否正常
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"数据库会话异常: {str(e)}")
        raise
    finally:
        db.close()

# 创建表格 - 添加重试机制
@retry(
    retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=16),
    before_sleep=lambda retry_state: logger.warning(f"创建数据库表失败，正在重试... 第{retry_state.attempt_number}次")
)
def create_tables():
    """创建数据库表，带重试机制"""
    try:
        # 延迟导入避免循环导入
        from app.models import Base
        logger.info("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        raise

# 在模块导入时创建数据库表
try:
    create_tables()
except Exception as e:
    logger.error(f"初始化数据库表失败: {str(e)}")
    raise 