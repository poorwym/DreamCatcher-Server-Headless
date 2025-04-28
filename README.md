# DreamCatcher 服务端

DreamCatcher是一个拍照辅助工具，允许通过建立拍照计划的方式，预确定拍照的位置、角度、方向等信息。特别适用于拍摄月亮、太阳、飞机、建筑物或自然景观等场景，提供高效的预构图体验。

## 主要功能

- **3D场景预览**：支持导入b3dm模型，显示建筑、水体等
- **拍摄计划管理**：创建、编辑和管理拍摄计划
- **光照模拟**：根据时间模拟太阳高度角、照射方位、月亮位置等
- **云渲染**：支持高质量场景渲染和实时预览

## 系统架构

系统由以下主要组件构成：

- **FastAPI应用**：提供HTTP和WebSocket API
- **PostgreSQL数据库**：存储拍摄计划数据
- **CRenderer渲染服务**：基于Cesium-Native和Vulkan的渲染引擎

详细架构请参阅[系统架构文档](./doc/architecture.md)。

## 快速开始

### 使用Docker Compose部署

```bash
# 克隆仓库
git clone https://github.com/yourusername/DreamCatcher.git
cd DreamCatcher/DreamCatcher-Server-Headless

# 配置环境
mkdir -p configs
```
```bash
# 创建.env文件，配置必要的环境变量
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dreamcatcher 
RENDERER_WS_URL=ws://localhost:9000/ws
OPENAI_API_KEY=sk-***
OPENAI_BASE_URL=https://api.chatanywhere.tech
```

# 启动服务
```
docker-compose up -d
```

### 本地部署
```bash
chmod +x ./script/run.sh
./script/run.sh
```
这里之后因为默认用户会是你的电脑用户名,,比如我是`alexwu`,之后就要手动进入创建相关用户.
```bash
psql -h localhost -p 5432 -U alexwu -d postgres
```
```sql
CREATE ROLE postgres WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'postgres';
```

更多详细信息请参阅[部署指南](./doc/deployment.md)。

## API文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

API接口详细说明请参阅[API文档](./doc/api.md)。

## 开发指南

参与项目开发请参阅[开发指南](./doc/development.md)。

## 文档

项目完整文档位于`doc`目录：

- [系统架构](./doc/architecture.md)
- [API文档](./doc/api.md)
- [数据模型](./doc/models.md)
- [部署指南](./doc/deployment.md)
- [渲染服务](./doc/renderer.md)
- [开发指南](./doc/development.md)

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件

