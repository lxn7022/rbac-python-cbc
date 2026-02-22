"""
直接使用 Supabase 连接和初始化数据库
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("=" * 60)
print("Supabase 数据库连接测试")
print("=" * 60)
print(f"\n数据库 URL: {DATABASE_URL[:50]}...")

try:
    # 连接到 Supabase
    print("\n正在连接到 Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("✅ 连接成功！")
    
    # 检查现有表
    print("\n检查现有表...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"找到 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table['table_name']}")
    else:
        print("数据库为空，需要创建表")
    
    # 读取 SQL 初始化脚本
    sql_file = os.path.join(os.path.dirname(__file__), 'supabase_init.sql')
    if os.path.exists(sql_file):
        print(f"\n读取 SQL 初始化脚本: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行 SQL 脚本
        print("\n执行 SQL 脚本...")
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ SQL 脚本执行成功！")
        
        # 再次检查表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        new_tables = cursor.fetchall()
        print(f"\n当前共有 {len(new_tables)} 个表")
        
        # 检查初始数据
        print("\n检查初始数据...")
        cursor.execute("SELECT COUNT(*) as count FROM users;")
        user_count = cursor.fetchone()['count']
        print(f"  - 用户: {user_count} 条")
        
        cursor.execute("SELECT COUNT(*) as count FROM roles;")
        role_count = cursor.fetchone()['count']
        print(f"  - 角色: {role_count} 条")
        
        cursor.execute("SELECT COUNT(*) as count FROM permissions;")
        perm_count = cursor.fetchone()['count']
        print(f"  - 权限: {perm_count} 条")
        
    else:
        print(f"\n⚠️  SQL 初始化脚本不存在: {sql_file}")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Supabase 数据库初始化完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 连接或初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
