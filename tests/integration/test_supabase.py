"""
Supabase 连接测试
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from supabase import create_client, Client


def test_supabase_connection_api():
    """测试 Supabase API 连接"""
    # Supabase 配置
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://orygzioqsfvuauzklogx.supabase.co")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "YOUR_SUPABASE_ANON_KEY_HERE")

    # 创建客户端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    # 查询所有数据
    response = supabase.table("users").select("*").execute()
    
    # 验证连接成功
    assert response.data is not None
    print(f"连接成功，用户数量: {len(response.data)}")


def test_supabase_roles_query():
    """测试查询角色"""
    from src.db.supabase_client import supabase_db
    
    roles = supabase_db.get_all_roles()
    
    assert isinstance(roles, list)
    print(f"角色数量: {len(roles)}")


def test_supabase_permissions_query():
    """测试查询权限"""
    from src.db.supabase_client import supabase_db
    
    permissions = supabase_db.get_all_permissions(page=1, size=10)
    
    assert isinstance(permissions, dict)
    assert "items" in permissions
    assert "total" in permissions
    print(f"权限数量: {permissions['total']}")


if __name__ == "__main__":
    test_supabase_connection_api()
    test_supabase_roles_query()
    test_supabase_permissions_query()
