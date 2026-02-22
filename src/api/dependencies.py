"""
API 依赖注入
"""

from src.db.supabase_client import supabase_db


def get_supabase():
    """
    获取 Supabase 客户端实例
    
    用于依赖注入：
    ```python
    @app.get("/users")
    async def get_users(supabase = Depends(get_supabase)):
        return supabase.get_all_users()
    ```
    """
    return supabase_db
