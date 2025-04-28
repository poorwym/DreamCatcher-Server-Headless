from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    camera = Column(JSON, nullable=False)  # 存储Camera对象
    tileset_url = Column(String, nullable=False)
    user_id = Column(String, nullable=False, index=True)  # 添加用户ID字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 