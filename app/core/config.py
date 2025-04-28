import os
import json
import re
from typing import ClassVar
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class ConfigLoader:
    def __init__(self, config_path=None):
        # 获取项目根目录, 为DreamCatcher-Server-Headless的根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # 加载 .env 文件
        env_path = os.path.join(self.project_root, 'configs', '.env')
        load_dotenv(env_path)
        try:
            print(os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(e)
        
        try:
            print(os.getenv("DATABASE_URL"))
        except Exception as e:
            print(e)

        try:
            print(os.getenv("OPENAI_BASE_URL"))
        except Exception as e:
            print(e)
        
        if config_path is None:
            config_path = os.path.join(self.project_root, 'configs', 'config.json')
        else:
            config_path = os.path.join(self.project_root, config_path)
        try:
            self.config = self._load_config(config_path)
        except Exception as e:
            print(e)

    def _load_config(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return self._resolve_env_vars(raw)

    def _resolve_env_vars(self, obj):
        """递归解析所有 ${ENV_VAR} 环境变量"""
        if isinstance(obj, dict):
            return {k: self._resolve_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_env_vars(i) for i in obj]
        elif isinstance(obj, str):
            return re.sub(r"\$\{([^}^{]+)\}", lambda m: os.getenv(m.group(1), ""), obj)
        else:
            return obj

    def get(self, key, default=None):
        """支持通过点号路径访问嵌套字段，如 'llm.model'"""
        parts = key.split(".")
        val = self.config
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val

    def get_path(self, key, default=None):
        """专门用于获取路径类配置，返回以项目根目录为基准的绝对路径"""
        rel_path = self.get(key, default)
        if rel_path is None:
            return None
        return os.path.join(self.project_root, rel_path)
    
    def get_env(self, key, default=None):
        """专门用于获取环境变量"""
        return os.getenv(key, default)

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DreamCatcher"
    
    # 从ConfigLoader获取环境变量
    config_loader: ClassVar = ConfigLoader()
    # 默认使用本地数据库连接
    DATABASE_URL: str = config_loader.get_env("DATABASE_URL", "postgresql://postgres:password@localhost:5432/dreamcatcher")
    RENDERER_WS_URL: str = config_loader.get_env("RENDERER_WS_URL", "ws://localhost:9000/ws")
    
    model_config = {
        "case_sensitive": True
    }

# 初始化设置
settings = Settings()