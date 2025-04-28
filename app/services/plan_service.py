from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from models import Plan as PlanModel
from schemas.plan import PlanCreate, PlanUpdate, Plan

def get_plan(db: Session, plan_id: UUID) -> Optional[Plan]:
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    return plan

def get_plans(db: Session, user_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Plan]:
    query = db.query(PlanModel)
    
    # 如果提供了user_id，则按用户筛选
    if user_id:
        query = query.filter(PlanModel.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

# 保留这个函数用于向后兼容，但它实际上只是调用新的get_plans函数
def get_plans_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Plan]:
    return get_plans(db, user_id=user_id, skip=skip, limit=limit)

def create_plan(db: Session, plan: PlanCreate) -> Plan:
    db_plan = PlanModel(
        name=plan.name,
        description=plan.description,
        start_time=plan.start_time,
        camera=plan.camera.dict(),
        tileset_url=plan.tileset_url,
        user_id=plan.user_id
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: UUID, plan: PlanUpdate) -> Optional[Plan]:
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return None
    
    update_data = plan.dict(exclude_unset=True)
    
    # 特殊处理camera字段，因为它是嵌套对象
    # if "camera" in update_data and update_data["camera"]:
    #    update_data["camera"] = update_data["camera"].model_dump()
    
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db_plan.updated_at = datetime.now()
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: UUID) -> bool:
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return False
    
    db.delete(db_plan)
    db.commit()
    return True 