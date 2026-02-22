"""
API 路由定义
完全使用 Supabase REST API
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.db.supabase_client import supabase_db
from src.api.schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    PermissionCreate, PermissionResponse, PermissionListResponse,
    LoginRequest, LoginResponse, RegisterRequest, TokenResponse,
    AssignRoleRequest, GrantPermissionRequest, MessageResponse,
)
from src.core.auth.services import auth_service
from src.core.auth.decorators import get_current_user
from src.core.rbac.manager import rbac_manager
from src.utils.exceptions import (
    UserNotFoundError, RoleNotFoundError, PermissionDeniedError,
    ConstraintViolationError, AuthenticationError
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 创建路由
api_router = APIRouter()


# ============================================================================
# 认证路由
# ============================================================================

@api_router.post("/auth/login", tags=["认证"])
async def login(request: LoginRequest):
    """用户登录"""
    try:
        result = auth_service.login(request.username, request.password)
        
        # 返回响应同时设置 Cookie（用于前端自动携带 Token）
        from fastapi.responses import JSONResponse
        response_data = {
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "expires_in": result["expires_in"],
            "user": {
                "username": result["user"].get("username"),
                "email": result["user"].get("email"),
                "full_name": result["user"].get("full_name"),
            }
        }
        
        response = JSONResponse(content=response_data)
        # 设置 HttpOnly Cookie
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            max_age=result["expires_in"],
            samesite="lax"
        )
        
        return response
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败")


@api_router.post("/auth/register", tags=["认证"])
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        user = auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        return {
            "message": "注册成功",
            "username": user.get("username")
        }
        
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail="注册失败")


@api_router.post("/auth/refresh", tags=["认证"])
async def refresh_token(request: TokenResponse):
    """刷新 Token"""
    try:
        result = auth_service.refresh_token(request.refresh_token)
        return result
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token 刷新失败: {e}")
        raise HTTPException(status_code=500, detail="Token 刷新失败")


@api_router.post("/auth/logout", tags=["认证"])
async def logout():
    """用户登出"""
    from fastapi.responses import JSONResponse
    response = JSONResponse(content={"message": "登出成功"})
    response.delete_cookie("access_token")
    return response


@api_router.get("/auth/me", tags=["认证"])
async def get_me(current_user: dict = get_current_user):
    """获取当前用户信息"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的用户信息")
        
        user = auth_service.get_current_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


# ============================================================================
# 用户管理路由
# ============================================================================

@api_router.get("/users", response_model=UserListResponse, tags=["用户管理"])
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = get_current_user
):
    """获取用户列表"""
    try:
        result = supabase_db.get_all_users(
            page=page,
            size=size,
            search=search,
            is_active=is_active
        )
        
        return UserListResponse(
            items=[UserResponse(**user) for user in result["items"]],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户列表失败")


@api_router.post("/users", response_model=UserResponse, status_code=201, tags=["用户管理"])
async def create_user(request: UserCreate):
    """创建用户（公开接口，用于注册）"""
    try:
        # 使用认证服务注册用户
        user = auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        return UserResponse(**user)
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建用户失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@api_router.get("/users/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def get_user(user_id: int, current_user: dict = get_current_user):
    """获取用户详情"""
    try:
        user = supabase_db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取用户角色
        roles = rbac_manager.get_user_roles(user_id)
        user["roles"] = roles
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户详情失败")


@api_router.put("/users/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: dict = get_current_user
):
    """更新用户"""
    try:
        # 只更新提供的字段
        update_data = request.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="没有要更新的数据")
        
        user = supabase_db.update_user(user_id, update_data)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败: {e}")
        raise HTTPException(status_code=500, detail="更新用户失败")


@api_router.delete("/users/{user_id}", tags=["用户管理"])
async def delete_user(user_id: int, current_user: dict = get_current_user):
    """删除用户"""
    try:
        success = supabase_db.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {"message": "用户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        raise HTTPException(status_code=500, detail="删除用户失败")


# ============================================================================
# 角色管理路由
# ============================================================================

@api_router.get("/roles", response_model=RoleListResponse, tags=["角色管理"])
async def get_roles(current_user: dict = get_current_user):
    """获取角色列表"""
    try:
        roles = supabase_db.get_all_roles()
        
        return RoleListResponse(
            items=[RoleResponse(**role) for role in roles],
            total=len(roles)
        )
    except Exception as e:
        logger.error(f"获取角色列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取角色列表失败")


@api_router.get("/roles/{role_id}", response_model=RoleResponse, tags=["角色管理"])
async def get_role(role_id: int, current_user: dict = get_current_user):
    """获取角色详情"""
    try:
        role = supabase_db.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 获取角色权限
        permissions = rbac_manager.get_role_permissions(role_id)
        role["permissions"] = permissions
        
        return RoleResponse(**role)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取角色详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取角色详情失败")


@api_router.post("/roles", response_model=RoleResponse, tags=["角色管理"])
async def create_role(request: RoleCreate, current_user: dict = get_current_user):
    """创建角色"""
    try:
        # 检查 slug 是否已存在
        existing = supabase_db.get_role_by_slug(request.slug)
        if existing:
            raise HTTPException(status_code=400, detail="角色标识已存在")
        
        role_data = request.dict()
        role = supabase_db.create_role(role_data)
        
        if not role:
            raise HTTPException(status_code=500, detail="创建角色失败")
        
        return RoleResponse(**role)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建角色失败: {e}")
        raise HTTPException(status_code=500, detail="创建角色失败")


@api_router.put("/roles/{role_id}", response_model=RoleResponse, tags=["角色管理"])
async def update_role(
    role_id: int,
    request: RoleUpdate,
    current_user: dict = get_current_user
):
    """更新角色"""
    try:
        # 只更新提供的字段
        update_data = request.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="没有要更新的数据")
        
        role = supabase_db.update_role(role_id, update_data)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return RoleResponse(**role)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新角色失败: {e}")
        raise HTTPException(status_code=500, detail="更新角色失败")


@api_router.delete("/roles/{role_id}", tags=["角色管理"])
async def delete_role(role_id: int, current_user: dict = get_current_user):
    """删除角色"""
    try:
        # 检查是否为系统角色
        role = supabase_db.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        if role.get("is_system"):
            raise HTTPException(status_code=400, detail="系统角色不能删除")
        
        success = supabase_db.delete_role(role_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除角色失败")
        
        return {"message": "角色删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除角色失败: {e}")
        raise HTTPException(status_code=500, detail="删除角色失败")


# ============================================================================
# 权限管理路由
# ============================================================================

@api_router.get("/permissions", response_model=PermissionListResponse, tags=["权限管理"])
async def get_permissions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    module: Optional[str] = Query(None),
    current_user: dict = get_current_user
):
    """获取权限列表"""
    try:
        result = supabase_db.get_all_permissions(
            module=module,
            page=page,
            size=size
        )
        
        return PermissionListResponse(
            items=[PermissionResponse(**perm) for perm in result["items"]],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as e:
        logger.error(f"获取权限列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取权限列表失败: {str(e)}")
    except Exception as e:
        logger.error(f"获取权限列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取权限列表失败")


@api_router.post("/permissions", response_model=PermissionResponse, tags=["权限管理"])
async def create_permission(
    request: PermissionCreate,
    current_user: dict = get_current_user
):
    """创建权限"""
    try:
        permission_data = request.dict()
        permission = supabase_db.create_permission(permission_data)
        
        if not permission:
            raise HTTPException(status_code=500, detail="创建权限失败")
        
        return PermissionResponse(**permission)
    except Exception as e:
        logger.error(f"创建权限失败: {e}")
        raise HTTPException(status_code=500, detail="创建权限失败")


@api_router.delete("/permissions/{permission_id}", tags=["权限管理"])
async def delete_permission(permission_id: int, current_user: dict = get_current_user):
    """删除权限"""
    try:
        # 检查是否为系统权限
        permission = supabase_db.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="权限不存在")
        
        if permission.get("is_system"):
            raise HTTPException(status_code=400, detail="系统权限不能删除")
        
        success = supabase_db.delete_permission(permission_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除权限失败")
        
        return {"message": "权限删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除权限失败: {e}")
        raise HTTPException(status_code=500, detail="删除权限失败")


# ============================================================================
# 用户角色分配
# ============================================================================

@api_router.post("/users/{user_id}/roles", tags=["用户角色"])
async def assign_role(
    user_id: int,
    request: AssignRoleRequest,
    current_user: dict = get_current_user
):
    """为用户分配角色"""
    try:
        result = rbac_manager.assign_role(
            user_id=user_id,
            role_id=request.role_id,
            assigned_by=current_user.get("user_id"),
            expires_at=request.expires_at
        )
        
        return {"message": "角色分配成功", "role_id": request.role_id}
    except ConstraintViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"分配角色失败: {e}")
        raise HTTPException(status_code=500, detail="分配角色失败")


@api_router.delete("/users/{user_id}/roles/{role_id}", tags=["用户角色"])
async def revoke_role(
    user_id: int,
    role_id: int,
    current_user: dict = get_current_user
):
    """撤销用户角色"""
    try:
        success = rbac_manager.revoke_role(user_id, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户角色关联不存在")
        
        return {"message": "角色撤销成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"撤销角色失败: {e}")
        raise HTTPException(status_code=500, detail="撤销角色失败")


@api_router.get("/users/{user_id}/roles", tags=["用户角色"])
async def get_user_roles(user_id: int, current_user: dict = get_current_user):
    """获取用户的角色列表"""
    try:
        roles = rbac_manager.get_user_roles(user_id)
        return {"roles": roles}
    except Exception as e:
        logger.error(f"获取用户角色失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户角色失败")


# ============================================================================
# 角色权限分配
# ============================================================================

@api_router.post("/roles/{role_id}/permissions", tags=["角色权限"])
async def grant_permission(
    role_id: int,
    request: GrantPermissionRequest,
    current_user: dict = get_current_user
):
    """为角色授予权限"""
    try:
        result = rbac_manager.grant_permission(
            role_id=role_id,
            permission_id=request.permission_id,
            granted_by=current_user.get("user_id")
        )
        
        return {"message": "权限授予成功", "permission_id": request.permission_id}
    except Exception as e:
        logger.error(f"授予权限失败: {e}")
        raise HTTPException(status_code=500, detail="授予权限失败")


@api_router.delete("/roles/{role_id}/permissions/{permission_id}", tags=["角色权限"])
async def revoke_permission(
    role_id: int,
    permission_id: int,
    current_user: dict = get_current_user
):
    """撤销角色权限"""
    try:
        success = rbac_manager.revoke_permission(role_id, permission_id)
        if not success:
            raise HTTPException(status_code=404, detail="角色权限关联不存在")
        
        return {"message": "权限撤销成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"撤销权限失败: {e}")
        raise HTTPException(status_code=500, detail="撤销权限失败")


@api_router.get("/roles/{role_id}/permissions", tags=["角色权限"])
async def get_role_permissions(role_id: int, current_user: dict = get_current_user):
    """获取角色的权限列表"""
    try:
        permissions = rbac_manager.get_role_permissions(role_id)
        return {"permissions": permissions}
    except Exception as e:
        logger.error(f"获取角色权限失败: role_id={role_id}, error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取角色权限失败: {str(e)}")


# ============================================================================
# 权限检查
# ============================================================================

@api_router.get("/users/{user_id}/permissions", tags=["权限检查"])
async def get_user_permissions(user_id: int, current_user: dict = get_current_user):
    """获取用户的所有权限"""
    try:
        permissions = rbac_manager.get_all_permissions(user_id)
        return {"permissions": list(permissions)}
    except Exception as e:
        logger.error(f"获取用户权限失败: user_id={user_id}, error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取用户权限失败: {str(e)}")


@api_router.post("/check-permission", tags=["权限检查"])
async def check_permission(
    request: dict,
    current_user: dict = get_current_user
):
    """检查用户是否拥有特定权限"""
    try:
        user_id = request.get("user_id")
        resource = request.get("resource")
        action = request.get("action")
        
        if not all([user_id, resource, action]):
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        has_perm = rbac_manager.has_permission(user_id, resource, action)
        
        return {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "has_permission": has_perm
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"权限检查失败: {e}")
        raise HTTPException(status_code=500, detail="权限检查失败")
