"""
修复 Supabase 数据库连接
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Supabase 配置（从环境变量读取）
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL:
    print("错误: SUPABASE_URL 环境变量未设置")
    sys.exit(1)

# 提取项目引用
project_ref = SUPABASE_URL.split('//')[1].split('.supabase.co')[0]

print("=" * 70)
print("Supabase 数据库连接修复")
print("=" * 70)
print(f"\n项目引用: {project_ref}")
print(f"SUPABASE_URL: {SUPABASE_URL}")

# 尝试不同的连接格式
connection_formats = [
    # Pooler 格式（推荐用于无服务器/事务性连接）
    f"postgresql://postgres.{project_ref}:postgres@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
    
    # 直连格式（推荐用于有状态连接）
    f"postgresql://postgres.{project_ref}:postgres@db.{project_ref}.supabase.co:5432/postgres",
    
    # Session pooler 格式
    f"postgresql://postgres.{project_ref}:postgres@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
]

print("\n尝试不同的连接格式...\n")

for i, conn_url in enumerate(connection_formats, 1):
    print(f"[{i}] 尝试连接:")
    # 隐藏密码
    display_url = conn_url.replace(':postgres@', ':****@')
    print(f"    {display_url}")
    
    try:
        conn = psycopg2.connect(conn_url)
        print(f"    [成功] 连接成功！")
        
        # 测试查询
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"    数据库版本: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        
        print(f"\n推荐更新 .env 文件的 DATABASE_URL 为:")
        print(f"DATABASE_URL={conn_url}\n")
        
        sys.exit(0)
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "FATAL:  password authentication failed" in error_msg:
            print(f"    [失败] 密码错误")
        elif "FATAL:  Tenant or user not found" in error_msg:
            print(f"    [失败] 项目引用或用户名错误")
        elif "FATAL:  database does not exist" in error_msg:
            print(f"    [失败] 数据库不存在")
        else:
            print(f"    [失败] {error_msg}")
    except psycopg2.InterfaceError as e:
        print(f"    [失败] 接口错误: {e}")
    except Exception as e:
        print(f"    [失败] 未知错误: {e}")
    
    print()

print("\n" + "=" * 70)
print("所有连接格式均失败")
print("=" * 70)
print(f"""
建议:
1. 访问 Supabase Dashboard: https://supabase.com/dashboard/project/{project_ref}
2. 进入 Settings -> Database
3. 找到 "Connection string"
4. 选择 "URI" 格式
5. 复制正确的连接字符串（包含正确的密码）
6. 更新 .env 文件

注意:
- 不要使用 'postgres' 作为默认密码
- Supabase 项目创建时会生成随机密码
- 可以在 Dashboard 中重置密码
""")
