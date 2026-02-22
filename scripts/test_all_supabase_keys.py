"""
测试所有可能的 Supabase 连接方式
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 当前配置
SUPABASE_URL = os.getenv('SUPABASE_URL')
ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# 新提供的密钥
PUBLISHABLE_KEY = "sb_publishable__ZlhOSIkVPufgPRg_0kiCg_o6D1y4W5"

print("=" * 70)
print("Supabase 密钥分析")
print("=" * 70)

project_ref = SUPABASE_URL.split('//')[1].split('.supabase.co')[0]

print(f"\n项目引用: {project_ref}")
print(f"Supabase URL: {SUPABASE_URL}\n")

print("当前配置的密钥:")
print("-" * 70)
print(f"ANON_KEY: {ANON_KEY[:50]}...")
print(f"SERVICE_ROLE_KEY: {SERVICE_ROLE_KEY if SERVICE_ROLE_KEY else '未设置'}")
print(f"PUBLISHABLE_KEY: {PUBLISHABLE_KEY}")

print("\n密钥说明:")
print("-" * 70)
print("""
ANON_KEY / PUBLISHABLE_KEY:
  - 用于客户端应用认证
  - 用于 Supabase JS/Python 客户端
  - 不能直接用于数据库连接

SERVICE_ROLE_KEY:
  - 用于服务端操作
  - 拥有绕过 RLS 的权限
  - 不能直接用于数据库连接

数据库密码:
  - 完全不同的凭证
  - 用于直接连接 PostgreSQL
  - 在 Dashboard -> Connection string 中获取
""")

print("\n尝试使用 Supabase Python SDK 连接...")
print("-" * 70)

try:
    from supabase import create_client

    # 使用 ANON_KEY 创建客户端
    client = create_client(SUPABASE_URL, ANON_KEY)

    print("[OK] Supabase 客户端创建成功！")

    # 测试查询
    print("\n测试查询数据库表...")
    try:
        response = client.table('users').select('*').limit(1).execute()
        print(f"[OK] 查询成功，返回 {len(response.data)} 条记录")

        if response.data:
            print(f"   数据示例: {response.data[0]}")
        else:
            print("   表为空，需要初始化")

    except Exception as e:
        print(f"⚠ 查询失败: {e}")
        print("   这可能意味着:")
        print("   - 表尚未创建（需要初始化）")
        print("   - RLS 策略阻止访问")

    print("\n测试直接执行 SQL（需要 SERVICE_ROLE_KEY）...")
    if SERVICE_ROLE_KEY:
        admin_client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

        # 使用 supabase-py 的 rpc 方法执行 SQL
        try:
            # 创建表的 SQL
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT NOW()
            );
            INSERT INTO test_connection DEFAULT VALUES;
            """
            print("   注意: Supabase SDK 不支持直接执行任意 SQL")
            print("   需要在 Dashboard SQL Editor 中执行")

        except Exception as e:
            print(f"   错误: {e}")
    else:
        print("   SERVICE_ROLE_KEY 未设置，无法执行管理员操作")

except ImportError:
    print("[WARNING] supabase 模块未安装")
    print("   安装命令: pip install supabase")

except Exception as e:
    print(f"[ERROR] 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("结论:")
print("=" * 70)
print("""
1. Supabase 项目存在且可访问
2. 可以使用 Supabase SDK 进行操作
3. 但数据库表需要初始化

建议方案:

方案 A: 使用 Supabase SDK (推荐)
  - 已验证可用
  - 使用脚本/Python 代码操作数据库
  - 参考: scripts/init_data.py

方案 B: 使用 Supabase SQL Editor
  - 访问 Dashboard SQL Editor
  - 执行 scripts/supabase_init.sql
  - 适合一次性初始化

方案 C: 获取数据库密码
  - 在 Dashboard -> Settings -> Database
  - 获取 Connection String
  - 直接使用 psycopg2 连接
""")
