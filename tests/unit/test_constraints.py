"""
RBAC 约束规则单元测试
使用 Supabase REST API
"""

import pytest
from datetime import datetime
from src.core.rbac.constraints import (
    MutuallyExclusiveConstraint,
    CardinalityConstraint,
    PrerequisiteConstraint,
    ConstraintManager
)
from src.db.supabase_client import supabase_db
from src.utils.exceptions import ConstraintViolationError


class TestMutuallyExclusiveConstraint:
    """互斥约束测试"""
    
    created_user_ids = []
    created_role_ids = []
    created_constraint_ids = []
    
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
    
    def _create_test_role(self, name: str, slug: str) -> dict:
        """创建测试角色"""
        role_data = {
            "name": name,
            "slug": slug,
            "description": f"测试角色 - {name}",
            "priority": 50,
            "is_system": False
        }
        role = supabase_db.create_role(role_data)
        self.created_role_ids.append(role["id"])
        return role
    
    def test_mutually_exclusive_pass(self):
        """测试互斥约束 - 通过"""
        # 创建角色
        role1 = self._create_test_role("出纳员", "cashier-test")
        role2 = self._create_test_role("会计", "accountant-test")
        
        # 创建约束
        config = {"roles": ["cashier-test", "accountant-test"], "check_type": "static"}
        constraint = MutuallyExclusiveConstraint(supabase_db, config)
        
        # 创建用户
        user = self._create_test_user()
        
        # 分配角色 - 应该通过
        result = constraint.check(user["id"], role1["id"], "assign")
        assert result is True
    
    def test_mutually_exclusive_violation(self):
        """测试互斥约束 - 违反"""
        # 创建角色
        role1 = self._create_test_role("出纳员2", "cashier-test2")
        role2 = self._create_test_role("会计2", "accountant-test2")
        
        # 创建约束
        config = {"roles": ["cashier-test2", "accountant-test2"], "check_type": "static"}
        constraint = MutuallyExclusiveConstraint(supabase_db, config)
        
        # 创建用户，分配出纳员角色
        user = self._create_test_user()
        supabase_db.assign_role_to_user(user["id"], role1["id"])
        
        # 尝试分配会计角色 - 应该抛出异常
        with pytest.raises(ConstraintViolationError) as exc_info:
            constraint.check(user["id"], role2["id"], "assign")
        
        assert "违反互斥约束" in str(exc_info.value)


class TestCardinalityConstraint:
    """基数约束测试"""
    
    created_user_ids = []
    created_role_ids = []
    
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
    
    def _create_test_role(self, slug: str) -> dict:
        """创建测试角色"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        role_data = {
            "name": f"测试角色_{timestamp}",
            "slug": slug,
            "description": "测试角色",
            "priority": 50,
            "is_system": False
        }
        role = supabase_db.create_role(role_data)
        self.created_role_ids.append(role["id"])
        return role
    
    def test_cardinality_pass(self):
        """测试基数约束 - 通过"""
        # 创建角色
        role = self._create_test_role("admin-card-test")
        
        # 创建约束 - 最多 3 个用户
        config = {"role": "admin-card-test", "max_users": 3}
        constraint = CardinalityConstraint(supabase_db, config)
        
        # 创建 2 个用户并分配角色
        for _ in range(2):
            user = self._create_test_user()
            supabase_db.assign_role_to_user(user["id"], role["id"])
        
        # 添加第 3 个用户 - 应该通过
        user3 = self._create_test_user()
        result = constraint.check(user3["id"], role["id"], "assign")
        assert result is True
    
    def test_cardinality_violation(self):
        """测试基数约束 - 违反"""
        # 创建角色
        role = self._create_test_role("admin-card-test2")
        
        # 创建约束 - 最多 3 个用户
        config = {"role": "admin-card-test2", "max_users": 3}
        constraint = CardinalityConstraint(supabase_db, config)
        
        # 创建 3 个用户并分配角色
        for _ in range(3):
            user = self._create_test_user()
            supabase_db.assign_role_to_user(user["id"], role["id"])
        
        # 尝试添加第 4 个用户 - 应该抛出异常
        user4 = self._create_test_user()
        
        with pytest.raises(ConstraintViolationError) as exc_info:
            constraint.check(user4["id"], role["id"], "assign")
        
        assert "违反基数约束" in str(exc_info.value)


class TestPrerequisiteConstraint:
    """先决条件约束测试"""
    
    created_user_ids = []
    created_role_ids = []
    
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
    
    def _create_test_role(self, name: str, slug: str) -> dict:
        """创建测试角色"""
        role_data = {
            "name": name,
            "slug": slug,
            "description": f"测试角色 - {name}",
            "priority": 50,
            "is_system": False
        }
        role = supabase_db.create_role(role_data)
        self.created_role_ids.append(role["id"])
        return role
    
    def test_prerequisite_pass(self):
        """测试先决条件约束 - 通过"""
        # 创建角色
        user_role = self._create_test_role("普通用户", "user-prereq-test")
        editor_role = self._create_test_role("编辑", "editor-prereq-test")
        
        # 创建约束 - 需要先拥有普通用户角色
        config = {"role": "editor-prereq-test", "required_roles": ["user-prereq-test"]}
        constraint = PrerequisiteConstraint(supabase_db, config)
        
        # 创建用户，分配普通用户角色
        user = self._create_test_user()
        supabase_db.assign_role_to_user(user["id"], user_role["id"])
        
        # 分配编辑角色 - 应该通过
        result = constraint.check(user["id"], editor_role["id"], "assign")
        assert result is True
    
    def test_prerequisite_violation(self):
        """测试先决条件约束 - 违反"""
        # 创建角色
        user_role = self._create_test_role("普通用户2", "user-prereq-test2")
        editor_role = self._create_test_role("编辑2", "editor-prereq-test2")
        
        # 创建约束 - 需要先拥有普通用户角色
        config = {"role": "editor-prereq-test2", "required_roles": ["user-prereq-test2"]}
        constraint = PrerequisiteConstraint(supabase_db, config)
        
        # 创建用户，不分配普通用户角色
        user = self._create_test_user()
        
        # 尝试分配编辑角色 - 应该抛出异常
        with pytest.raises(ConstraintViolationError) as exc_info:
            constraint.check(user["id"], editor_role["id"], "assign")
        
        assert "违反先决条件约束" in str(exc_info.value)


class TestConstraintManager:
    """约束管理器测试"""
    
    def test_load_constraints(self):
        """测试加载约束"""
        # 加载约束
        manager = ConstraintManager(supabase_db)
        constraints = manager.load_constraints(use_cache=False)
        
        # 验证约束列表不为空
        assert isinstance(constraints, list)
    
    def test_check_all_constraints(self):
        """测试检查所有约束"""
        manager = ConstraintManager(supabase_db)
        
        # 检查约束 - 应该通过（无约束违反）
        result = manager.check_constraints(1, 1, "assign")
        assert result is True
