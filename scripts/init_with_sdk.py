"""
使用 Supabase SDK 初始化数据库
通过 Supabase REST API 创建表和数据
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

print("=" * 70)
print("使用 Supabase SDK 初始化数据库")
print("=" * 70)

# 创建客户端
client = create_client(SUPABASE_URL, ANON_KEY)
print("\n[OK] Supabase 客户端创建成功")

# 检查现有表
print("\n检查现有数据...")
print("-" * 70)

tables = ['users', 'roles', 'permissions', 'user_roles', 'role_permissions', 'rbac_constraints']

for table in tables:
    try:
        count = client.table(table).select('*', count='exact').execute()
        print(f"{table}: {count.count} 条记录")
    except Exception as e:
        print(f"{table}: 错误 - {str(e)[:50]}")

# 初始化数据
print("\n开始初始化数据...")
print("-" * 70)

try:
    # 1. 创建角色
    print("\n[1/4] 创建角色...")
    roles_data = [
        {"name": "超级管理员", "slug": "super-admin", "description": "拥有系统所有权限", "is_system": True, "priority": 100},
        {"name": "管理员", "slug": "admin", "description": "系统管理员，拥有大部分权限", "priority": 80},
        {"name": "编辑", "slug": "editor", "description": "内容编辑人员", "priority": 60},
        {"name": "普通用户", "slug": "user", "description": "普通注册用户", "priority": 40},
        {"name": "访客", "slug": "guest", "description": "未登录或临时访客", "priority": 20},
    ]
    
    for role in roles_data:
        try:
            result = client.table('roles').insert(role).execute()
            print(f"  ✓ 创建角色: {role['name']}")
        except Exception as e:
            if 'duplicate' in str(e).lower():
                print(f"  - 角色已存在: {role['name']}")
            else:
                print(f"  ✗ 创建失败: {role['name']} - {e}")
    
    # 2. 创建权限
    print("\n[2/4] 创建权限...")
    permissions_data = [
        # 用户相关
        {"resource": "user", "action": "read", "description": "读取用户信息", "module": "auth"},
        {"resource": "user", "action": "write", "description": "编辑用户信息", "module": "auth"},
        {"resource": "user", "action": "create", "description": "创建用户", "module": "auth"},
        {"resource": "user", "action": "delete", "description": "删除用户", "module": "auth"},
        {"resource": "user", "action": "manage", "description": "管理用户", "module": "auth"},
        
        # 角色相关
        {"resource": "role", "action": "read", "description": "读取角色信息", "module": "rbac"},
        {"resource": "role", "action": "write", "description": "编辑角色信息", "module": "rbac"},
        {"resource": "role", "action": "create", "description": "创建角色", "module": "rbac"},
        {"resource": "role", "action": "delete", "description": "删除角色", "module": "rbac"},
        {"resource": "role", "action": "manage", "description": "管理角色", "module": "rbac"},
        
        # 权限相关
        {"resource": "permission", "action": "read", "description": "读取权限信息", "module": "rbac"},
        {"resource": "permission", "action": "assign", "description": "分配权限", "module": "rbac"},
        {"resource": "permission", "action": "revoke", "description": "撤销权限", "module": "rbac"},
        
        # 文章相关
        {"resource": "article", "action": "read", "description": "读取文章", "module": "content"},
        {"resource": "article", "action": "write", "description": "创建/编辑文章", "module": "content"},
        {"resource": "article", "action": "delete", "description": "删除文章", "module": "content"},
        {"resource": "article", "action": "publish", "description": "发布文章", "module": "content"},
        
        # 订单相关
        {"resource": "order", "action": "read", "description": "读取订单", "module": "order"},
        {"resource": "order", "action": "write", "description": "创建/编辑订单", "module": "order"},
        {"resource": "order", "action": "delete", "description": "删除订单", "module": "order"},
        {"resource": "order", "action": "manage", "description": "管理订单", "module": "order"},
    ]
    
    for perm in permissions_data:
        try:
            result = client.table('permissions').insert(perm).execute()
            print(f"  ✓ 创建权限: {perm['resource']}:{perm['action']}")
        except Exception as e:
            if 'duplicate' in str(e).lower():
                print(f"  - 权限已存在: {perm['resource']}:{perm['action']}")
            else:
                print(f"  ✗ 创建失败: {perm['resource']}:{perm['action']} - {e}")
    
    # 3. 创建默认用户
    print("\n[3/4] 创建默认用户...")
    
    # 注意: 密码需要在服务端哈希处理，这里只是示例
    # 实际应该使用 Supabase Auth API 创建用户
    try:
        user_data = {
            "username": "admin",
            "email": "admin@rbac.com",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NUhqv8JmF.C6",  # admin123
            "full_name": "系统管理员",
            "is_active": True,
            "is_verified": True
        }
        result = client.table('users').insert(user_data).execute()
        print(f"  [OK] 创建用户: admin (密码: admin123)")
    except Exception as e:
        if 'duplicate' in str(e).lower():
            print(f"  - 用户已存在: admin")
        else:
            print(f"  [ERROR] 创建失败: admin - {e}")
    
    # 4. 分配超级管理员角色
    print("\n[4/4] 分配超级管理员角色...")
    
    # 获取用户 ID
    users = client.table('users').select('*').eq('username', 'admin').execute()
    if users.data:
        user_id = users.data[0]['id']
        print(f"  用户 ID: {user_id}")
        
        # 获取角色 ID
        roles = client.table('roles').select('*').eq('slug', 'super-admin').execute()
        if roles.data:
            role_id = roles.data[0]['id']
            print(f"  角色 ID: {role_id}")
            
            # 分配角色
            try:
                user_role_data = {
                    "user_id": user_id,
                    "role_id": role_id,
                    "is_active": True
                }
                result = client.table('user_roles').insert(user_role_data).execute()
                print(f"  [OK] 分配角色: super-admin")
            except Exception as e:
                if 'duplicate' in str(e).lower():
                    print(f"  - 角色已分配")
                else:
                    print(f"  ✗ 分配失败: {e}")
    
    print("\n" + "=" * 70)
    print("初始化完成！")
    print("=" * 70)
    
    # 显示统计信息
    print("\n最终统计:")
    print("-" * 70)
    role_count = client.table('roles').select('*', count='exact').execute()
    perm_count = client.table('permissions').select('*', count='exact').execute()
    user_count = client.table('users').select('*', count='exact').execute()
    
    print(f"角色: {role_count.count} 个")
    print(f"权限: {perm_count.count} 个")
    print(f"用户: {user_count.count} 个")
    
    print("\n默认账号:")
    print("-" * 70)
    print("用户名: admin")
    print("密码: admin123")
    print("邮箱: admin@rbac.com")
    
except Exception as e:
    print(f"\n[ERROR] 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
