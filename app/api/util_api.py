from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.util_model import (
    WeatherRequest, WeatherResponse, 
    TileRequest, TileResponse,
    PositionRequest, PositionResponse
)
from app.services import util_service

router = APIRouter(prefix="/util", tags=["实用工具"])

@router.get("/weather", response_model=WeatherResponse, summary="获取天气信息")
async def get_weather(
    lat: float = Query(..., description="纬度", ge=-90, le=90),
    lon: float = Query(..., description="经度", ge=-180, le=180),
    dt: int = Query(..., description="Unix时间戳")
):
    """
    根据经纬度和时间获取历史天气信息
    
    使用OpenWeather API获取指定位置和时间的天气数据
    
    - **lat**: 纬度 (-90 到 90)
    - **lon**: 经度 (-180 到 180)  
    - **dt**: Unix时间戳
    """
    try:
        weather_data = await util_service.get_weather(lat, lon, dt)
        return WeatherResponse(**weather_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取天气信息失败: {str(e)}")

@router.get("/tile", response_model=TileResponse, summary="2D地图服务")
async def get_tile(
    x: int = Query(..., description="瓦片X坐标", ge=0),
    y: int = Query(..., description="瓦片Y坐标", ge=0),
    z: int = Query(..., description="缩放级别", ge=0, le=20)
):
    """
    获取地图瓦片URL
    
    使用天地图API获取指定坐标的地图瓦片
    
    - **x**: 瓦片X坐标
    - **y**: 瓦片Y坐标
    - **z**: 缩放级别 (0-20)
    """
    try:
        tile_url = await util_service.get_tile(x, y, z)
        return TileResponse(url=tile_url, x=x, y=y, z=z)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地图瓦片失败: {str(e)}")

@router.get("/position", response_model=PositionResponse, summary="模糊查询位置")
async def get_positions(
    name: str = Query(..., description="地点名称", min_length=1, max_length=100)
):
    """
    根据名称模糊搜索地理位置
    
    使用高德地图API进行地点搜索，返回匹配的位置列表
    
    - **name**: 要搜索的地点名称
    
    返回包含地点详细信息的列表，包括：
    - 地点ID、名称、地址
    - 行政区划信息
    - 经纬度坐标
    - POI分类信息
    """
    try:
        position_data = await util_service.get_position(name)
        return PositionResponse(**position_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"位置搜索失败: {str(e)}")
