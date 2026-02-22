"""
RBAC 管理器单元测试
使用 Supabase REST API
"""

import pytest
from datetime import datetime, timedelta
from src.core.rbac.manager import rbac_manager
from src.db.supabase_client import supabase_db


class TestRBACManager:
    """RBAC 管理器测试类"""
    
    created_user_ids = []
    created_role_ids = []
    created_permission_ids = []
    
    def teardown_method(self):
        """测试后清理"""
        # 清理创建的数据
        for user_id in self.created_user_ids:
            try:
                supabase_db.delete_user(user_id)
            except:
                pass
        for role_id in self.created_role_ids:
            try:
                supabase_db.delete_role(role_id)
            except:
                pass
        self.created_user_ids = []
        self.created_role_ids = []
        self.created_permission_ids = []
    
    def _create_test_user(self) -> dict:
        """创建测试用户"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        user_data = {
            "username": f"test_user_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password_hash": "hashed_password",
            "full_name": "测试用户",
            "is_active": True
        }
        user = supabase_db.create_user(user_data)
        self.created_user_ids.append(user["id"])
        return user
    
    def _create_test_role(self, name: str = None) -> dict:
        """创建测试角色"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        name = name or f"测试角色_{timestamp}"
        role_data = {
            "name": name,
            "slug": f"test-role-{timestamp}",
            "description": f"测试角色 - {name}",
            "priority": 50,
            "is_system": False
        }
        role = supabase_db.create_role(role_data)
        self.created_role_ids.append(role["id"])
        return role
    
    def _create_test_permission(self, resource: str = None, action: str = None) -> dict:
        """创建测试权限"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        resource = resource or f"test_resource_{timestamp}"
        action = action or f"test_action_{timestamp}"
        permission_data = {
            "resource": resource,
            "action": action,
            "description": f"测试权限 - {resource}:{action}",
            "module": "test",
            "is_system": False
        }
        permission = supabase_db.create_permission(permission_data)
        self.created_permission_ids.append(permission["id"])
        return permission
    
    def test_has_role_true(self):
        """测试检查用户角色 - 存在"""
        # 创建测试数据
        user = self._create_test_user()
        role = self._create_test_role("测试角色_has_role_true")
        
        # 分配角色
        supabase_db.assign_role_to_user(user["id"], role["id"])
        
        # 测试
        result = rbac_manager.has_role(user["id"], role["slug"])
        assert result is True
    
    def test_has_role_false(self):
        """测试检查用户角色 - 不存在"""
        # 创建测试数据
        user = self._create_test_user()
        role = self._create_test_role("测试角色_has_role_false")
        
        # 不分配角色
        
        # 测试
        result = rbac_manager.has_role(user["id"], role["slug"])
        assert result is False
    
    def test_has_permission_true(self):
        """测试检查用户权限 - 存在"""
        # 创建测试数据
        user = self._create_test_user()
        role = self._create_test_role("测试角色_has_permission")
        permission = self._create_test_permission("test_resource", "test_action")
        
        # 分配角色和权限
        supabase_db.grant_permission_to_role(role["id"], permission["id"])
        supabase_db.assign_role_to_user(user["id"], role["id"])
        
        # 测试
        result = rbac_manager.has_permission(
            user["id"], permission["resource"], permission["action"]
        )
        assert result is True
    
    def test_has_permission_false(self):
        """测试检查用户权限 - 不存在"""
        # 创建测试数据
        user = self._create_test_user()
        # 不分配任何权限
        
        # 测试
        result = rbac_manager.has_permission(user["id"], "nonexistent", "read")
        assert result is False
    
    def test_assign_role(self):
        """测试分配角色"""
        # 创建测试数据
        user = self._create_test_user()
        role = self._create_test_role("测试角色_assign")
        
        # 分配角色
        user_role = rbac_manager.assign_role(user["id"], role["id"])
        
        # 验证
        assert user_role["user_id"] == user["id"]
        assert user_role["role_id"] == role["id"]
        assert user_role["is_active"] is True
    
    def test_revoke_role(self):
        """测试撤销角色"""
        # 创建测试数据
        user = self._create_test_user()
        role = self._create_test_role("测试角色_revoke")
        
        # 先分配角色
        supabase_db.assign_role_to_user(user["id"], role["id"])
        
        # 撤销角色
        result = rbac_manager.revoke_role(user["id"], role["id"])
        
        # 验证
        assert result is True
        
        # 验证角色已被撤销
        user_roles = supabase_db.get_user_roles(user["id"])
        active_roles = [ur for ur in user_roles if ur.get("is_active")]
        assert len(active_roles) == 0
    
    def test_grant_permission(self):
        """测试授予权限"""
        # 创建测试数据
        role = self._create_test_role("测试角色_grant_perm")
        permission = self._create_test_permission("grant_test", "action")
        
        # 授予权限
        role_permission = rbac_manager.grant_permission(role["id"], permission["id"])
        
        # 验证
        assert role_permission["role_id"] == role["id"]
        assert role_permission["permission_id"] == permission["id"]
        assert role_permission["is_active"] is True
    
    def test_get_all_permissions(self):
        """测试获取用户所有权限"""
        # 创建测试数据
        user = self._create_test_user()
        role = self._create_test_role("测试角色_get_perms")
        permission1 = self._create_test_permission("resource1", "action1")
        permission2 = self._create_test_permission("resource2", "action2")
        
        # 分配角色和权限
        supabase_db.grant_permission_to_role(role["id"], permission1["id"])
        supabase_db.grant_permission_to_role(role["id"], permission2["id"])
        supabase_db.assign_role_to_user(user["id"], role["id"])
        
        # 获取权限
        permissions = rbac_manager.get_all_permissions(user["id"])
        
        # 验证
        assert f"{permission1['resource']}:{permission1['action']}" in permissions
        assert f"{permission2['resource']}:{permission2['action']}" in permissions
