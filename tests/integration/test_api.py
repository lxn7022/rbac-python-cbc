"""
API 集成测试
测试主要的 API 端点
"""

def test_root_endpoint(client):
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_endpoint(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_user(client):
    """测试创建用户"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "测试用户"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code in [200, 201]
    
    data = response.json()
    assert "id" in data or "username" in data


def test_get_users(client):
    """测试获取用户列表"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_roles(client):
    """测试获取角色列表"""
    response = client.get("/api/v1/roles/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_permissions(client):
    """测试获取权限列表"""
    response = client.get("/api/v1/permissions/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
