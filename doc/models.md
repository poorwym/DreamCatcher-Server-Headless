# 数据模型

本文档详细描述DreamCatcher系统使用的数据模型，包括SQLAlchemy数据库模型和Pydantic验证模型。

## 数据库模型 (SQLAlchemy ORM)

### Plan 模型

拍摄计划数据库模型，存储在数据库的`plans`表中。

```python
class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    camera = Column(JSON, nullable=False)  # 存储Camera对象
    tileset_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**字段说明**:

- `id`: 主键，自增整数
- `name`: 计划名称，用于在UI中显示
- `description`: 计划描述，可为空
- `start_time`: 计划开始时间，支持时区信息
- `camera`: 相机参数，JSON格式存储
- `tileset_url`: 3D模型URL，用于渲染
- `created_at`: 创建时间，自动填充
- `updated_at`: 更新时间，自动更新

## API模型 (Pydantic)

### Camera 模型

相机参数验证模型。

```python
class Camera(BaseModel):
    focal_length: float
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float, float]
```

**字段说明**:

- `focal_length`: 焦距，单位毫米
- `position`: 位置坐标，依次为经度、纬度、高度
- `rotation`: 四元数表示的旋转，格式为[x, y, z, w]

### 计划基础模型 (PlanBase)

拍摄计划基础模型，包含创建计划所需的所有字段。

```python
class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    camera: Camera
    tileset_url: str
```

### 计划创建模型 (PlanCreate)

用于创建新计划的模型，继承自PlanBase。

```python
class PlanCreate(PlanBase):
    pass
```

### 计划更新模型 (PlanUpdate)

用于更新现有计划的模型，所有字段都设置为可选。

```python
class PlanUpdate(PlanBase):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    camera: Optional[Camera] = None
    tileset_url: Optional[str] = None
```

### 计划响应模型 (Plan)

API响应中使用的完整计划模型，包含所有数据库字段。

```python
class Plan(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

**特性**:
- `orm_mode = True`: 允许模型直接从ORM对象创建

## 数据流转换

系统中的数据流转换如下：

1. **API请求** → **Pydantic模型**:
   - 客户端发送JSON数据
   - FastAPI自动验证并转换为Pydantic模型
   - 验证失败时返回422错误

2. **Pydantic模型** → **SQLAlchemy模型**:
   - 服务层将Pydantic模型转为SQLAlchemy模型
   - 例如，`plan.camera.dict()` 将Camera对象转为JSON

3. **SQLAlchemy模型** → **数据库**:
   - ORM层将模型写入数据库

4. **数据库** → **SQLAlchemy模型** → **Pydantic模型** → **API响应**:
   - 读取时按反向流程处理
   - `orm_mode` 允许直接从ORM对象创建Pydantic模型

## 数据校验

系统使用Pydantic进行数据校验，包括：

- 类型检查：确保字段类型正确
- 必填字段：确保所有必填字段存在
- 嵌套校验：对嵌套对象（如Camera）进行递归校验
- 默认值：为可选字段提供默认值 