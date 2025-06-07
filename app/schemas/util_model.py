from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class WeatherRequest(BaseModel):
    lat: float = Field(..., description="纬度", ge=-90, le=90)
    lon: float = Field(..., description="经度", ge=-180, le=180)
    dt: int = Field(..., description="Unix时间戳")

class WeatherData(BaseModel):
    dt: int = Field(..., description="时间戳")
    sunrise: int = Field(..., description="日出时间戳")
    sunset: int = Field(..., description="日落时间戳")
    temp: float = Field(..., description="温度(K)")
    feels_like: float = Field(..., description="体感温度(K)")
    pressure: int = Field(..., description="大气压(hPa)")
    humidity: int = Field(..., description="湿度(%)")
    dew_point: float = Field(..., description="露点(K)")
    uvi: float = Field(..., description="紫外线指数")
    clouds: int = Field(..., description="云量(%)")
    visibility: int = Field(..., description="能见度(m)")
    wind_speed: float = Field(..., description="风速(m/s)")
    wind_deg: int = Field(..., description="风向(度)")
    weather: List[Dict[str, Any]] = Field(..., description="天气描述")

class WeatherResponse(BaseModel):
    lat: float = Field(..., description="纬度")
    lon: float = Field(..., description="经度")
    timezone: str = Field(..., description="时区")
    timezone_offset: int = Field(..., description="时区偏移(秒)")
    data: List[WeatherData] = Field(..., description="天气数据")

class TileRequest(BaseModel):
    x: int = Field(..., description="瓦片X坐标", ge=0)
    y: int = Field(..., description="瓦片Y坐标", ge=0)
    z: int = Field(..., description="缩放级别", ge=0, le=20)

class TileResponse(BaseModel):
    url: str = Field(..., description="瓦片URL")
    x: int = Field(..., description="瓦片X坐标")
    y: int = Field(..., description="瓦片Y坐标")
    z: int = Field(..., description="缩放级别")

class PositionRequest(BaseModel):
    name: str = Field(..., description="地点名称", min_length=1, max_length=100)

class PositionTip(BaseModel):
    id: str = Field(..., description="地点ID")
    name: str = Field(..., description="地点名称")
    district: str = Field(..., description="行政区域")
    adcode: str = Field(..., description="行政区划代码")
    location: str = Field(..., description="经纬度")
    address: str = Field(..., description="详细地址")
    typecode: str = Field(..., description="POI分类代码")
    city: List[str] = Field(default=[], description="城市信息")

class PositionResponse(BaseModel):
    tips: List[PositionTip] = Field(..., description="搜索结果列表")
    status: str = Field(..., description="请求状态")
    info: str = Field(..., description="状态信息")
    infocode: str = Field(..., description="状态码")
    count: str = Field(..., description="结果数量")