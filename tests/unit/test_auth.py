"""
认证模块单元测试
使用 Supabase REST API
"""

import pytest
from datetime import timedelta
from src.core.auth.services import auth_service
from src.core.auth.models import UserCreate
from src.db.supabase_client import supabase_db


class TestAuthService:
    """认证服务测试类"""
    
    created_user_ids = []
    
    def teardown_method(self):
        """测试后清理"""
        # 清理创建的用户
        for user_id in self.created_user_ids:
            try:
                supabase_db.delete_user(user_id)
            except:
                pass
        self.created_user_ids = []
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "testpass123"
        
        hashed = auth_service.hash_password(password)
        
        # 验证哈希不等于原密码
        assert hashed != password
        
        # 验证可以验证密码
        assert auth_service.verify_password(password, hashed) is True
        assert auth_service.verify_password("wrongpass", hashed) is False
    
    def test_create_user(self):
        """测试创建用户"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        user_data = UserCreate(
            username=f"testuser_{timestamp}",
            email=f"test_{timestamp}@example.com",
            password="testpass123",
            full_name="测试用户"
        )
        
        user = auth_service.create_user(user_data)
        self.created_user_ids.append(user["id"])
        
        # 验证用户创建成功
        assert user["id"] is not None
        assert user["username"] == user_data.username
        assert user["email"] == user_data.email
        assert user["is_active"] is True
        assert user["password_hash"] != "testpass123"  # 密码应该被哈希
    
    def test_authenticate_user_success(self):
        """测试用户认证 - 成功"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 创建用户
        user_data = UserCreate(
            username=f"testuser_{timestamp}",
            email=f"test_{timestamp}@example.com",
            password="testpass123",
            full_name="测试用户"
        )
        user = auth_service.create_user(user_data)
        self.created_user_ids.append(user["id"])
        
        # 认证用户
        authenticated_user = auth_service.authenticate_user(
            user_data.username, "testpass123"
        )
        
        # 验证认证成功
        assert authenticated_user is not None
        assert authenticated_user["id"] == user["id"]
        assert authenticated_user["username"] == user_data.username
    
    def test_authenticate_user_wrong_password(self):
        """测试用户认证 - 错误密码"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 创建用户
        user_data = UserCreate(
            username=f"testuser_{timestamp}",
            email=f"test_{timestamp}@example.com",
            password="testpass123",
            full_name="测试用户"
        )
        auth_service.create_user(user_data)
        
        # 使用错误密码认证
        authenticated_user = auth_service.authenticate_user(
            user_data.username, "wrongpass"
        )
        
        # 验证认证失败
        assert authenticated_user is None
    
    def test_authenticate_user_not_exist(self):
        """测试用户认证 - 用户不存在"""
        # 认证不存在的用户
        authenticated_user = auth_service.authenticate_user(
            "nonexistent_user_12345", "testpass123"
        )
        
        # 验证认证失败
        assert authenticated_user is None
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        # 创建访问令牌
        token = auth_service.create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=30)
        )
        
        # 验证令牌创建成功
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self):
        """测试验证令牌"""
        # 创建访问令牌
        token = auth_service.create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=30)
        )
        
        # 验证令牌
        payload = auth_service.verify_token(token)
        
        # 验证令牌验证成功
        assert payload is not None
        assert payload.get("sub") == "testuser"
    
    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        # 验证无效令牌
        payload = auth_service.verify_token("invalid.token.here")
        
        # 验证验证失败
        assert payload is None
    
    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        # 创建刷新令牌
        token = auth_service.create_refresh_token(data={"sub": "testuser"})
        
        # 验证令牌创建成功
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
