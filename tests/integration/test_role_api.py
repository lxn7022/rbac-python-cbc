"""
角色和权限 API 集成测试
使用 Supabase REST API
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


class TestRoleAPI:
    """角色 API 测试类"""
    
    def test_get_roles(self, client: TestClient):
        """测试获取角色列表"""
        response = client.get("/api/v1/roles/")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_role_by_id(self, client: TestClient):
        """测试通过 ID 获取角色"""
        # 获取角色列表
        response = client.get("/api/v1/roles/")
        assert response.status_code == 200
        roles = response.json()
        
        if len(roles) > 0:
            role_id = roles[0]["id"]
            response = client.get(f"/api/v1/roles/{role_id}")
            assert response.status_code == 200


class TestPermissionAPI:
    """权限 API 测试类"""
    
    def test_get_permissions(self, client: TestClient):
        """测试获取权限列表"""
        response = client.get("/api/v1/permissions/")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_permissions_by_module(self, client: TestClient):
        """测试按模块获取权限"""
        response = client.get("/api/v1/permissions/?module=auth")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestRolePermissionAPI:
    """角色-权限关联 API 测试类"""
    
    def test_get_role_permissions(self, client: TestClient):
        """测试获取角色权限"""
        # 获取角色列表
        response = client.get("/api/v1/roles/")
        assert response.status_code == 200
        roles = response.json()
        
        if len(roles) > 0:
            role_id = roles[0]["id"]
            response = client.get(f"/api/v1/roles/{role_id}/permissions")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
