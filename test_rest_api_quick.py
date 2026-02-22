"""
快速测试 Supabase REST API 连接

验证当前实现是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_rest_api():
    """测试 REST API 客户端"""
    print("=" * 60)
    print("测试 Supabase REST API 连接".center(60))
    print("=" * 60)
    
    try:
        from src.db.supabase_client import supabase_db
        from dotenv import load_dotenv
        
        # 加载环境变量
        load_dotenv()
        
        print("\n测试 1: 查询用户列表")
        users = supabase_db.get_all_users(page=1, size=5)
        print(f"✅ 查询成功！总用户数: {users['total']}")
        if users['items']:
            print(f"   前5个用户:")
            for user in users['items']:
                print(f"   - {user.get('username')}: {user.get('email')}")
        
        print("\n测试 2: 根据用户名查询")
        user = supabase_db.get_user_by_username("admin")
        if user:
            print(f"✅ 找到用户: {user.get('username')}")
        else:
            print("✅ 查询成功（用户不存在）")
        
        print("\n测试 3: 根据邮箱查询")
        user = supabase_db.get_user_by_email("admin@example.com")
        if user:
            print(f"✅ 找到用户: {user.get('email')}")
        else:
            print("✅ 查询成功（邮箱不存在）")
        
        print("\n测试 4: 查询角色列表")
        roles = supabase_db.get_all_roles()
        print(f"✅ 查询成功！角色数量: {len(roles)}")
        for role in roles[:3]:
            print(f"   - {role.get('name')} ({role.get('slug')})")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！REST API 连接正常".center(60))
        print("=" * 60)
        
        print("\n💡 结论:")
        print("   - REST API 通过 HTTPS 443 端口连接成功")
        print("   - 不受防火墙限制")
        print("   - 推荐继续使用此方案")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 解决方案:")
        print("   1. 检查 .env 文件是否存在")
        print("   2. 检查 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 是否正确")
        print("   3. 检查网络连接是否正常")
        
        return False


if __name__ == "__main__":
    success = test_rest_api()
    sys.exit(0 if success else 1)
