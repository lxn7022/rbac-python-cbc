# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## 项目概述

这是一个基于 Python 的 RBAC（基于角色的访问控制）项目。项目名称 `rbac-python-cbc` 中的 `cbc` 是 CodeBuddy 的缩写。

## 项目结构

```
rbac-python-cbc/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── main.py                 # 程序入口
│   ├── config/                 # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py         # 配置管理（数据库、环境变量等）
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── rbac/               # RBAC 核心
│   │   │   ├── __init__.py
│   │   │   ├── models.py       # 数据模型（User, Role, Permission）
│   │   │   ├── manager.py      # RBAC 管理器（权限检查、角色分配）
│   │   │   ├── permissions.py  # 权限定义和常量
│   │   │   └── constraints.py  # RBAC 约束规则（互斥、基数等）
│   │   └── auth/               # 认证模块
│   │       ├── __init__.py
│   │       ├── models.py       # 认证相关模型
│   │       ├── services.py     # 认证服务（登录、token）
│   │       └── decorators.py   # 装饰器（@require_login）
│   ├── db/                     # 数据库层
│   │   ├── __init__.py
│   │   ├── base.py             # 数据库基类和连接
│   │   ├── repository.py       # 数据访问层
│   │   └── migrations/         # 数据库迁移
│   ├── api/                    # API 接口层
│   │   ├── __init__.py
│   │   ├── routers.py          # 路由定义
│   │   ├── schemas.py          # Pydantic 数据模型
│   │   └── dependencies.py     # 依赖注入
│   ├── utils/                  # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py           # 日志工具
│   │   ├── exceptions.py       # 自定义异常
│   │   └── helpers.py          # 辅助函数
│   └── middleware/             # 中间件
│       ├── __init__.py
│       ├── auth.py             # 认证中间件
│       └── rbac.py             # RBAC 权限中间件
├── tests/                      # 测试模块
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置和 fixtures
│   ├── unit/                   # 单元测试
│   │   ├── test_rbac_manager.py
│   │   ├── test_permissions.py
│   │   └── test_constraints.py
│   ├── integration/            # 集成测试
│   │   ├── test_auth.py
│   │   └── test_api.py
│   └── fixtures/               # 测试数据
│       └── test_data.py
├── requirements.txt             # 项目依赖
├── setup.py                    # 项目安装配置
├── .env.example                # 环境变量示例
├── .gitignore
└── CODEBUDDY.md
```

## 常用命令

### 环境设置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_specific_file.py

# 运行特定测试函数
pytest tests/test_specific_file.py::test_function_name

# 运行测试并显示详细输出
pytest -v

# 运行测试并显示覆盖率
pytest --cov=src --cov-report=html
```

### 代码检查
```bash
# 运行 flake8 代码检查
flake8 src/

# 运行 black 代码格式化
black src/

# 运行 mypy 类型检查
mypy src/

# 运行 isort 导入排序
isort src/
```

### 运行项目
```bash
# 启动开发服务器（FastAPI）
uvicorn src.main:app --reload

# 或使用 Python 模块方式
python -m uvicorn src.main:app --reload

# 运行主程序
python -m src.main

# 或者
python src/main.py
```

## RBAC 模型详解

### RBAC 核心概念

RBAC（Role-Based Access Control，基于角色的访问控制）是一种通过角色来管理用户权限的访问控制模型。

#### 核心实体

1. **用户（User）**
   - 系统中的实际使用者
   - 具有唯一标识符
   - 可以拥有多个角色

2. **角色（Role）**
   - 权限的集合
   - 代表职位、职能或职责
   - 示例：管理员、编辑、访客

3. **权限（Permission）**
   - 对特定资源执行特定操作的许可
   - 通常格式为：`资源:操作`（如 `user:read`）
   - 示例：读取用户数据、创建订单、删除文章

4. **资源（Resource）**
   - 系统中需要保护的对象
   - 可以是实体（用户、订单）或功能（报表、API）

#### 关系

```
用户 ←→ 角色 ←→ 权限
 N:M     N:M     N:M
```

- 用户和角色：多对多关系
- 角色和权限：多对多关系

### RBAC 模型层次

1. **RBAC0（基础模型）**
   - 包含用户、角色、权限的最小集
   - 支持用户-角色和角色-权限的分配

2. **RBAC1（层次模型）**
   - 在 RBAC0 基础上增加角色继承
   - 支持角色间的上下级关系
   - 上级角色继承下级角色的所有权限

3. **RBAC2（约束模型）**
   - 在 RBAC0 基础上增加约束规则
   - 互斥约束：用户不能同时拥有某些角色
   - 基数约束：一个角色最多可分配给 N 个用户
   - 先决条件：拥有角色 A 才能拥有角色 B

4. **RBAC3（统一模型）**
   - 结合 RBAC1 和 RBAC2
   - 支持角色继承和约束规则

### 常用约束类型

1. **静态职责分离（SSD）**
   - 约束：用户不能同时被分配互斥的角色
   - 示例：出纳员和会计不能是同一人

2. **动态职责分离（DSD）**
   - 约束：同一会话中不能激活互斥的角色
   - 示例：用户可以同时有出纳员和会计角色，但不能同时激活

3. **基数约束**
   - 角色基数：限制角色可以分配给的最大用户数
   - 用户基数：限制用户可以拥有的最大角色数

### RBAC 的优势

1. **简化权限管理**
   - 不需要单独为每个用户分配权限
   - 只需管理角色-权限的映射

2. **灵活性好**
   - 用户职责变更时，只需调整角色
   - 新增权限时，只需更新相关角色

3. **可审计性强**
   - 清晰的角色和权限层次
   - 便于追踪权限使用情况

4. **符合最小权限原则**
   - 用户只能获得其角色所需的权限

## 架构设计

### 核心模块说明

#### core/rbac/models.py
数据模型定义，包含 User、Role、Permission 及关联模型。

#### core/rbac/manager.py
RBAC 管理器，核心功能：
- `has_permission(user_id, resource, action)`：检查权限
- `has_role(user_id, role_name)`：检查角色
- `assign_role(user_id, role_id)`：分配角色
- `revoke_role(user_id, role_id)`：撤销角色
- `grant_permission(role_id, permission_id)`：授予权限
- `revoke_permission(role_id, permission_id)`：撤销权限
- `get_all_permissions(user_id)`：获取用户所有权限

#### core/rbac/permissions.py
权限常量定义和枚举，预定义系统权限。

#### core/rbac/constraints.py
实现 RBAC2 约束模型，包括互斥约束、基数约束、先决条件约束。

### 核心模块详细设计

#### 1. core/rbac/models.py - 数据模型设计

使用 SQLAlchemy ORM 定义数据库模型，映射到 PostgreSQL 表结构。

**文件结构：**
```python
"""
RBAC 数据模型
定义用户、角色、权限及关联关系
"""

from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text, Integer,
    ForeignKey, TIMESTAMP, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from db.base import Base
from datetime import datetime
```

**核心类设计：**

```python
# ============================================================================
# User 模型
# ============================================================================
class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 基本信息
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    
    # 状态字段
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # 时间戳
    last_login_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# ============================================================================
# Role 模型
# ============================================================================
class Role(Base):
    """角色模型（支持继承）"""
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'public'}
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 基本信息
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # 系统标识和优先级
    is_system = Column(Boolean, default=False, index=True)
    priority = Column(Integer, default=0, index=True)
    
    # 角色继承（RBAC1）
    parent_id = Column(BigInteger, ForeignKey('public.roles.id', ondelete='SET NULL'), index=True)
    
    # 时间戳
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    parent = relationship('Role', remote_side=[id], backref='children')
    users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    permissions = relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    def get_all_permissions(self):
        """获取角色所有权限（包括继承的权限）"""
        # 实现递归获取继承的权限
        pass


# ============================================================================
# Permission 模型
# ============================================================================
class Permission(Base):
    """权限模型"""
    __tablename__ = 'permissions'
    __table_args__ = (
        UniqueConstraint('resource', 'action', name='unique_resource_action'),
        {'schema': 'public'}
    )
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 权限定义：资源:操作
    resource = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    
    # 描述和分组
    description = Column(Text)
    is_system = Column(Boolean, default=False, index=True)
    module = Column(String(50), index=True)
    
    # 时间戳
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    roles = relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Permission(id={self.id}, resource='{self.resource}', action='{self.action}')>"
    
    @property
    def full_name(self):
        """返回完整权限名称（如：user:read）"""
        return f"{self.resource}:{self.action}"


# ============================================================================
# UserRole 关联模型
# ============================================================================
class UserRole(Base):
    """用户-角色关联模型"""
    __tablename__ = 'user_roles'
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
        {'schema': 'public'}
    )
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 外键
    user_id = Column(BigInteger, ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(BigInteger, ForeignKey('public.roles.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 审计字段
    assigned_by = Column(BigInteger, ForeignKey('public.users.id', ondelete='SET NULL'))
    assigned_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # 过期时间和状态
    expires_at = Column(TIMESTAMP(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    
    # 关系
    user = relationship('User', foreign_keys=[user_id], back_populates='roles')
    role = relationship('Role', back_populates='users')
    
    def is_expired(self):
        """检查角色是否过期"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


# ============================================================================
# RolePermission 关联模型
# ============================================================================
class RolePermission(Base):
    """角色-权限关联模型"""
    __tablename__ = 'role_permissions'
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),
        {'schema': 'public'}
    )
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 外键
    role_id = Column(BigInteger, ForeignKey('public.roles.id', ondelete='CASCADE'), nullable=False, index=True)
    permission_id = Column(BigInteger, ForeignKey('public.permissions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 审计字段
    granted_by = Column(BigInteger, ForeignKey('public.users.id', ondelete='SET NULL'))
    granted_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # 状态
    is_active = Column(Boolean, default=True, index=True)
    
    # 关系
    role = relationship('Role', back_populates='permissions')
    permission = relationship('Permission', back_populates='roles')


# ============================================================================
# RBACConstraint 模型
# ============================================================================
class RBACConstraint(Base):
    """RBAC 约束规则模型（RBAC2）"""
    __tablename__ = 'rbac_constraints'
    __table_args__ = {'schema': 'public'}
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 约束定义
    constraint_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # 配置（JSONB 格式）
    config = Column(JSONB, nullable=False)
    
    # 状态
    is_active = Column(Boolean, default=True, index=True)
    
    # 时间戳
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RBACConstraint(id={self.id}, name='{self.name}', type='{self.constraint_type}')>"
```

**设计要点：**
- ✅ 使用 SQLAlchemy ORM 映射数据库表
- ✅ 支持角色继承（Role.parent_id）
- ✅ 审计字段（assigned_by、granted_by）
- ✅ 临时角色支持（expires_at）
- ✅ 软删除支持（is_active）
- ✅ JSONB 存储约束配置

---

#### 2. core/rbac/manager.py - RBAC 管理器设计

RBAC 核心业务逻辑，提供权限检查、角色管理、权限管理等功能。

**文件结构：**
```python
"""
RBAC 管理器
提供权限检查、角色管理、权限管理等核心功能
"""

from typing import List, Optional, Dict, Set
from sqlalchemy.orm import Session
from datetime import datetime
from core.rbac.models import User, Role, Permission, UserRole, RolePermission
from core.rbac.constraints import ConstraintManager
from utils.logger import get_logger
from utils.exceptions import (
    RBACError, PermissionDeniedError, RoleNotFoundError,
    ConstraintViolationError
)

logger = get_logger(__name__)
```

**核心类设计：**

```python
class RBACManager:
    """
    RBAC 管理器
    
    负责：
    1. 权限检查
    2. 角色分配与撤销
    3. 权限授予与撤销
    4. 约束检查
    """
    
    def __init__(self, db: Session):
        """
        初始化 RBAC 管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.constraint_manager = ConstraintManager(db)
    
    # ========================================================================
    # 权限检查方法
    # ========================================================================
    
    def has_permission(
        self,
        user_id: int,
        resource: str,
        action: str,
        check_inheritance: bool = True
    ) -> bool:
        """
        检查用户是否拥有特定权限
        
        Args:
            user_id: 用户ID
            resource: 资源名称（如：user, article）
            action: 操作类型（如：read, write）
            check_inheritance: 是否检查继承的角色权限
        
        Returns:
            bool: 是否拥有权限
        
        Example:
            >>> manager.has_permission(1, 'user', 'read')
            True
        """
        try:
            # 获取用户所有权限
            permissions = self.get_all_permissions(
                user_id,
                include_inherited=check_inheritance
            )
            
            # 检查是否存在匹配的权限
            permission_key = f"{resource}:{action}"
            return permission_key in permissions
            
        except Exception as e:
            logger.error(f"检查权限失败: user_id={user_id}, resource={resource}, action={action}, error={e}")
            raise RBACError(f"权限检查失败: {e}")
    
    def has_role(self, user_id: int, role_slug: str) -> bool:
        """
        检查用户是否拥有特定角色
        
        Args:
            user_id: 用户ID
            role_slug: 角色标识符（如：admin, editor）
        
        Returns:
            bool: 是否拥有角色
        """
        try:
            query = self.db.query(UserRole).join(Role).filter(
                UserRole.user_id == user_id,
                Role.slug == role_slug,
                UserRole.is_active == True,
                (UserRole.expires_at.is_(None)) | (UserRole.expires_at > datetime.utcnow())
            )
            return query.first() is not None
            
        except Exception as e:
            logger.error(f"检查角色失败: user_id={user_id}, role_slug={role_slug}, error={e}")
            raise RBACError(f"角色检查失败: {e}")
    
    def get_all_permissions(
        self,
        user_id: int,
        include_inherited: bool = True
    ) -> Set[str]:
        """
        获取用户所有权限
        
        Args:
            user_id: 用户ID
            include_inherited: 是否包含继承的角色权限
        
        Returns:
            Set[str]: 权限集合（格式：resource:action）
        
        Example:
            >>> permissions = manager.get_all_permissions(1)
            {'user:read', 'user:write', 'article:read'}
        """
        try:
            permissions = set()
            
            # 1. 获取用户直接拥有的角色
            user_roles = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                (UserRole.expires_at.is_(None)) | (UserRole.expires_at > datetime.utcnow())
            ).all()
            
            # 2. 遍历每个角色获取权限
            for user_role in user_roles:
                role = user_role.role
                
                # 获取角色的直接权限
                role_permissions = self.db.query(RolePermission).filter(
                    RolePermission.role_id == role.id,
                    RolePermission.is_active == True
                ).all()
                
                for rp in role_permissions:
                    perm = rp.permission
                    permissions.add(f"{perm.resource}:{perm.action}")
                
                # 3. 如果启用继承，递归获取父角色权限
                if include_inherited and role.parent_id:
                    parent_permissions = self._get_inherited_permissions(role.parent_id)
                    permissions.update(parent_permissions)
            
            return permissions
            
        except Exception as e:
            logger.error(f"获取用户权限失败: user_id={user_id}, error={e}")
            raise RBACError(f"获取权限失败: {e}")
    
    def _get_inherited_permissions(self, role_id: int) -> Set[str]:
        """递归获取继承的权限"""
        permissions = set()
        
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return permissions
        
        # 获取当前角色权限
        role_permissions = self.db.query(RolePermission).filter(
            RolePermission.role_id == role.id,
            RolePermission.is_active == True
        ).all()
        
        for rp in role_permissions:
            perm = rp.permission
            permissions.add(f"{perm.resource}:{perm.action}")
        
        # 递归获取父角色权限
        if role.parent_id:
            parent_permissions = self._get_inherited_permissions(role.parent_id)
            permissions.update(parent_permissions)
        
        return permissions
    
    # ========================================================================
    # 角色管理方法
    # ========================================================================
    
    def assign_role(
        self,
        user_id: int,
        role_id: int,
        assigned_by: Optional[int] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            assigned_by: 分配人ID
            expires_at: 过期时间（可选）
        
        Returns:
            UserRole: 用户角色关联记录
        
        Raises:
            ConstraintViolationError: 违反约束规则
        """
        try:
            # 1. 检查约束规则
            self.constraint_manager.check_constraints(
                user_id=user_id,
                role_id=role_id,
                action='assign'
            )
            
            # 2. 检查是否已存在
            existing = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            ).first()
            
            if existing:
                # 如果已存在但不活跃，重新激活
                if not existing.is_active:
                    existing.is_active = True
                    existing.assigned_at = datetime.utcnow()
                    existing.expires_at = expires_at
                    existing.assigned_by = assigned_by
                    self.db.commit()
                    return existing
                else:
                    logger.warning(f"用户已拥有该角色: user_id={user_id}, role_id={role_id}")
                    return existing
            
            # 3. 创建新的关联
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
                expires_at=expires_at,
                is_active=True
            )
            
            self.db.add(user_role)
            self.db.commit()
            
            logger.info(f"分配角色成功: user_id={user_id}, role_id={role_id}")
            return user_role
            
        except ConstraintViolationError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"分配角色失败: user_id={user_id}, role_id={role_id}, error={e}")
            raise RBACError(f"分配角色失败: {e}")
    
    def revoke_role(self, user_id: int, role_id: int) -> bool:
        """
        撤销用户的角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
        
        Returns:
            bool: 是否成功撤销
        """
        try:
            user_role = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_active == True
            ).first()
            
            if not user_role:
                logger.warning(f"未找到用户角色关联: user_id={user_id}, role_id={role_id}")
                return False
            
            # 软删除（设置为不活跃）
            user_role.is_active = False
            self.db.commit()
            
            logger.info(f"撤销角色成功: user_id={user_id}, role_id={role_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"撤销角色失败: user_id={user_id}, role_id={role_id}, error={e}")
            raise RBACError(f"撤销角色失败: {e}")
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """
        获取用户的所有角色
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[Role]: 角色列表
        """
        try:
            user_roles = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                (UserRole.expires_at.is_(None)) | (UserRole.expires_at > datetime.utcnow())
            ).all()
            
            return [ur.role for ur in user_roles]
            
        except Exception as e:
            logger.error(f"获取用户角色失败: user_id={user_id}, error={e}")
            raise RBACError(f"获取角色失败: {e}")
    
    # ========================================================================
    # 权限管理方法
    # ========================================================================
    
    def grant_permission(
        self,
        role_id: int,
        permission_id: int,
        granted_by: Optional[int] = None
    ) -> RolePermission:
        """
        为角色授予权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            granted_by: 授权人ID
        
        Returns:
            RolePermission: 角色权限关联记录
        """
        try:
            # 检查是否已存在
            existing = self.db.query(RolePermission).filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            ).first()
            
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.granted_at = datetime.utcnow()
                    existing.granted_by = granted_by
                    self.db.commit()
                    return existing
                else:
                    logger.warning(f"角色已拥有该权限: role_id={role_id}, permission_id={permission_id}")
                    return existing
            
            # 创建新的关联
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id,
                granted_by=granted_by,
                is_active=True
            )
            
            self.db.add(role_permission)
            self.db.commit()
            
            logger.info(f"授予权限成功: role_id={role_id}, permission_id={permission_id}")
            return role_permission
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"授予权限失败: role_id={role_id}, permission_id={permission_id}, error={e}")
            raise RBACError(f"授予权限失败: {e}")
    
    def revoke_permission(self, role_id: int, permission_id: int) -> bool:
        """
        撤销角色的权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
        
        Returns:
            bool: 是否成功撤销
        """
        try:
            role_permission = self.db.query(RolePermission).filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
                RolePermission.is_active == True
            ).first()
            
            if not role_permission:
                logger.warning(f"未找到角色权限关联: role_id={role_id}, permission_id={permission_id}")
                return False
            
            # 软删除
            role_permission.is_active = False
            self.db.commit()
            
            logger.info(f"撤销权限成功: role_id={role_id}, permission_id={permission_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"撤销权限失败: role_id={role_id}, permission_id={permission_id}, error={e}")
            raise RBACError(f"撤销权限失败: {e}")
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def check_multiple_permissions(
        self,
        user_id: int,
        permissions: List[tuple]
    ) -> Dict[str, bool]:
        """
        批量检查权限
        
        Args:
            user_id: 用户ID
            permissions: 权限列表 [(resource, action), ...]
        
        Returns:
            Dict[str, bool]: 权限检查结果
        
        Example:
            >>> result = manager.check_multiple_permissions(1, [
            ...     ('user', 'read'),
            ...     ('article', 'write')
            ... ])
            {'user:read': True, 'article:write': False}
        """
        try:
            user_permissions = self.get_all_permissions(user_id)
            
            result = {}
            for resource, action in permissions:
                permission_key = f"{resource}:{action}"
                result[permission_key] = permission_key in user_permissions
            
            return result
            
        except Exception as e:
            logger.error(f"批量检查权限失败: user_id={user_id}, error={e}")
            raise RBACError(f"批量检查权限失败: {e}")
```

**设计要点：**
- ✅ 权限检查支持角色继承
- ✅ 角色分配前进行约束检查
- ✅ 支持临时角色（过期时间）
- ✅ 软删除机制
- ✅ 完整的错误处理和日志记录
- ✅ 批量权限检查支持

---

#### 3. core/rbac/permissions.py - 权限定义设计

定义系统权限常量和枚举，便于代码中引用。

**文件结构：**
```python
"""
权限定义和常量
预定义系统权限，便于代码中引用
"""

from enum import Enum
from typing import List, Dict


# ============================================================================
# 权限枚举
# ============================================================================

class Resource(Enum):
    """资源枚举"""
    USER = 'user'
    ROLE = 'role'
    PERMISSION = 'permission'
    ARTICLE = 'article'
    ORDER = 'order'
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有资源"""
        return [item.value for item in cls]


class Action(Enum):
    """操作枚举"""
    READ = 'read'
    WRITE = 'write'
    CREATE = 'create'
    DELETE = 'delete'
    MANAGE = 'manage'
    ASSIGN = 'assign'
    REVOKE = 'revoke'
    PUBLISH = 'publish'
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有操作"""
        return [item.value for item in cls]


class Module(Enum):
    """模块枚举"""
    AUTH = 'auth'
    RBAC = 'rbac'
    CONTENT = 'content'
    ORDER = 'order'
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有模块"""
        return [item.value for item in cls]


# ============================================================================
# 权限常量类
# ============================================================================

class Permission:
    """
    权限常量类
    
    使用示例：
        Permission.USER_READ
        Permission.ARTICLE_WRITE
    """
    
    # 用户相关权限
    USER_READ = 'user:read'
    USER_WRITE = 'user:write'
    USER_CREATE = 'user:create'
    USER_DELETE = 'user:delete'
    USER_MANAGE = 'user:manage'
    
    # 角色相关权限
    ROLE_READ = 'role:read'
    ROLE_WRITE = 'role:write'
    ROLE_CREATE = 'role:create'
    ROLE_DELETE = 'role:delete'
    ROLE_MANAGE = 'role:manage'
    
    # 权限相关权限
    PERMISSION_READ = 'permission:read'
    PERMISSION_ASSIGN = 'permission:assign'
    PERMISSION_REVOKE = 'permission:revoke'
    
    # 文章相关权限
    ARTICLE_READ = 'article:read'
    ARTICLE_WRITE = 'article:write'
    ARTICLE_DELETE = 'article:delete'
    ARTICLE_PUBLISH = 'article:publish'
    
    # 订单相关权限
    ORDER_READ = 'order:read'
    ORDER_WRITE = 'order:write'
    ORDER_DELETE = 'order:delete'
    ORDER_MANAGE = 'order:manage'


# ============================================================================
# 角色常量类
# ============================================================================

class Role:
    """
    角色常量类
    
    使用示例：
        Role.SUPER_ADMIN
        Role.ADMIN
    """
    
    SUPER_ADMIN = 'super-admin'
    ADMIN = 'admin'
    EDITOR = 'editor'
    USER = 'user'
    GUEST = 'guest'


# ============================================================================
# 权限分组定义
# ============================================================================

PERMISSION_GROUPS: Dict[str, List[str]] = {
    '用户管理': [
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_CREATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE,
    ],
    '角色管理': [
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_CREATE,
        Permission.ROLE_DELETE,
        Permission.ROLE_MANAGE,
    ],
    '权限管理': [
        Permission.PERMISSION_READ,
        Permission.PERMISSION_ASSIGN,
        Permission.PERMISSION_REVOKE,
    ],
    '内容管理': [
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
    ],
    '订单管理': [
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ORDER_MANAGE,
    ],
}


# ============================================================================
# 默认角色权限映射
# ============================================================================

DEFAULT_ROLE_PERMISSIONS: Dict[str, List[str]] = {
    Role.SUPER_ADMIN: [
        # 超级管理员拥有所有权限
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_CREATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE,
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_CREATE,
        Permission.ROLE_DELETE,
        Permission.ROLE_MANAGE,
        Permission.PERMISSION_READ,
        Permission.PERMISSION_ASSIGN,
        Permission.PERMISSION_REVOKE,
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ORDER_MANAGE,
    ],
    Role.ADMIN: [
        # 管理员（无删除用户和角色权限）
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_CREATE,
        Permission.USER_MANAGE,
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_CREATE,
        Permission.ROLE_MANAGE,
        Permission.PERMISSION_READ,
        Permission.PERMISSION_ASSIGN,
        Permission.PERMISSION_REVOKE,
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ORDER_MANAGE,
    ],
    Role.EDITOR: [
        # 编辑（内容管理权限）
        Permission.USER_READ,
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
    ],
    Role.USER: [
        # 普通用户（基础读取权限）
        Permission.ARTICLE_READ,
        Permission.ORDER_READ,
    ],
    Role.GUEST: [
        # 访客（无权限）
    ],
}


# ============================================================================
# 辅助函数
# ============================================================================

def parse_permission(permission_str: str) -> tuple:
    """
    解析权限字符串
    
    Args:
        permission_str: 权限字符串（如：'user:read'）
    
    Returns:
        tuple: (resource, action)
    
    Example:
        >>> parse_permission('user:read')
        ('user', 'read')
    """
    parts = permission_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"无效的权限格式: {permission_str}")
    return parts[0], parts[1]


def format_permission(resource: str, action: str) -> str:
    """
    格式化权限字符串
    
    Args:
        resource: 资源名称
        action: 操作类型
    
    Returns:
        str: 权限字符串
    
    Example:
        >>> format_permission('user', 'read')
        'user:read'
    """
    return f"{resource}:{action}"
```

**设计要点：**
- ✅ 使用枚举类定义资源和操作
- ✅ 权限常量便于代码引用
- ✅ 权限分组便于管理
- ✅ 默认角色权限映射
- ✅ 辅助函数解析权限

---

#### 4. core/rbac/constraints.py - 约束规则设计

实现 RBAC2 约束模型，包括互斥约束、基数约束、先决条件约束。

**文件结构：**
```python
"""
RBAC 约束规则
实现 RBAC2 约束模型
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.rbac.models import User, Role, UserRole, RBACConstraint
from utils.logger import get_logger
from utils.exceptions import ConstraintViolationError

logger = get_logger(__name__)


# ============================================================================
# 约束基类
# ============================================================================

class Constraint(ABC):
    """
    约束基类
    
    所有约束类型必须继承此类并实现 check 方法
    """
    
    def __init__(self, db: Session, config: Dict[str, Any]):
        """
        初始化约束
        
        Args:
            db: 数据库会话
            config: 约束配置
        """
        self.db = db
        self.config = config
    
    @abstractmethod
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """
        检查约束
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            action: 操作类型（assign/revoke）
        
        Returns:
            bool: 是否通过约束检查
        
        Raises:
            ConstraintViolationError: 违反约束
        """
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """获取错误消息"""
        pass


# ============================================================================
# 互斥约束（Mutually Exclusive）
# ============================================================================

class MutuallyExclusiveConstraint(Constraint):
    """
    互斥约束（静态职责分离 - SSD）
    
    用户不能同时拥有互斥的角色
    """
    
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """检查互斥约束"""
        if action != 'assign':
            return True
        
        # 获取互斥角色列表
        mutually_exclusive_roles = self.config.get('roles', [])
        check_type = self.config.get('check_type', 'static')  # static 或 dynamic
        
        # 获取当前角色标识
        current_role = self.db.query(Role).filter(Role.id == role_id).first()
        if not current_role:
            return True
        
        # 检查当前角色是否在互斥列表中
        if current_role.slug not in mutually_exclusive_roles:
            return True
        
        # 获取用户当前拥有的角色
        user_roles = self.db.query(UserRole).join(Role).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        ).all()
        
        # 检查用户是否拥有互斥角色
        for user_role in user_roles:
            if user_role.role.slug in mutually_exclusive_roles:
                # 发现互斥角色
                if user_role.role.slug != current_role.slug:
                    raise ConstraintViolationError(
                        f"违反互斥约束：用户已拥有角色 '{user_role.role.name}'，"
                        f"不能同时拥有角色 '{current_role.name}'"
                    )
        
        return True
    
    def get_error_message(self) -> str:
        return f"违反互斥约束：不能同时拥有这些角色 {self.config.get('roles', [])}"


# ============================================================================
# 基数约束（Cardinality）
# ============================================================================

class CardinalityConstraint(Constraint):
    """
    基数约束
    
    限制角色可以分配给的最大用户数
    """
    
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """检查基数约束"""
        if action != 'assign':
            return True
        
        # 获取角色限制
        role_slug = self.config.get('role')
        max_users = self.config.get('max_users', 1)
        
        # 获取当前角色
        current_role = self.db.query(Role).filter(Role.id == role_id).first()
        if not current_role:
            return True
        
        # 只检查指定的角色
        if current_role.slug != role_slug:
            return True
        
        # 统计当前拥有该角色的用户数
        current_count = self.db.query(func.count(UserRole.id)).filter(
            UserRole.role_id == role_id,
            UserRole.is_active == True
        ).scalar()
        
        # 检查是否超过限制
        if current_count >= max_users:
            # 检查用户是否已经拥有该角色
            existing = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_active == True
            ).first()
            
            if not existing:
                raise ConstraintViolationError(
                    f"违反基数约束：角色 '{current_role.name}' 最多只能分配给 {max_users} 个用户，"
                    f"当前已有 {current_count} 个用户"
                )
        
        return True
    
    def get_error_message(self) -> str:
        return f"违反基数约束：角色 '{self.config.get('role')}' 最多分配给 {self.config.get('max_users')} 个用户"


# ============================================================================
# 先决条件约束（Prerequisite）
# ============================================================================

class PrerequisiteConstraint(Constraint):
    """
    先决条件约束
    
    用户必须先拥有某个角色才能分配另一个角色
    """
    
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """检查先决条件约束"""
        if action != 'assign':
            return True
        
        # 获取先决条件配置
        role_slug = self.config.get('role')
        required_roles = self.config.get('required_roles', [])
        
        # 获取当前角色
        current_role = self.db.query(Role).filter(Role.id == role_id).first()
        if not current_role:
            return True
        
        # 只检查指定的角色
        if current_role.slug != role_slug:
            return True
        
        # 获取用户当前拥有的角色
        user_roles = self.db.query(UserRole).join(Role).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        ).all()
        
        user_role_slugs = {ur.role.slug for ur in user_roles}
        
        # 检查是否满足所有先决条件
        missing_roles = []
        for required_role_slug in required_roles:
            if required_role_slug not in user_role_slugs:
                missing_roles.append(required_role_slug)
        
        if missing_roles:
            raise ConstraintViolationError(
                f"违反先决条件约束：分配角色 '{current_role.name}' 需要先拥有角色 {missing_roles}"
            )
        
        return True
    
    def get_error_message(self) -> str:
        return f"违反先决条件约束：需要先拥有角色 {self.config.get('required_roles', [])}"


# ============================================================================
# 约束管理器
# ============================================================================

class ConstraintManager:
    """
    约束管理器
    
    负责加载和执行所有约束规则
    """
    
    # 约束类型映射
    CONSTRAINT_TYPES = {
        'mutually_exclusive': MutuallyExclusiveConstraint,
        'cardinality': CardinalityConstraint,
        'prerequisite': PrerequisiteConstraint,
    }
    
    def __init__(self, db: Session):
        """
        初始化约束管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self._constraints_cache = None
    
    def load_constraints(self, use_cache: bool = True) -> List[Constraint]:
        """
        加载所有活跃的约束规则
        
        Args:
            use_cache: 是否使用缓存
        
        Returns:
            List[Constraint]: 约束对象列表
        """
        if use_cache and self._constraints_cache is not None:
            return self._constraints_cache
        
        constraints = []
        
        # 从数据库加载约束
        db_constraints = self.db.query(RBACConstraint).filter(
            RBACConstraint.is_active == True
        ).all()
        
        for db_constraint in db_constraints:
            constraint_type = db_constraint.constraint_type
            constraint_class = self.CONSTRAINT_TYPES.get(constraint_type)
            
            if constraint_class:
                constraint = constraint_class(self.db, db_constraint.config)
                constraints.append(constraint)
            else:
                logger.warning(f"未知的约束类型: {constraint_type}")
        
        if use_cache:
            self._constraints_cache = constraints
        
        return constraints
    
    def check_constraints(
        self,
        user_id: int,
        role_id: int,
        action: str
    ) -> bool:
        """
        检查所有约束
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            action: 操作类型（assign/revoke）
        
        Returns:
            bool: 是否通过所有约束检查
        
        Raises:
            ConstraintViolationError: 违反约束
        """
        try:
            constraints = self.load_constraints()
            
            for constraint in constraints:
                constraint.check(user_id, role_id, action)
            
            logger.debug(f"约束检查通过: user_id={user_id}, role_id={role_id}, action={action}")
            return True
            
        except ConstraintViolationError:
            raise
        except Exception as e:
            logger.error(f"约束检查失败: user_id={user_id}, role_id={role_id}, action={action}, error={e}")
            raise
    
    def refresh_cache(self):
        """刷新约束缓存"""
        self._constraints_cache = None
        self.load_constraints(use_cache=True)
    
    def add_constraint(
        self,
        constraint_type: str,
        name: str,
        description: str,
        config: Dict[str, Any]
    ) -> RBACConstraint:
        """
        添加新的约束规则
        
        Args:
            constraint_type: 约束类型
            name: 约束名称
            description: 约束描述
            config: 约束配置
        
        Returns:
            RBACConstraint: 约束记录
        """
        try:
            constraint = RBACConstraint(
                constraint_type=constraint_type,
                name=name,
                description=description,
                config=config,
                is_active=True
            )
            
            self.db.add(constraint)
            self.db.commit()
            
            # 刷新缓存
            self.refresh_cache()
            
            logger.info(f"添加约束成功: name={name}, type={constraint_type}")
            return constraint
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加约束失败: name={name}, error={e}")
            raise
```

**设计要点：**
- ✅ 抽象基类定义约束接口
- ✅ 三种约束类型实现
- ✅ 约束管理器统一管理
- ✅ 支持缓存提升性能
- ✅ 动态加载约束配置
- ✅ 完整的错误处理

---

### 模块间协作流程

```
用户请求权限检查
       ↓
┌──────────────────┐
│  RBACManager     │
│  has_permission  │
└────────┬─────────┘
         │
         ├─→ 查询用户角色（models.py: User, UserRole）
         │
         ├─→ 检查角色过期状态
         │
         ├─→ 获取角色权限（models.py: RolePermission）
         │
         └─→ 递归获取继承权限（Role.parent_id）
                   ↓
            返回权限检查结果


用户请求分配角色
       ↓
┌──────────────────┐
│  RBACManager     │
│  assign_role     │
└────────┬─────────┘
         │
         ├─→ 加载约束规则（constraints.py）
         │
         ├─→ 执行约束检查
         │    ├─→ MutuallyExclusiveConstraint
         │    ├─→ CardinalityConstraint
         │    └─→ PrerequisiteConstraint
         │
         ├─→ 检查通过 → 创建 UserRole
         │
         └─→ 返回结果
```

#### core/auth/services.py
认证服务，包括：
- 用户认证
- JWT Token 生成和验证
- 密码加密（使用 bcrypt）

#### core/auth/decorators.py
装饰器工具：
- `@require_login`：需要登录
- `@require_permission(resource, action)`：需要特定权限
- `@require_role(role_name)`：需要特定角色

#### db/repository.py
数据访问层，封装数据库操作，提供统一的 CRUD 接口。

#### api/schemas.py
Pydantic 数据验证模型，定义请求/响应模型。

### 模块依赖关系

```
main.py
  └─> api/routers.py
        ├─> api/schemas.py
        ├─> api/dependencies.py
        └─> core/
              ├─> rbac/manager.py
              │     ├─> db/repository.py
              │     ├─> rbac/models.py
              │     ├─> rbac/permissions.py
              │     └─> rbac/constraints.py
              └─> auth/services.py
                    ├─> db/repository.py
                    └─> auth/models.py

config/settings.py (被所有模块引用)
db/base.py (数据库基类，被 repository 使用)
utils/logger.py (全局日志工具)
utils/exceptions.py (自定义异常)
```

### 设计原则

1. **分层架构**
   - API 层 → 业务逻辑层 → 数据访问层
   - 每层职责单一，易于测试和维护

2. **依赖注入**
   - 使用 FastAPI 的依赖注入
   - 便于测试和解耦

3. **单一职责**
   - 每个模块职责明确
   - RBAC 核心逻辑独立于认证和 API

4. **可扩展性**
   - 支持自定义约束规则
   - 支持多种认证方式

5. **测试友好**
   - 模块化设计便于单元测试
   - 提供测试 fixtures

## 开发注意事项

### 编码规范

- 遵循 PEP 8 编码风格
- 使用 4 空格缩进（不使用 Tab）
- 复杂逻辑添加中文注释
- 始终使用 try-catch 包裹可能出错的代码

### 测试

- 所有新功能必须包含单元测试
- 测试覆盖率目标：80% 以上
- 使用 pytest 作为测试框架

### 安全

- 永远不要在代码中硬编码密钥或密码
- 敏感信息应通过环境变量或配置文件管理
- 加密密钥应妥善存储，使用密钥管理服务或安全存储

## 依赖管理

### 核心依赖

- `fastapi`：Web 框架（高性能、异步支持）
- `sqlalchemy`：ORM
- `alembic`：数据库迁移
- `pydantic`：数据验证
- `pyjwt`：JWT Token
- `bcrypt`：密码加密
- `pytest`：测试框架
- `python-dotenv`：环境变量管理

### 可选依赖

- `redis`：缓存（权限缓存）
- `celery`：异步任务
- `uvicorn`：ASGI 服务器

### 开发依赖

- `pytest-cov`：测试覆盖率
- `black`：代码格式化
- `flake8`：代码检查
- `mypy`：类型检查
- `isort`：导入排序

## 环境变量

建议创建 `.env` 文件（不提交到版本控制）：

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
DEBUG=False
LOG_LEVEL=INFO

# 可选：Redis 配置
REDIS_URL=redis://localhost:6379/0
```

## 数据库设计

### 数据库表结构概览

本系统使用 PostgreSQL 作为数据库，设计了完整的 RBAC 表结构。

#### 表关系图

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐
│   users     │       │    roles    │       │ permissions  │
├─────────────┤       ├─────────────┤       ├──────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)      │
│ username    │       │ name        │       │ resource     │
│ email       │       │ slug        │       │ action       │
│ password_   │       │ parent_id   │       │ description  │
│ full_name   │       │ priority    │       │ module       │
└──────┬──────┘       └──────┬──────┘       └───────┬──────┘
       │                     │                      │
       │     ┌───────────────┴──────────────┐       │
       │     │                              │       │
       ▼     ▼                              ▼       ▼
┌─────────────────┐                ┌────────────────────┐
│   user_roles    │                │ role_permissions   │
├─────────────────┤                ├────────────────────┤
│ user_id (FK)    │                │ role_id (FK)       │
│ role_id (FK)    │                │ permission_id (FK) │
│ assigned_by     │                │ granted_by         │
│ expires_at      │                │ is_active          │
│ is_active       │                └────────────────────┘
└─────────────────┘

┌──────────────────────┐
│  rbac_constraints    │
├──────────────────────┤
│ id (PK)              │
│ constraint_type      │
│ name                 │
│ config (JSONB)       │
│ is_active            │
└──────────────────────┘
```

### 核心表设计

#### 1. users 表（用户表）

```sql
CREATE TABLE public.users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,      -- bcrypt 加密
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,           -- 账户状态
    is_verified BOOLEAN DEFAULT false,        -- 邮箱验证状态
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT valid_username CHECK (char_length(username) >= 3)
);
```

**设计要点：**
- 使用 `BIGSERIAL` 支持大规模用户
- 邮箱格式约束（正则表达式）
- 用户名最小长度约束
- 自动更新时间戳（触发器）
- 索引优化：email、username、is_active、created_at

#### 2. roles 表（角色表）

```sql
CREATE TABLE public.roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,         -- 用于代码引用
    description TEXT,
    is_system BOOLEAN DEFAULT false,          -- 系统角色不可删除
    priority INTEGER DEFAULT 0,               -- 权限合并优先级
    parent_id BIGINT REFERENCES public.roles(id) ON DELETE SET NULL,  -- 角色继承（RBAC1）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_name CHECK (char_length(name) >= 2),
    CONSTRAINT valid_slug CHECK (slug ~* '^[a-z0-9-]+$')
);
```

**设计要点：**
- 支持 RBAC1 角色继承：`parent_id` 字段实现角色层级
- `slug` 字段用于代码中引用角色（如 `'super-admin'`）
- `priority` 用于权限冲突时的优先级判断
- `is_system` 保护系统关键角色
- 索引优化：slug、parent_id、is_system、priority

**角色继承示例：**
```
超级管理员 (priority: 100)
    └── 管理员 (priority: 80)
            └── 编辑 (priority: 60)
                    └── 普通用户 (priority: 40)
                            └── 访客 (priority: 20)
```

#### 3. permissions 表（权限表）

```sql
CREATE TABLE public.permissions (
    id BIGSERIAL PRIMARY KEY,
    resource VARCHAR(50) NOT NULL,            -- 资源名称（如：user, article）
    action VARCHAR(50) NOT NULL,              -- 操作类型（如：read, write）
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    module VARCHAR(50),                       -- 所属模块（如：auth, content）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_resource CHECK (char_length(resource) >= 2),
    CONSTRAINT valid_action CHECK (char_length(action) >= 2),
    CONSTRAINT unique_resource_action UNIQUE (resource, action)  -- 资源+操作唯一
);
```

**设计要点：**
- 权限格式：`资源:操作`（如 `user:read`）
- 资源作为字段而非独立表：简化设计，适合大多数场景
- `module` 字段支持按模块分组管理权限
- 复合唯一约束：`(resource, action)` 组合唯一
- 索引优化：resource、action、module、复合索引

**权限示例：**
```
user:read      - 读取用户信息
user:write     - 编辑用户信息
user:delete    - 删除用户
article:read   - 读取文章
article:write  - 创建/编辑文章
order:manage   - 管理订单
```

#### 4. user_roles 表（用户-角色关联表）

```sql
CREATE TABLE public.user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    assigned_by BIGINT REFERENCES public.users(id) ON DELETE SET NULL,  -- 谁分配的
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,      -- 过期时间（临时角色）
    is_active BOOLEAN DEFAULT true,           -- 可临时禁用
    
    CONSTRAINT unique_user_role UNIQUE (user_id, role_id),
    CONSTRAINT valid_expires_at CHECK (expires_at IS NULL OR expires_at > assigned_at)
);
```

**设计要点：**
- 支持多对多关系：用户可有多个角色
- 审计追踪：`assigned_by` 记录谁分配的角色
- 临时角色：`expires_at` 支持角色过期（如临时管理员）
- 软禁用：`is_active` 可临时禁用角色而不删除记录
- 级联删除：用户删除时自动清理关联

#### 5. role_permissions 表（角色-权限关联表）

```sql
CREATE TABLE public.role_permissions (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    granted_by BIGINT REFERENCES public.users(id) ON DELETE SET NULL,  -- 谁授权的
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT unique_role_permission UNIQUE (role_id, permission_id)
);
```

**设计要点：**
- 支持多对多关系：角色可包含多个权限
- 审计追踪：`granted_by` 记录谁授予的权限
- 软禁用：`is_active` 可临时禁用权限
- 级联删除：角色删除时自动清理关联

#### 6. rbac_constraints 表（RBAC2 约束规则表）

```sql
CREATE TABLE public.rbac_constraints (
    id BIGSERIAL PRIMARY KEY,
    constraint_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    config JSONB NOT NULL,                    -- 灵活的约束配置
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_constraint_type CHECK (constraint_type IN (
        'mutually_exclusive',  -- 互斥角色（SSD）
        'cardinality',         -- 基数约束
        'prerequisite'          -- 先决条件
    ))
);
```

**设计要点：**
- 支持 RBAC2 约束模型
- 使用 `JSONB` 存储灵活的约束配置
- 支持三种约束类型：
  - `mutually_exclusive`：互斥角色（用户不能同时拥有）
  - `cardinality`：基数约束（角色最多分配给 N 个用户）
  - `prerequisite`：先决条件（必须先拥有某角色）

**约束配置示例：**
```json
// 互斥角色
{
  "constraint_type": "mutually_exclusive",
  "config": {
    "roles": ["cashier", "accountant"],
    "check_type": "static"
  }
}

// 基数约束
{
  "constraint_type": "cardinality",
  "config": {
    "role": "admin",
    "max_users": 5
  }
}

// 先决条件
{
  "constraint_type": "prerequisite",
  "config": {
    "role": "editor",
    "required_roles": ["user"]
  }
}
```

### 数据库视图设计

#### 1. view_user_roles - 用户及其角色

```sql
CREATE OR REPLACE VIEW public.view_user_roles AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    json_agg(
        json_build_object(
            'id', r.id,
            'name', r.name,
            'slug', r.slug,
            'description', r.description,
            'priority', r.priority,
            'assigned_at', ur.assigned_at,
            'expires_at', ur.expires_at
        ) ORDER BY r.priority DESC
    ) AS roles
FROM public.users u
LEFT JOIN public.user_roles ur ON u.id = ur.user_id AND ur.is_active = true
    AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
LEFT JOIN public.roles r ON ur.role_id = r.id
GROUP BY u.id, u.username, u.email, u.full_name, u.is_active;
```

**用途：** 快速查询用户拥有的所有角色

#### 2. view_role_permissions - 角色及其权限

```sql
CREATE OR REPLACE VIEW public.view_role_permissions AS
SELECT 
    r.id AS role_id,
    r.name,
    r.slug,
    r.description,
    r.is_system,
    r.priority,
    json_agg(
        json_build_object(
            'id', p.id,
            'resource', p.resource,
            'action', p.action,
            'description', p.description,
            'module', p.module
        )
    ) AS permissions
FROM public.roles r
LEFT JOIN public.role_permissions rp ON r.id = rp.role_id AND rp.is_active = true
LEFT JOIN public.permissions p ON rp.permission_id = p.id
GROUP BY r.id, r.name, r.slug, r.description, r.is_system, r.priority;
```

**用途：** 快速查询角色拥有的所有权限

#### 3. view_user_permissions - 用户的所有权限

```sql
CREATE OR REPLACE VIEW public.view_user_permissions AS
SELECT DISTINCT
    u.id AS user_id,
    u.username,
    u.email,
    p.id AS permission_id,
    p.resource,
    p.action,
    p.description,
    p.module
FROM public.users u
INNER JOIN public.user_roles ur ON u.id = ur.user_id 
    AND ur.is_active = true 
    AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
INNER JOIN public.role_permissions rp ON ur.role_id = rp.role_id AND rp.is_active = true
INNER JOIN public.permissions p ON rp.permission_id = p.id
ORDER BY u.id, p.module, p.resource, p.action;
```

**用途：** 权限检查时快速查询用户的所有权限（包括从角色继承的）

### 初始数据设计

#### 默认角色（5个）

| 角色名称 | slug | 优先级 | 说明 |
|---------|------|--------|------|
| 超级管理员 | super-admin | 100 | 拥有系统所有权限 |
| 管理员 | admin | 80 | 系统管理员，拥有大部分权限 |
| 编辑 | editor | 60 | 内容编辑人员 |
| 普通用户 | user | 40 | 普通注册用户 |
| 访客 | guest | 20 | 未登录或临时访客 |

#### 系统权限（19个）

**用户相关（5个）：**
- `user:read` - 读取用户信息
- `user:write` - 编辑用户信息
- `user:delete` - 删除用户
- `user:create` - 创建用户
- `user:manage` - 管理用户（包含所有操作）

**角色相关（5个）：**
- `role:read` - 读取角色信息
- `role:write` - 编辑角色信息
- `role:delete` - 删除角色
- `role:create` - 创建角色
- `role:manage` - 管理角色（包含所有操作）

**权限相关（3个）：**
- `permission:read` - 读取权限信息
- `permission:assign` - 分配权限
- `permission:revoke` - 撤销权限

**文章相关（4个）：**
- `article:read` - 读取文章
- `article:write` - 创建/编辑文章
- `article:delete` - 删除文章
- `article:publish` - 发布文章

**订单相关（4个）：**
- `order:read` - 读取订单
- `order:write` - 创建/编辑订单
- `order:delete` - 删除订单
- `order:manage` - 管理订单

#### 约束规则示例（3个）

1. **出纳员和会计互斥**
   - 类型：静态职责分离（SSD）
   - 规则：用户不能同时拥有出纳员和会计角色

2. **管理员角色限制**
   - 类型：基数约束
   - 规则：管理员角色最多分配给 5 个用户

3. **编辑角色先决条件**
   - 类型：先决条件
   - 规则：用户必须拥有普通用户角色才能分配编辑角色

### 设计亮点总结

| 特性 | 实现方式 | 支持 |
|------|----------|------|
| **RBAC0 基础模型** | users、roles、permissions 表 | ✅ |
| **RBAC1 角色继承** | roles.parent_id 字段 | ✅ |
| **RBAC2 约束规则** | rbac_constraints 表（JSONB配置） | ✅ |
| **RBAC3 统一模型** | 同时支持继承和约束 | ✅ |
| **审计追踪** | assigned_by、granted_by 字段 | ✅ |
| **临时角色** | user_roles.expires_at 字段 | ✅ |
| **软删除/禁用** | is_active 字段 | ✅ |
| **性能优化** | 合理的索引设计 | ✅ |
| **数据完整性** | CHECK 约束、外键级联 | ✅ |
| **自动时间戳** | 触发器自动更新 | ✅ |

### 迁移文件位置

完整的数据库迁移文件位于：`db/migrations/001_init_rbac_tables.sql`

## 前端交互设计

### 设计概述

本系统提供一个简洁实用的 Web 交互界面，用于管理用户、角色和权限。

**核心功能：**
- 用户管理（列表、创建、编辑、禁用）
- 角色管理（列表、创建、编辑、删除）
- 权限管理（列表、分配、撤销）
- 用户角色分配
- 角色权限分配

**技术栈：**
- **前端**：HTML5 + CSS3 + JavaScript (原生)
- **UI框架**：Bootstrap 5（简洁响应式）
- **后端API**：FastAPI
- **数据交互**：Fetch API + JSON

---

### 页面结构设计

#### 整体布局

```
┌─────────────────────────────────────────────────────────┐
│  Logo  RBAC 管理系统         [用户名] [退出登录]       │  ← 顶部导航栏
├─────────┬───────────────────────────────────────────────┤
│         │                                               │
│  📊 概览  │              主内容区域                      │
│         │                                               │
│  👥 用户  │   ┌─────────────────────────────────────┐  │
│         │   │                                     │  │
│  🔐 角色  │   │    表格/表单/详情展示                │  │
│         │   │                                     │  │
│  🎫 权限  │   │                                     │  │
│         │   └─────────────────────────────────────┘  │
│  ⚙️ 设置  │                                               │
│         │                                               │
└─────────┴───────────────────────────────────────────────┘
    ↑
  侧边导航栏
```

---

### 主要页面设计

#### 1. 概览页面（Dashboard）

**功能：** 展示系统关键数据统计

**页面布局：**
```
┌─────────────────────────────────────────────────────────┐
│  系统概览                                                │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ 用户总数  │ 角色总数  │ 权限总数  │ 活跃用户  │ 今日登录   │
│   128    │    5     │    19    │    98    │    32     │
│  ↑12%   │   -      │   -      │  ↑5%    │   ↑8%     │
└──────────┴──────────┴──────────┴──────────┴────────────┘

┌─────────────────────────────────────────────────────────┐
│  最近活动                                                │
├─────────────────────────────────────────────────────────┤
│  • 用户张三被分配了"编辑"角色 - 2024-01-15 14:30        │
│  • 角色权限更新：管理员新增 article:publish 权限         │
│  • 新用户注册：李四 - 2024-01-15 13:20                  │
│  • 角色创建：审核员 - 2024-01-15 10:15                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────┬───────────────────────────────────┐
│   用户角色分布       │      权限使用 Top 5              │
├─────────────────────┼───────────────────────────────────┤
│  普通用户  ████████ │  1. user:read      ████████████  │
│  编辑      ████     │  2. article:read   ██████████    │
│  管理员    ██       │  3. article:write  ████████      │
│  超级管理员 █        │  4. order:read     ██████        │
│  访客      █        │  5. user:write     ████          │
└─────────────────────┴───────────────────────────────────┘
```

---

#### 2. 用户管理页面

**功能：** 用户列表、搜索、创建、编辑、禁用/启用

**页面布局：**
```
┌─────────────────────────────────────────────────────────┐
│  用户管理                              [+ 新建用户]     │
├─────────────────────────────────────────────────────────┤
│  搜索: [____________] [状态 ▼] [角色 ▼] [搜索] [重置]  │
├─────────────────────────────────────────────────────────┤
│  ID │ 用户名  │ 邮箱          │ 角色     │ 状态 │ 操作  │
├─────┼─────────┼────────────────┼──────────┼──────┼──────┤
│  1  │ admin   │ admin@mail.com │ 超级管理员│ 活跃 │ ⋮    │
│  2  │ zhangsan│ zhang@mail.com │ 编辑     │ 活跃 │ ⋮    │
│  3  │ lisi    │ li@mail.com    │ 普通用户 │ 禁用 │ ⋮    │
│  4  │ wangwu  │ wang@mail.com  │ 管理员   │ 活跃 │ ⋮    │
└─────┴─────────┴────────────────┴──────────┴──────┴──────┘
                                              [◀ 1 2 3 ▶]

操作菜单（⋮）:
┌─────────────┐
│ 📝 编辑     │
│ 🔐 分配角色  │
│ 🚫 禁用     │
│ 🗑️ 删除     │
└─────────────┘
```

**创建/编辑用户表单：**
```
┌─────────────────────────────────────────────────────────┐
│  新建用户                                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  用户名 *        [________________________]              │
│                                                          │
│  邮箱 *          [________________________]              │
│                                                          │
│  密码 *          [________________________] [👁]        │
│                                                          │
│  全名            [________________________]              │
│                                                          │
│  状态           [活跃 ▼]                                │
│                                                          │
│                [取消]        [保存]                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**用户角色分配弹窗：**
```
┌─────────────────────────────────────────────────────────┐
│  分配角色 - 张三                                    [×] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  当前角色：                                              │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ 编辑   [×]   │  │ 普通用户 [×] │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
│  可用角色：                                              │
│  ☐ 管理员    (需要先决条件：普通用户)                   │
│  ☐ 访客                                              │
│                                                          │
│  过期时间：     [____-__-__ __:__] (可选)               │
│                                                          │
│                [取消]        [确定]                      │
└─────────────────────────────────────────────────────────┘
```

---

#### 3. 角色管理页面

**功能：** 角色列表、创建、编辑、删除、权限分配

**页面布局：**
```
┌─────────────────────────────────────────────────────────┐
│  角色管理                              [+ 新建角色]     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🔴 超级管理员 (super-admin)              [⋮]     │  │
│  │    拥有系统所有权限                                │  │
│  │    权限: 19个  用户: 1个  优先级: 100              │  │
│  │    [查看权限] [查看用户]                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🔵 管理员 (admin)                        [⋮]     │  │
│  │    系统管理员，拥有大部分权限                       │  │
│  │    权限: 15个  用户: 3个  优先级: 80               │  │
│  │    继承自: 超级管理员                             │  │
│  │    [查看权限] [查看用户]                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🟢 编辑 (editor)                         [⋮]     │  │
│  │    内容编辑人员                                    │  │
│  │    权限: 5个  用户: 10个  优先级: 60               │  │
│  │    [查看权限] [查看用户]                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**角色权限分配页面：**
```
┌─────────────────────────────────────────────────────────┐
│  编辑角色权限 - "编辑"                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  按模块筛选: [全部 ▼]                                   │
│                                                          │
│  ┌─ 用户管理 ─────────────────────────────────────┐    │
│  │ ☑ user:read    读取用户信息                     │    │
│  │ ☐ user:write   编辑用户信息                     │    │
│  │ ☐ user:delete  删除用户                         │    │
│  │ ☐ user:create  创建用户                         │    │
│  │ ☐ user:manage  管理用户（包含所有操作）         │    │
│  └───────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ 内容管理 ─────────────────────────────────────┐    │
│  │ ☑ article:read    读取文章                      │    │
│  │ ☑ article:write   创建/编辑文章                 │    │
│  │ ☑ article:delete  删除文章                      │    │
│  │ ☐ article:publish 发布文章                      │    │
│  └───────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ 订单管理 ─────────────────────────────────────┐    │
│  │ ☑ order:read   读取订单                         │    │
│  │ ☐ order:write  创建/编辑订单                    │    │
│  │ ☐ order:delete 删除订单                         │    │
│  │ ☐ order:manage 管理订单                         │    │
│  └───────────────────────────────────────────────┘    │
│                                                          │
│                [取消]        [保存]                      │
└─────────────────────────────────────────────────────────┘
```

---

#### 4. 权限管理页面

**功能：** 权限列表、创建、删除

**页面布局：**
```
┌─────────────────────────────────────────────────────────┐
│  权限管理                              [+ 新建权限]     │
├─────────────────────────────────────────────────────────┤
│  搜索: [____________] [模块 ▼] [搜索]                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ 用户管理 (auth) ──────────────────────────────┐    │
│  │  user:read      读取用户信息           [删除]   │    │
│  │  user:write     编辑用户信息           [删除]   │    │
│  │  user:delete    删除用户               [删除]   │    │
│  │  user:create    创建用户               [删除]   │    │
│  │  user:manage    管理用户               [删除]   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ 角色管理 (rbac) ───────────────────────────────┐    │
│  │  role:read      读取角色信息           [删除]   │    │
│  │  role:write     编辑角色信息           [删除]   │    │
│  │  role:delete    删除角色               [删除]   │    │
│  │  role:create    创建角色               [删除]   │    │
│  │  role:manage    管理角色               [删除]   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ 内容管理 (content) ────────────────────────────┐    │
│  │  article:read   读取文章               [删除]   │    │
│  │  article:write  创建/编辑文章          [删除]   │    │
│  │  article:delete 删除文章               [删除]   │    │
│  │  article:publish 发布文章              [删除]   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### API 接口设计

#### 用户管理 API

```python
# 获取用户列表
GET /api/v1/users?search={keyword}&status={status}&page={page}&size={size}

# 创建用户
POST /api/v1/users
Body: {
    "username": "zhangsan",
    "email": "zhang@example.com",
    "password": "******",
    "full_name": "张三"
}

# 获取用户详情
GET /api/v1/users/{user_id}

# 更新用户
PUT /api/v1/users/{user_id}
Body: {
    "email": "newemail@example.com",
    "full_name": "张三",
    "is_active": true
}

# 删除用户
DELETE /api/v1/users/{user_id}

# 获取用户角色
GET /api/v1/users/{user_id}/roles

# 分配角色
POST /api/v1/users/{user_id}/roles
Body: {
    "role_id": 3,
    "expires_at": "2024-12-31T23:59:59"  // 可选
}

# 撤销角色
DELETE /api/v1/users/{user_id}/roles/{role_id}
```

#### 角色管理 API

```python
# 获取角色列表
GET /api/v1/roles?search={keyword}

# 创建角色
POST /api/v1/roles
Body: {
    "name": "审核员",
    "slug": "reviewer",
    "description": "内容审核人员",
    "parent_id": 3,  // 父角色ID（可选）
    "priority": 50
}

# 获取角色详情
GET /api/v1/roles/{role_id}

# 更新角色
PUT /api/v1/roles/{role_id}

# 删除角色
DELETE /api/v1/roles/{role_id}

# 获取角色权限
GET /api/v1/roles/{role_id}/permissions

# 分配权限
POST /api/v1/roles/{role_id}/permissions
Body: {
    "permission_ids": [1, 2, 3]
}

# 撤销权限
DELETE /api/v1/roles/{role_id}/permissions/{permission_id}

# 获取角色的用户列表
GET /api/v1/roles/{role_id}/users
```

#### 权限管理 API

```python
# 获取权限列表
GET /api/v1/permissions?module={module}

# 创建权限
POST /api/v1/permissions
Body: {
    "resource": "comment",
    "action": "delete",
    "description": "删除评论",
    "module": "content"
}

# 删除权限
DELETE /api/v1/permissions/{permission_id}
```

#### 系统统计 API

```python
# 获取系统概览数据
GET /api/v1/dashboard/stats
Response: {
    "total_users": 128,
    "total_roles": 5,
    "total_permissions": 19,
    "active_users": 98,
    "today_logins": 32
}

# 获取用户角色分布
GET /api/v1/dashboard/user-role-distribution
Response: {
    "普通用户": 80,
    "编辑": 30,
    "管理员": 15,
    "超级管理员": 2,
    "访客": 1
}

# 获取权限使用统计
GET /api/v1/dashboard/permission-usage
Response: [
    {"permission": "user:read", "count": 150},
    {"permission": "article:read", "count": 120},
    ...
]
```

---

### 前端文件结构

```
src/
├── static/
│   ├── css/
│   │   ├── main.css          # 主样式
│   │   ├── components.css     # 组件样式
│   │   └── responsive.css     # 响应式样式
│   ├── js/
│   │   ├── main.js           # 主逻辑
│   │   ├── api.js            # API 封装
│   │   ├── utils.js          # 工具函数
│   │   ├── components/
│   │   │   ├── user.js       # 用户管理组件
│   │   │   ├── role.js       # 角色管理组件
│   │   │   └── permission.js # 权限管理组件
│   │   └── validators.js     # 表单验证
│   └── images/
│       └── logo.png
└── templates/
    ├── base.html             # 基础模板
    ├── index.html            # 概览页面
    ├── users.html            # 用户管理
    ├── roles.html            # 角色管理
    └── permissions.html      # 权限管理
```

---

### 界面交互流程

#### 用户创建流程

```
用户点击"新建用户"
       ↓
弹出创建表单
       ↓
填写用户信息
       ↓
前端验证（用户名、邮箱格式、密码强度）
       ↓
验证通过 → POST /api/v1/users
       ↓
后端验证（唯一性、密码加密）
       ↓
创建成功 → 返回用户数据
       ↓
前端更新列表，显示成功提示
```

#### 角色分配流程

```
用户点击"分配角色"
       ↓
弹出角色选择框
       ↓
加载用户当前角色（GET /api/v1/users/{id}/roles）
       ↓
加载可用角色列表（GET /api/v1/roles）
       ↓
用户选择角色，设置过期时间（可选）
       ↓
前端验证（先决条件检查）
       ↓
POST /api/v1/users/{id}/roles
       ↓
后端约束检查（互斥、基数、先决条件）
       ↓
检查通过 → 分配成功
检查失败 → 显示错误提示
```

#### 权限检查流程

```
用户访问页面
       ↓
前端检查本地权限缓存
       ↓
缓存存在 → 渲染页面
缓存不存在 → GET /api/v1/users/me/permissions
       ↓
后端查询用户所有权限（含继承）
       ↓
返回权限列表
       ↓
前端缓存权限，渲染页面
       ↓
权限不足的操作按钮隐藏/禁用
```

---

### 响应式设计

**断点设计：**
- **桌面端**：≥ 1200px（完整侧边栏 + 内容区）
- **平板端**：768px - 1199px（折叠侧边栏）
- **移动端**：< 768px（抽屉式导航）

**移动端适配：**
- 侧边栏转为抽屉式导航
- 表格转为卡片列表
- 弹窗全屏显示
- 按钮堆叠排列

---

### 用户体验优化

**实时反馈：**
- 操作按钮加载状态（禁用 + 旋转图标）
- 成功/失败 Toast 提示
- 表单字段实时验证

**确认机制：**
- 删除操作二次确认
- 批量操作确认
- 不可逆操作警告

**快捷操作：**
- 快捷键支持（Ctrl+S 保存、Esc 关闭弹窗）
- 批量操作（批量分配角色、批量禁用用户）
- 拖拽排序（角色优先级）

---

### 技术实现要点

**前端关键技术：**

| 功能 | 实现方式 |
|------|----------|
| HTTP 请求 | Fetch API + async/await |
| 表单验证 | 自定义验证器 + 正则表达式 |
| 状态管理 | LocalStorage + SessionStorage |
| 消息提示 | 自定义 Toast 组件 |
| 模态框 | Bootstrap Modal |
| 数据表格 | 原生表格 + 分页组件 |

**安全措施：**
- JWT Token 存储在 HttpOnly Cookie
- CSRF Token 验证
- XSS 防护（输入转义）
- 权限前端二次验证（按钮显示控制）

---

### 设计特点总结

| 特点 | 说明 |
|------|------|
| **简洁实用** | 界面清晰，操作直观 |
| **响应式设计** | 支持桌面、平板、移动端 |
| **实时反馈** | 操作即时响应，状态清晰 |
| **权限控制** | UI 根据权限动态渲染 |
| **错误处理** | 友好的错误提示和恢复机制 |
| **性能优化** | 前端缓存、懒加载、防抖节流 |

## 下一步

此文件应在项目开发过程中不断更新，以反映实际的代码结构、架构设计和最佳实践。
