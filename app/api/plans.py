from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from schemas.plan import Plan, PlanCreate, PlanUpdate
from services import plan_service
from db import get_db

router = APIRouter(prefix="/plans", tags=["plans"])

@router.get("/{plan_id}", response_model=Plan)
def get_plan(plan_id: UUID, db: Session = Depends(get_db)):
    """获取指定ID的拍摄计划"""
    plan = plan_service.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="计划未找到")
    return plan

@router.get("/", response_model=List[Plan])
def get_plans(
    user_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取拍摄计划列表
    
    可以通过user_id筛选特定用户的计划，支持分页
    """
    plans = plan_service.get_plans(db, user_id=user_id, skip=skip, limit=limit)
    return plans

@router.post("/", response_model=Plan, status_code=status.HTTP_201_CREATED)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    """创建新的拍摄计划"""
    return plan_service.create_plan(db=db, plan=plan)

@router.patch("/{plan_id}", response_model=Plan)
def update_plan(plan_id: UUID, plan: PlanUpdate, db: Session = Depends(get_db)):
    """更新指定ID的拍摄计划"""
    updated_plan = plan_service.update_plan(db=db, plan_id=plan_id, plan=plan)
    if updated_plan is None:
        raise HTTPException(status_code=404, detail="计划未找到")
    return updated_plan

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: UUID, db: Session = Depends(get_db)):
    """删除指定ID的拍摄计划"""
    deleted = plan_service.delete_plan(db=db, plan_id=plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="计划未找到")
    return 