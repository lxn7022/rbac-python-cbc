"""
测试 Supabase 项目引用是否存在
"""

import sys
import os
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')

print("=" * 70)
print("Supabase 项目验证")
print("=" * 70)
print(f"\nSUPABASE_URL: {SUPABASE_URL}")

if not SUPABASE_URL:
    print("\n错误: SUPABASE_URL 未设置")
    sys.exit(1)

# 提取项目引用
if 'supabase.co' in SUPABASE_URL:
    project_ref = SUPABASE_URL.split('//')[1].split('.supabase.co')[0]
    print(f"项目引用: {project_ref}")
    
    print(f"\n正在验证项目...")
    print(f"访问: https://supabase.com/dashboard/project/{project_ref}")
    
    # 尝试访问 Supabase REST API（不需要认证）
    api_url = f"{SUPABASE_URL}/rest/v1/"
    
    print(f"\n测试 API 连接: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=10)
        
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 404:
            print("\n[错误] 项目不存在或已被删除")
            print("\n解决方案:")
            print("1. 访问 https://supabase.com/dashboard")
            print("2. 检查项目列表中是否存在该项目")
            print("3. 如果项目被删除，需要创建新项目")
            print("4. 获取新项目的连接字符串")
        elif response.status_code == 401:
            print("\n[警告] 需要认证（项目存在但需要密钥）")
            print("这是正常的，说明项目存在")
        elif response.status_code == 200:
            print("\n[成功] 项目存在且可访问")
        else:
            print(f"\n[未知] 响应状态: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("\n[超时] 连接超时")
        print("可能原因:")
        print("- 网络问题")
        print("- Supabase 服务暂时不可用")
        print("- 防火墙阻止连接")
    except requests.exceptions.ConnectionError:
        print("\n[连接错误] 无法连接到 Supabase")
        print("可能原因:")
        print("- URL 格式错误")
        print("- 网络不可达")
        print("- DNS 解析失败")
    except Exception as e:
        print(f"\n[错误] {e}")
        
else:
    print("\n错误: SUPABASE_URL 格式不正确")
    print("应为: https://[project-ref].supabase.co")

print("\n" + "=" * 70)
