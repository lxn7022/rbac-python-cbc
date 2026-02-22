# Supabase 数据库初始化步骤

## 前提条件

你已经有一个 Supabase 项目。如果没有，请先创建：
- 访问 https://supabase.com/dashboard
- 点击 "New Project"

## 步骤 1：在 Supabase 中执行 SQL 初始化脚本

1. **登录 Supabase Dashboard**
   - 访问：https://supabase.com/dashboard
   - 使用你的账号登录

2. **选择项目**
   - 在左侧导航栏中选择你的 RBAC Python 项目

3. **打开 SQL Editor**
   - 点击左侧菜单的 **SQL Editor** 图标（数据库图标）
   - 或使用快捷键：`Ctrl + /` (Mac) 或 `Ctrl + K` (Windows)

4. **粘贴 SQL 脚本**
   - 点击 **New query** 按钮
   - 打开文件：`scripts/supabase_init.sql`
   - 将全部内容复制并粘贴到 SQL Editor 中

5. **执行 SQL**
   - 点击 **Run** 按钮或按 `Ctrl + Enter`
   - 等待执行完成（约 5-10 秒）

6. **验证结果**
   - 你应该看到类似以下的输出：
     ```
     status
     --------------------
     数据库初始化完成！
     
     info
     --------------------
     角色数量: 5
     
     info
     --------------------
     权限数量: 19
     
     info
     --------------------
     默认用户: admin (admin@example.com)
     ```

## 步骤 2：更新 .env 文件（如果需要）

如果 Supabase 项目引用与代码库中的不同，需要更新 `.env` 文件：

1. **获取正确的连接字符串**
   - 在 Supabase Dashboard
   - Settings > Database
   - 找到 **Connection String** 部分
   - 选择 **URI** 标签
   - 点击 **Copy**

2. **更新 .env 文件**
   - 打开 `.env` 文件
   - 替换 `DATABASE_URL` 的值为复制的连接字符串
   - 保存文件

3. **验证连接**
   ```bash
   python test_supabase_connection.py
   ```

## 步骤 3：运行应用

### 方式 1：使用启动脚本

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
bash start.sh
```

### 方式 2：手动启动

```bash
# 安装依赖（如果还没有）
pip install -r requirements.txt

# 启动 FastAPI 服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 步骤 4：验证初始化

### 访问 API 文档

浏览器打开以下任一地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 测试登录

使用默认管理员账号登录：

```json
POST /api/v1/auth/login

{
  "username": "admin",
  "password": "admin123"
}
```

### 检查数据

在 Supabase Dashboard > Table Editor 中，你应该能看到：

- `users` 表：1 条记录（admin 用户）
- `roles` 表：5 条记录（超级管理员、管理员、编辑、普通用户、访客）
- `permissions` 表：19 条记录
- `role_permissions` 表：约 35 条关联记录
- `rbac_constraints` 表：2 条约束规则

## 默认账号信息

### 管理员账号
- **用户名**: `admin`
- **邮箱**: `admin@example.com`
- **密码**: `admin123`
- **角色**: 超级管理员

**⚠️ 重要提醒**: 首次登录后请立即修改密码！

## 创建的默认数据

### 角色（5个）
1. 超级管理员 - 所有权限
2. 管理员 - 大部分权限（无删除用户和角色）
3. 编辑 - 内容管理权限
4. 普通用户 - 基础读取权限
5. 访客 - 无权限

### 权限（19个）
- 用户管理：5个权限
- 角色管理：5个权限
- 权限管理：3个权限
- 内容管理：4个权限
- 订单管理：4个权限

### 约束规则（2个）
1. 管理员数量限制 - 最多 5 个用户
2. 编辑角色先决条件 - 必须先拥有普通用户角色

## 常见问题

### Q: SQL 执行失败？
A: 检查：
1. Supabase 项目是否正常运行
2. SQL 是否完全复制（不要缺少分号）
3. 网络连接是否正常

### Q: 连接仍然失败？
A: 
1. 确认 Supabase 项目没有被暂停
2. 检查 `.env` 文件中的 DATABASE_URL 是否正确
3. 尝试使用 pooler 端口 (6543) 而不是直连端口 (5432)

### Q: 如何重置数据库？
A: 
1. 在 Supabase Dashboard
2. Settings > Database
3. 点击 "Reset database password"
4. 重新运行 SQL 脚本

### Q: 默认密码不安全？
A: 是的！生产环境中必须修改：
```bash
# 通过 API 修改密码
POST /api/v1/auth/change-password
{
  "old_password": "admin123",
  "new_password": "your-strong-password"
}
```

## 下一步

1. **访问应用**: http://localhost:8000/docs
2. **测试 API**: 尝试各种端点
3. **运行测试**: `pytest`
4. **开发功能**: 基于 RBAC 模型开发业务逻辑

## 技术支持

如果遇到问题：
- 查看 `SUPABASE_SETUP.md` 获取详细的连接配置指南
- 检查 Supabase 状态: https://status.supabase.com
- 查看 `CODEBUDDY.md` 获取项目架构说明
