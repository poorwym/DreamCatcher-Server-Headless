from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from uuid import UUID
import uuid

from app.models import User as UserModel
from app.schemas.auth_model import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse, 
    LoginRequest, LoginResponse, RegisterResponse, Token, TokenData,
    PasswordChangeRequest, MessageResponse
)

# JWT配置
SECRET_KEY = "dreamcatcher-secret-key-change-in-production"  # 生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            return None
        token_data = TokenData(user_id=UUID(user_id), email=email)
        return token_data
    except JWTError:
        return None

def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserModel]:
    """根据用户ID获取用户"""
    return db.query(UserModel).filter(UserModel.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """根据邮箱获取用户"""
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    """验证用户登录"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_user(db: Session, user: UserCreate) -> UserModel:
    """创建新用户"""
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, str(user.email))
    if db_user:
        raise ValueError("邮箱已被注册")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        user_name=user.user_name,
        email=str(user.email),
        password=hashed_password,
        user_id=uuid.uuid4()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[UserModel]:
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # 如果更新邮箱，检查是否已存在
    if "email" in update_data:
        existing_user = get_user_by_email(db, update_data["email"])
        if existing_user and existing_user.user_id != user_id:
            raise ValueError("邮箱已被其他用户使用")
    
    # 如果更新密码，进行哈希处理
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def change_password(db: Session, user_id: UUID, password_change: PasswordChangeRequest) -> bool:
    """修改密码"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    # 验证原密码
    if not verify_password(password_change.old_password, db_user.password):
        return False
    
    # 更新密码
    db_user.password = get_password_hash(password_change.new_password)
    db.commit()
    return True

def register_user(db: Session, user_create: UserCreate) -> RegisterResponse:
    """用户注册"""
    try:
        db_user = create_user(db, user_create)
        user_response = UserResponse(
            user_id=db_user.user_id,
            user_name=db_user.user_name,
            email=db_user.email
        )
        return RegisterResponse(user=user_response, message="注册成功")
    except ValueError as e:
        raise e

def login_user(db: Session, login_request: LoginRequest) -> LoginResponse:
    """用户登录"""
    user = authenticate_user(db, str(login_request.email), login_request.password)
    if not user:
        raise ValueError("邮箱或密码错误")
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email}, 
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email
    )
    
    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return LoginResponse(user=user_response, token=token, message="登录成功")

def get_current_user(db: Session, token: str) -> Optional[UserModel]:
    """根据JWT令牌获取当前用户"""
    token_data = verify_token(token)
    if token_data is None:
        return None
    
    user = get_user_by_id(db, token_data.user_id)
    return user
