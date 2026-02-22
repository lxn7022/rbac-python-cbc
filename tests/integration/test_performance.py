"""
性能测试示例
使用 Supabase REST API
"""

import pytest
import time
from fastapi.testclient import TestClient
from datetime import datetime


class TestPerformance:
    """性能测试类"""
    
    def test_api_response_time(self, client: TestClient):
        """测试 API 响应时间"""
        # 测试健康检查端点
        num_requests = 100
        
        start_time = time.time()
        
        for _ in range(num_requests):
            response = client.get("/health")
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / num_requests
        
        print(f"\n执行 {num_requests} 次健康检查请求耗时: {duration:.3f}秒")
        print(f"平均每次请求响应时间: {avg_time * 1000:.2f}毫秒")
        
        # 性能要求：每次请求响应时间应小于 100 毫秒（网络延迟）
        assert avg_time < 0.1, f"API 响应速度过慢: {avg_time * 1000:.2f}毫秒/次"
    
    def test_user_list_performance(self, client: TestClient):
        """测试用户列表性能"""
        num_requests = 50
        
        start_time = time.time()
        
        for _ in range(num_requests):
            response = client.get("/api/v1/users/")
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / num_requests
        
        print(f"\n执行 {num_requests} 次用户列表请求耗时: {duration:.3f}秒")
        print(f"平均每次请求响应时间: {avg_time * 1000:.2f}毫秒")
        
        # 性能要求：每次请求响应时间应小于 500 毫秒
        assert avg_time < 0.5, f"用户列表请求速度过慢: {avg_time * 1000:.2f}毫秒/次"
    
    def test_role_list_performance(self, client: TestClient):
        """测试角色列表性能"""
        num_requests = 50
        
        start_time = time.time()
        
        for _ in range(num_requests):
            response = client.get("/api/v1/roles/")
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / num_requests
        
        print(f"\n执行 {num_requests} 次角色列表请求耗时: {duration:.3f}秒")
        print(f"平均每次请求响应时间: {avg_time * 1000:.2f}毫秒")
        
        # 性能要求：每次请求响应时间应小于 500 毫秒
        assert avg_time < 0.5, f"角色列表请求速度过慢: {avg_time * 1000:.2f}毫秒/次"
    
    def test_permission_list_performance(self, client: TestClient):
        """测试权限列表性能"""
        num_requests = 50
        
        start_time = time.time()
        
        for _ in range(num_requests):
            response = client.get("/api/v1/permissions/")
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / num_requests
        
        print(f"\n执行 {num_requests} 次权限列表请求耗时: {duration:.3f}秒")
        print(f"平均每次请求响应时间: {avg_time * 1000:.2f}毫秒")
        
        # 性能要求：每次请求响应时间应小于 500 毫秒
        assert avg_time < 0.5, f"权限列表请求速度过慢: {avg_time * 1000:.2f}毫秒/次"
