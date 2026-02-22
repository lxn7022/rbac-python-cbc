# Supabase 数据库连接配置指南

## 问题诊断

当前错误：`FATAL: Tenant or user not found`

这说明提供的 Supabase 凭据有问题：
1. 项目引用（project ref）不正确
2. 数据库密码已更改
3. Supabase 项目已被删除或暂停

## 获取正确的 Supabase 连接信息

请按照以下步骤获取正确的数据库连接字符串：

### 步骤 1: 登录 Supabase

访问 https://supabase.com/dashboard 并登录

### 步骤 2: 选择项目

在左侧导航栏选择你的项目

### 步骤 3: 获取数据库连接字符串

1. 点击左侧菜单的 **Settings**
2. 选择 **Database** 标签
3. 向下滚动到 **Connection String** 部分
4. 选择 **URI** 标签
5. 点击 **Copy** 按钮复制连接字符串

### 步骤 4: 更新 .env 文件

复制出来的连接字符串格式如下：

```
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

请将其粘贴到 `.env` 文件的 `DATABASE_URL` 变量中。

### 示例配置

```env
DATABASE_URL=postgresql://postgres.abcdef123456:your-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## 验证连接

更新 `.env` 文件后，运行以下命令验证：

```bash
python test_supabase_connection.py
```

## 替代方案：使用 Supabase SQL Editor

如果暂时无法获取正确的连接字符串，可以使用 Supabase 的 SQL Editor：

1. 登录 Supabase Dashboard
2. 点击左侧菜单的 **SQL Editor**
3. 点击 **New query**
4. 粘贴以下 SQL 并执行：

```sql
-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建角色表
CREATE TABLE IF NOT EXISTS roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 0,
    parent_id BIGINT REFERENCES roles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建权限表
CREATE TABLE IF NOT EXISTS permissions (
    id BIGSERIAL PRIMARY KEY,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    module VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_resource_action UNIQUE (resource, action)
);

-- 创建用户-角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT unique_user_role UNIQUE (user_id, role_id)
);

-- 创建角色-权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT unique_role_permission UNIQUE (role_id, permission_id)
);

-- 创建约束表
CREATE TABLE IF NOT EXISTS rbac_constraints (
    id BIGSERIAL PRIMARY KEY,
    constraint_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_roles_slug ON roles(slug);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);
```

## 常见问题

### Q: 为什么连接超时？
A: 可能原因：
- 网络防火墙阻止
- Supabase 项目已暂停
- 项目引用错误

### Q: 什么是 Project Ref？
A: Project Ref 是 Supabase 项目的唯一标识符，可以在项目设置中找到。

### Q: 如何重置数据库密码？
A:
1. 登录 Supabase Dashboard
2. Settings > Database
3. Database Password 部分
4. 点击 "Generate new password"

### Q: Pooler 和 Direct 连接有什么区别？
A:
- **Pooler (6543)**: 推荐使用，自动管理连接池
- **Direct (5432)**: 直连数据库，适合特定场景

## 获取帮助

如果仍然无法连接：
1. 检查 Supabase 项目状态：https://supabase.com/dashboard
2. 查看 Supabase 状态页面：https://status.supabase.com
3. 联系 Supabase 支持
