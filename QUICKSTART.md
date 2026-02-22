# 快速开始指南

本文档帮助您快速启动和运行 RBAC Python 项目。

## 前置要求

- Python 3.9 或更高版本
- PostgreSQL 15 或更高版本
- pip 包管理器

## 5 分钟快速启动

### 步骤 1：克隆项目（如果从远程）

```bash
git clone <repository-url>
cd rbac-python-cbc
```

### 步骤 2：创建虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 4：配置环境变量

```bash
# 复制环境变量示例
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下变量：

```env
# 数据库连接
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rbac_db

# JWT 密钥（生产环境请使用强密钥）
JWT_SECRET_KEY=your-secret-key-change-this-in-production

# 调试模式
DEBUG=True
```

### 步骤 5：启动数据库

如果您本地没有 PostgreSQL，可以使用 Docker 快速启动：

```bash
# 启动 PostgreSQL 容器
docker-compose up -d db
```

或者使用本地 PostgreSQL：

```bash
# 创建数据库
createdb rbac_db
```

### 步骤 6：运行数据库迁移

```bash
# 使用 Supabase（已配置）
# 数据库表已通过迁移脚本创建
# db/migrations/001_init_rbac_tables.sql

# 或者使用 Alembic（需要配置）
alembic upgrade head
```

### 步骤 7：初始化数据

```bash
# 填充默认角色、权限和约束
python scripts/init_data.py
```

这会创建：
- 5 个默认角色（超级管理员、管理员、编辑、普通用户、访客）
- 19 个系统权限
- 2 个默认约束规则

### 步骤 8：启动应用

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
bash start.sh
```

或者直接运行：
```bash
uvicorn src.main:app --reload
```

### 步骤 9：访问应用

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

## 验证安装

### 1. 检查健康状态

```bash
curl http://localhost:8000/health
```

应该返回：
```json
{
  "status": "healthy"
}
```

### 2. 访问 API 文档

在浏览器中打开 http://localhost:8000/docs，您应该看到 Swagger UI 界面。

### 3. 创建第一个用户

使用 Swagger UI 中的 `POST /api/v1/users/` 端点创建用户：

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin123",
  "full_name": "系统管理员"
}
```

### 4. 分配角色

使用 `POST /api/v1/users/{user_id}/roles` 端点为用户分配角色。

## 常见问题

### Q: 找不到 `psycopg2-binary` 模块？

A: 确保已安装 PostgreSQL 开发库：
- **Ubuntu/Debian**: `sudo apt-get install libpq-dev`
- **CentOS/RHEL**: `sudo yum install postgresql-devel`
- **macOS**: `brew install postgresql`

### Q: 数据库连接失败？

A: 检查：
1. PostgreSQL 服务是否运行
2. `.env` 文件中的数据库连接字符串是否正确
3. 数据库是否存在

### Q: 导入错误：找不到模块？

A: 确保在项目根目录下运行，并且虚拟环境已激活。

### Q: 如何运行测试？

```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=src --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

## 下一步

- 阅读 [CODEBUDDY.md](CODEBUDDY.md) 了解项目详细设计
- 查看 [API 文档](http://localhost:8000/docs) 了解所有可用端点
- 阅读测试用例了解功能用法
- 根据需求自定义角色和权限

## 获取帮助

如遇到问题：
1. 检查日志输出
2. 查看 [README.md](README.md)
3. 查看 [CODEBUDDY.md](CODEBUDDY.md)
4. 提交 Issue

## 开发模式

开发模式下，应用会：
- 自动重新加载（Auto-reload）
- 显示详细的错误堆栈
- 启用调试工具栏
- 使用开发日志级别

生产环境部署时，请确保：
- 设置 `DEBUG=False`
- 使用强密钥
- 配置正确的 CORS 源
- 使用 HTTPS
- 配置日志收集

祝您使用愉快！
