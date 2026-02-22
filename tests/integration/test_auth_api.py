"""
认证 API 集成测试
使用 Supabase REST API
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


class TestAuthAPI:
    """认证 API 测试类"""
    
    def test_register_user(self, client: TestClient):
        """测试注册用户"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        user_data = {
            "username": f"newuser_{timestamp}",
            "email": f"newuser_{timestamp}@example.com",
            "password": "password123",
            "full_name": "新用户"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # 验证响应
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["username"] == f"newuser_{timestamp}"
        assert data["email"] == f"newuser_{timestamp}@example.com"
        assert "password" not in data  # 密码不应该返回
    
    def test_login_success(self, client: TestClient):
        """测试登录 - 成功"""
        # 先注册用户
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "password123",
            "full_name": "测试用户"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # 登录
        login_data = {
            "username": f"testuser_{timestamp}",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient):
        """测试登录 - 错误密码"""
        # 先注册用户
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "password123",
            "full_name": "测试用户"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # 使用错误密码登录
        login_data = {
            "username": f"testuser_{timestamp}",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # 验证响应
        assert response.status_code in [400, 401]
    
    def test_get_current_user(self, client: TestClient):
        """测试获取当前用户信息"""
        # 注册并登录
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "password123",
            "full_name": "测试用户"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": f"testuser_{timestamp}",
            "password": "password123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # 获取当前用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == f"testuser_{timestamp}"
        assert data["email"] == f"test_{timestamp}@example.com"
    
    def test_get_current_user_no_token(self, client: TestClient):
        """测试获取当前用户信息 - 无令牌"""
        response = client.get("/api/v1/auth/me")
        
        # 验证响应
        assert response.status_code in [401, 403]
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """测试获取当前用户信息 - 无效令牌"""
        headers = {"Authorization": "Bearer invalid.token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # 验证响应
        assert response.status_code in [401, 403]
