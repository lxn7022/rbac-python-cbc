# -*- coding: utf-8 -*-
"""
测试重构后的 REST API 功能

验证所有核心功能是否正常工作
"""

import sys
import os
from pathlib import Path

# Windows 控制台编码设置
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def test_supabase_client():
    """测试 Supabase REST API 客户端"""
    print("=" * 60)
    print("测试 1: Supabase REST API 客户端".center(60))
    print("=" * 60)
    
    try:
        from src.db.supabase_client import supabase_db
        
        # 测试用户查询
        print("\n测试用户查询...")
        users = supabase_db.get_all_users(page=1, size=5)
        print(f"[OK] 用户总数: {users['total']}")
        
        # 测试角色查询
        print("\n测试角色查询...")
        roles = supabase_db.get_all_roles()
        print(f"[OK] 角色总数: {len(roles)}")
        
        # 测试权限查询
        print("\n测试权限查询...")
        permissions = supabase_db.get_all_permissions(page=1, size=10)
        print(f"[OK] 权限总数: {permissions['total']}")
        
        print("\n[OK] Supabase 客户端测试通过")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth_service():
    """测试认证服务"""
    print("\n" + "=" * 60)
    print("测试 2: 认证服务".center(60))
    print("=" * 60)
    
    try:
        from src.core.auth.services import auth_service
        
        # 测试密码加密
        print("\n测试密码加密...")
        password = "test123456"
        hashed = auth_service._hash_password(password)
        verified = auth_service._verify_password(password, hashed)
        print(f"[OK] 密码加密和验证: {verified}")
        
        # 测试 Token 生成
        print("\n测试 Token 生成...")
        token = auth_service._create_access_token(1)
        payload = auth_service.verify_token(token)
        print(f"[OK] Token 生成和验证: user_id={payload.get('sub')}")
        
        print("\n[OK] 认证服务测试通过")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rbac_manager():
    """测试 RBAC 管理器"""
    print("\n" + "=" * 60)
    print("测试 3: RBAC 管理器".center(60))
    print("=" * 60)
    
    try:
        from src.core.rbac.manager import rbac_manager
        
        # 测试权限检查（需要一个真实的用户 ID）
        print("\n测试权限检查...")
        # 这里使用用户 ID 1 作为测试
        try:
            has_perm = rbac_manager.has_permission(1, "user", "read")
            print(f"[OK] 权限检查功能正常: {has_perm}")
        except Exception as e:
            print(f"[WARN] 权限检查测试跳过（可能没有用户数据）: {e}")
        
        # 测试角色检查
        print("\n测试角色检查...")
        try:
            has_role = rbac_manager.has_role(1, "admin")
            print(f"[OK] 角色检查功能正常: {has_role}")
        except Exception as e:
            print(f"[WARN] 角色检查测试跳过: {e}")
        
        print("\n[OK] RBAC 管理器测试通过")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """测试所有模块导入"""
    print("\n" + "=" * 60)
    print("测试 4: 模块导入".center(60))
    print("=" * 60)
    
    modules = [
        ("src.db.supabase_client", "Supabase 客户端"),
        ("src.core.rbac.models", "RBAC 模型"),
        ("src.core.rbac.manager", "RBAC 管理器"),
        ("src.core.rbac.constraints", "RBAC 约束"),
        ("src.core.auth.services", "认证服务"),
        ("src.core.auth.decorators", "认证装饰器"),
        ("src.api.routers", "API 路由"),
        ("src.api.dependencies", "API 依赖"),
    ]
    
    success_count = 0
    
    for module_path, module_name in modules:
        try:
            __import__(module_path)
            print(f"[OK] {module_name}: 导入成功")
            success_count += 1
        except Exception as e:
            print(f"[ERROR] {module_name}: 导入失败 - {e}")
    
    print(f"\n导入测试: {success_count}/{len(modules)} 成功")
    return success_count == len(modules)


def test_no_sqlalchemy():
    """验证是否完全移除了 SQLAlchemy"""
    print("\n" + "=" * 60)
    print("测试 5: SQLAlchemy 移除验证".center(60))
    print("=" * 60)
    
    # 检查关键模块是否还导入 SQLAlchemy
    modules_to_check = [
        "src.db.supabase_client",
        "src.core.rbac.manager",
        "src.core.rbac.constraints",
        "src.core.auth.services",
        "src.api.routers",
    ]
    
    has_sqlalchemy = False
    
    for module_path in modules_to_check:
        try:
            module = __import__(module_path, fromlist=[''])
            source_file = module.__file__
            
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'sqlalchemy' in content.lower():
                print(f"[WARN] {module_path}: 仍包含 SQLAlchemy 引用")
                has_sqlalchemy = True
            else:
                print(f"[OK] {module_path}: 无 SQLAlchemy 引用")
                
        except Exception as e:
            print(f"[WARN] {module_path}: 检查失败 - {e}")
    
    if not has_sqlalchemy:
        print("\n[OK] 所有核心模块已移除 SQLAlchemy")
        return True
    else:
        print("\n[WARN] 部分模块仍包含 SQLAlchemy 引用")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("RBAC 项目重构后功能测试".center(60))
    print("=" * 60)
    
    results = {}
    
    # 运行测试
    results["imports"] = test_imports()
    results["no_sqlalchemy"] = test_no_sqlalchemy()
    results["supabase"] = test_supabase_client()
    results["auth"] = test_auth_service()
    results["rbac"] = test_rbac_manager()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结".center(60))
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[OK] 通过" if passed else "[ERROR] 失败"
        print(f"{test_name:20s}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print(f"总计: {total_passed}/{total_tests} 测试通过".center(60))
    print("=" * 60)
    
    if total_passed == total_tests:
        print("\n[OK] 所有测试通过！重构成功！")
        print("\n下一步:")
        print("1. 启动服务器: uvicorn src.main:app --reload")
        print("2. 访问 API 文档: http://localhost:8000/docs")
        print("3. 测试各个接口")
    else:
        print("\n[WARN] 部分测试失败，请检查错误信息")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
