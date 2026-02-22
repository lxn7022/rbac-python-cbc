"""
Supabase 连接助手
帮助获取和验证 Supabase 连接配置
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 70)
print("Supabase 连接配置检查")
print("=" * 70)

# 读取当前配置
DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

print("\n当前配置:")
print("-" * 70)

if DATABASE_URL:
    print(f"DATABASE_URL: {DATABASE_URL}")
    
    # 解析连接字符串
    if '@' in DATABASE_URL:
        parts = DATABASE_URL.split('@')
        user_part = parts[0]
        server_part = parts[1]
        
        # 提取项目引用
        if '.' in user_part:
            project_ref = user_part.split('.')[1]
            print(f"\n解析信息:")
            print(f"  项目引用 (Project Ref): {project_ref}")
            print(f"  服务器: {server_part.split(':')[0]}")
            print(f"  端口: {server_part.split(':')[1].split('/')[0]}")
            print(f"  数据库: {server_part.split('/')[-1]}")
        
        # 验证格式
        print(f"\n格式检查:")
        if DATABASE_URL.startswith('postgresql://'):
            print("  [OK] 使用 PostgreSQL 协议")
        else:
            print("  [ERROR] 协议错误，应为 postgresql://")
        
        if 'pooler.supabase.com' in DATABASE_URL:
            print("  [OK] 使用 Pooler 连接")
        elif '.supabase.co' in DATABASE_URL:
            print("  [OK] 使用直连")
        else:
            print("  [WARNING] 未知的服务器类型")
else:
    print("DATABASE_URL: 未设置")

print(f"\nSUPABASE_URL: {SUPABASE_URL or '未设置'}")
print(f"SUPABASE_ANON_KEY: {'已设置' if SUPABASE_ANON_KEY else '未设置'}")

print("\n" + "=" * 70)
print("获取正确的 Supabase 连接信息:")
print("=" * 70)
print("""
1. 访问 Supabase Dashboard: https://supabase.com/dashboard
2. 选择你的项目
3. 进入 Settings -> Database
4. 找到 "Connection string" -> "URI"
5. 选择 "Transaction mode" 或 "Session mode"
6. 复制连接字符串，格式如下:
   
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   
   或者直连格式:
   
   postgresql://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres

7. 更新 .env 文件中的 DATABASE_URL
""")

print("\n" + "=" * 70)
print("常见连接问题:")
print("=" * 70)
print("""
1. "Tenant or user not found"
   - 项目引用 (project-ref) 错误
   - 项目已被删除或暂停
   - 密码已过期

2. "Connection timeout"
   - 网络问题
   - 防火墙阻止
   - Supabase 服务宕机

3. "Password authentication failed"
   - 密码错误
   - 数据库密码已被重置

解决方案:
- 在 Supabase Dashboard 重新获取连接字符串
- 重置数据库密码（Settings -> Database -> Reset password）
- 检查项目状态是否为 Active
""")

print("\n" + "=" * 70)
print("快速验证 Supabase 项目:")
print("=" * 70)
print("""
访问以下 URL 验证项目是否存在:
https://supabase.com/dashboard/project/[你的项目-ref]/settings/database

例如（如果项目引用是 orygzioqsfvuauzklogx）:
https://supabase.com/dashboard/project/orygzioqsfvuauzklogx/settings/database
""")
