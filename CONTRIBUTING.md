# 开发指南

本文档介绍如何为 RBAC Python 项目做出贡献。

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd rbac-python-cbc
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装开发依赖

```bash
pip install -r requirements.txt
```

### 4. 安装预提交钩子（可选）

```bash
pip install pre-commit
pre-commit install
```

## 开发流程

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 编写代码

遵循项目的编码规范：

- 使用 4 空格缩进
- 复杂逻辑添加中文注释
- 使用类型提示
- 编写单元测试

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_rbac_manager.py

# 运行测试并查看覆盖率
pytest --cov=src --cov-report=html
```

### 4. 代码格式化和检查

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

### 5. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能描述"
```

### 6. 推送和创建 Pull Request

```bash
git push origin feature/your-feature-name
```

然后在 GitHub/GitLab 上创建 Pull Request。

## 代码规范

### Python 编码规范

遵循 PEP 8 风格：

- 使用 4 空格缩进（不使用 Tab）
- 每行最大长度 100 字符
- 函数和类使用文档字符串
- 使用类型提示

### 示例

```python
from typing import Optional
from datetime import datetime


class User:
    """用户模型"""
    
    def __init__(
        self,
        username: str,
        email: str,
        created_at: Optional[datetime] = None
    ):
        """
        初始化用户
        
        Args:
            username: 用户名
            email: 邮箱地址
            created_at: 创建时间（可选）
        """
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.utcnow()
    
    def get_full_name(self) -> str:
        """获取用户全名"""
        return f"{self.first_name} {self.last_name}"
```

### 注释规范

- 复杂逻辑添加行内中文注释
- 函数和类使用文档字符串
- 注释解释"为什么"而不是"是什么"

### 错误处理

```python
from src.utils.exceptions import RBACError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def some_function(user_id: int) -> dict:
    """
    执行某个操作
    
    Args:
        user_id: 用户 ID
    
    Returns:
        dict: 操作结果
    
    Raises:
        RBACError: 操作失败时
    """
    try:
        # 执行操作
        result = perform_operation(user_id)
        return result
        
    except Exception as e:
        # 记录详细的错误日志
        logger.error(f"操作失败: user_id={user_id}, error={e}")
        
        # 抛出友好的错误信息
        raise RBACError(f"操作失败: {e}")
```

## 测试规范

### 单元测试

- 每个功能模块都需要单元测试
- 使用 pytest 框架
- 测试文件命名为 `test_*.py`
- 测试函数命名为 `test_*`

### 示例

```python
import pytest
from src.core.rbac.manager import RBACManager
from src.core.rbac.models import User, Role


class TestRBACManager:
    """RBAC 管理器测试类"""
    
    def test_has_role_true(self, db_session):
        """测试检查用户角色 - 存在"""
        # 创建测试数据
        user = User(username="testuser", email="test@example.com")
        role = Role(name="管理员", slug="admin")
        db_session.add_all([user, role])
        db_session.commit()
        
        # 分配角色
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db_session.add(user_role)
        db_session.commit()
        
        # 测试
        manager = RBACManager(db_session)
        assert manager.has_role(user.id, "admin") is True
```

### 集成测试

- 测试 API 端点
- 使用 TestClient
- 测试完整的请求-响应流程

### 性能测试

- 关键功能需要性能测试
- 设定性能基准
- 使用 `@pytest.mark.slow` 标记慢速测试

## Commit 消息规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型（type）

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

### 示例

```
feat(rbac): 添加角色继承支持

- 支持多级角色继承
- 实现继承权限自动获取
- 添加角色继承单元测试

Closes #123
```

## Pull Request 规范

### PR 标题

使用清晰的标题，格式：

```
[类型] 简短描述

例如：
[feat] 添加角色继承功能
[fix] 修复权限检查 bug
```

### PR 描述

包含以下内容：

1. **变更说明**：做了什么
2. **相关 Issue**：关联的 Issue
3. **测试**：如何测试
4. **截图**（如有 UI 变更）

### 示例

```
## 变更说明
添加了角色继承功能，支持 RBAC1 模型。

## 相关 Issue
Closes #45

## 测试
- 运行单元测试：`pytest tests/unit/test_role_inheritance.py`
- 测试通过：✅

## 截图
（可选）
```

## 文档规范

### 更新文档

如果修改了 API，需要更新：

1. `API_EXAMPLES.md`：更新 API 示例
2. `README.md`：更新功能说明
3. `CODEBUDDY.md`：更新设计文档

### 代码文档

- 函数和类添加 docstring
- 使用 Google 风格或 NumPy 风格
- 参数和返回值需要说明

## 发布流程

### 版本号规范

遵循语义化版本：`MAJOR.MINOR.PATCH`

- `MAJOR`：不兼容的 API 变更
- `MINOR`：向后兼容的新功能
- `PATCH`：向后兼容的 bug 修复

### 发布步骤

1. 更新版本号
   - `setup.py`
   - `CODEBUDDY.md`
   
2. 更新 `CHANGELOG.md`

3. 创建 Git 标签

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

4. 构建发布包

```bash
python -m build
```

## 常见问题

### Q: 如何运行项目？

A: 参考 [QUICKSTART.md](QUICKSTART.md)

### Q: 测试失败怎么办？

A: 
1. 检查数据库连接
2. 确保所有依赖已安装
3. 查看错误日志
4. 运行 `pytest -v` 查看详细输出

### Q: 如何添加新的权限？

A: 
1. 在 `scripts/init_data.py` 中添加权限定义
2. 运行 `python scripts/init_data.py` 初始化
3. 在 API 中实现相关逻辑

### Q: 如何自定义约束规则？

A: 参考 `src/core/rbac/constraints.py`，继承 `Constraint` 基类并实现 `check` 方法。

## 获取帮助

- 提交 Issue
- 查看 [API 文档](http://localhost:8000/docs)
- 阅读 [CODEBUDDY.md](CODEBUDDY.md)

## 许可证

提交代码即表示您同意按照项目的许可证（MIT License）发布您的贡献。
