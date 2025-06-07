# 数据模型

本文档详细描述DreamCatcher系统使用的数据模型，包括SQLAlchemy数据库模型和Pydantic验证模型。

## 数据库模型 (SQLAlchemy ORM)

### User 模型

用户数据库模型，存储在数据库的`users`表中。

```python
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**字段说明**:

- `user_id`: 主键，UUID格式的用户唯一标识
- `user_name`: 用户名，用于显示
- `email`: 用户邮箱，用于登录和联系
- `password`: 密码哈希值，使用bcrypt加密
- `created_at`: 创建时间，自动填充
- `updated_at`: 更新时间，自动更新

### Plan 模型

拍摄计划数据库模型，存储在数据库的`plans`表中。

```python
class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    camera = Column(JSON, nullable=False)  # 存储Camera对象
    tileset_url = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # 关联用户ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**字段说明**:

- `id`: 主键，UUID格式的计划唯一标识
- `name`: 计划名称，用于在UI中显示
- `description`: 计划描述，可为空
- `start_time`: 计划开始时间，支持时区信息
- `camera`: 相机参数，JSON格式存储
- `tileset_url`: 3D模型URL，用于渲染
- `user_id`: 创建此计划的用户ID，外键关联
- `created_at`: 创建时间，自动填充
- `updated_at`: 更新时间，自动更新

## API模型 (Pydantic)

### 认证相关模型

#### UserCreate 模型

用于用户注册的数据验证模型。

```python
class UserCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
```

**字段说明**:
- `user_name`: 用户名，1-50个字符
- `email`: 邮箱地址，自动验证格式
- `password`: 密码，6-100个字符

#### UserResponse 模型

用于API响应的用户信息模型，不包含敏感信息。

```python
class UserResponse(BaseModel):
    user_id: uuid.UUID = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
```

#### LoginRequest 模型

用户登录请求模型。

```python
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")
```

#### Token 模型

JWT令牌信息模型。

```python
class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
```

#### LoginResponse 模型

登录成功响应模型。

```python
class LoginResponse(BaseModel):
    user: UserResponse = Field(..., description="用户信息")
    token: Token = Field(..., description="令牌信息")
    message: str = Field(default="登录成功", description="响应消息")
```

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
    user_id: UUID
```

**字段说明**:
- `user_id`: 用户ID，UUID格式，标识计划所属用户

### 计划创建模型 (PlanCreate)

用于创建新计划的模型，继承自PlanBase。

```python
class PlanCreate(PlanBase):
    pass
```

**注意**: 创建计划时，`user_id`会被自动设置为当前认证用户的ID。

### 计划更新模型 (PlanUpdate)

用于更新现有计划的模型，所有字段都设置为可选。

```python
class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    camera: Optional[Camera] = None
    tileset_url: Optional[str] = None
    # 注意：更新时不允许修改user_id
```

**安全特性**:
- `user_id`字段不在更新模型中，防止恶意修改计划所有者
- 只有计划的创建者才能更新计划

### 计划响应模型 (Plan)

API响应中使用的完整计划模型，包含所有数据库字段。

```python
class Plan(PlanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
```

**特性**:
- `from_attributes = True`: 允许模型直接从ORM对象创建
- `id`: UUID格式的计划唯一标识

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
   - `from_attributes = True` 允许直接从ORM对象创建Pydantic模型

## 数据校验

系统使用Pydantic进行数据校验，包括：

- **类型检查**：确保字段类型正确（如UUID格式验证）
- **必填字段**：确保所有必填字段存在
- **嵌套校验**：对嵌套对象（如Camera）进行递归校验
- **默认值**：为可选字段提供默认值
- **权限校验**：确保用户只能操作自己的数据

## 安全设计

### 用户隔离

- 所有计划操作都必须通过用户认证
- 数据库查询自动过滤用户权限
- 防止用户访问其他用户的计划

### 数据完整性

- 使用UUID作为主键，避免ID推测攻击
- 更新操作不允许修改关键字段（如user_id）
- 严格的数据类型验证

### API安全

- 所有计划API都需要Bearer Token认证
- 自动验证用户对资源的所有权
- 错误信息不泄露敏感数据 