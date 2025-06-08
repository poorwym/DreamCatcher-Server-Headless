from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID

from app.models import Plan as PlanModel
from app.schemas.plan_model import PlanCreate, PlanUpdate, Plan

def _validate_start_time(start_time: datetime) -> None:
    """验证开始时间不能是过去的时间"""
    now = datetime.now(timezone.utc)
    
    # 如果start_time没有时区信息，假设它是UTC时间
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    
    if start_time <= now:
        raise ValueError("计划开始时间不能是过去的时间，计划将立即过期")

def is_plan_expired(plan: Plan) -> bool:
    """检查计划是否已过期"""
    if not plan or not plan.start_time:
        return False
    
    now = datetime.now(timezone.utc)
    
    # 如果plan.start_time没有时区信息，假设它是UTC时间
    start_time = plan.start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    
    return start_time <= now

def get_plan(db: Session, plan_id: UUID, user_id: Optional[UUID] = None) -> Optional[Plan]:
    """获取单个计划，可选择性检查用户权限"""
    query = db.query(PlanModel).filter(PlanModel.id == plan_id)
    
    # 如果提供了user_id，则只返回该用户的计划
    if user_id:
        query = query.filter(PlanModel.user_id == user_id)
    
    return query.first()

def get_plans(db: Session, user_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Plan]:
    """获取计划列表，支持按用户筛选"""
    query = db.query(PlanModel)
    
    # 如果提供了user_id，则按用户筛选
    if user_id:
        query = query.filter(PlanModel.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

# 保留这个函数用于向后兼容，但它实际上只是调用新的get_plans函数
def get_plans_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Plan]:
    """根据用户ID获取该用户的所有计划"""
    return get_plans(db, user_id=user_id, skip=skip, limit=limit)

def create_plan(db: Session, plan: PlanCreate) -> Plan:
    """创建新计划"""
    # 验证开始时间
    _validate_start_time(plan.start_time)
    
    db_plan = PlanModel(
        name=plan.name,
        description=plan.description,
        start_time=plan.start_time,
        camera=plan.camera.model_dump(),
        tileset_url= plan.tileset_url,
        user_id=plan.user_id
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: UUID, plan: PlanUpdate, user_id: UUID) -> Optional[Plan]:
    """更新计划，仅允许计划所有者更新"""
    # 首先检查计划是否存在且属于当前用户
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return None
    
    update_data = plan.model_dump(exclude_unset=True)
    
    # 移除user_id，防止恶意修改
    update_data.pop('user_id', None)
    
    # 验证开始时间（如果有更新）
    if "start_time" in update_data and update_data["start_time"]:
        _validate_start_time(update_data["start_time"])
    
    # 特殊处理camera字段，因为它是嵌套对象
    if "camera" in update_data and update_data["camera"]:
        # 如果 camera 是 Pydantic 模型对象，转换为字典
        if hasattr(update_data["camera"], 'model_dump'):
            update_data["camera"] = update_data["camera"].model_dump()
        # 如果已经是字典，保持不变
        # 如果是 JSON 字符串，SQLAlchemy 会自动处理

    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db_plan.updated_at = datetime.now()
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: UUID, user_id: UUID) -> bool:
    """删除计划，仅允许计划所有者删除"""
    # 首先检查计划是否存在且属于当前用户
    db_plan = get_plan(db, plan_id, user_id)
    if not db_plan:
        return False
    
    db.delete(db_plan)
    db.commit()
    return True

def check_plan_owner(db: Session, plan_id: UUID, user_id: UUID) -> bool:
    """检查计划是否属于指定用户"""
    plan = db.query(PlanModel).filter(
        PlanModel.id == plan_id,
        PlanModel.user_id == user_id
    ).first()
    return plan is not None

def get_plan_with_status(db: Session, plan_id: UUID, user_id: Optional[UUID] = None) -> Optional[dict]:
    """获取计划并包含过期状态信息"""
    plan = get_plan(db, plan_id, user_id)
    if not plan:
        return None
    
    return {
        "plan": plan,
        "is_expired": is_plan_expired(plan)
    }

# 使用示例:
# 
# 1. 创建计划时，如果start_time是过去的时间，会抛出ValueError:
#    try:
#        plan = PlanCreate(name="Test", start_time=datetime(2020, 1, 1), ...)
#        created_plan = create_plan(db, plan)
#    except ValueError as e:
#        print(f"创建失败: {e}")  # 输出: 创建失败: 计划开始时间不能是过去的时间，计划将立即过期
#
# 2. 更新计划时，同样会验证start_time:
#    try:
#        plan_update = PlanUpdate(start_time=datetime(2020, 1, 1))
#        updated_plan = update_plan(db, plan_id, plan_update, user_id)
#    except ValueError as e:
#        print(f"更新失败: {e}")
#
# 3. 检查计划是否过期:
#    plan_info = get_plan_with_status(db, plan_id, user_id)
#    if plan_info and plan_info["is_expired"]:
#        print("计划已过期")
#    else:
#        print("计划仍然有效") 