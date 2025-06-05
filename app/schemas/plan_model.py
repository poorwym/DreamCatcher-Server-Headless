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
    user_id: UUID

# 创建拍摄计划
class PlanCreate(PlanBase):
    pass

# 更新拍摄计划
class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    camera: Optional[Camera] = None
    tileset_url: Optional[str] = None
    # 注意：更新时不允许修改user_id

# 拍摄计划
class Plan(PlanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
    