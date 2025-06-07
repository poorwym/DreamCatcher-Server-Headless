from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LLMRequest(BaseModel):
    query: str = Field(..., description="用户的问题或请求", min_length=1, max_length=2000)

class LLMResponse(BaseModel):
    response: str = Field(..., description="LLM的回复内容")
    success: bool = Field(..., description="请求是否成功处理")
    message: str = Field(..., description="状态消息")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="响应时间戳")

class LLMHealthResponse(BaseModel):
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    message: str = Field(..., description="健康状态消息")