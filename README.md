# RBAC Python CBC

基于 Python 的 RBAC（基于角色的访问控制）项目，使用 CBC 加密模式保护敏感数据。

## 项目概述

本项目实现了一个安全的 RBAC 系统，具有以下特性：
- 用户-角色-权限的三层权限模型
- 使用 CBC 模式加密敏感数据
- 支持装饰器式的权限验证
- 完整的单元测试覆盖

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from rbac import RBACManager

# 初始化 RBAC 管理器
rbac = RBACManager()

# 添加用户
rbac.add_user('alice')

# 添加角色
rbac.add_role('admin')

# 分配角色
rbac.assign_role('alice', 'admin')

# 检查权限
if rbac.check_permission('alice', 'delete_user'):
    print('Alice 有权限删除用户')
```

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT