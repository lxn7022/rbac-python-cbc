"""
Supabase 连接诊断工具

检查网络连通性和配置是否正确
"""

import socket
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def test_port_connectivity():
    """测试端口连通性"""
    print_header("测试 1: 端口连通性检查")
    
    # 从环境变量获取项目 URL
    supabase_url = os.getenv('SUPABASE_URL')
    if not supabase_url:
        print("  ❌ SUPABASE_URL 未设置，无法测试端口连通性")
        return {}
    
    # 提取项目引用
    try:
        project_ref = supabase_url.split('//')[1].split('.supabase.co')[0]
    except:
        print(f"  ❌ 无法解析 SUPABASE_URL: {supabase_url}")
        return {}
    
    hosts = [
        (f"db.{project_ref}.supabase.co", 5432, "Supabase 直连"),
        ("aws-0-ap-southeast-1.pooler.supabase.com", 6543, "Supabase Pooler"),
    ]
    
    results = {}
    
    for host, port, name in hosts:
        try:
            print(f"\n测试 {name} ({host}:{port})...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            
            if result == 0:
                print(f"  ✅ 端口 {port} 可访问")
                results[f"{host}:{port}"] = True
            else:
                print(f"  ❌ 端口 {port} 不可访问（错误码: {result}）")
                print(f"  💡 可能原因：防火墙阻挡或网络限制")
                results[f"{host}:{port}"] = False
            
            sock.close()
        except socket.gaierror:
            print(f"  ❌ DNS 解析失败")
            results[f"{host}:{port}"] = False
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            results[f"{host}:{port}"] = False
    
    return results


def test_https_connectivity():
    """测试 HTTPS 连接"""
    print_header("测试 2: HTTPS 连接检查")
    
    try:
        import requests
        
        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url:
            print("  ❌ SUPABASE_URL 未设置，无法测试 HTTPS 连接")
            return False
        
        url = f"{supabase_url}/rest/v1/"
        
        print(f"\n测试 REST API ({url})...")
        
        # 不需要认证，只测试连通性
        response = requests.options(url, timeout=10)
        
        if response.status_code in [200, 204, 401, 403]:
            print(f"  ✅ HTTPS 连接成功（状态码: {response.status_code}）")
            print(f"  💡 REST API 可用（端口 443）")
            return True
        else:
            print(f"  ⚠️ HTTPS 连接异常（状态码: {response.status_code}）")
            return False
            
    except Exception as e:
        print(f"  ❌ HTTPS 连接失败: {e}")
        return False


def check_environment():
    """检查环境变量配置"""
    print_header("测试 3: 环境变量检查")
    
    env_vars = {
        "SUPABASE_URL": "Supabase 项目 URL",
        "SUPABASE_SERVICE_ROLE_KEY": "Service Role Key",
        "SUPABASE_DATABASE_URL": "数据库直连 URL",
        "SUPABASE_ANON_KEY": "Anon Key",
        "DATABASE_URL": "本地数据库 URL",
        "ENVIRONMENT": "运行环境",
    }
    
    configured = []
    missing = []
    
    for var, desc in env_vars.items():
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if "KEY" in var or "PASSWORD" in var:
                display = value[:20] + "..." if len(value) > 20 else "***"
            elif "URL" in var and "@" in value:
                # 隐藏密码部分
                parts = value.split("@")
                display = parts[0].rsplit(":", 1)[0] + ":***@" + parts[1]
            else:
                display = value
            
            print(f"  ✅ {var}: {display}")
            configured.append(var)
        else:
            print(f"  ⚪ {var}: 未配置")
            missing.append(var)
    
    return configured, missing


def test_current_rest_api():
    """测试当前 REST API 实现"""
    print_header("测试 4: REST API 功能测试")
    
    try:
        from src.db.supabase_client import supabase_db
        
        print("\n测试查询用户...")
        user = supabase_db.get_user_by_username("admin")
        
        if user:
            print(f"  ✅ REST API 查询成功")
            print(f"  ✅ 找到用户: {user.get('username')}")
            return True
        else:
            print(f"  ✅ REST API 查询成功（用户不存在）")
            return True
            
    except Exception as e:
        print(f"  ❌ REST API 测试失败: {e}")
        return False


def test_sqlalchemy_connection():
    """测试 SQLAlchemy 连接"""
    print_header("测试 5: SQLAlchemy 连接测试")
    
    database_url = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not database_url:
        print("  ⚪ 未配置数据库连接字符串")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        
        print(f"\n尝试连接数据库...")
        
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "sslmode": "require"
            }
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"  ✅ SQLAlchemy 连接成功")
            print(f"  ✅ PostgreSQL 版本: {version[:50]}...")
            return True
            
    except Exception as e:
        print(f"  ❌ SQLAlchemy 连接失败: {e}")
        return False


def generate_recommendation(results):
    """生成推荐方案"""
    print_header("推荐方案")
    
    port_ok = any(results.get("port_tests", {}).values())
    https_ok = results.get("https_test", False)
    rest_api_ok = results.get("rest_api_test", False)
    sqlalchemy_ok = results.get("sqlalchemy_test", False)
    
    print()
    
    if sqlalchemy_ok:
        print("✅ SQLAlchemy 直连可用")
        print("   推荐使用 SQLAlchemy ORM 模式")
        print()
        print("   配置步骤：")
        print("   1. 在 .env 中配置 SUPABASE_DATABASE_URL")
        print("   2. 使用端口 6543（Pooler）而非 5432")
        print("   3. 修改代码使用 SQLAlchemy")
        
    elif port_ok and not sqlalchemy_ok:
        print("⚠️ 端口可访问但 SQLAlchemy 连接失败")
        print("   请检查：")
        print("   1. 连接字符串是否正确")
        print("   2. 数据库密码是否正确")
        print("   3. SSL 配置是否启用")
        
    elif rest_api_ok:
        print("✅ REST API 可用（推荐）")
        print("   防火墙阻挡了 PostgreSQL 端口，但 REST API 可用")
        print()
        print("   当前实现：")
        print("   - 使用 src/db/supabase_client.py")
        print("   - 通过 HTTPS 443 端口连接")
        print("   - 无需开放额外端口")
        print()
        print("   优势：")
        print("   ✅ 不受防火墙限制")
        print("   ✅ 已实现并测试通过")
        print("   ✅ 适合生产环境")
        
    elif https_ok:
        print("⚠️ HTTPS 可用但 REST API 配置有问题")
        print("   请检查：")
        print("   1. SUPABASE_URL 是否正确")
        print("   2. SUPABASE_SERVICE_ROLE_KEY 是否有效")
        
    else:
        print("❌ 所有连接方式都不可用")
        print("   请检查：")
        print("   1. 网络连接是否正常")
        print("   2. Supabase 项目是否激活")
        print("   3. 防火墙是否完全阻挡")


def main():
    """运行所有诊断"""
    print("\n" + "🔍 Supabase 连接诊断工具".center(60, "="))
    
    # 加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("\n✅ 已加载 .env 文件")
    except:
        print("\n⚠️ 未找到 .env 文件（使用系统环境变量）")
    
    # 运行测试
    results = {}
    
    # 1. 端口连通性
    results["port_tests"] = test_port_connectivity()
    
    # 2. HTTPS 连接
    results["https_test"] = test_https_connectivity()
    
    # 3. 环境变量
    results["env_configured"], results["env_missing"] = check_environment()
    
    # 4. REST API
    results["rest_api_test"] = test_current_rest_api()
    
    # 5. SQLAlchemy
    results["sqlalchemy_test"] = test_sqlalchemy_connection()
    
    # 生成推荐
    generate_recommendation(results)
    
    # 总结
    print_header("测试总结")
    print()
    print("端口连通性:")
    for endpoint, ok in results["port_tests"].items():
        status = "✅ 可访问" if ok else "❌ 不可访问"
        print(f"  {endpoint}: {status}")
    
    print(f"\nHTTPS 连接: {'✅ 可用' if results['https_test'] else '❌ 不可用'}")
    print(f"REST API: {'✅ 可用' if results['rest_api_test'] else '❌ 不可用'}")
    print(f"SQLAlchemy: {'✅ 可用' if results['sqlalchemy_test'] else '❌ 不可用'}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
