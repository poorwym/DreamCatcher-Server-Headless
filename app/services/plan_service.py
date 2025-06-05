from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.models import Plan as PlanModel
from app.schemas.plan_model import PlanCreate, PlanUpdate, Plan

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
    db_plan = PlanModel(
        name=plan.name,
        description=plan.description,
        start_time=plan.start_time,
        camera=plan.camera.model_dump(),
        tileset_url=plan.tileset_url,
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
    
    # 特殊处理camera字段，因为它是嵌套对象
    if "camera" in update_data and update_data["camera"]:
        update_data["camera"] = update_data["camera"].model_dump()
    
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