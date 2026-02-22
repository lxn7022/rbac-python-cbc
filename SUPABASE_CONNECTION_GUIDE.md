# Supabase 连接问题解决方案

## 问题现象

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) 
connection to server at "db.orygzioqsfvuauzklogx.supabase.co", port 5432 failed: 
Connection timed out
```

## 根本原因

**腾讯云防火墙阻挡了 Supabase PostgreSQL 端口**

- ❌ 端口 5432（直连）被阻挡
- ❌ 端口 6543（连接池）可能也被阻挡
- ✅ 端口 443（HTTPS）可访问

---

## 解决方案

### 方案 1：使用 REST API（推荐，已实现）

**优势**：
- ✅ 通过 HTTPS 443 端口，不受防火墙限制
- ✅ 已实现并测试通过
- ✅ 无需额外配置

**当前实现**：

```python
# src/db/supabase_client.py
from src.db.supabase_client import supabase_db

# 创建用户
user = supabase_db.create_user({
    "username": "testuser",
    "email": "test@example.com",
    "password_hash": "hashed_password"
})

# 查询用户
user = supabase_db.get_user_by_username("testuser")

# 更新用户
user = supabase_db.update_user(user_id, {"full_name": "Test User"})

# 删除用户
supabase_db.delete_user(user_id)
```

**已实现功能**：
- ✅ 用户管理（创建、查询、更新、删除）
- ✅ 角色管理（查询）
- ✅ 权限管理（查询用户权限）
- ✅ 分页查询

---

### 方案 2：开放防火墙端口（如需 SQLAlchemy ORM）

#### 腾讯云配置步骤

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 **轻量应用服务器** → 选择实例 → **防火墙**
3. 点击 **添加规则**

**添加规则**：
```
应用类型：自定义
协议：TCP
端口：6543
策略：允许
备注：Supabase Pooler
```

#### 验证端口

```bash
# Windows
Test-NetConnection -ComputerName aws-0-ap-southeast-1.pooler.supabase.com -Port 6543

# Linux
nc -zv aws-0-ap-southeast-1.pooler.supabase.com 6543
```

#### 配置 SQLAlchemy

```bash
# .env
SUPABASE_DATABASE_URL=postgresql://postgres.项目ID:密码@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

**注意**：使用端口 **6543**（Pooler），不要使用 5432

---

## 快速诊断

运行诊断脚本：

```bash
python diagnose_connection.py
```

这个脚本会：
1. 测试端口连通性（5432, 6543）
2. 测试 HTTPS 连接（443）
3. 检查环境变量配置
4. 测试 REST API 功能
5. 测试 SQLAlchemy 连接
6. 生成推荐方案

---

## 当前项目架构

```
┌─────────────────────┐
│  FastAPI 应用       │
│  (腾讯云服务器)      │
└──────────┬──────────┘
           │
           ├─→ 方案 1: REST API (HTTPS 443) ✅ 推荐
           │       ↓
           │   Supabase PostgREST API
           │       ↓
           │   PostgreSQL 数据库
           │
           └─→ 方案 2: SQLAlchemy (TCP 6543) ⚠️ 需开放端口
                   ↓
               Supabase Pooler
                   ↓
               PostgreSQL 数据库
```

---

## 功能对比

| 功能 | REST API | SQLAlchemy |
|------|----------|------------|
| **端口** | 443 (HTTPS) | 6543 (TCP) |
| **防火墙** | ✅ 不受限制 | ⚠️ 需开放端口 |
| **ORM 支持** | ❌ 无 | ✅ 完整 |
| **连接池** | ✅ 自动管理 | ⚠️ 需配置 |
| **性能** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **实现难度** | ⭐ 简单 | ⭐⭐ 中等 |

---

## 推荐路径

```
开始
  ↓
能否开放端口 6543？
  ├─ 是 → 开放防火墙 → 使用 SQLAlchemy
  │        ↓
  │     配置 SUPABASE_DATABASE_URL
  │        ↓
  │     使用完整 ORM 功能
  │
  └─ 否 → 使用 REST API（当前方案）
           ↓
        已实现并可用
           ↓
        无需修改
```

---

## 下一步操作

### 选择 A：继续使用 REST API（推荐）

```bash
# 无需任何操作，当前方案已可用
# REST API 客户端已实现：
# - src/db/supabase_client.py
# - 支持 CRUD 操作
# - 已在注册接口中使用
```

### 选择 B：切换到 SQLAlchemy

```bash
# 1. 在腾讯云防火墙开放端口 6543
# 2. 配置环境变量
echo "SUPABASE_DATABASE_URL=postgresql://..." >> .env

# 3. 测试连接
python diagnose_connection.py

# 4. 修改代码使用 SQLAlchemy
# 参考 src/db/base.py
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `src/db/supabase_client.py` | REST API 客户端（已实现） |
| `diagnose_connection.py` | 连接诊断工具 |
| `docs/open_supabase_port.md` | 防火墙配置详细指南 |

---

## 常见问题

### Q1: 为什么推荐使用 REST API？

**A**: 
- 不受防火墙限制（使用 HTTPS 443 端口）
- 已经实现并测试通过
- 性能满足大多数场景
- 无需额外配置

### Q2: REST API 性能如何？

**A**: 
- 对于大多数应用场景足够
- 自动管理连接池
- 支持批量操作
- 适合中小型项目

### Q3: 什么时候需要 SQLAlchemy？

**A**: 
- 需要复杂查询（JOIN、子查询）
- 需要事务支持
- 需要完整的 ORM 功能
- 高性能要求场景

### Q4: 两个方案可以共存吗？

**A**: 可以，参考 `src/db/supabase_sqlalchemy.py` 中的混合模式实现。

---

## 技术支持

如需帮助：
1. 运行诊断脚本：`python diagnose_connection.py`
2. 查看日志：检查应用日志中的错误信息
3. 查看文档：`docs/open_supabase_port.md`
