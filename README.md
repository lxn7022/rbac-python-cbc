# RBAC Python - CodeBuddy Edition

基于角色的访问控制系统（RBAC），支持完整的 RBAC0/1/2/3 模型。

## 功能特性

- ✅ **RBAC0**：基础用户-角色-权限模型
- ✅ **RBAC1**：角色继承支持
- ✅ **RBAC2**：约束规则（互斥、基数、先决条件）
- ✅ **RBAC3**：统一模型（继承+约束）
- ✅ JWT 认证
- ✅ PostgreSQL 数据库
- ✅ FastAPI Web 框架
- ✅ RESTful API
- ✅ 完整的审计日志

## 技术栈

- **Web 框架**：FastAPI 0.109.0
- **数据库**：PostgreSQL + SQLAlchemy 2.0
- **认证**：JWT (python-jose)
- **密码加密**：bcrypt
- **数据验证**：Pydantic 2.5
- **ORM**：SQLAlchemy 2.0
- **测试**：pytest

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接和其他参数
```

### 3. 初始化数据库

```bash
# 使用 Alembic 运行数据库迁移
alembic upgrade head
```

### 4. 初始化数据库数据

```bash
# 运行初始化脚本，填充默认角色、权限和约束
python scripts/init_data.py
```

### 5. 运行项目

```bash
# 方式 1：使用启动脚本
# Windows:
start.bat
# Linux/Mac:
bash start.sh

# 方式 2：使用 uvicorn
uvicorn src.main:app --reload

# 方式 3：使用 Python 模块方式
python -m uvicorn src.main:app --reload

# 访问 API 文档
http://localhost:8000/docs
```

### Docker 部署

```bash
# 使用 Docker Compose 启动（包含 PostgreSQL）
docker-compose up --build

# 访问应用
http://localhost:8000
```

## 项目结构

```
rbac-python-cbc/
├── src/                        # 源代码目录
│   ├── main.py                 # 程序入口
│   ├── config/                 # 配置模块
│   ├── core/                   # 核心业务逻辑
│   │   ├── rbac/               # RBAC 核心
│   │   └── auth/               # 认证模块
│   ├── db/                     # 数据库层
│   ├── api/                    # API 接口层
│   ├── utils/                  # 工具模块
│   └── middleware/             # 中间件
├── tests/                      # 测试模块
├── db/migrations/              # 数据库迁移
├── requirements.txt             # 项目依赖
├── setup.py                    # 项目安装配置
├── .env.example                # 环境变量示例
├── .gitignore
└── README.md
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_rbac_manager.py
```

## 代码检查

```bash
# 代码格式化
black src/

# 代码检查
flake8 src/

# 类型检查
mypy src/

# 导入排序
isort src/
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 数据库连接字符串 | - |
| `JWT_SECRET_KEY` | JWT 密钥 | - |
| `DEBUG` | 调试模式 | `False` |
| `CORS_ORIGINS` | CORS 允许的源 | `[]` |

## 许可证

MIT License

## 作者

CodeBuddy
