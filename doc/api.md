# API 文档

本文档详细描述DreamCatcher服务端提供的API接口，包括HTTP REST API和WebSocket接口。

## API 基础信息

- **基础URL**: `/api/v1`
- **内容类型**: `application/json`
- **认证方式**: JWT Bearer Token认证

## 认证

### Bearer Token认证

大部分API端点需要使用Bearer Token认证。获取token后，在请求头中添加：

```
Authorization: Bearer <your_access_token>
```

## HTTP REST API

### 用户认证

#### 用户注册

```
POST /api/v1/auth/register
```

**请求体**:
```json
{
  "user_name": "张三",
  "email": "zhangsan@example.com",
  "password": "secure_password123"
}
```

**字段说明**:
- `user_name`: 用户名（1-50个字符）
- `email`: 邮箱地址
- `password`: 密码（6-100个字符）

**响应**:
```json
{
  "user": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_name": "张三",
    "email": "zhangsan@example.com"
  },
  "message": "注册成功"
}
```

**错误响应**:
- 400: 邮箱已被注册或参数验证失败

#### 用户登录

```
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "email": "zhangsan@example.com",
  "password": "secure_password123"
}
```

**响应**:
```json
{
  "user": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_name": "张三",
    "email": "zhangsan@example.com"
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "登录成功"
}
```

**错误响应**:
- 401: 邮箱或密码错误

#### 获取当前用户信息

```
GET /api/v1/auth/me
```

**认证**: 需要Bearer Token

**响应**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_name": "张三",
  "email": "zhangsan@example.com"
}
```

#### 获取当前用户详细信息

```
GET /api/v1/auth/me/detail
```

**认证**: 需要Bearer Token

**响应**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_name": "张三",
  "email": "zhangsan@example.com",
  "created_at": "2023-06-10T08:30:00Z",
  "updated_at": "2023-06-10T08:30:00Z"
}
```

#### 更新当前用户信息

```
PUT /api/v1/auth/me
```

**认证**: 需要Bearer Token

**请求体**:
```json
{
  "user_name": "李四",
  "email": "lisi@example.com",
  "password": "new_password123"
}
```

**注意**: 所有字段都是可选的，只更新提供的字段。

**响应**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_name": "李四",
  "email": "lisi@example.com"
}
```

**错误响应**:
- 400: 邮箱已被其他用户使用或参数验证失败

#### 修改密码

```
POST /api/v1/auth/change-password
```

**认证**: 需要Bearer Token

**请求体**:
```json
{
  "old_password": "old_password123",
  "new_password": "new_password123"
}
```

**响应**:
```json
{
  "message": "密码修改成功",
  "success": true
}
```

**错误响应**:
- 400: 原密码错误

#### 根据ID获取用户信息

```
GET /api/v1/auth/user/{user_id}
```

**认证**: 需要Bearer Token

**路径参数**:
- `user_id` (UUID): 用户ID

**响应**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_name": "张三",
  "email": "zhangsan@example.com"
}
```

**错误响应**:
- 404: 用户不存在

#### 验证令牌

```
POST /api/v1/auth/verify-token
```

**认证**: 需要Bearer Token

**响应**:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_name": "张三",
  "email": "zhangsan@example.com"
}
```

**错误响应**:
- 401: 令牌无效或已过期

### 拍摄计划管理

**注意**: 所有拍摄计划API都需要Bearer Token认证，用户只能操作自己创建的计划。

#### 获取拍摄计划列表

```
GET /api/v1/plans
```

**认证**: 需要Bearer Token

**查询参数**:
- `skip` (整数, 可选): 分页起始位置，默认为0
- `limit` (整数, 可选): 每页数量，默认为100

**响应**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "黄昏下的建筑",
    "description": "捕捉夕阳照射下的城市建筑",
    "start_time": "2025-04-25T10:00:00Z",
    "camera": {
      "focal_length": 35.0,
      "position": [30.2741, 120.1551, 100.0],
      "rotation": [0.0, 0.0, 0.0, 1.0]
    },
    "tileset_url": "https://mycdn.com/city/tileset.json",
    "user_id": "456e7890-e89b-12d3-a456-426614174001",
    "created_at": "2023-06-10T08:30:00Z",
    "updated_at": "2023-06-10T08:30:00Z"
  }
]
```

#### 获取指定拍摄计划

```
GET /api/v1/plans/{plan_id}
```

**认证**: 需要Bearer Token

**路径参数**:
- `plan_id` (UUID): 拍摄计划ID

**响应**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "黄昏下的建筑",
  "description": "捕捉夕阳照射下的城市建筑",
  "start_time": "2025-04-25T10:00:00Z",
  "camera": {
    "focal_length": 35.0,
    "position": [30.2741, 120.1551, 100.0],
    "rotation": [0.0, 0.0, 0.0, 1.0]
  },
  "tileset_url": "https://mycdn.com/city/tileset.json",
  "user_id": "456e7890-e89b-12d3-a456-426614174001",
  "created_at": "2023-06-10T08:30:00Z",
  "updated_at": "2023-06-10T08:30:00Z"
}
```

**错误响应**:
- 404: 计划未找到或无权访问

#### 创建拍摄计划

```
POST /api/v1/plans
```

**认证**: 需要Bearer Token

**请求体**:
```json
{
  "name": "黄昏下的建筑",
  "description": "捕捉夕阳照射下的城市建筑",
  "start_time": "2025-04-25T10:00:00Z",
  "camera": {
    "focal_length": 35.0,
    "position": [30.2741, 120.1551, 100.0],
    "rotation": [0.0, 0.0, 0.0, 1.0]
  },
  "tileset_url": "https://mycdn.com/city/tileset.json",
  "user_id": "456e7890-e89b-12d3-a456-426614174001"
}
```

**注意**: `user_id`字段会被自动设置为当前认证用户的ID，即使在请求中提供了不同的值。

**响应**:
- 状态码: 201 Created
- 响应体: 创建的拍摄计划对象

#### 更新拍摄计划

```
PATCH /api/v1/plans/{plan_id}
```

**认证**: 需要Bearer Token

**路径参数**:
- `plan_id` (UUID): 拍摄计划ID

**请求体**:
```json
{
  "name": "修改后的计划名称",
  "description": "更新的描述信息",
  "camera": {
    "focal_length": 50.0,
    "position": [30.2741, 120.1551, 120.0],
    "rotation": [0.1, 0.0, 0.0, 0.9]
  }
}
```

**注意**: 
- 请求体中的字段为可选，只更新提供的字段
- 不能修改`user_id`字段
- 只能更新当前用户创建的计划

**响应**:
- 状态码: 200 OK
- 响应体: 更新后的拍摄计划对象

**错误响应**:
- 404: 计划未找到或无权访问

#### 删除拍摄计划

```
DELETE /api/v1/plans/{plan_id}
```

**认证**: 需要Bearer Token

**路径参数**:
- `plan_id` (UUID): 拍摄计划ID

**响应**:
- 状态码: 204 No Content

**错误响应**:
- 404: 计划未找到或无权访问

#### 管理员获取所有计划

```
GET /api/v1/plans/admin/all
```

**认证**: 需要Bearer Token（管理员权限）

**查询参数**:
- `user_id` (UUID, 可选): 筛选属于指定用户的计划
- `skip` (整数, 可选): 分页起始位置，默认为0
- `limit` (整数, 可选): 每页数量，默认为100

**注意**: 此端点用于管理员查看所有用户的计划，目前暂未实现管理员权限检查。

**响应**: 与"获取拍摄计划列表"相同，但可能包含多个用户的计划。

## WebSocket API

### 渲染计划场景

```
WebSocket /api/v1/ws/render/{plan_id}
```

用于获取特定拍摄计划的实时渲染结果。

**认证**: 需要Bearer Token（通过查询参数或升级头传递）

**连接参数**:
- `plan_id` (UUID): 拍摄计划ID

**权限**: 只能渲染当前用户创建的计划

**客户端到服务器消息**:

启动渲染:
```json
{
  "action": "start_render"
}
```

停止渲染:
```json
{
  "action": "stop_render"
}
```

**服务器到客户端消息**:

渲染帧数据:
```json
{
  "type": "frame",
  "frame_number": 1,
  "timestamp": "2025-04-25T10:00:01Z",
  "image_data": "base64编码的图像数据"
}
```

错误消息:
```json
{
  "type": "error",
  "message": "错误详情"
}
```

**错误情况**:
- 连接时，如果计划不存在或无权访问，会以代码1008关闭连接
- 渲染过程中出现错误，会发送错误消息

## 数据模型

### 相机参数 (Camera)

```json
{
  "focal_length": 35.0,     // 焦距，单位毫米
  "position": [30.2741, 120.1551, 100.0],  // 经度、纬度、高度
  "rotation": [0.0, 0.0, 0.0, 1.0]  // 四元数表示的旋转
}
```

### 拍摄计划 (Plan)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",  // 计划ID (UUID)
  "name": "计划名称",        // 计划名称
  "description": "描述信息", // 计划描述，可选
  "start_time": "2025-04-25T10:00:00Z",  // 计划开始时间
  "camera": {               // 相机参数
    "focal_length": 35.0,
    "position": [30.2741, 120.1551, 100.0],
    "rotation": [0.0, 0.0, 0.0, 1.0]
  },
  "tileset_url": "https://mycdn.com/city/tileset.json", // 3D模型URL
  "user_id": "456e7890-e89b-12d3-a456-426614174001", // 用户ID (UUID)
  "created_at": "2023-06-10T08:30:00Z",  // 创建时间
  "updated_at": "2023-06-10T08:30:00Z"   // 更新时间
}
```

## 权限说明

### 用户权限

- 用户只能查看、创建、更新和删除自己的拍摄计划
- 用户无法访问其他用户的计划
- 所有计划操作都需要认证

### 管理员权限

- 管理员可以查看所有用户的计划（通过`/plans/admin/all`端点）
- 管理员权限验证功能待实现

### 安全措施

- 所有API使用JWT Bearer Token认证
- 计划创建时自动关联到当前用户
- 更新时不允许修改`user_id`字段
- 数据库查询时自动过滤用户权限 