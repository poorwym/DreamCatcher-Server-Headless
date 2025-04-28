import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base
from db import get_db
from main import app
from fastapi.testclient import TestClient

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 创建测试引擎
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 创建测试会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    """创建数据库会话"""
    # 每次测试前创建数据库表
    Base.metadata.create_all(bind=test_engine)
    
    # 创建一个新的会话
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 每次测试后删除所有表
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    # 重写依赖项
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # 测试后清除依赖项覆盖
    app.dependency_overrides.clear() 