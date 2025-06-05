from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.schemas.llm_model import LLMRequest, LLMResponse, LLMHealthResponse
from app.services.llm_service import llm_service
from app.api.auth_api import get_current_user
from app.models import User

router = APIRouter(prefix="/llm", tags=["LLM聊天"])

@router.post("/chat", response_model=LLMResponse, summary="LLM聊天")
async def chat_with_llm(
    request: LLMRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    与LLM聊天，支持拍摄计划管理
    
    - **query**: 用户的问题或请求
    
    支持的功能：
    - 查询拍摄计划
    - 创建新的拍摄计划
    - 获取地点经纬度
    - 查询天气信息
    - 获取当前时间
    
    需要提供有效的Bearer token
    """
    try:
        # 使用当前用户的ID而不是请求中的user_id，确保安全性
        user_id = str(current_user.user_id)
        
        # 调用LLM服务
        response = llm_service(user_id, request.query)
        
        return LLMResponse(
            response=response,
            success=True,
            message="请求处理成功"
        )
        
    except Exception as e:
        # 记录错误日志
        print(f"LLM服务错误: {str(e)}")
        
        return LLMResponse(
            response="抱歉，处理您的请求时发生了错误，请稍后重试。",
            success=False,
            message=f"服务错误: {str(e)}"
        )

@router.get("/health", response_model=LLMHealthResponse, summary="检查LLM服务状态")
async def check_llm_health():
    """
    检查LLM服务的健康状态
    
    返回服务状态信息
    """
    try:
        # 简单的健康检查
        return LLMHealthResponse(
            status="healthy",
            service="LLM Chat Service",
            message="LLM服务运行正常"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM服务不可用: {str(e)}"
        )

