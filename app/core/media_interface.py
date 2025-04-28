from abc import ABC, abstractmethod
import json
from typing import Dict, Any

class MediaGateway(ABC):
    """抽象媒体网关接口"""
    
    @abstractmethod
    async def connect(self):
        """连接到渲染服务"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """断开与渲染服务的连接"""
        pass
    
    @abstractmethod
    async def send_render_request(self, request_data: Dict[str, Any]):
        """发送渲染请求"""
        pass
    
    @abstractmethod
    async def receive_frame(self):
        """接收渲染帧"""
        pass

class StubMediaGateway(MediaGateway):
    """用于测试的媒体网关存根实现"""
    
    def __init__(self):
        self.connected = False
        self.frame_count = 0
    
    async def connect(self):
        """模拟连接"""
        self.connected = True
        print("连接到测试渲染服务")
    
    async def disconnect(self):
        """模拟断开连接"""
        self.connected = False
        print("断开与测试渲染服务的连接")
    
    async def send_render_request(self, request_data: Dict[str, Any]):
        """模拟发送渲染请求"""
        if not self.connected:
            raise RuntimeError("未连接到渲染服务")
        
        print(f"发送渲染请求: {json.dumps(request_data, ensure_ascii=False)}")
        self.frame_count = 0
    
    async def receive_frame(self):
        """模拟接收渲染帧，返回测试图像数据"""
        if not self.connected:
            raise RuntimeError("未连接到渲染服务")
        
        self.frame_count += 1
        if self.frame_count > 100:  # 模拟渲染结束
            return None
        
        # 返回测试帧数据
        return json.dumps({
            "type": "frame",
            "frame_number": self.frame_count,
            "timestamp": "2025-04-25T10:00:01Z",
            "image_data": f"test_image_data_{self.frame_count}" # 实际应为base64编码的图像数据
        }) 