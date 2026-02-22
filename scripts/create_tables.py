"""
数据库表创建脚本
使用 SQLAlchemy 创建所有数据库表
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.base import engine, Base
from src.core.rbac.models import User, Role, Permission, UserRole, RolePermission, RBACConstraint
from src.config.settings import settings


def main():
    """创建所有数据库表"""
    print("=" * 60)
    print("开始创建数据库表 (Supabase PostgreSQL)...")
    print("=" * 60 + "\n")

    print(f"数据库 URL: {settings.DATABASE_URL}")
    print(f"调试模式: {settings.DEBUG}\n")

    try:
        # 导入所有模型，确保它们被注册到 Base.metadata
        print("导入数据库模型...")
        print("  - User (用户表)")
        print("  - Role (角色表)")
        print("  - Permission (权限表)")
        print("  - UserRole (用户-角色关联表)")
        print("  - RolePermission (角色-权限关联表)")
        print("  - RBACConstraint (约束规则表)")
        print()

        # 创建所有表
        print("创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print()

        # 列出创建的表
        print("已创建的表:")
        tables = Base.metadata.tables.keys()
        for table in sorted(tables):
            print(f"  - {table}")

        print()
        print("=" * 60)
        print("数据库表创建成功！")
        print("=" * 60)

    except Exception as e:
        print(f"\n[X] 创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
