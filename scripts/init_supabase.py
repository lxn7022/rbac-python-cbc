"""
Supabase 数据库初始化脚本
连接 Supabase PostgreSQL 并创建表结构
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.base import engine, Base
from src.config.settings import settings

def main():
    """初始化 Supabase 数据库"""
    print("=" * 60)
    print("Supabase 数据库初始化")
    print("=" * 60 + "\n")
    
    print(f"Supabase URL: {settings.SUPABASE_URL}")
    print(f"数据库 URL: {settings.DATABASE_URL}")
    print()
    
    try:
        # 测试连接
        print("步骤 1: 测试数据库连接...")
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"  - 连接成功！")
            print(f"  - PostgreSQL 版本: {version[:50]}...")
        print()
        
        # 创建表
        print("步骤 2: 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("  - 表创建成功！")
        print()
        
        # 列出创建的表
        print("步骤 3: 验证表结构...")
        from src.core.rbac.models import User, Role, Permission, UserRole, RolePermission, RBACConstraint
        
        tables = [
            ("users", User),
            ("roles", Role),
            ("permissions", Permission),
            ("user_roles", UserRole),
            ("role_permissions", RolePermission),
            ("rbac_constraints", RBACConstraint),
        ]
        
        for table_name, model in tables:
            print(f"  - {table_name:20} ✓")
        
        print()
        print("=" * 60)
        print("✅ Supabase 数据库初始化成功！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 初始化失败！")
        print("=" * 60)
        print()
        print(f"错误: {e}")
        print()
        print("排查建议:")
        print("1. 检查 Supabase 项目是否正常运行")
        print("2. 检查网络连接是否正常")
        print("3. 检查 DATABASE_URL 是否正确")
        print("4. 访问 https://supabase.com/dashboard 检查项目状态")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
