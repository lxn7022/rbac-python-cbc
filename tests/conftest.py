"""
Pytest 配置和 fixtures
使用 Supabase REST API
"""

import pytest
import sys
import os
from pathlib import Path

# Windows 控制台编码设置
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="session")
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture(scope="session")
def supabase_db():
    """获取 Supabase 数据库客户端"""
    from src.db.supabase_client import supabase_db
    return supabase_db


# 以下 fixtures 已弃用，保留仅为向后兼容
@pytest.fixture(scope="function")
def db_session():
    """
    已弃用：数据库会话 fixture
    项目已迁移到 Supabase REST API，此 fixture 不再使用
    """
    return None
