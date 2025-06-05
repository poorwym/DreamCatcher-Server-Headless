# DreamCatcher API 文档

## 概述

DreamCatcher是一个拍照辅助工具的后端API，提供用户认证、拍摄计划管理和LLM聊天功能。

**基础URL**: `http://localhost:8000/api/v1`

## 认证方式

API使用Bearer Token认证。在请求头中包含：
```
Authorization: Bearer <your_token>
```

## API端点

### 认证相关 (`/auth`)

#### 1. 用户注册
```http
POST /auth/register
```

**请求体**:
```json
{
  "user_name": "用户名",
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "user_id": "uuid",
  "user_name": "用户名",
  "email": "user@example.com",
  "message": "注册成功",
  "success": true
}
```

**说明**:
- user_name: 1-50个字符
- password: 6-100个字符

#### 2. 用户登录
```http
POST /auth/login
```

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "user": {
    "user_id": "uuid",
    "user_name": "用户名",
    "email": "user@example.com"
  },
  "access_token": "jwt_token",
  "token_type": "bearer",
  "message": "登录成功",
  "success": true
}
```

#### 3. 获取当前用户信息
```http
GET /auth/me
```

**需要认证**: ✅

**响应**:
```json
{
  "user_id": "uuid",
  "user_name": "用户名",
  "email": "user@example.com"
}
```

#### 4. 获取当前用户详细信息
```http
GET /auth/me/detail
```

**需要认证**: ✅

**响应**:
```json
{
  "user_id": "uuid",
  "user_name": "用户名",
  "email": "user@example.com",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 5. 更新当前用户信息
```http
PUT /auth/me
```

**需要认证**: ✅

**请求体**:
```json
{
  "user_name": "新用户名",
  "email": "new@example.com",
  "password": "newpassword123"
}
```

**响应**:
```json
{
  "user_id": "uuid",
  "user_name": "新用户名",
  "email": "new@example.com"
}
```

#### 6. 修改密码
```http
POST /auth/change-password
```

**需要认证**: ✅

**请求体**:
```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**响应**:
```json
{
  "message": "密码修改成功",
  "success": true
}
```

#### 7. 根据ID获取用户信息
```http
GET /auth/user/{user_id}
```

**需要认证**: ✅

**路径参数**:
- `user_id`: 用户UUID

**响应**:
```json
{
  "user_id": "uuid",
  "user_name": "用户名",
  "email": "user@example.com"
}
```

#### 8. 验证令牌
```http
POST /auth/verify-token
```

**需要认证**: ✅

**响应**:
```json
{
  "user_id": "uuid",
  "user_name": "用户名",
  "email": "user@example.com"
}
```

### LLM聊天 (`/llm`)

#### 1. LLM聊天
```http
POST /llm/chat
```

**需要认证**: ✅

**请求体**:
```json
{
  "query": "用户的问题或请求"
}
```

**响应**:
```json
{
  "response": "LLM的回复内容",
  "success": true,
  "message": "请求处理成功"
}
```

**支持的功能**:
- 查询拍摄计划
- 创建新的拍摄计划
- 获取地点经纬度
- 查询天气信息
- 获取当前时间

#### 2. 检查LLM服务状态
```http
GET /llm/health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "LLM Chat Service",
  "message": "LLM服务运行正常"
}
```

### 拍摄计划管理 (`/plans`)

#### 1. 获取指定拍摄计划
```http
GET /plans/{plan_id}
```

**需要认证**: ✅

**路径参数**:
- `plan_id`: 计划UUID

**响应**:
```json
{
  "plan_id": "uuid",
  "user_id": "uuid",
  "title": "计划标题",
  "description": "计划描述",
  "location": "拍摄地点",
  "scheduled_time": "2023-12-25T10:00:00Z",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 2. 获取拍摄计划列表
```http
GET /plans/
```

**需要认证**: ✅

**查询参数**:
- `skip`: 跳过的记录数（默认0）
- `limit`: 限制返回数量（默认100）

**响应**:
```json
[
  {
    "plan_id": "uuid",
    "user_id": "uuid",
    "title": "计划标题",
    "description": "计划描述",
    "location": "拍摄地点",
    "scheduled_time": "2023-12-25T10:00:00Z",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

#### 3. 创建拍摄计划
```http
POST /plans/
```

**需要认证**: ✅

**请求体**:
```json
{
  "title": "计划标题",
  "description": "计划描述",
  "location": "拍摄地点",
  "scheduled_time": "2023-12-25T10:00:00Z"
}
```

**响应**:
```json
{
  "plan_id": "uuid",
  "user_id": "uuid",
  "title": "计划标题",
  "description": "计划描述",
  "location": "拍摄地点",
  "scheduled_time": "2023-12-25T10:00:00Z",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 4. 更新拍摄计划
```http
PATCH /plans/{plan_id}
```

**需要认证**: ✅

**路径参数**:
- `plan_id`: 计划UUID

**请求体**:
```json
{
  "title": "新标题",
  "description": "新描述",
  "location": "新地点",
  "scheduled_time": "2023-12-26T10:00:00Z"
}
```

**响应**:
```json
{
  "plan_id": "uuid",
  "user_id": "uuid",
  "title": "新标题",
  "description": "新描述",
  "location": "新地点",
  "scheduled_time": "2023-12-26T10:00:00Z",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 5. 删除拍摄计划
```http
DELETE /plans/{plan_id}
```

**需要认证**: ✅

**路径参数**:
- `plan_id`: 计划UUID

**响应**: HTTP 204 No Content

#### 6. 管理员获取所有计划
```http
GET /plans/admin/all
```

**需要认证**: ✅
**权限要求**: 管理员（暂未实现权限检查）

**查询参数**:
- `user_id`: 筛选特定用户的计划（可选）
- `skip`: 跳过的记录数（默认0）
- `limit`: 限制返回数量（默认100）

**响应**:
```json
[
  {
    "plan_id": "uuid",
    "user_id": "uuid",
    "title": "计划标题",
    "description": "计划描述",
    "location": "拍摄地点",
    "scheduled_time": "2023-12-25T10:00:00Z",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

## 错误响应

所有API端点在出错时会返回以下格式的错误响应：

```json
{
  "detail": "错误详细信息",
  "status_code": 400
}
```

### 常见错误代码

- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 未提供有效的认证令牌
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求格式正确但内容无效
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

## 注意事项

1. 所有时间字段使用ISO 8601格式（UTC时间）
2. UUID字段使用标准UUID格式
3. 用户只能访问自己创建的拍摄计划
4. 密码要求6-100个字符
5. 用户名要求1-50个字符
6. 邮箱地址必须是有效格式

## 示例代码

### Python 示例

```python
import requests

# 用户注册
register_data = {
    "user_name": "测试用户",
    "email": "test@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/auth/register", json=register_data)

# 用户登录
login_data = {
    "email": "test@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/auth/login", json=login_data)
token = response.json()["access_token"]

# 使用token访问受保护的端点
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/auth/me", headers=headers)

# 创建拍摄计划
plan_data = {
    "title": "日出拍摄",
    "description": "在海边拍摄日出",
    "location": "青岛海滩",
    "scheduled_time": "2023-12-25T06:00:00Z"
}
response = requests.post("http://localhost:8000/plans/", json=plan_data, headers=headers)
```

### JavaScript 示例

```javascript
// 用户登录
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.access_token;

// 获取拍摄计划列表
const plansResponse = await fetch('http://localhost:8000/plans/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const plans = await plansResponse.json();
console.log(plans);
```
