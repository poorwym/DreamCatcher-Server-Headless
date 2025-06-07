# DreamCatcher 服务端

DreamCatcher是一个拍照辅助工具，允许通过建立拍照计划的方式，预确定拍照的位置、角度、方向等信息。特别适用于拍摄月亮、太阳.

## 快速开始

### 使用Docker Compose部署

```bash
# 克隆仓库
git clone https://github.com/yourusername/DreamCatcher.git
cd DreamCatcher/DreamCatcher-Server-Headless

# 配置环境
mkdir -p configs
```
在configs文件夹下创建.env文件
```bash
# 数据库URL
DATABASE_URL=url
# 高德API KEY
GAODE_API_KEY=key
# 天地图API KEY
TIANDITU_API_KEY=key
# OpenWeather API KEY
OPENWEATHER_API_KEY=key
# SimpleLLMFunc 配置
LOG_DIR=./logs
LOG_FILE=agent.log
LOG_LEVEL=DEBUG

# SHA256 密钥
DREAMCATCHER_SECRET_KEY=key
```

在configs/目录下创建provider.json文件
```json
{
    "dreamcatcher": [
        {
            "model_name": "gpt-4o",
            "api_keys": [
                "your-api-key"
            ],
            "base_url": "https://api.chatanywhere.tech"
        },
        {
            "model_name": "o1",
            "api_keys": [
                "your-api-key"
            ],
            "base_url": "https://api.chatanywhere.tech"
        },
        {
            "model_name": "gemini-2.5-pro-exp-03-25",
            "api_keys": [
                "your-api-key"
            ],
            "base_url": "https://api.chatanywhere.tech"
        }
    ]
}
```

## 启动服务
### docker部署
#### 启动
```
docker-compose up -d
```


### 本地部署
#### 依赖
需要本地有postgres@14
#### 配置环境
```bash
conda create -n dreamcatcher python=3.13
conda activate dreamcatcher
uv pip install -r requirements.txt
```

#### 启动
```bash
chmod +x ./script/run.sh
./script/run.sh
```
#### 停止
```bash
chmod +x ./script/stop.sh
./script/stop.sh
```

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件

