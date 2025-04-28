from datetime import datetime
from pydantic import BaseModel
from typing import Tuple, Optional
import uuid
from uuid import UUID

# 相机类
class Camera(BaseModel):
    focal_length: float
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float, float]

# 拍摄计划基类
class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    camera: Camera
    tileset_url: str
    user_id: str

# 创建拍摄计划
class PlanCreate(PlanBase):
    pass

# 更新拍摄计划
class PlanUpdate(PlanBase):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    camera: Optional[Camera] = None
    tileset_url: Optional[str] = None
    user_id: Optional[str] = None

# 拍摄计划
class Plan(PlanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
    