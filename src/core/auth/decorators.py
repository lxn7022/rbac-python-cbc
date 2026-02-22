"""
认证装饰器
用于保护需要登录的接口
"""

from functools import wraps
from typing import Callable, Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.auth.services import auth_service
from src.core.rbac.manager import rbac_manager
from src.utils.exceptions import AuthenticationError, PermissionDeniedError
from src.utils.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前登录用户
    
    从 Authorization Header 中提取 Token 并验证
    
    Returns:
        dict: 用户信息 {"user_id": int, "username": str, ...}
    
    Raises:
        HTTPException: Token 无效或过期
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # 验证 Token
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="无效的 Token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 获取用户信息
        user = auth_service.get_current_user(int(user_id))
        
        return {
            "user_id": user["id"],
            "username": user.get("username"),
            "email": user.get("email"),
            "is_active": user.get("is_active", True)
        }
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except AuthenticationError as e:
        logger.warning(f"认证失败: {e}")
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"获取当前用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_login(func: Callable) -> Callable:
    """
    登录验证装饰器
    
    使用示例：
    ```python
    @app.get("/protected")
    @require_login
    async def protected_route(current_user: dict):
        return {"user": current_user}
    ```
    
    注意：在 FastAPI 中推荐使用 Depends(get_current_user) 代替装饰器
    """
    @wraps(func)
    async def wrapper(*args, current_user: dict = None, **kwargs):
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="需要登录",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper


def require_permission(resource: str, action: str):
    """
    权限验证装饰器
    
    Args:
        resource: 资源名称
        action: 操作类型
    
    使用示例：
    ```python
    @app.delete("/users/{user_id}")
    @require_permission("user", "delete")
    async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
        # 只有拥有 user:delete 权限的用户才能访问
        pass
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="需要登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # 检查权限
            user_id = current_user.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="无效的用户信息")
            
            has_permission = rbac_manager.has_permission(user_id, resource, action)
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足：需要 {resource}:{action} 权限"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_role(role_slug: str):
    """
    角色验证装饰器
    
    Args:
        role_slug: 角色标识符
    
    使用示例：
    ```python
    @app.get("/admin/dashboard")
    @require_role("admin")
    async def admin_dashboard(current_user: dict = Depends(get_current_user)):
        # 只有管理员角色才能访问
        pass
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="需要登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # 检查角色
            user_id = current_user.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="无效的用户信息")
            
            has_role = rbac_manager.has_role(user_id, role_slug)
            
            if not has_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足：需要 {role_slug} 角色"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
