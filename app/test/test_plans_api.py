import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
import uuid

def test_create_plan_api(client):
    """测试创建拍摄计划API"""
    # 准备测试数据
    plan_data = {
        "name": "API测试计划",
        "description": "通过API创建的计划",
        "start_time": datetime.utcnow().isoformat(),
        "camera": {
            "focal_length": 35.0,
            "position": [30.2741, 120.1551, 100.0],
            "rotation": [0.0, 0.0, 0.0, 1.0]
        },
        "tileset_url": "https://test.com/api_tileset.json",
        "user_id": "api_test_user"
    }
    
    # 发送请求
    response = client.post("/api/v1/plans/", json=plan_data)
    
    # 验证结果
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API测试计划"
    assert data["description"] == "通过API创建的计划"
    assert data["tileset_url"] == "https://test.com/api_tileset.json"
    assert data["user_id"] == "api_test_user"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_plan_invalid_data(client):
    """测试创建拍摄计划API - 无效数据"""
    # 准备缺少必要字段的测试数据
    plan_data = {
        "name": "无效计划",
        # 缺少start_time
        "camera": {
            "focal_length": 35.0,
            "position": [30.2741, 120.1551, 100.0],
            # 缺少rotation
        },
        # 缺少tileset_url
        "user_id": "api_test_user"
    }
    
    # 发送请求
    response = client.post("/api/v1/plans/", json=plan_data)
    
    # 验证结果
    assert response.status_code == 422  # Unprocessable Entity

def test_get_user_plans(client):
    """测试获取用户拍摄计划API"""
    # 先创建一些测试计划
    user_id = "test_api_user_456"
    
    for i in range(3):
        plan_data = {
            "name": f"用户计划{i+1}",
            "description": f"用户{user_id}的计划{i+1}",
            "start_time": datetime.utcnow().isoformat(),
            "camera": {
                "focal_length": 35.0,
                "position": [30.2741, 120.1551, 100.0],
                "rotation": [0.0, 0.0, 0.0, 1.0]
            },
            "tileset_url": f"https://test.com/user_tileset{i+1}.json",
            "user_id": user_id
        }
        client.post("/api/v1/plans/", json=plan_data)
    
    # 为另一用户创建一个计划
    other_plan_data = {
        "name": "其他用户计划",
        "description": "其他用户的计划",
        "start_time": datetime.utcnow().isoformat(),
        "camera": {
            "focal_length": 35.0,
            "position": [30.2741, 120.1551, 100.0],
            "rotation": [0.0, 0.0, 0.0, 1.0]
        },
        "tileset_url": "https://test.com/other_tileset.json",
        "user_id": "other_user"
    }
    client.post("/api/v1/plans/", json=other_plan_data)
    
    # 获取特定用户的计划
    response = client.get(f"/api/v1/plans?user_id={user_id}")
    
    # 验证结果
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(plan["user_id"] == user_id for plan in data)

def test_get_plan_by_id(client):
    """测试通过ID获取拍摄计划API"""
    # 先创建一个计划
    plan_data = {
        "name": "ID查询计划",
        "description": "通过ID查询的计划",
        "start_time": datetime.utcnow().isoformat(),
        "camera": {
            "focal_length": 35.0,
            "position": [30.2741, 120.1551, 100.0],
            "rotation": [0.0, 0.0, 0.0, 1.0]
        },
        "tileset_url": "https://test.com/id_query.json",
        "user_id": "id_query_user"
    }
    
    create_response = client.post("/api/v1/plans/", json=plan_data)
    created_plan = create_response.json()
    plan_id = created_plan["id"]
    
    # 通过ID获取计划
    response = client.get(f"/api/v1/plans/{plan_id}")
    
    # 验证结果
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan_id
    assert data["name"] == "ID查询计划"
    assert data["description"] == "通过ID查询的计划"

def test_get_nonexistent_plan_by_id(client):
    """测试通过不存在的ID获取拍摄计划API"""
    # 生成一个不存在的ID
    non_existent_id = str(uuid.uuid4())
    
    # 尝试获取不存在的计划
    response = client.get(f"/api/v1/plans/{non_existent_id}")
    
    # 验证结果
    assert response.status_code == 404

def test_update_plan(client):
    """测试更新拍摄计划API"""
    # 先创建一个计划
    plan_data = {
        "name": "待更新计划",
        "description": "待更新的计划描述",
        "start_time": datetime.utcnow().isoformat(),
        "camera": {
            "focal_length": 35.0,
            "position": [30.2741, 120.1551, 100.0],
            "rotation": [0.0, 0.0, 0.0, 1.0]
        },
        "tileset_url": "https://test.com/update_test.json",
        "user_id": "update_test_user"
    }
    
    create_response = client.post("/api/v1/plans/", json=plan_data)
    created_plan = create_response.json()
    plan_id = created_plan["id"]
    
    # 准备更新数据
    update_data = {
        "name": "已更新计划",
        "description": "已更新的计划描述",
        "camera": {
            "focal_length": 50.0,
            "position": [30.2742, 120.1552, 120.0],
            "rotation": [0.1, 0.0, 0.0, 0.9]
        },
        "tileset_url": "https://test.com/updated_test.json",
        "user_id": "update_test_user"
    }
    
    # 发送更新请求
    response = client.patch(f"/api/v1/plans/{plan_id}", json=update_data)
    
    # 验证结果
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan_id
    assert data["name"] == "已更新计划"
    assert data["description"] == "已更新的计划描述"
    assert data["tileset_url"] == "https://test.com/updated_test.json"
    assert data["camera"]["focal_length"] == 50.0
    assert data["camera"]["position"] == [30.2742, 120.1552, 120.0]
    assert data["camera"]["rotation"] == [0.1, 0.0, 0.0, 0.9]

def test_update_nonexistent_plan(client):
    """测试更新不存在的拍摄计划API"""
    # 生成一个不存在的ID
    non_existent_id = str(uuid.uuid4())
    
    # 准备更新数据
    update_data = {
        "name": "不存在的计划",
        "description": "尝试更新不存在的计划",
        "camera": {
            "focal_length": 50.0,
            "position": [30.2742, 120.1552, 120.0],
            "rotation": [0.1, 0.0, 0.0, 0.9]
        }
    }
    
    # 尝试更新不存在的计划
    response = client.patch(f"/api/v1/plans/{non_existent_id}", json=update_data)
    
    # 验证结果
    assert response.status_code == 404

def test_delete_plan(client):
    """测试删除拍摄计划API"""
    # 先创建一个计划
    plan_data = {
        "name": "待删除计划",
        "description": "即将被删除的计划",
        "start_time": datetime.utcnow().isoformat(),
        "camera": {
            "focal_length": 35.0,
            "position": [30.2741, 120.1551, 100.0],
            "rotation": [0.0, 0.0, 0.0, 1.0]
        },
        "tileset_url": "https://test.com/delete_test.json",
        "user_id": "delete_test_user"
    }
    
    create_response = client.post("/api/v1/plans/", json=plan_data)
    created_plan = create_response.json()
    plan_id = created_plan["id"]
    
    # 删除计划
    response = client.delete(f"/api/v1/plans/{plan_id}")
    
    # 验证结果
    assert response.status_code == 204
    
    # 尝试再次获取已删除的计划
    get_response = client.get(f"/api/v1/plans/{plan_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_plan(client):
    """测试删除不存在的拍摄计划API"""
    # 生成一个不存在的ID
    non_existent_id = str(uuid.uuid4())
    
    # 尝试删除不存在的计划
    response = client.delete(f"/api/v1/plans/{non_existent_id}")
    
    # 验证结果
    assert response.status_code == 404 