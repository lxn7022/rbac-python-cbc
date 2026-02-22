"""
Supabase 数据库连接测试脚本
用于验证 Supabase 连接是否正确
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings

print("=" * 60)
print("Supabase 数据库连接测试")
print("=" * 60)
print()

print(f"数据库 URL: {settings.DATABASE_URL}")
print(f"Supabase URL: {settings.SUPABASE_URL}")
print()

# 尝试连接
try:
    from sqlalchemy import create_engine, text
    from urllib.parse import urlparse

    # 解析连接字符串
    parsed = urlparse(settings.DATABASE_URL)
    
    print("连接信息:")
    print(f"  主机: {parsed.hostname}")
    print(f"  端口: {parsed.port}")
    print(f"  数据库: {parsed.path[1:]}")
    print(f"  用户: {parsed.username}")
    print(f"  密码: {'*' * len(parsed.password)}")
    print()

    # 尝试连接
    engine = create_engine(settings.DATABASE_URL)
    
    print("尝试连接数据库...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print()
        print("=" * 60)
        print("连接成功！")
        print("=" * 60)
        print()
        print(f"PostgreSQL 版本: {version}")
        
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("连接失败！")
    print("=" * 60)
    print()
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print()
    
    print("可能的原因:")
    print("1. Supabase 项目不存在或已被删除")
    print("2. 数据库密码已更改")
    print("3. Supabase 项目已暂停")
    print("4. IP 地址被限制访问")
    print()
    
    print("解决方法:")
    print("1. 登录 Supabase 控制台: https://supabase.com/dashboard")
    print("2. 选择你的项目")
    print("3. 进入 Settings > Database")
    print("4. 复制 Connection String > URI")
    print("5. 更新 .env 文件中的 DATABASE_URL")
    print()
    print("正确的连接字符串格式:")
    print("postgresql://postgres.[PROJECT_REF]:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres")
