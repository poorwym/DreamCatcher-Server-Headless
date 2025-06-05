# 认证系统说明

本文档详细说明DreamCatcher系统的用户认证和授权机制。

## 概述

DreamCatcher使用JWT (JSON Web Token) 进行用户认证和授权。系统提供用户注册、登录、信息管理等功能。

## 认证流程

### 1. 用户注册

用户首次使用系统需要注册账号：

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "user_name": "张三",
  "email": "zhangsan@example.com", 
  "password": "secure_password123"
}
```

### 2. 用户登录

注册成功后，用户可以使用邮箱和密码登录：

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "zhangsan@example.com",
  "password": "secure_password123"
}
```

登录成功会返回JWT访问令牌：

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

### 3. 使用访问令牌

获取令牌后，在后续请求中添加Authorization头：

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API端点

### 认证相关

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/auth/register` | POST | 用户注册 | 否 |
| `/auth/login` | POST | 用户登录 | 否 |
| `/auth/me` | GET | 获取当前用户信息 | 是 |
| `/auth/me/detail` | GET | 获取当前用户详细信息 | 是 |
| `/auth/me` | PUT | 更新当前用户信息 | 是 |
| `/auth/change-password` | POST | 修改密码 | 是 |
| `/auth/user/{user_id}` | GET | 根据ID获取用户信息 | 是 |
| `/auth/verify-token` | POST | 验证令牌有效性 | 是 |

## 安全特性

### 密码安全

- 密码使用bcrypt哈希算法加密存储
- 最小密码长度：6个字符
- 最大密码长度：100个字符

### JWT令牌

- 使用HS256算法签名
- 默认过期时间：30分钟
- 包含用户ID和邮箱信息

### 数据验证

- 邮箱格式自动验证
- 用户名长度限制：1-50个字符
- 防止邮箱重复注册

## 错误处理

### 常见错误码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 400 | 请求参数错误 | 邮箱已被注册、密码格式错误 |
| 401 | 认证失败 | 用户名或密码错误、令牌无效 |
| 404 | 资源不存在 | 用户不存在 |

### 错误响应格式

```json
{
  "detail": "邮箱已被注册"
}
```

## 使用示例

### JavaScript/TypeScript

```javascript
// 用户登录
async function login(email, password) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    // 保存令牌
    localStorage.setItem('access_token', data.token.access_token);
    return data;
  } else {
    throw new Error('登录失败');
  }
}

// 获取用户信息
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/v1/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('获取用户信息失败');
  }
}
```

### Python

```python
import requests

# 用户登录
def login(email, password):
    response = requests.post('/api/v1/auth/login', json={
        'email': email,
        'password': password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data['token']['access_token']
    else:
        raise Exception('登录失败')

# 获取用户信息
def get_current_user(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('/api/v1/auth/me', headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('获取用户信息失败')
```

## 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| JWT_SECRET_KEY | dreamcatcher-secret-key-change-in-production | JWT签名密钥 |
| JWT_ALGORITHM | HS256 | JWT签名算法 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | 访问令牌过期时间（分钟） |

**注意**: 生产环境中必须修改JWT_SECRET_KEY为强密钥。

## 最佳实践

1. **令牌管理**：
   - 将访问令牌存储在安全的地方（如httpOnly cookie）
   - 定期检查令牌有效性
   - 令牌过期后重新登录

2. **密码安全**：
   - 使用强密码
   - 定期更换密码
   - 不要在代码中硬编码密码

3. **API调用**：
   - 始终使用HTTPS
   - 正确处理认证错误
   - 实现令牌刷新机制

## 故障排除

### 常见问题

1. **401 Unauthorized**
   - 检查令牌是否正确设置
   - 检查令牌是否过期
   - 确认Authorization头格式正确

2. **400 Bad Request**
   - 检查请求参数格式
   - 验证邮箱格式是否正确
   - 确认密码长度符合要求

3. **邮箱已被注册**
   - 尝试使用不同的邮箱地址
   - 如果是本人邮箱，直接登录

### 调试技巧

1. 使用API测试工具（如Postman）测试接口
2. 检查服务器日志获取详细错误信息
3. 验证数据库连接和表结构 