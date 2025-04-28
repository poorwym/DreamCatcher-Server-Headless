import json
import asyncio
import websockets
from fastapi import WebSocket
from datetime import datetime
from uuid import UUID

from core.config import settings
from schemas.plan import Plan

class MediaService:
    """媒体服务，负责与渲染器通信"""
    
    async def start_render(self, plan_id: UUID, plan: Plan, client_ws: WebSocket):
        """启动渲染，并将结果推送给客户端"""
        try:
            # 连接到渲染器WebSocket
            async with websockets.connect(settings.RENDERER_WS_URL) as renderer_ws:
                # 构建渲染请求
                render_request = {
                    "camera": plan.camera.dict(),
                    "tileset_url": plan.tileset_url,
                    "current_time": datetime.now().isoformat() if plan.start_time < datetime.now() else plan.start_time.isoformat()
                }
                
                # 发送渲染请求
                await renderer_ws.send(json.dumps(render_request))
                
                # 接收渲染帧并转发给客户端
                while True:
                    frame_data = await renderer_ws.recv()
                    # 转发给客户端
                    await client_ws.send_text(frame_data)
                    
                    # 可以添加额外逻辑，例如保存渲染帧等
        
        except websockets.exceptions.ConnectionClosed:
            # 渲染器连接关闭
            await client_ws.send_json({"type": "error", "message": "渲染器连接已关闭"})
        except Exception as e:
            # 其他错误
            await client_ws.send_json({"type": "error", "message": f"渲染错误: {str(e)}"})
    
    async def stop_render(self, plan_id: UUID):
        """停止渲染"""
        try:
            # 连接到渲染器WebSocket
            async with websockets.connect(settings.RENDERER_WS_URL) as renderer_ws:
                # 发送停止渲染请求
                await renderer_ws.send(json.dumps({"action": "stop"}))
        except Exception:
            # 忽略停止时的错误
            pass 