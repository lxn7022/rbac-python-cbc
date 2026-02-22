# API 使用示例

本文档提供 RBAC Python 项目的 API 使用示例。

## 目录

- [认证](#认证)
- [用户管理](#用户管理)
- [角色管理](#角色管理)
- [权限管理](#权限管理)
- [权限检查](#权限检查)

---

## 认证

### 1. 注册用户

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

**响应：**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. 登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=securepassword123"
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 获取当前用户信息

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 用户管理

### 1. 获取用户列表

```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**查询参数：**
- `search`: 搜索关键词
- `page`: 页码
- `size`: 每页数量

**示例：**
```bash
curl -X GET "http://localhost:8000/api/v1/users/?search=john&page=1&size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. 获取用户详情

```bash
curl -X GET "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 更新用户

```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "email": "johnsmith@example.com"
  }'
```

### 4. 删除用户

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. 获取用户角色

```bash
curl -X GET "http://localhost:8000/api/v1/users/1/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应：**
```json
[
  {
    "id": 1,
    "name": "管理员",
    "slug": "admin",
    "priority": 80,
    "assigned_at": "2024-01-15T10:30:00Z"
  }
]
```

### 6. 分配角色

```bash
curl -X POST "http://localhost:8000/api/v1/users/1/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 2,
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

### 7. 撤销角色

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1/roles/2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 角色管理

### 1. 获取角色列表

```bash
curl -X GET "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应：**
```json
[
  {
    "id": 1,
    "name": "超级管理员",
    "slug": "super-admin",
    "priority": 100,
    "is_system": true,
    "created_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "name": "管理员",
    "slug": "admin",
    "priority": 80,
    "parent_id": 1,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### 2. 创建角色

```bash
curl -X POST "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "审核员",
    "slug": "reviewer",
    "description": "内容审核人员",
    "priority": 50,
    "parent_id": 2
  }'
```

### 3. 获取角色详情

```bash
curl -X GET "http://localhost:8000/api/v1/roles/2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 更新角色

```bash
curl -X PUT "http://localhost:8000/api/v1/roles/2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "系统管理员，拥有大部分权限"
  }'
```

### 5. 删除角色

```bash
curl -X DELETE "http://localhost:8000/api/v1/roles/2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. 获取角色权限

```bash
curl -X GET "http://localhost:8000/api/v1/roles/2/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应：**
```json
[
  {
    "id": 1,
    "resource": "user",
    "action": "read",
    "description": "读取用户信息",
    "module": "auth"
  },
  {
    "id": 2,
    "resource": "user",
    "action": "write",
    "description": "编辑用户信息",
    "module": "auth"
  }
]
```

### 7. 为角色分配权限

```bash
curl -X POST "http://localhost:8000/api/v1/roles/2/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_ids": [1, 2, 3, 4]
  }'
```

### 8. 撤销角色权限

```bash
curl -X DELETE "http://localhost:8000/api/v1/roles/2/permissions/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 9. 获取角色的用户列表

```bash
curl -X GET "http://localhost:8000/api/v1/roles/2/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 权限管理

### 1. 获取权限列表

```bash
curl -X GET "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**查询参数：**
- `module`: 按模块过滤
- `resource`: 按资源过滤

**示例：**
```bash
curl -X GET "http://localhost:8000/api/v1/permissions/?module=auth" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应：**
```json
[
  {
    "id": 1,
    "resource": "user",
    "action": "read",
    "description": "读取用户信息",
    "module": "auth"
  },
  {
    "id": 2,
    "resource": "user",
    "action": "write",
    "description": "编辑用户信息",
    "module": "auth"
  }
]
```

### 2. 创建权限

```bash
curl -X POST "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "comment",
    "action": "delete",
    "description": "删除评论",
    "module": "content"
  }'
```

### 3. 删除权限

```bash
curl -X DELETE "http://localhost:8000/api/v1/permissions/20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 权限检查

### 1. 检查用户权限

```bash
curl -X GET "http://localhost:8000/api/v1/auth/check-permission?resource=user&action=read" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应：**
```json
{
  "has_permission": true
}
```

### 2. 批量检查权限

```bash
curl -X POST "http://localhost:8000/api/v1/auth/check-permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": [
      {"resource": "user", "action": "read"},
      {"resource": "user", "action": "write"},
      {"resource": "article", "action": "delete"}
    ]
  }'
```

**响应：**
```json
{
  "results": {
    "user:read": true,
    "user:write": false,
    "article:delete": true
  }
}
```

### 3. 获取用户所有权限

```bash
curl -X GET "http://localhost:8000/api/v1/auth/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应：**
```json
{
  "permissions": [
    "user:read",
    "user:write",
    "article:read",
    "article:write",
    "article:delete"
  ]
}
```

---

## Python 客户端示例

### 使用 requests 库

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 登录获取 token
login_data = {
    "username": "johndoe",
    "password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
token = response.json()["access_token"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 获取用户列表
response = requests.get(f"{BASE_URL}/users/", headers=headers)
users = response.json()
print(f"用户列表: {users}")

# 3. 创建角色
role_data = {
    "name": "测试角色",
    "slug": "test-role",
    "description": "这是一个测试角色"
}
response = requests.post(f"{BASE_URL}/roles/", json=role_data, headers=headers)
role = response.json()
print(f"创建的角色: {role}")

# 4. 检查权限
response = requests.get(
    f"{BASE_URL}/auth/check-permission?resource=user&action=read",
    headers=headers
)
has_permission = response.json()["has_permission"]
print(f"是否有权限: {has_permission}")
```

### 使用异步 httpx 库

```python
import httpx
import asyncio

async def main():
    BASE_URL = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. 登录
        login_data = {
            "username": "johndoe",
            "password": "securepassword123"
        }
        response = await client.post(f"{BASE_URL}/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. 获取用户列表
        response = await client.get(f"{BASE_URL}/users/", headers=headers)
        users = response.json()
        print(f"用户列表: {users}")
        
        # 3. 检查权限
        response = await client.get(
            f"{BASE_URL}/auth/check-permission?resource=user&action=read",
            headers=headers
        )
        has_permission = response.json()["has_permission"]
        print(f"是否有权限: {has_permission}")

asyncio.run(main())
```

---

## 错误处理

所有 API 错误都遵循统一的错误响应格式：

```json
{
  "detail": "错误信息描述"
}
```

常见 HTTP 状态码：
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权（未登录或 token 无效）
- `403`: 权限不足
- `404`: 资源不存在
- `422`: 验证错误
- `500`: 服务器内部错误

---

## 速率限制

API 实现了速率限制以防止滥用：

- 每个用户每分钟最多 100 个请求
- 超过限制返回 `429 Too Many Requests`

**响应头：**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642289200
```

---

## 更多信息

- [完整 API 文档](http://localhost:8000/docs)
- [项目 README](README.md)
- [快速开始指南](QUICKSTART.md)
