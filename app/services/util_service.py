import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from app.core.config import ConfigLoader
import httpx
import logging
from typing import Optional

config = ConfigLoader()
GAODE_API_KEY = config.get_env("GAODE_API_KEY")
TIANDITU_API_KEY = config.get_env("TIANDITU_API_KEY")
OPENWEATHER_API_KEY = config.get_env("OPENWEATHER_API_KEY")

# 配置日志
logger = logging.getLogger(__name__)

async def get_tile(x: int, y: int, z: int) -> str:
    """
    获取瓦片数据,使用天地图API获取tile
    http://t0.tianditu.gov.cn/vec_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=TIANDITU_API_KEY
    
    Args:
        x: 瓦片X坐标
        y: 瓦片Y坐标  
        z: 缩放级别
        
    Returns:
        str: 瓦片URL
    """
    try:
        # 构建天地图瓦片URL
        url = f"http://t0.tianditu.gov.cn/vec_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk={TIANDITU_API_KEY}"
        logger.info(f"获取瓦片: x={x}, y={y}, z={z}")
        return url
    except Exception as e:
        logger.error(f"获取瓦片失败: x={x}, y={y}, z={z}, 错误: {str(e)}")
        raise Exception(f"获取瓦片失败: {str(e)}")

async def get_position(name: str) -> dict:
    """
    模糊查询位置,使用高德地图API进行模糊查询
    
    Args:
        name: 地点名称
        
    Returns:
        dict: 完整的搜索结果
    """
    try:
        url = "https://restapi.amap.com/v3/assistant/inputtips"
        params = {
            "key": GAODE_API_KEY,
            "keywords": name
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"位置搜索完成: {name}, 结果数量: {result.get('count', 0)}")
            return result
            
    except httpx.HTTPError as e:
        logger.error(f"位置搜索HTTP错误: {name}, 错误: {str(e)}")
        raise Exception(f"位置搜索请求失败: {str(e)}")
    except Exception as e:
        logger.error(f"位置搜索失败: {name}, 错误: {str(e)}")
        raise Exception(f"位置搜索失败: {str(e)}")

async def get_weather(lat: float, lon: float, dt: int) -> dict:
    """
    根据输入的经纬度和日期获得天气信息,使用openweather的api
    
    Args:
        lat: 纬度
        lon: 经度
        dt: Unix时间戳
        
    Returns:
        dict: 天气信息
    """
    try:
        url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        params = {
            "lat": lat,
            "lon": lon,
            "dt": dt,
            "appid": OPENWEATHER_API_KEY
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"天气查询完成: lat={lat}, lon={lon}, dt={dt}")
            return result
            
    except httpx.HTTPError as e:
        logger.error(f"天气查询HTTP错误: lat={lat}, lon={lon}, dt={dt}, 错误: {str(e)}")
        raise Exception(f"天气查询请求失败: {str(e)}")
    except Exception as e:
        logger.error(f"天气查询失败: lat={lat}, lon={lon}, dt={dt}, 错误: {str(e)}")
        raise Exception(f"天气查询失败: {str(e)}")