# 开发指南

本文档为DreamCatcher服务端开发者提供指导，包括环境搭建、代码风格和贡献流程等信息。

## 开发环境搭建

### 前提条件

- Python 3.8+
- PostgreSQL 13+
- 支持Vulkan的GPU和驱动
- Docker和Docker Compose (用于完整部署)

### 本地开发环境

#### 1. 克隆代码库

```bash
git clone git@github.com:poorwym/DreamCatcher-Server-Headless.git
cd DreamCatcher/DreamCatcher-Server-Headless
```

#### 2. 创建虚拟环境

```bash
conda env create -f configs/environment.yml
```

#### 3. 激活虚拟环境

```bash
conda activate dreamcatcher
```

#### 4. 配置环境变量

创建`.env`文件并添加以下配置：

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/dreamcatcher
RENDERER_WS_URL=ws://localhost:9000/ws
```

#### 5. 创建数据库

```bash
# 在PostgreSQL中创建数据库
createdb dreamcatcher
```

#### 6. 启动应用

```bash
uvicorn app.main:app --reload
```

应用将在http://localhost:8000启动，并提供自动重载功能。

## 项目结构

```
DreamCatcher-Server-Headless/
├─ app/                   # 主应用代码
│  ├─ api/                # API路由
│  ├─ core/               # 核心功能和工具
│  ├─ schemas/            # Pydantic模型
│  ├─ services/           # 业务逻辑
│  ├─ models.py           # SQLAlchemy数据库模型
│  ├─ db.py               # 数据库配置
│  └─ main.py             # 应用入口
├─ c_renderer/            # 渲染服务
├─ docs/                  # 文档
├─ scripts/               # 辅助脚本
├─ tests/                 # 测试代码
├─ requirements.txt       # Python依赖
└─ docker-compose.yml     # Docker配置
```

## 代码规范

### Python风格指南

项目遵循PEP 8风格指南，并使用以下工具保证代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查

### 命名约定

- **类名**: 使用CamelCase
- **函数和变量**: 使用snake_case
- **常量**: 使用大写字母和下划线
- **文件名**: 使用snake_case

### 类型提示

项目使用Python类型注解，请在所有函数和方法中添加类型提示：

```python
def get_plan(db: Session, plan_id: int) -> Optional[Plan]:
    """获取指定ID的拍摄计划"""
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    return plan
```

## API开发指南

### 添加新的API端点

1. 在`app/api`目录下创建新的路由文件或扩展现有文件
2. 在`app/schemas`中定义请求和响应模型
3. 在`app/services`中实现业务逻辑
4. 在`app/main.py`中注册路由

示例：

```python
# app/api/plans.py
@router.get("/{plan_id}", response_model=Plan)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """获取指定ID的拍摄计划"""
    plan = plan_service.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="计划未找到")
    return plan
```

### 实现WebSocket端点

WebSocket端点应在`app/api`目录下实现，示例：

```python
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 处理数据
            await websocket.send_text(f"处理结果: {data}")
    except WebSocketDisconnect:
        # 处理断开连接
        pass
```

## 数据库操作

### 模型定义

在`app/models.py`中使用SQLAlchemy定义模型：

```python
class SomeModel(Base):
    __tablename__ = "some_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # 其他字段
```

### 数据库迁移

项目使用Alembic进行数据库迁移：

```bash
# 创建迁移
alembic revision --autogenerate -m "Migration description"

# 应用迁移
alembic upgrade head
```

## 测试

### 测试框架

项目使用pytest进行测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_plans.py
```

### 测试结构

```
tests/
├─ conftest.py         # 测试配置和固件
├─ test_api/           # API测试
├─ test_services/      # 服务层测试
└─ test_models/        # 模型测试
```

### 编写测试

测试示例：

```python
def test_create_plan(client, test_plan_data):
    response = client.post("/api/v1/plans/", json=test_plan_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_plan_data["name"]
```

## 渲染服务开发

渲染服务开发需要C++知识和Vulkan经验。主要组件位于`c_renderer`目录：

```
c_renderer/
├─ Renderer/           # Vulkan渲染器
├─ cesium-native/      # Cesium-Native集成
└─ CMakeLists.txt      # CMake构建配置
```

### 构建渲染服务

```bash
cd c_renderer
mkdir build && cd build
cmake ..
make
```

## 贡献流程

### 提交代码

1. Fork项目仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am '添加新功能'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交Pull Request

### 提交规范

提交消息应遵循以下格式：

```
<类型>: <简短描述>

<详细描述>
```

类型包括：
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更改
- `style`: 代码风格更改
- `refactor`: 代码重构
- `test`: 添加测试
- `chore`: 构建过程或辅助工具变动

### 代码审查

所有代码都需要通过代码审查后才能合并。审查重点包括：

- 代码质量和风格
- 测试覆盖率
- 文档完整性
- 性能考虑

## 持续集成

项目使用GitHub Actions进行持续集成：

- 运行代码风格检查
- 执行自动化测试
- 构建Docker镜像

## 文档

### 添加文档

新功能应在`doc`目录下添加相应文档：

```markdown
# 功能标题

功能描述...

## 使用方法

使用示例...
```

### API文档

API文档通过FastAPI自动生成，访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 