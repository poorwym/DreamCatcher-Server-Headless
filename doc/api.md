# API 文档

本文档详细描述DreamCatcher服务端提供的API接口，包括HTTP REST API和WebSocket接口。

## API 基础信息

- **基础URL**: `/api/v1`
- **内容类型**: `application/json`
- **认证方式**: 暂未实现，后续可能添加JWT认证

## HTTP REST API

### 拍摄计划管理
#### 获取拍摄计划列表

```
GET /api/v1/plans
```

**查询参数**:
- `user_id` (字符串, 可选): 筛选属于指定用户的计划
- `skip` (整数, 可选): 分页起始位置，默认为0
- `limit` (整数, 可选): 每页数量，默认为100

**示例调用**:
```
GET /api/v1/plans?user_id=test_user_123&skip=0&limit=10
```

**响应**:
```json
[
  {
    "id": 1,
    "name": "黄昏下的建筑",
    "description": "捕捉夕阳照射下的城市建筑",
    "start_time": "2025-04-25T10:00:00Z",
    "camera": {
      "focal_length": 35.0,
      "position": [30.2741, 120.1551, 100.0],
      "rotation": [0.0, 0.0, 0.0, 1.0]
    },
    "tileset_url": "https://mycdn.com/city/tileset.json",
    "user_id": "test_user_123",
    "created_at": "2023-06-10T08:30:00Z",
    "updated_at": "2023-06-10T08:30:00Z"
  },
  ...
]
```

#### 获取指定拍摄计划

```
GET /api/v1/plans/{plan_id}
```

**路径参数**:
- `plan_id` (UUID 或整数): 拍摄计划ID

**响应**:
```json
{
  "id": 1,
  "name": "黄昏下的建筑",
  "description": "捕捉夕阳照射下的城市建筑",
  "start_time": "2025-04-25T10:00:00Z",
  "camera": {
    "focal_length": 35.0,
    "position": [30.2741, 120.1551, 100.0],
    "rotation": [0.0, 0.0, 0.0, 1.0]
  },
  "tileset_url": "https://mycdn.com/city/tileset.json",
  "user_id": "test_user_123",
  "created_at": "2023-06-10T08:30:00Z",
  "updated_at": "2023-06-10T08:30:00Z"
}
```

**错误响应**:
- 404: 计划未找到

#### 创建拍摄计划

```
POST /api/v1/plans
```

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
  "user_id": "test_user_123"
}
```

**响应**:
- 状态码: 201 Created
- 响应体: 创建的拍摄计划对象

#### 更新拍摄计划

```
PATCH /api/v1/plans/{plan_id}
```

**路径参数**:
- `plan_id` (UUID 或整数): 拍摄计划ID

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

**注意**: 请求体中的字段为可选，只更新提供的字段。

**响应**:
- 状态码: 200 OK
- 响应体: 更新后的拍摄计划对象

**错误响应**:
- 404: 计划未找到

#### 删除拍摄计划

```
DELETE /api/v1/plans/{plan_id}
```

**路径参数**:
- `plan_id` (UUID 或整数): 拍摄计划ID

**响应**:
- 状态码: 204 No Content

**错误响应**:
- 404: 计划未找到

## WebSocket API

### 渲染计划场景

```
WebSocket /api/v1/ws/render/{plan_id}
```

用于获取特定拍摄计划的实时渲染结果。

**连接参数**:
- `plan_id` (UUID 或整数): 拍摄计划ID

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
- 连接时，如果计划不存在，会以代码1008关闭连接
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
  "id": 1,                  // 计划ID
  "name": "计划名称",        // 计划名称
  "description": "描述信息", // 计划描述，可选
  "start_time": "2025-04-25T10:00:00Z",  // 计划开始时间
  "camera": {               // 相机参数
    "focal_length": 35.0,
    "position": [30.2741, 120.1551, 100.0],
    "rotation": [0.0, 0.0, 0.0, 1.0]
  },
  "tileset_url": "https://mycdn.com/city/tileset.json", // 3D模型URL
  "user_id": "test_user_123", // 用户ID
  "created_at": "2023-06-10T08:30:00Z",  // 创建时间
  "updated_at": "2023-06-10T08:30:00Z"   // 更新时间
}
``` 