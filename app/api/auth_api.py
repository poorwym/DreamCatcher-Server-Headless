from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db import get_db
from app.schemas.auth_model import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    LoginRequest, LoginResponse, RegisterResponse, 
    PasswordChangeRequest, MessageResponse
)
from app.services.auth_service import (
    register_user, login_user, get_current_user as get_user_from_token,
    update_user, change_password, get_user_by_id
)

router = APIRouter(prefix="/auth", tags=["认证"])

# HTTP Bearer token 认证
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前认证用户"""
    token = credentials.credentials
    user = get_user_from_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", response_model=RegisterResponse, summary="用户注册")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **user_name**: 用户名（1-50个字符）
    - **email**: 邮箱地址
    - **password**: 密码（6-100个字符）
    """
    try:
        return register_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    
    返回用户信息和访问令牌
    """
    try:
        return login_user(db, login_request)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    获取当前登录用户的基本信息
    
    需要提供有效的Bearer token
    """
    return UserResponse(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        email=current_user.email
    )

@router.get("/me/detail", response_model=UserDetailResponse, summary="获取当前用户详细信息")
async def get_current_user_detail(current_user = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息（包含创建时间等）
    
    需要提供有效的Bearer token
    """
    return UserDetailResponse(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        email=current_user.email,
        created_at=getattr(current_user, 'created_at', None),
        updated_at=getattr(current_user, 'updated_at', None)
    )

@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    - **user_name**: 新用户名（可选）
    - **email**: 新邮箱地址（可选）
    - **password**: 新密码（可选，6-100个字符）
    
    需要提供有效的Bearer token
    """
    try:
        updated_user = update_user(db, current_user.user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return UserResponse(
            user_id=updated_user.user_id,
            user_name=updated_user.user_name,
            email=updated_user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-password", response_model=MessageResponse, summary="修改密码")
async def change_password_endpoint(
    password_change: PasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码（6-100个字符）
    
    需要提供有效的Bearer token
    """
    success = change_password(db, current_user.user_id, password_change)
    if not success:
        raise HTTPException(status_code=400, detail="原密码错误")
    
    return MessageResponse(message="密码修改成功", success=True)

@router.get("/user/{user_id}", response_model=UserResponse, summary="根据ID获取用户信息")
async def get_user_by_id_endpoint(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # 需要认证才能查看其他用户
):
    """
    根据用户ID获取用户基本信息
    
    需要提供有效的Bearer token
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email
    )

@router.post("/verify-token", response_model=UserResponse, summary="验证令牌")
async def verify_token(current_user = Depends(get_current_user)):
    """
    验证Bearer token是否有效
    
    如果token有效，返回用户信息
    """
    return UserResponse(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        email=current_user.email
    )


