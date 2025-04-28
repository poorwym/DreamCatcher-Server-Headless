import pytest
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from schemas.plan import PlanCreate, PlanUpdate, Camera
from services import plan_service
from models import Plan

def test_create_plan(db_session: Session):
    """测试创建拍摄计划"""
    # 准备测试数据
    camera_data = Camera(
        focal_length=35.0,
        position=(30.2741, 120.1551, 100.0),
        rotation=(0.0, 0.0, 0.0, 1.0)
    )
    
    plan_data = PlanCreate(
        name="测试计划",
        description="测试描述",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/tileset.json",
        user_id="test_user_123"
    )
    
    # 执行测试
    result = plan_service.create_plan(db=db_session, plan=plan_data)
    
    # 验证结果
    assert result is not None
    assert result.name == "测试计划"
    assert result.description == "测试描述"
    assert result.tileset_url == "https://test.com/tileset.json"
    assert result.user_id == "test_user_123"
    assert result.camera["focal_length"] == 35.0
    assert result.camera["position"] == [30.2741, 120.1551, 100.0]
    assert result.camera["rotation"] == [0.0, 0.0, 0.0, 1.0]

def test_get_plan(db_session: Session):
    """测试获取单个拍摄计划"""
    # 先创建一个计划
    camera_data = Camera(
        focal_length=35.0,
        position=(30.2741, 120.1551, 100.0),
        rotation=(0.0, 0.0, 0.0, 1.0)
    )
    
    plan_data = PlanCreate(
        name="测试计划",
        description="测试描述",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/tileset.json",
        user_id="test_user_123"
    )
    
    created_plan = plan_service.create_plan(db=db_session, plan=plan_data)
    
    # 获取计划
    result = plan_service.get_plan(db=db_session, plan_id=created_plan.id)
    
    # 验证结果
    assert result is not None
    assert result.id == created_plan.id
    assert result.name == "测试计划"
    assert result.description == "测试描述"

def test_get_nonexistent_plan(db_session: Session):
    """测试获取不存在的拍摄计划"""
    # 生成一个不存在的ID
    non_existent_id = uuid.uuid4()
    
    # 尝试获取不存在的计划
    result = plan_service.get_plan(db=db_session, plan_id=non_existent_id)
    
    # 验证结果
    assert result is None

def test_get_plans_by_user(db_session: Session):
    """测试获取用户的所有拍摄计划"""
    # 创建测试数据
    camera_data = Camera(
        focal_length=35.0,
        position=(30.2741, 120.1551, 100.0),
        rotation=(0.0, 0.0, 0.0, 1.0)
    )
    
    # 为同一用户创建两个计划
    user_id = "test_user_456"
    
    plan_data1 = PlanCreate(
        name="测试计划1",
        description="测试描述1",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/tileset1.json",
        user_id=user_id
    )
    
    plan_data2 = PlanCreate(
        name="测试计划2",
        description="测试描述2",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/tileset2.json",
        user_id=user_id
    )
    
    # 为另一用户创建一个计划
    plan_data3 = PlanCreate(
        name="其他用户计划",
        description="其他用户的计划",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/tileset3.json",
        user_id="another_user"
    )
    
    # 创建计划
    plan_service.create_plan(db=db_session, plan=plan_data1)
    plan_service.create_plan(db=db_session, plan=plan_data2)
    plan_service.create_plan(db=db_session, plan=plan_data3)
    
    # 获取特定用户的计划
    results = plan_service.get_plans_by_user(db=db_session, user_id=user_id)
    
    # 验证结果
    assert len(results) == 2
    assert all(plan.user_id == user_id for plan in results)
    assert any(plan.name == "测试计划1" for plan in results)
    assert any(plan.name == "测试计划2" for plan in results)

def test_update_plan(db_session: Session):
    """测试更新拍摄计划"""
    # 先创建一个计划
    camera_data = Camera(
        focal_length=35.0,
        position=(30.2741, 120.1551, 100.0),
        rotation=(0.0, 0.0, 0.0, 1.0)
    )
    
    plan_data = PlanCreate(
        name="原始计划名",
        description="原始描述",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/original.json",
        user_id="test_user_123"
    )
    
    created_plan = plan_service.create_plan(db=db_session, plan=plan_data)
    
    # 创建更新数据
    new_camera = Camera(
        focal_length=50.0,
        position=(30.2742, 120.1552, 120.0),
        rotation=(0.1, 0.0, 0.0, 0.9)
    )
    
    update_data = PlanUpdate(
        name="更新后的计划名",
        description="更新后的描述",
        start_time=datetime.utcnow(),
        camera=new_camera,
        tileset_url="https://test.com/updated.json",
        user_id="test_user_123"
    )
    
    # 执行更新
    updated_plan = plan_service.update_plan(db=db_session, plan_id=created_plan.id, plan=update_data)
    
    # 验证结果
    assert updated_plan is not None
    assert updated_plan.id == created_plan.id
    assert updated_plan.name == "更新后的计划名"
    assert updated_plan.description == "更新后的描述"
    assert updated_plan.tileset_url == "https://test.com/updated.json"
    assert updated_plan.camera["focal_length"] == 50.0
    assert updated_plan.camera["position"] == [30.2742, 120.1552, 120.0]
    assert updated_plan.camera["rotation"] == [0.1, 0.0, 0.0, 0.9]

def test_update_nonexistent_plan(db_session: Session):
    """测试更新不存在的拍摄计划"""
    # 生成一个不存在的ID
    non_existent_id = uuid.uuid4()
    
    # 创建更新数据
    camera_data = Camera(
        focal_length=50.0,
        position=(30.2742, 120.1552, 120.0),
        rotation=(0.1, 0.0, 0.0, 0.9)
    )
    
    update_data = PlanUpdate(
        name="更新名称",
        description="更新描述",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/updated.json",
        user_id="test_user_123"
    )
    
    # 尝试更新不存在的计划
    result = plan_service.update_plan(db=db_session, plan_id=non_existent_id, plan=update_data)
    
    # 验证结果
    assert result is None

def test_delete_plan(db_session: Session):
    """测试删除拍摄计划"""
    # 先创建一个计划
    camera_data = Camera(
        focal_length=35.0,
        position=(30.2741, 120.1551, 100.0),
        rotation=(0.0, 0.0, 0.0, 1.0)
    )
    
    plan_data = PlanCreate(
        name="待删除计划",
        description="待删除描述",
        start_time=datetime.utcnow(),
        camera=camera_data,
        tileset_url="https://test.com/delete.json",
        user_id="test_user_123"
    )
    
    created_plan = plan_service.create_plan(db=db_session, plan=plan_data)
    
    # 删除计划
    result = plan_service.delete_plan(db=db_session, plan_id=created_plan.id)
    
    # 验证删除成功
    assert result is True
    
    # 验证计划已被删除
    check_plan = plan_service.get_plan(db=db_session, plan_id=created_plan.id)
    assert check_plan is None

def test_delete_nonexistent_plan(db_session: Session):
    """测试删除不存在的拍摄计划"""
    # 生成一个不存在的ID
    non_existent_id = uuid.uuid4()
    
    # 尝试删除不存在的计划
    result = plan_service.delete_plan(db=db_session, plan_id=non_existent_id)
    
    # 验证结果
    assert result is False 