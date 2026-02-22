# -*- coding: utf-8 -*-
"""
Supabase 客户端单元测试
连接真实 Supabase 环境进行测试
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
load_dotenv()

from src.db.supabase_client import supabase_db, SupabaseDB


class TestSupabaseConnection:
    """测试 Supabase 连接"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        assert supabase_db._client is not None, "客户端应该成功初始化"
    
    def test_client_property(self):
        """测试客户端属性访问"""
        client = supabase_db.client
        assert client is not None, "客户端属性应该返回有效的客户端实例"


class TestUserOperations:
    """测试用户操作"""
    
    # 测试数据
    test_user_data = {
        "username": f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password_hash": "$2b$12$test_hash_value",
        "full_name": "测试用户",
        "is_active": True,
        "is_verified": False
    }
    
    created_user_id = None
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前后清理"""
        yield
        # 测试后清理创建的用户（如果有）
        if self.created_user_id:
            try:
                supabase_db.delete_user(self.created_user_id)
            except:
                pass
            self.created_user_id = None
    
    def test_create_user(self):
        """测试创建用户"""
        user = supabase_db.create_user(self.test_user_data)
        
        assert user is not None, "创建用户应该返回用户数据"
        assert "id" in user, "用户数据应该包含 id"
        assert user["username"] == self.test_user_data["username"]
        assert user["email"] == self.test_user_data["email"]
        
        # 保存创建的用户 ID 用于清理
        TestUserOperations.created_user_id = user["id"]
    
    def test_get_user_by_id(self):
        """测试根据 ID 获取用户"""
        # 先创建一个用户
        user = supabase_db.create_user(self.test_user_data)
        assert user is not None
        TestUserOperations.created_user_id = user["id"]
        
        # 测试获取用户
        fetched_user = supabase_db.get_user_by_id(user["id"])
        
        assert fetched_user is not None, "应该能找到用户"
        assert fetched_user["id"] == user["id"]
        assert fetched_user["username"] == self.test_user_data["username"]
    
    def test_get_user_by_username(self):
        """测试根据用户名获取用户"""
        # 先创建一个用户
        user = supabase_db.create_user(self.test_user_data)
        assert user is not None
        TestUserOperations.created_user_id = user["id"]
        
        # 测试获取用户
        fetched_user = supabase_db.get_user_by_username(self.test_user_data["username"])
        
        assert fetched_user is not None, "应该能找到用户"
        assert fetched_user["username"] == self.test_user_data["username"]
    
    def test_get_user_by_email(self):
        """测试根据邮箱获取用户"""
        # 先创建一个用户
        user = supabase_db.create_user(self.test_user_data)
        assert user is not None
        TestUserOperations.created_user_id = user["id"]
        
        # 测试获取用户
        fetched_user = supabase_db.get_user_by_email(self.test_user_data["email"])
        
        assert fetched_user is not None, "应该能找到用户"
        assert fetched_user["email"] == self.test_user_data["email"]
    
    def test_get_user_not_found(self):
        """测试获取不存在的用户"""
        user = supabase_db.get_user_by_id(999999999)
        assert user is None, "不存在的用户应该返回 None"
    
    def test_update_user(self):
        """测试更新用户"""
        # 先创建一个用户
        user = supabase_db.create_user(self.test_user_data)
        assert user is not None
        TestUserOperations.created_user_id = user["id"]
        
        # 更新用户
        update_data = {
            "full_name": "更新后的用户名",
            "is_verified": True
        }
        updated_user = supabase_db.update_user(user["id"], update_data)
        
        assert updated_user is not None, "更新应该返回用户数据"
        assert updated_user["full_name"] == "更新后的用户名"
        assert updated_user["is_verified"] is True
    
    def test_get_all_users(self):
        """测试获取用户列表"""
        result = supabase_db.get_all_users(page=1, size=10)
        
        assert "items" in result, "结果应该包含 items"
        assert "total" in result, "结果应该包含 total"
        assert "page" in result, "结果应该包含 page"
        assert "size" in result, "结果应该包含 size"
        assert result["page"] == 1
        assert result["size"] == 10
    
    def test_get_all_users_with_search(self):
        """测试搜索用户"""
        # 先创建一个用户
        user = supabase_db.create_user(self.test_user_data)
        assert user is not None
        TestUserOperations.created_user_id = user["id"]
        
        # 搜索用户
        result = supabase_db.get_all_users(page=1, size=10, search=self.test_user_data["username"])
        
        assert result["total"] >= 1, "应该至少找到一个用户"
    
    def test_delete_user(self):
        """测试删除用户"""
        # 先创建一个用户
        user = supabase_db.create_user(self.test_user_data)
        assert user is not None
        
        # 删除用户
        result = supabase_db.delete_user(user["id"])
        assert result is True, "删除应该成功"
        
        # 验证删除
        deleted_user = supabase_db.get_user_by_id(user["id"])
        assert deleted_user is None, "删除后应该找不到用户"


class TestRoleOperations:
    """测试角色操作"""
    
    created_role_id = None
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前后清理"""
        # 生成唯一的测试数据（slug 只能包含小写字母、数字和连字符）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        self.test_role_data = {
            "name": f"测试角色_{timestamp}",
            "slug": f"test-role-{timestamp}",  # 使用连字符代替下划线
            "description": "测试角色描述",
            "priority": 50,
            "is_system": False
        }
        yield
        if self.created_role_id:
            try:
                supabase_db.delete_role(self.created_role_id)
            except:
                pass
            self.created_role_id = None
    
    def test_get_all_roles(self):
        """测试获取所有角色"""
        roles = supabase_db.get_all_roles()
        
        assert isinstance(roles, list), "应该返回列表"
        assert len(roles) >= 5, "应该至少有 5 个默认角色"
    
    def test_get_role_by_slug(self):
        """测试根据 slug 获取角色"""
        # 假设数据库中有 admin 角色
        role = supabase_db.get_role_by_slug("admin")
        
        # 可能不存在，测试逻辑正确即可
        if role:
            assert "id" in role
            assert "name" in role
            assert "slug" in role
    
    def test_create_role(self):
        """测试创建角色"""
        role = supabase_db.create_role(self.test_role_data)
        
        assert role is not None, "创建角色应该返回角色数据"
        assert "id" in role
        assert role["name"] == self.test_role_data["name"]
        assert role["slug"] == self.test_role_data["slug"]
        
        TestRoleOperations.created_role_id = role["id"]
    
    def test_get_role_by_id(self):
        """测试根据 ID 获取角色"""
        # 先创建一个角色
        role = supabase_db.create_role(self.test_role_data)
        assert role is not None
        TestRoleOperations.created_role_id = role["id"]
        
        # 获取角色
        fetched_role = supabase_db.get_role_by_id(role["id"])
        
        assert fetched_role is not None
        assert fetched_role["id"] == role["id"]
    
    def test_update_role(self):
        """测试更新角色"""
        # 先创建一个角色
        role = supabase_db.create_role(self.test_role_data)
        assert role is not None
        TestRoleOperations.created_role_id = role["id"]
        
        # 更新角色
        update_data = {
            "description": "更新后的描述",
            "priority": 60
        }
        updated_role = supabase_db.update_role(role["id"], update_data)
        
        assert updated_role is not None
        assert updated_role["description"] == "更新后的描述"
        assert updated_role["priority"] == 60


class TestPermissionOperations:
    """测试权限操作"""
    
    def test_get_all_permissions(self):
        """测试获取所有权限"""
        result = supabase_db.get_all_permissions(page=1, size=10)
        
        assert "items" in result
        assert "total" in result
        assert result["total"] >= 0
    
    def test_get_all_permissions_with_module(self):
        """测试按模块获取权限"""
        result = supabase_db.get_all_permissions(module="auth", page=1, size=10)
        
        assert "items" in result
        # 验证返回的权限都属于 auth 模块
        for item in result["items"]:
            assert item.get("module") == "auth"
    
    def test_get_permission_by_id(self):
        """测试根据 ID 获取权限"""
        # 先获取一个权限
        result = supabase_db.get_all_permissions(page=1, size=1)
        
        if result["items"]:
            perm_id = result["items"][0]["id"]
            perm = supabase_db.get_permission_by_id(perm_id)
            
            assert perm is not None
            assert perm["id"] == perm_id


class TestUserRoleOperations:
    """测试用户角色关联操作"""
    
    test_user_data = {
        "username": f"test_ur_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"test_ur_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password_hash": "$2b$12$test_hash_value",
        "full_name": "测试用户角色",
        "is_active": True
    }
    
    created_user_id = None
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前后清理"""
        # 创建测试用户
        user = supabase_db.create_user(self.test_user_data)
        if user:
            TestUserRoleOperations.created_user_id = user["id"]
        
        yield
        
        # 清理用户
        if self.created_user_id:
            try:
                supabase_db.delete_user(self.created_user_id)
            except:
                pass
            self.created_user_id = None
    
    def test_assign_role(self):
        """测试分配角色"""
        if not self.created_user_id:
            pytest.skip("用户创建失败")
        
        # 获取一个角色
        roles = supabase_db.get_all_roles()
        if not roles:
            pytest.skip("没有可用角色")
        
        role_id = roles[0]["id"]
        
        # 分配角色
        result = supabase_db.assign_role(
            user_id=self.created_user_id,
            role_id=role_id
        )
        
        assert result is not None, "分配角色应该成功"
        assert result["user_id"] == self.created_user_id
        assert result["role_id"] == role_id
    
    def test_get_user_roles(self):
        """测试获取用户角色"""
        if not self.created_user_id:
            pytest.skip("用户创建失败")
        
        # 先分配一个角色
        roles = supabase_db.get_all_roles()
        if roles:
            supabase_db.assign_role(
                user_id=self.created_user_id,
                role_id=roles[0]["id"]
            )
        
        # 获取用户角色
        user_roles = supabase_db.get_user_roles(self.created_user_id)
        
        assert isinstance(user_roles, list)
    
    def test_revoke_role(self):
        """测试撤销角色"""
        if not self.created_user_id:
            pytest.skip("用户创建失败")
        
        # 先分配一个角色
        roles = supabase_db.get_all_roles()
        if not roles:
            pytest.skip("没有可用角色")
        
        role_id = roles[0]["id"]
        supabase_db.assign_role(
            user_id=self.created_user_id,
            role_id=role_id
        )
        
        # 撤销角色
        result = supabase_db.revoke_role(
            user_id=self.created_user_id,
            role_id=role_id
        )
        
        assert result is True, "撤销角色应该成功"


class TestRolePermissionOperations:
    """测试角色权限关联操作"""
    
    def test_get_role_permissions(self):
        """测试获取角色权限"""
        # 获取一个角色
        roles = supabase_db.get_all_roles()
        if not roles:
            pytest.skip("没有可用角色")
        
        role_id = roles[0]["id"]
        
        # 获取角色权限
        permissions = supabase_db.get_role_permissions(role_id)
        
        assert isinstance(permissions, list)


class TestPermissionCheck:
    """测试权限检查"""
    
    def test_has_permission(self):
        """测试权限检查"""
        # 使用一个存在的用户 ID（通常是 admin 用户，ID=1）
        result = supabase_db.has_permission(1, "user", "read")
        
        # 结果可能是 True 或 False，取决于用户权限
        assert isinstance(result, bool)
    
    def test_has_role(self):
        """测试角色检查"""
        # 使用一个存在的用户 ID
        result = supabase_db.has_role(1, "admin")
        
        # 结果可能是 True 或 False
        assert isinstance(result, bool)
    
    def test_get_user_permissions(self):
        """测试获取用户权限"""
        permissions = supabase_db.get_user_permissions(1)
        
        assert isinstance(permissions, list)


class TestConstraintOperations:
    """测试 RBAC 约束操作"""
    
    test_constraint_data = {
        "constraint_type": "cardinality",
        "name": f"test_constraint_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "测试约束",
        "config": {"role": "admin", "max_users": 5},
        "is_active": True
    }
    
    created_constraint_id = None
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前后清理"""
        yield
        if self.created_constraint_id:
            try:
                supabase_db.delete_constraint(self.created_constraint_id)
            except:
                pass
            self.created_constraint_id = None
    
    def test_get_all_constraints(self):
        """测试获取所有约束"""
        constraints = supabase_db.get_all_constraints()
        
        assert isinstance(constraints, list)
    
    def test_create_constraint(self):
        """测试创建约束"""
        constraint = supabase_db.create_constraint(self.test_constraint_data)
        
        assert constraint is not None
        assert "id" in constraint
        assert constraint["name"] == self.test_constraint_data["name"]
        
        TestConstraintOperations.created_constraint_id = constraint["id"]
    
    def test_get_constraint_by_id(self):
        """测试根据 ID 获取约束"""
        # 先创建一个约束
        constraint = supabase_db.create_constraint(self.test_constraint_data)
        assert constraint is not None
        TestConstraintOperations.created_constraint_id = constraint["id"]
        
        # 获取约束
        fetched = supabase_db.get_constraint_by_id(constraint["id"])
        
        assert fetched is not None
        assert fetched["id"] == constraint["id"]
    
    def test_update_constraint(self):
        """测试更新约束"""
        # 先创建一个约束
        constraint = supabase_db.create_constraint(self.test_constraint_data)
        assert constraint is not None
        TestConstraintOperations.created_constraint_id = constraint["id"]
        
        # 更新约束
        update_data = {
            "description": "更新后的描述"
        }
        updated = supabase_db.update_constraint(constraint["id"], update_data)
        
        assert updated is not None
        assert updated["description"] == "更新后的描述"


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_get_nonexistent_user(self):
        """测试获取不存在的用户"""
        user = supabase_db.get_user_by_id(999999999)
        assert user is None
    
    def test_get_nonexistent_role(self):
        """测试获取不存在的角色"""
        role = supabase_db.get_role_by_id(999999999)
        assert role is None
    
    def test_get_nonexistent_permission(self):
        """测试获取不存在的权限"""
        perm = supabase_db.get_permission_by_id(999999999)
        assert perm is None
    
    def test_update_nonexistent_user(self):
        """测试更新不存在的用户"""
        result = supabase_db.update_user(999999999, {"full_name": "test"})
        assert result is None
    
    def test_delete_nonexistent_user(self):
        """测试删除不存在的用户"""
        result = supabase_db.delete_user(999999999)
        assert result is False


# 运行测试
if __name__ == "__main__":
    # 设置编码
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul 2>&1')
    
    # 运行测试
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
