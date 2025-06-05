import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from app.core.config import ConfigLoader
import datetime
import logging
from typing import List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_loader = ConfigLoader()
project_root = config_loader.project_root
logger.info(f"项目根路径: {project_root}")

from SimpleLLMFunc import OpenAICompatible

try:
    # 从配置文件加载模型接口
    llm_interface = OpenAICompatible.load_from_json_file(project_root / "configs" / "provider.json")["volc_engine"]["deepseek-v3-250324"]
    logger.info("LLM接口加载成功")
    logger.info(f"基础URL: {llm_interface.base_url}")
    logger.info(f"模型名称: {llm_interface.model_name}")
except Exception as e:
    logger.error(f"LLM接口加载失败: {str(e)}")
    raise

from SimpleLLMFunc import tool
import app.services.plan_service as plan_service
import app.services.auth_service as auth_service
from app.db import SessionLocal
import asyncio
import requests
from app.schemas.plan_model import PlanCreate, Camera
import uuid
import json

GAODE_API_KEY = config_loader.get_env("GAODE_API_KEY")

# llm tool kit

@tool(name="get_position", description="从地点名称，获取经纬度")
def get_position(name : str) -> tuple[float, float]:
    '''
    从地点名称，获取经纬度
    Args:
        name: 模糊输入的地点名称
    Returns:
        tuple[float, float]: 经纬度
    '''
    try:
        logger.info(f"正在查询地点: {name}")
        tips_url = f"https://restapi.amap.com/v3/assistant/inputtips?key={GAODE_API_KEY}&keywords={name}"
        tips_response = requests.get(tips_url, timeout=10)
        tips_data = tips_response.json()
        
        if tips_data["status"] == "1" and tips_data.get("tips"):
            location = tips_data["tips"][0]["location"]
            # 将字符串格式的经纬度转换为tuple
            lon, lat = location.split(',')
            result = (float(lon), float(lat))
            logger.info(f"地点查询成功: {name} -> {result}")
            return result
        else:
            logger.warning(f"地点查询失败: {name}")
            return None
    except Exception as e:
        logger.error(f"地点查询异常: {name}, 错误: {str(e)}")
        return None

@tool(name="get_weather", description="从经纬度获取天气")
def get_weather(position : tuple[float, float], date : str) -> dict:
    '''
    从经纬度，获取天气
    Args:
        position: 经纬度, 格式为tuple[float, float]
        date: 日期, 格式为"YYYY-MM-DD"
    Returns:
        dict: 天气, 格式为dict
    '''
    try:
        logger.info(f"正在查询天气: 位置={position}, 日期={date}")
        # 这里暂时返回模拟数据，实际应该调用天气API
        result = {
            "weather": "晴天",
            "temperature": "25°C",
            "humidity": "60%",
            "wind": "微风",
            "date": date,
            "position": position
        }
        logger.info(f"天气查询完成: {result}")
        return result
    except Exception as e:
        logger.error(f"天气查询异常: 位置={position}, 日期={date}, 错误: {str(e)}")
        return {
            "error": f"天气查询失败: {str(e)}",
            "date": date
        }

@tool(name="get_current_time", description="获取当前时间")
def get_current_time() -> str:
    '''
    获取当前时间
    Returns:
        str: 当前时间, 格式为"YYYY-MM-DD HH:MM:SS"  
    '''
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"获取当前时间: {current_time}")
        return current_time
    except Exception as e:
        logger.error(f"获取当前时间异常: {str(e)}")
        return "时间获取失败"

@tool(name="get_plans_by_user", description="获取用户创建的拍摄计划")
def get_plans_by_user(user_id : str) -> str:
    '''
    获取用户创建的拍摄计划
    Args:
        user_id: 用户ID
    Returns:
        list[dict]: 拍摄计划列表, 格式为list[dict]
    '''
    db = SessionLocal()
    try:
        logger.info(f"正在查询用户计划: {user_id}")
        user_id_uuid = uuid.UUID(user_id)
        plans = plan_service.get_plans_by_user(db, user_id_uuid)
        
        # 将计划对象转换为字典列表
        plans_dict = []
        for plan in plans:
            plan_dict = {
                "id": str(plan.id),
                "name": plan.name,
                "description": plan.description,
                "start_time": plan.start_time.isoformat() if plan.start_time else None,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "user_id": str(plan.user_id)
            }
            if hasattr(plan, 'camera') and plan.camera:
                plan_dict["camera"] = {
                    "focal_length": plan.camera["focal_length"],
                    "position": plan.camera["position"],
                    "rotation": plan.camera["rotation"]
                }
            plans_dict.append(plan_dict)
            
        logger.info(f"用户计划查询成功: 找到 {len(plans_dict)} 个计划")
        return json.dumps(plans_dict)
        
    except Exception as e:
        logger.error(f"查询用户计划异常: {user_id}, 错误: {str(e)}")
        return json.dumps({"error": f"查询计划失败: {str(e)}"})
    finally:
        db.close()

@tool(name="create_plan", description="创建拍摄计划")
def create_plan(name: str, description: str, start_time: str, focal_length: float, position: List[float], rotation: List[float], user_id: str, tileset_url: str = "") -> dict:
    '''
    创建拍摄计划,要求提供所有必须的字段
    Args:
        name: 拍摄计划名称
        description: 拍摄计划描述
        start_time: 拍摄计划开始时间
        focal_length: 相机焦距
        position: 相机位置, 格式为[x, y, z]
        rotation: 相机旋转, 格式为[x, y, z, w]
        user_id: 用户ID
        tileset_url: 3D模型URL (可选)
    Returns:
        dict: 拍摄计划, 格式为dict
    '''
    db = SessionLocal()
    try:
        logger.info(f"正在创建拍摄计划: {name}")
        
        # 解析start_time
        start_time_parsed = None
        if start_time:
            if isinstance(start_time, str):
                start_time_parsed = datetime.datetime.fromisoformat(start_time)
            else:
                start_time_parsed = start_time
        
        camera = Camera(
            focal_length=focal_length,
            position=tuple(position),
            rotation=tuple(rotation)
        )
        
        plan = PlanCreate(
            name=name,
            description=description,
            start_time=start_time_parsed if start_time_parsed else datetime.datetime.now(),
            camera=camera,
            tileset_url=tileset_url,
            user_id=uuid.UUID(user_id)
        )
        created_plan = plan_service.create_plan(db, plan)
        
        # 将创建的计划转换为字典
        result = {
            "id": str(created_plan.id),
            "name": created_plan.name,
            "description": created_plan.description,
            "start_time": created_plan.start_time.isoformat() if created_plan.start_time else None,
            "created_at": created_plan.created_at.isoformat() if created_plan.created_at else None,
            "user_id": str(created_plan.user_id),
            "status": "created"
        }
        logger.info(f"拍摄计划创建成功: {result['id']}")
        return result
        
    except Exception as e:
        logger.error(f"创建拍摄计划异常: {str(e)}")
        return {
            "error": f"创建计划失败: {str(e)}",
            "status": "failed"
        }
    finally:
        db.close()


# llm interface
from SimpleLLMFunc import llm_function

@llm_function(
    llm_interface=llm_interface,
    toolkit=[get_position, get_weather, get_current_time, get_plans_by_user, create_plan],
)
def llm_service(user_id : str, query : str) -> str:
    '''
    你是一个专业的拍照计划管理助手，根据用户的请求提供帮助。
    
    你可以：
    1. 查询和管理用户的拍摄计划
    2. 创建新的拍摄计划
    3. 获取地点的经纬度信息
    4. 查询天气信息
    5. 获取当前时间
    
    请友好、专业地回应用户的请求，并清楚地说明你执行了哪些操作。
    
    Args:
        user_id: 用户ID
        query: 用户的请求
    Returns:
        str: 友好的回复，包含你执行的操作和结果,要求清晰的陈述你调用了哪些工具.
    '''
    pass

if __name__ == "__main__":
    # 测试代码
    try:
        result = get_plans_by_user("89f0f3a0-4c1e-4a41-bb8e-a786dd0828b4")
        print("测试计划查询:", result)
        
        ans = llm_service("89f0f3a0-4c1e-4a41-bb8e-a786dd0828b4", "我有哪些计划？今天天气怎么样？")
        print("LLM回复:", ans)
    except Exception as e:
        logger.error(f"测试运行失败: {str(e)}")
