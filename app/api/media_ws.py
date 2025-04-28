from typing import Dict
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from services import plan_service
from services.media_service import MediaService
from db import get_db

router = APIRouter(prefix="/ws", tags=["media"])

# 活跃的WebSocket连接
active_connections: Dict[UUID, WebSocket] = {}

@router.websocket("/render/{plan_id}")
async def render_websocket(websocket: WebSocket, plan_id: UUID, db: Session = Depends(get_db)):
    """处理渲染请求的WebSocket连接"""
    # 获取计划数据
    plan = plan_service.get_plan(db, plan_id)
    if not plan:
        await websocket.close(code=1008, reason="计划不存在")
        return
    
    # 接受WebSocket连接
    await websocket.accept()
    active_connections[plan_id] = websocket
    
    # 创建媒体服务
    media_service = MediaService()
    
    try:
        while True:
            # 等待客户端消息（可以是渲染控制命令）
            data = await websocket.receive_json()
            
            # 处理渲染控制命令
            if data.get("action") == "start_render":
                # 发送渲染请求到CRenderer
                await media_service.start_render(plan_id, plan, websocket)
            elif data.get("action") == "stop_render":
                # 停止渲染
                await media_service.stop_render(plan_id)
            
    except WebSocketDisconnect:
        # 客户端断开连接
        if plan_id in active_connections:
            del active_connections[plan_id]
        await media_service.stop_render(plan_id) 