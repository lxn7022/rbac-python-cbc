"""
角色继承单元测试（RBAC1）
使用 Supabase REST API
"""

import pytest
from datetime import datetime
from src.core.rbac.manager import rbac_manager
from src.db.supabase_client import supabase_db


class TestRoleInheritance:
    """角色继承测试类"""
    
    created_user_ids = []
    created_role_ids = []
    created_permission_ids = []
    
    def teardown_method(self):
        """测试后清理"""
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
    
    def _create_test_role(self, name: str, slug: str, priority: int = 50, parent_id: int = None) -> dict:
        """创建测试角色"""
        role_data = {
            "name": name,
            "slug": slug,
            "description": f"测试角色 - {name}",
            "priority": priority,
            "parent_id": parent_id,
            "is_system": False
        }
        role = supabase_db.create_role(role_data)
        self.created_role_ids.append(role["id"])
        return role
    
    def _create_test_permission(self, resource: str, action: str) -> dict:
        """创建测试权限"""
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
    
    def test_role_hierarchy(self):
        """测试角色层级结构"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 创建角色层级
        super_admin = self._create_test_role(
            "超级管理员", f"super-admin-{timestamp}", priority=100
        )
        admin = self._create_test_role(
            "管理员", f"admin-{timestamp}", priority=80, parent_id=super_admin["id"]
        )
        editor = self._create_test_role(
            "编辑", f"editor-{timestamp}", priority=60, parent_id=admin["id"]
        )
        user_role = self._create_test_role(
            "普通用户", f"user-{timestamp}", priority=40, parent_id=editor["id"]
        )
        
        # 验证继承关系
        assert admin["parent_id"] == super_admin["id"]
        assert editor["parent_id"] == admin["id"]
        assert user_role["parent_id"] == editor["id"]
    
    def test_inherited_permissions(self):
        """测试继承权限"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 创建角色层级
        parent_role = self._create_test_role(
            "管理员", f"admin-inherit-{timestamp}", priority=80
        )
        child_role = self._create_test_role(
            "编辑", f"editor-inherit-{timestamp}", priority=60, parent_id=parent_role["id"]
        )
        
        # 为父角色授予权限
        permission1 = self._create_test_permission("user", "read")
        permission2 = self._create_test_permission("article", "write")
        supabase_db.grant_permission_to_role(parent_role["id"], permission1["id"])
        supabase_db.grant_permission_to_role(parent_role["id"], permission2["id"])
        
        # 为子角色授予权限
        permission3 = self._create_test_permission("article", "delete")
        supabase_db.grant_permission_to_role(child_role["id"], permission3["id"])
        
        # 创建用户并分配子角色
        user = self._create_test_user()
        supabase_db.assign_role_to_user(user["id"], child_role["id"])
        
        # 获取用户权限（应该包含继承的权限）
        permissions = rbac_manager.get_all_permissions(user["id"], include_inherited=True)
        
        # 验证权限
        assert "user:read" in permissions  # 从父角色继承
        assert "article:write" in permissions  # 从父角色继承
        assert "article:delete" in permissions  # 子角色自己的权限
    
    def test_no_inheritance_disabled(self):
        """测试禁用继承的情况"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 创建角色层级
        parent_role = self._create_test_role(
            "管理员", f"admin-no-inherit-{timestamp}", priority=80
        )
        child_role = self._create_test_role(
            "编辑", f"editor-no-inherit-{timestamp}", priority=60, parent_id=parent_role["id"]
        )
        
        # 为父角色授予权限
        permission = self._create_test_permission("user", "read-no-inherit")
        supabase_db.grant_permission_to_role(parent_role["id"], permission["id"])
        
        # 创建用户并分配子角色
        user = self._create_test_user()
        supabase_db.assign_role_to_user(user["id"], child_role["id"])
        
        # 获取用户权限（不包含继承的权限）
        permissions = rbac_manager.get_all_permissions(user["id"], include_inherited=False)
        
        # 验证权限（应该只有子角色自己的权限）
        assert "user:read-no-inherit" not in permissions  # 不应该包含父角色权限
    
    def test_multi_level_inheritance(self):
        """测试多级继承"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 创建角色层级：超级管理员 > 管理员 > 编辑 > 用户
        super_admin = self._create_test_role(
            "超级管理员", f"super-admin-multi-{timestamp}", priority=100
        )
        admin = self._create_test_role(
            "管理员", f"admin-multi-{timestamp}", priority=80, parent_id=super_admin["id"]
        )
        editor = self._create_test_role(
            "编辑", f"editor-multi-{timestamp}", priority=60, parent_id=admin["id"]
        )
        user_role = self._create_test_role(
            "普通用户", f"user-multi-{timestamp}", priority=40, parent_id=editor["id"]
        )
        
        # 为每个角色授予权限
        perm1 = self._create_test_permission("super", "read")
        perm2 = self._create_test_permission("admin", "read")
        perm3 = self._create_test_permission("editor", "read")
        perm4 = self._create_test_permission("user-multi", "read")
        
        supabase_db.grant_permission_to_role(super_admin["id"], perm1["id"])
        supabase_db.grant_permission_to_role(admin["id"], perm2["id"])
        supabase_db.grant_permission_to_role(editor["id"], perm3["id"])
        supabase_db.grant_permission_to_role(user_role["id"], perm4["id"])
        
        # 创建用户并分配最低级角色
        user = self._create_test_user()
        supabase_db.assign_role_to_user(user["id"], user_role["id"])
        
        # 获取用户权限（应该包含所有继承的权限）
        permissions = rbac_manager.get_all_permissions(user["id"], include_inherited=True)
        
        # 验证权限（应该包含所有层级的权限）
        assert "super:read" in permissions
        assert "admin:read" in permissions
        assert "editor:read" in permissions
        assert "user-multi:read" in permissions
