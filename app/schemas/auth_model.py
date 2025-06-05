from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

# 用户创建模型
class UserCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

# 用户更新模型
class UserUpdate(BaseModel):
    user_name: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")

# 用户响应模型 (不包含密码)
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: uuid.UUID = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")

# 用户详情响应模型 (包含创建时间等额外信息)
class UserDetailResponse(UserResponse):
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

# 登录请求模型
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")

# Token模型
class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")

# Token数据模型
class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = Field(None, description="用户ID")
    email: Optional[str] = Field(None, description="邮箱地址")

# 登录响应模型
class LoginResponse(BaseModel):
    user: UserResponse = Field(..., description="用户信息")
    token: Token = Field(..., description="令牌信息")
    message: str = Field(default="登录成功", description="响应消息")

# 注册响应模型
class RegisterResponse(BaseModel):
    user: UserResponse = Field(..., description="用户信息")
    message: str = Field(default="注册成功", description="响应消息")

# 密码修改请求模型
class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")

# 密码重置请求模型
class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")

# 密码重置确认模型
class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")

# 通用响应模型
class MessageResponse(BaseModel):
    message: str = Field(..., description="响应消息")
    success: bool = Field(default=True, description="操作是否成功")

# 验证邮箱请求模型
class EmailVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")

# 验证邮箱确认模型
class EmailVerificationConfirm(BaseModel):
    token: str = Field(..., description="验证令牌")

# 刷新Token请求模型
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")

# 刷新Token响应模型
class RefreshTokenResponse(BaseModel):
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
