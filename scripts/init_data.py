"""
数据库初始化脚本
用于填充默认角色、权限和约束数据
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.db.base import SessionLocal
from src.core.rbac.models import Role, Permission, RBACConstraint
from src.core.rbac.permissions import DEFAULT_ROLE_PERMISSIONS


def create_default_roles(db: Session):
    """创建默认角色"""
    print("创建默认角色...")
    
    roles_data = [
        {"name": "超级管理员", "slug": "super-admin", "priority": 100, "is_system": True},
        {"name": "管理员", "slug": "admin", "priority": 80, "is_system": False},
        {"name": "编辑", "slug": "editor", "priority": 60, "is_system": False},
        {"name": "普通用户", "slug": "user", "priority": 40, "is_system": False},
        {"name": "访客", "slug": "guest", "priority": 20, "is_system": True},
    ]
    
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.slug == role_data["slug"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            print(f"  ✓ 创建角色: {role_data['name']}")
        else:
            print(f"  - 角色已存在: {role_data['name']}")
    
    db.commit()
    print("默认角色创建完成！\n")


def create_default_permissions(db: Session):
    """创建默认权限"""
    print("创建默认权限...")
    
    permissions_data = [
        # 用户管理
        {"resource": "user", "action": "read", "description": "读取用户信息", "module": "auth"},
        {"resource": "user", "action": "write", "description": "编辑用户信息", "module": "auth"},
        {"resource": "user", "action": "create", "description": "创建用户", "module": "auth"},
        {"resource": "user", "action": "delete", "description": "删除用户", "module": "auth"},
        {"resource": "user", "action": "manage", "description": "管理用户（包含所有操作）", "module": "auth"},
        
        # 角色管理
        {"resource": "role", "action": "read", "description": "读取角色信息", "module": "rbac"},
        {"resource": "role", "action": "write", "description": "编辑角色信息", "module": "rbac"},
        {"resource": "role", "action": "create", "description": "创建角色", "module": "rbac"},
        {"resource": "role", "action": "delete", "description": "删除角色", "module": "rbac"},
        {"resource": "role", "action": "manage", "description": "管理角色（包含所有操作）", "module": "rbac"},
        
        # 权限管理
        {"resource": "permission", "action": "read", "description": "读取权限信息", "module": "rbac"},
        {"resource": "permission", "action": "assign", "description": "分配权限", "module": "rbac"},
        {"resource": "permission", "action": "revoke", "description": "撤销权限", "module": "rbac"},
        
        # 内容管理
        {"resource": "article", "action": "read", "description": "读取文章", "module": "content"},
        {"resource": "article", "action": "write", "description": "创建/编辑文章", "module": "content"},
        {"resource": "article", "action": "delete", "description": "删除文章", "module": "content"},
        {"resource": "article", "action": "publish", "description": "发布文章", "module": "content"},
        
        # 订单管理
        {"resource": "order", "action": "read", "description": "读取订单", "module": "order"},
        {"resource": "order", "action": "write", "description": "创建/编辑订单", "module": "order"},
        {"resource": "order", "action": "delete", "description": "删除订单", "module": "order"},
        {"resource": "order", "action": "manage", "description": "管理订单（包含所有操作）", "module": "order"},
    ]
    
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(
            Permission.resource == perm_data["resource"],
            Permission.action == perm_data["action"]
        ).first()
        
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            print(f"  ✓ 创建权限: {perm_data['resource']}:{perm_data['action']}")
        else:
            print(f"  - 权限已存在: {perm_data['resource']}:{perm_data['action']}")
    
    db.commit()
    print("默认权限创建完成！\n")


def assign_role_permissions(db: Session):
    """为角色分配默认权限"""
    print("为角色分配默认权限...")
    
    # 获取所有角色和权限
    roles = {role.slug: role for role in db.query(Role).all()}
    permissions = {
        f"{perm.resource}:{perm.action}": perm 
        for perm in db.query(Permission).all()
    }
    
    from src.core.rbac.models import RolePermission
    
    # 遍历默认角色权限映射
    for role_slug, permission_list in DEFAULT_ROLE_PERMISSIONS.items():
        role = roles.get(role_slug)
        if not role:
            print(f"  ✗ 角色不存在: {role_slug}")
            continue
        
        for perm_str in permission_list:
            perm = permissions.get(perm_str)
            if not perm:
                print(f"  ✗ 权限不存在: {perm_str}")
                continue
            
            # 检查是否已存在
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id
            ).first()
            
            if not existing:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=perm.id,
                    is_active=True
                )
                db.add(role_permission)
                print(f"  ✓ 为角色 '{role.name}' 分配权限: {perm_str}")
            else:
                print(f"  - 权限已分配: {role.name} -> {perm_str}")
    
    db.commit()
    print("角色权限分配完成！\n")


def create_default_constraints(db: Session):
    """创建默认约束规则"""
    print("创建默认约束规则...")
    
    constraints_data = [
        {
            "constraint_type": "cardinality",
            "name": "管理员数量限制",
            "description": "管理员角色最多分配给 5 个用户",
            "config": {"role": "admin", "max_users": 5}
        },
        {
            "constraint_type": "prerequisite",
            "name": "编辑角色先决条件",
            "description": "用户必须拥有普通用户角色才能分配编辑角色",
            "config": {"role": "editor", "required_roles": ["user"]}
        },
    ]
    
    for constraint_data in constraints_data:
        existing = db.query(RBACConstraint).filter(
            RBACConstraint.name == constraint_data["name"]
        ).first()
        
        if not existing:
            constraint = RBACConstraint(**constraint_data)
            db.add(constraint)
            print(f"  ✓ 创建约束: {constraint_data['name']}")
        else:
            print(f"  - 约束已存在: {constraint_data['name']}")
    
    db.commit()
    print("默认约束创建完成！\n")


def main():
    """主函数"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60 + "\n")
    
    db: Session = SessionLocal()
    
    try:
        create_default_roles(db)
        create_default_permissions(db)
        assign_role_permissions(db)
        create_default_constraints(db)
        
        print("=" * 60)
        print("数据库初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
