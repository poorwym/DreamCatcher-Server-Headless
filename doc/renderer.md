# 渲染服务 (CRenderer)

本文档详细描述DreamCatcher系统的渲染服务组件，包括其架构、接口定义和工作流程。

## 渲染服务概述

CRenderer是DreamCatcher系统的核心渲染服务，由Cesium-Native和自定义Vulkan渲染器组成。其主要功能包括：

1. 加载3D地形和建筑模型
2. 根据相机参数和时间设置渲染场景
3. 生成高质量渲染图像
4. 通过WebSocket实时传输渲染结果

## 架构设计

CRenderer内部由以下组件构成：

### Cesium-Native

Cesium-Native是CesiumJS的C++实现，用于处理3D地理空间数据：

- 加载3D Tiles (b3dm格式)
- 处理地理坐标转换
- 提供地形和建筑物模型

### Vulkan渲染器

自定义的Vulkan渲染器，负责高性能图形渲染：

- 基于Vulkan API实现的现代图形管线
- 支持高级渲染效果，如PBR材质、全局光照等
- 高性能并行渲染

### 渲染服务接口

提供WebSocket API，接收渲染请求并返回渲染结果：

- 接收相机参数和时间信息
- 实时返回渲染帧
- 支持控制命令（开始/停止渲染）

## WebSocket API

### 连接

```
WebSocket ws://localhost:9000/ws
```

### 客户端到服务器消息

渲染请求：
```json
{
  "camera": {
    "focal_length": 35.0,
    "position": [30.2741, 120.1551, 100.0],
    "rotation": [0.0, 0.0, 0.0, 1.0]
  },
  "tileset_url": "https://mycdn.com/city/tileset.json",
  "current_time": "2025-04-25T10:00:00Z"
}
```

停止渲染：
```json
{
  "action": "stop"
}
```

### 服务器到客户端消息

渲染帧：
```json
{
  "type": "frame",
  "plan_id": "plan_123",
  "frame_number": 1,
  "timestamp": "2025-04-25T10:00:01Z",
  "image_path": "/shared/output/frame001.jpg"  // 或 base64 图像数据
}
```

错误消息：
```json
{
  "type": "error",
  "message": "渲染错误详情"
}
```

## 渲染流程

1. **初始化**：
   - 加载Vulkan渲染器
   - 初始化Cesium-Native环境
   - 启动WebSocket服务器

2. **接收渲染请求**：
   - 接收包含相机参数和时间信息的WebSocket消息
   - 解析请求参数

3. **场景准备**：
   - 根据URL加载3D Tileset
   - 设置相机位置和方向
   - 计算特定时间的太阳/月亮位置和光照

4. **渲染执行**：
   - 渲染场景到帧缓冲区
   - 应用后处理效果
   - 编码为图像数据

5. **结果传输**：
   - 通过WebSocket发送渲染帧
   - 可选择保存渲染结果到磁盘

## 渲染参数说明

### 相机参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| focal_length | 浮点数 | 焦距，单位毫米 |
| position | 数组[3] | [经度, 纬度, 高度] |
| rotation | 数组[4] | 四元数 [x, y, z, w] |

### 时间参数

时间参数`current_time`采用ISO 8601格式的字符串，例如`2025-04-25T10:00:00Z`。渲染器会根据这个时间：

- 计算太阳位置和角度
- 模拟特定时间的光照条件
- 渲染对应时间的阴影效果

### Tileset参数

`tileset_url`指向3D Tiles格式的模型数据，支持：

- 远程HTTP/HTTPS URL
- 本地文件路径
- Cesium ion资产ID (需配置access token)

## 渲染输出配置

渲染输出可通过配置文件进行调整：

```json
{
  "renderer": {
    "output_format": "jpg",    // 输出格式: jpg, png
    "output_quality": 90,      // JPEG质量 (1-100)
    "resolution": [1920, 1080], // 输出分辨率
    "output_dir": "/app/output", // 输出目录
    "save_frames": true        // 是否保存帧到磁盘
  }
}
```

## 性能优化

CRenderer采用多项技术优化性能：

- GPU并行渲染
- 动态细节层次 (LOD)
- 视锥体剔除
- 异步模型加载
- 纹理压缩和缓存

## 调试与故障排除

### 日志

渲染服务日志位于容器内的`/app/c_renderer/logs`目录，包含：

- 初始化日志
- 渲染请求和响应
- 错误和警告信息

### 常见问题

1. **模型加载失败**：
   - 确认URL可访问
   - 检查模型格式是否支持

2. **渲染性能问题**：
   - 检查GPU资源
   - 调整模型复杂度
   - 优化分辨率设置

3. **图像质量问题**：
   - 调整相机参数
   - 检查光照设置
   - 增加采样率 