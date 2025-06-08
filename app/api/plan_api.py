from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.plan_model import Plan, PlanCreate, PlanUpdate
from app.services import plan_service
from app.db import get_db
from app.api.auth_api import get_current_user
from app.models import User

router = APIRouter(prefix="/plans", tags=["拍摄计划"])

@router.get("/{plan_id}", response_model=Plan, summary="获取指定拍摄计划")
def get_plan(
    plan_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定ID的拍摄计划
    
    只能获取当前用户创建的计划
    """
    plan = plan_service.get_plan(db, plan_id, current_user.user_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="计划未找到或无权访问")
    return plan

@router.get("/", response_model=List[Plan], summary="获取拍摄计划列表")
def get_plans(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的拍摄计划列表
    
    支持分页，只返回当前用户创建的计划
    """
    plans = plan_service.get_plans(db, user_id=current_user.user_id, skip=skip, limit=limit)
    return plans

@router.post("/", response_model=Plan, status_code=status.HTTP_201_CREATED, summary="创建拍摄计划")
def create_plan(
    plan: PlanCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的拍摄计划
    
    计划将自动关联到当前用户，开始时间不能是过去的时间
    """
    # 确保计划关联到当前用户
    plan.user_id = current_user.user_id
    
    try:
        return plan_service.create_plan(db=db, plan=plan)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.patch("/{plan_id}", response_model=Plan, summary="更新拍摄计划")
def update_plan(
    plan_id: UUID, 
    plan: PlanUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新指定ID的拍摄计划
    
    只能更新当前用户创建的计划，如果更新开始时间，不能设置为过去的时间
    """
    try:
        updated_plan = plan_service.update_plan(
            db=db, 
            plan_id=plan_id, 
            plan=plan, 
            user_id=current_user.user_id
        )
        if updated_plan is None:
            raise HTTPException(status_code=404, detail="计划未找到或无权访问")
        return updated_plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除拍摄计划")
def delete_plan(
    plan_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除指定ID的拍摄计划
    
    只能删除当前用户创建的计划
    """
    deleted = plan_service.delete_plan(
        db=db, 
        plan_id=plan_id, 
        user_id=current_user.user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="计划未找到或无权访问")
    return

# 管理员专用端点：获取所有用户的计划（可选实现）
@router.get("/admin/all", response_model=List[Plan], summary="管理员获取所有计划")
def get_all_plans(
    user_id: Optional[UUID] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    管理员专用：获取所有用户的计划列表
    
    可以通过user_id筛选特定用户的计划
    注意：此端点需要管理员权限（暂未实现权限检查）
    """
    # TODO: 添加管理员权限检查
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    plans = plan_service.get_plans(db, user_id=user_id, skip=skip, limit=limit)
    return plans 