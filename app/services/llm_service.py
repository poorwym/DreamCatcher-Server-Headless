import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
from zoneinfo import ZoneInfo
from app.core.config import ConfigLoader
import datetime
import logging
from typing import List
import threading
import time
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_loader = ConfigLoader()
project_root = config_loader.project_root
logger.info(f"项目根路径: {project_root}")

from SimpleLLMFunc import OpenAICompatible

try:
    # 从配置文件加载模型接口
    # llm_interface = OpenAICompatible.load_from_json_file(project_root / "configs" / "provider.json")["volc_engine"]["deepseek-v3-250324"]
    llm_interface = OpenAICompatible.load_from_json_file(project_root / "configs" / "provider.json")["dreamcatcher"]["gemini-2.5-pro-exp-03-25"]
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
from app.schemas.plan_model import PlanCreate, PlanUpdate, Camera
import uuid
import json
from duckduckgo_search import DDGS

GAODE_API_KEY = config_loader.get_env("GAODE_API_KEY")

# 线程本地存储，用于统一的数据库连接管理
thread_local = threading.local()

def get_db_session():
    """获取当前线程的数据库会话"""
    if not hasattr(thread_local, 'db_session') or thread_local.db_session is None:
        thread_local.db_session = SessionLocal()
    return thread_local.db_session

def close_db_session():
    """关闭当前线程的数据库会话"""
    if hasattr(thread_local, 'db_session') and thread_local.db_session is not None:
        thread_local.db_session.close()
        thread_local.db_session = None

# llm tool kit

@tool(name="search", description="搜索所有你需要的,别的工具无法提供的信息")
def search(query: str) -> str:
    '''
    搜索所有你需要的,别的工具无法提供的信息，使用DuckDuckGo搜索引擎

    Args:
        query: 搜索关键词
    Returns:
        str: 搜索结果，包含标题、链接和描述
    '''
    try:
        logger.info(f"正在搜索: {query}")

        # 设置完整的Headers，包括User-Agent、语言等
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

        results = []
        with DDGS(headers=headers) as ddgs:
            # 获取前5个搜索结果，设置中文区域
            search_results = list(ddgs.text(query, region='cn-zh', max_results=5))

            for i, result in enumerate(search_results, 1):
                title = result.get('title', '无标题')
                body = result.get('body', '无描述')
                href = result.get('href', '无链接')

                results.append(f"{i}. 标题: {title}\n   链接: {href}\n   描述: {body}\n")

        if results:
            search_summary = f"搜索 '{query}' 的结果:\n\n" + "\n".join(results)
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return search_summary
        else:
            logger.warning(f"搜索 '{query}' 未找到任何结果")
            return f"抱歉，没有找到关于 '{query}' 的相关信息。"

    except Exception as e:
        logger.error(f"搜索异常: {query}, 错误: {str(e)}")
        return f"搜索时发生错误: {str(e)}"

@tool(name="fetch", description="fetch 一个url, 返回url的内容")
def fetch(url : str) -> str:
    '''
    fetch 一个url, 返回url的内容
    Args:
        url: 需要fetch的url
    Returns:
        str: url的内容
    '''
    try:
        logger.info(f"正在fetch: {url}")
        response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        logger.error(f"fetch异常: {url}, 错误: {str(e)}")
        return f"fetch时发生错误: {str(e)}"

@tool(name="get_position", description="从地点名称，获取经纬度")
def get_positions(name : str) -> dict:
    '''
    从地点名称，获取可能的所有经纬度,你需要判断用户最可能选择的地点
    Args:
        name: 模糊输入的地点名称
    Returns:
        dict: 包含所有可能的地点信息
    '''
    try:
        logger.info(f"正在查询地点: {name}")
        tips_url = f"https://restapi.amap.com/v3/assistant/inputtips?key={GAODE_API_KEY}&keywords={name}"
        tips_response = requests.get(tips_url, timeout=10)
        tips_data = tips_response.json()
        return tips_data
    except Exception as e:
        logger.error(f"地点查询异常: {name}, 错误: {str(e)}")
        return {"error": f"地点查询失败: {str(e)}"}

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
    获取中国标准时间（Asia/Shanghai）
    Returns:
        str: 当前时间, 格式为"YYYY-MM-DD HH:MM:SS"
    '''
    try:
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.datetime.now(tz=china_tz).strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"获取当前时间（中国时区）: {current_time}")
        return current_time
    except Exception as e:
        logger.error(f"获取当前时间异常: {str(e)}")
        return "时间获取失败"

@tool(name="get_plans_by_user", description="获取用户创建的拍摄计划")
def get_plans_by_user(user_id : str) -> List[dict]:
    '''
    获取用户创建的拍摄计划
    Args:
        user_id: 用户ID
    Returns:
        List[dict]: 拍摄计划列表, 格式为list[dict]
    '''
    try:
        logger.info(f"正在查询用户计划: {user_id}")
        db = get_db_session()
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
                # 确保 camera 字段是字典类型，避免重复序列化
                if isinstance(plan.camera, str):
                    # 如果是 JSON 字符串，先解析为字典
                    camera_data = json.loads(plan.camera)
                else:
                    # 如果已经是字典，直接使用
                    camera_data = plan.camera
                
                plan_dict["camera"] = {
                    "focal_length": camera_data["focal_length"],
                    "position": camera_data["position"],
                    "rotation": camera_data["rotation"]
                }
            plans_dict.append(plan_dict)
            
        logger.info(f"用户计划查询成功: 找到 {len(plans_dict)} 个计划")
        return plans_dict
        
    except Exception as e:
        logger.error(f"查询用户计划异常: {user_id}, 错误: {str(e)}")
        return [{"error": f"查询计划失败: {str(e)}"}]

@tool(name="create_plan", description="创建拍摄计划")
def create_plan(name: str, description: str, start_time: str, focal_length: float, position: List[float], rotation: List[float], user_id: str, tileset_url: str = "") -> dict:
    '''
    创建拍摄计划,要求提供所有必须的字段
    拍摄计划开始的时间必须晚于现在的时间,可以通过get_current_time工具获取当前时间
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
    try:
        logger.info(f"正在创建拍摄计划: {name}")
        db = get_db_session()
        
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

@tool(name="update_plan", description="更新拍摄计划")
def update_plan(plan_id: str, name: str = None, description: str = None, start_time: str = None, focal_length: float = None, position: List[float] = None, rotation: List[float] = None, user_id: str = None, tileset_url: str = None) -> dict:
    '''
    更新拍摄计划,要求提供要更新的字段
    注意,plan_id是必须的,可以通过get_plans_by_user工具获取所有计划的id,然后你自行判断哪个是需要更新的
    更新的时间必须晚于现在的时间,可以通过get_current_time工具获取当前时间
    Args:
        plan_id: 拍摄计划ID (必须)
        name: 拍摄计划名称 (可选)
        description: 拍摄计划描述 (可选)
        start_time: 拍摄计划开始时间 (可选)
        focal_length: 相机焦距 (可选)
        position: 相机位置, 格式为[x, y, z] (可选)
        rotation: 相机旋转, 格式为[x, y, z, w] (可选)
        user_id: 用户ID (必须)
        tileset_url: 3D模型URL (可选)
    Returns:
        dict: 更新后的拍摄计划, 格式为dict
    '''
    try:
        logger.info(f"正在更新拍摄计划: {plan_id}")
        db = get_db_session()
        
        # 构建更新数据字典，只包含非None的字段
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if start_time is not None:
            # 解析时间
            if isinstance(start_time, str):
                update_data["start_time"] = datetime.datetime.fromisoformat(start_time)
            else:
                update_data["start_time"] = start_time
        if tileset_url is not None:
            update_data["tileset_url"] = tileset_url
            
        # 如果相机参数有更新，构建相机对象
        if focal_length is not None or position is not None or rotation is not None:
            # 先获取现有计划的相机参数
            existing_plan = plan_service.get_plan(db, uuid.UUID(plan_id), uuid.UUID(user_id))
            if not existing_plan:
                return {"error": "计划不存在或无权限访问", "status": "failed"}
            
            # 解析现有相机数据
            existing_camera = existing_plan.camera
            if isinstance(existing_camera, str):
                existing_camera = json.loads(existing_camera)
            
            # 使用新值或保留现有值
            camera_data = {
                "focal_length": focal_length if focal_length is not None else existing_camera.get("focal_length", 50.0),
                "position": tuple(position) if position is not None else tuple(existing_camera.get("position", [0, 0, 0])),
                "rotation": tuple(rotation) if rotation is not None else tuple(existing_camera.get("rotation", [0, 0, 0, 1]))
            }
            
            camera = Camera(**camera_data)
            update_data["camera"] = camera
        
        # 创建更新对象
        plan_update = PlanUpdate(**update_data)
        
        # 执行更新
        updated_plan = plan_service.update_plan(db, uuid.UUID(plan_id), plan_update, uuid.UUID(user_id))
        
        if not updated_plan:
            return {"error": "计划不存在或无权限更新", "status": "failed"}
        
        # 将更新后的计划转换为字典
        result = {
            "id": str(updated_plan.id),
            "name": updated_plan.name,
            "description": updated_plan.description,
            "start_time": updated_plan.start_time.isoformat() if updated_plan.start_time else None,
            "created_at": updated_plan.created_at.isoformat() if updated_plan.created_at else None,
            "updated_at": updated_plan.updated_at.isoformat() if updated_plan.updated_at else None,
            "user_id": str(updated_plan.user_id),
            "status": "updated"
        }
        
        if hasattr(updated_plan, 'camera') and updated_plan.camera:
            if isinstance(updated_plan.camera, str):
                camera_data = json.loads(updated_plan.camera)
            else:
                camera_data = updated_plan.camera
            
            result["camera"] = {
                "focal_length": camera_data["focal_length"],
                "position": camera_data["position"],
                "rotation": camera_data["rotation"]
            }
        
        logger.info(f"拍摄计划更新成功: {result['id']}")
        return result
        
    except Exception as e:
        logger.error(f"更新拍摄计划异常: {str(e)}")
        return {
            "error": f"更新计划失败: {str(e)}",
            "status": "failed"
        }

@tool(name="delete_plan", description="删除拍摄计划")
def delete_plan(plan_id: str, user_id: str) -> dict:
    '''
    删除拍摄计划
    Args:
        plan_id: 拍摄计划ID
        user_id: 用户ID
    Returns:
        dict: 删除结果
    '''
    try:
        logger.info(f"正在删除拍摄计划: {plan_id}")
        db = get_db_session()
        
        # 执行删除操作
        success = plan_service.delete_plan(db, uuid.UUID(plan_id), uuid.UUID(user_id))
        
        if success:
            result = {
                "plan_id": plan_id,
                "status": "deleted",
                "message": "拍摄计划删除成功"
            }
            logger.info(f"拍摄计划删除成功: {plan_id}")
            return result
        else:
            return {
                "plan_id": plan_id,
                "status": "failed",
                "error": "计划不存在或无权限删除"
            }
            
    except Exception as e:
        logger.error(f"删除拍摄计划异常: {plan_id}, 错误: {str(e)}")
        return {
            "plan_id": plan_id,
            "status": "failed",
            "error": f"删除计划失败: {str(e)}"
        }


# llm interface
from SimpleLLMFunc import llm_function

@llm_function(
    llm_interface=llm_interface,
    toolkit=[search, get_positions, get_weather, get_current_time, get_plans_by_user, create_plan, update_plan, delete_plan, fetch],
)
def llm_service(user_id : str, query : str) -> str:
    '''
    你叫Morpheus,是一个专业的拍照计划管理助手，根据用户的请求提供帮助,
    在必要的时候调用工具函数来获取,删除或更新拍摄计划信息。
    你需要确保计划的创建和更新都不会设置为过去的时间,可以通过get_current_time工具获取当前时间。
    
    你可以：
    1. 查询和管理用户的拍摄计划
    2. 创建新的拍摄计划
    3. 获取地点的经纬度信息
    4. 查询天气信息
    5. 获取当前时间
    
    请友好、专业地回应用户的请求，并清楚地说明你执行了哪些操作。

    example:
        user: 帮我创建一个今天下午西湖的拍摄计划
        assistant: 好的，我已经为您创建了一个拍摄计划，计划名称为"西湖拍摄"，开始时间为今天下午3点，使用的相机焦距为35mm，位置在西湖附近。请问您还有其他需要吗？
        不要这样返回:"{
        "id": "f6dffffd-7516-4ee2-bd25-8ca2999484bb",
        "name": "西湖拍摄计划",
        "description": "今天下午的西湖拍摄计划",
        "start_time": "2025-06-07T15:00:00+08:00",
        "created_at": "2025-06-07T08:22:40.653487+08:00",
        "user_id": "bab087c3-7a55-494d-a4f7-cb375ade621a",
        "camera": {
          "focal_length": 50.0,
          "position": [120.167532, 30.245602, 0.0],
          "rotation": [0.0, 0.0, 0.0, 1.0]
        }
      }"
    
    Args:
        user_id: 用户ID
        query: 用户的请求
    Returns:
        str: 友好的回复，包含你执行的操作和结果,要求清晰的陈述你调用了哪些工具,切记不要直接返回tool返回的内容,而是根据tool的返回结果进行总结后友好的回答用户的请求.
    '''
    try:
        # 在开始处理前创建统一的数据库会话
        get_db_session()
        logger.info(f"为用户 {user_id} 创建统一数据库会话")
        
        # 这里会被SimpleLLMFunc框架填充实际的LLM逻辑
        pass
        
    finally:
        # 确保在处理完成后关闭数据库会话
        close_db_session()
        logger.info(f"关闭用户 {user_id} 的数据库会话")

if __name__ == "__main__":
    # 测试代码
    try:
        # result = get_plans_by_user("89f0f3a0-4c1e-4a41-bb8e-a786dd0828b4")
        # print("测试计划查询:", result)
        
        ans = llm_service("89f0f3a0-4c1e-4a41-bb8e-a786dd0828b4", "帮我更新西湖拍摄计划的开始时间为2025-06-09 15:00:00,焦距为35mm,位置在西湖附近")
        print("LLM回复:", ans)
    except Exception as e:
        logger.error(f"测试运行失败: {str(e)}")
    finally:
        close_db_session()
