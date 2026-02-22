"""
Supabase 数据库客户端
使用 Supabase 官方 Python Client Library
文档：https://supabase.com/docs/reference/python/introduction
"""

from typing import Any
from supabase import create_client, Client
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseDB:
    """Supabase 数据库操作类
    
    使用 Supabase 官方 Python 客户端
    通过 HTTPS 443 端口访问 Supabase API
    """

    def __init__(self):
        settings = get_settings()
        self.url: str | None = settings.SUPABASE_URL
        self.key: str | None = settings.SUPABASE_SERVICE_ROLE_KEY
        # 初始化官方客户端
        self._client: Client | None = None
        
        if self.url and self.key:
            try:
                self._client = create_client(self.url, self.key)
                # 出于安全考虑，不记录密钥信息
                logger.info(f"Supabase 客户端初始化成功。 url={self.url}")
            except Exception as e:
                logger.error(f"Supabase 客户端初始化失败: {e}")
                self._client = None
        else:
            logger.warning("Supabase 未配置（URL 或 Key 缺失）")
    
    @property
    def client(self) -> Client:
        """获取 Supabase 客户端实例"""
        if self._client is None:
            raise RuntimeError("Supabase 客户端未初始化")
        return self._client

    # ========================================================================
    # 用户管理
    # ========================================================================
    
    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """根据 ID 获取用户"""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取用户失败: user_id={user_id}, error={e}", exc_info=True)
            return None
    
    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        """根据用户名获取用户"""
        try:
            response = self.client.table("users").select("*").eq("username", username).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """根据邮箱获取用户（不区分大小写）"""
        try:
            # 使用 ilike 进行不区分大小写的查询
            response = self.client.table("users").select("*").ilike("email", email).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None

    def create_user(self, user_data: dict[str, Any]) -> dict[str, Any] | None:
        """创建用户"""
        try:
            response = self.client.table("users").insert(user_data).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None
    
    def update_user(self, user_id: int, user_data: dict[str, Any]) -> dict[str, Any] | None:
        """更新用户"""
        try:
            response = self.client.table("users").update(user_data).eq("id", user_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            response = self.client.table("users").delete().eq("id", user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False

    def get_all_users(
        self, 
        page: int = 1, 
        size: int = 20,
        search: str | None = None,
        is_active: bool | None = None
    ) -> dict[str, Any]:
        """获取所有用户（分页）"""
        try:
            # 参数验证
            if page < 1:
                page = 1
            if size < 1 or size > 100:
                size = 20
            
            # 计算偏移量
            offset = (page - 1) * size
            
            # 构建查询
            query = self.client.table("users").select("*", count="exact")
            
            # 添加搜索条件（检查非空字符串）
            if search and search.strip():
                search_term = search.strip()
                # 使用 or 条件搜索多个字段
                query = query.or_(f"username.ilike.%{search_term}%,email.ilike.%{search_term}%,full_name.ilike.%{search_term}%")
            
            # 添加状态过滤
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            # 排序和分页
            query = query.order("id", desc=False).range(offset, offset + size - 1)
            
            response = query.execute()
            
            return {
                "items": response.data or [],
                "total": response.count or 0,
                "page": page,
                "size": size
            }
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return {"items": [], "total": 0, "page": page, "size": size}
    
    # ========================================================================
    # 角色管理
    # ========================================================================
    
    def get_role_by_id(self, role_id: int) -> dict[str, Any] | None:
        """根据 ID 获取角色"""
        try:
            response = self.client.table("roles").select("*").eq("id", role_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取角色失败: {e}")
            return None
    
    def get_role_by_slug(self, slug: str) -> dict[str, Any] | None:
        """根据 slug 获取角色"""
        try:
            response = self.client.table("roles").select("*").eq("slug", slug).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取角色失败: {e}")
            return None
    
    def get_all_roles(self) -> list[dict[str, Any]]:
        """获取所有角色"""
        try:
            response = self.client.table("roles").select("*").order("priority", desc=True).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"获取角色列表失败: {e}")
            return []
    
    def create_role(self, role_data: dict[str, Any]) -> dict[str, Any] | None:
        """创建角色"""
        try:
            response = self.client.table("roles").insert(role_data).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            return None
    
    def update_role(self, role_id: int, role_data: dict[str, Any]) -> dict[str, Any] | None:
        """更新角色"""
        try:
            response = self.client.table("roles").update(role_data).eq("id", role_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"更新角色失败: {e}")
            return None
    
    def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        try:
            response = self.client.table("roles").delete().eq("id", role_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            return False
    
    # ========================================================================
    # 权限管理
    # ========================================================================
    
    def get_permission_by_id(self, permission_id: int) -> dict[str, Any] | None:
        """根据 ID 获取权限"""
        try:
            response = self.client.table("permissions").select("*").eq("id", permission_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取权限失败: {e}")
            return None
    
    def get_all_permissions(
        self, 
        module: str | None = None,
        page: int = 1,
        size: int = 20
    ) -> dict[str, Any]:
        """获取所有权限"""
        try:
            offset = (page - 1) * size
            
            query = self.client.table("permissions").select("*", count="exact")
            
            if module:
                query = query.eq("module", module)
            
            query = query.order("module").order("resource").order("action").range(offset, offset + size - 1)
            
            response = query.execute()
            
            return {
                "items": response.data or [],
                "total": response.count or 0,
                "page": page,
                "size": size
            }
        except Exception as e:
            logger.error(f"获取权限列表失败: {e}")
            return {"items": [], "total": 0, "page": page, "size": size}
    
    def create_permission(self, permission_data: dict[str, Any]) -> dict[str, Any] | None:
        """创建权限"""
        try:
            response = self.client.table("permissions").insert(permission_data).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"创建权限失败: {e}")
            return None
    
    def delete_permission(self, permission_id: int) -> bool:
        """删除权限"""
        try:
            response = self.client.table("permissions").delete().eq("id", permission_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"删除权限失败: {e}")
            return False
    
    # ========================================================================
    # 用户角色关联
    # ========================================================================
    
    def get_user_roles(self, user_id: int) -> list[dict[str, Any]]:
        """获取用户的所有角色"""
        try:
            # 使用关联查询获取角色信息
            response = (
                self.client.table("user_roles")
                .select("*, roles(id, name, slug, description, priority)")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .order("assigned_at", desc=True)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"获取用户角色失败: {e}")
            return []
    
    def assign_role(
        self, 
        user_id: int, 
        role_id: int, 
        assigned_by: int | None = None,
        expires_at: str | None = None
    ) -> dict[str, Any] | None:
        """为用户分配角色"""
        try:
            data = {
                "user_id": user_id,
                "role_id": role_id,
                "assigned_by": assigned_by,
                "expires_at": expires_at,
                "is_active": True
            }
            response = self.client.table("user_roles").insert(data).execute()
            result = response.data
            return result[0] if result else None
        except Exception as e:
            logger.error(f"分配角色失败: {e}")
            return None
    
    def revoke_role(self, user_id: int, role_id: int) -> bool:
        """撤销用户的角色（软删除）"""
        try:
            response = (
                self.client.table("user_roles")
                .update({"is_active": False})
                .eq("user_id", user_id)
                .eq("role_id", role_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"撤销角色失败: {e}")
            return False
    
    def get_user_role_by_id(self, user_id: int, role_id: int) -> dict[str, Any] | None:
        """获取用户角色关联"""
        try:
            response = (
                self.client.table("user_roles")
                .select("*")
                .eq("user_id", user_id)
                .eq("role_id", role_id)
                .execute()
            )
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取用户角色关联失败: {e}")
            return None
    
    # ========================================================================
    # 角色权限关联
    # ========================================================================
    
    def get_role_permissions(self, role_id: int) -> list[dict[str, Any]]:
        """获取角色的所有权限"""
        try:
            response = (
                self.client.table("role_permissions")
                .select("*, permissions(id, resource, action, description, module)")
                .eq("role_id", role_id)
                .eq("is_active", True)
                .order("granted_at", desc=True)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"获取角色权限失败: {e}")
            return []
    
    def grant_permission(
        self, 
        role_id: int, 
        permission_id: int, 
        granted_by: int | None = None
    ) -> dict[str, Any] | None:
        """为角色授予权限"""
        try:
            data = {
                "role_id": role_id,
                "permission_id": permission_id,
                "granted_by": granted_by,
                "is_active": True
            }
            response = self.client.table("role_permissions").insert(data).execute()
            result = response.data
            return result[0] if result else None
        except Exception as e:
            logger.error(f"授予权限失败: {e}")
            return None
    
    def revoke_permission(self, role_id: int, permission_id: int) -> bool:
        """撤销角色的权限（软删除）"""
        try:
            response = (
                self.client.table("role_permissions")
                .update({"is_active": False})
                .eq("role_id", role_id)
                .eq("permission_id", permission_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"撤销权限失败: {e}")
            return False
    
    def get_role_permission_by_id(self, role_id: int, permission_id: int) -> dict[str, Any] | None:
        """获取角色权限关联"""
        try:
            response = (
                self.client.table("role_permissions")
                .select("*")
                .eq("role_id", role_id)
                .eq("permission_id", permission_id)
                .execute()
            )
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取角色权限关联失败: {e}")
            return None
    
    # ========================================================================
    # 权限检查
    # ========================================================================
    
    def get_user_permissions(self, user_id: int) -> list[dict[str, Any]]:
        """获取用户的所有权限（包括从角色继承的）
        
        优化：使用单次关联查询替代 N+1 查询
        """
        try:
            # 一次性查询用户角色和权限，避免 N+1 问题
            response = (
                self.client.table("user_roles")
                .select(
                    "role_id, "
                    "roles!inner(id, slug), "
                    "roles.role_permissions(is_active, permissions!inner(id, resource, action, description, module))"
                )
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )
            
            user_roles = response.data or []
            
            if not user_roles:
                return []
            
            # 收集所有权限并去重
            permissions: list[dict[str, Any]] = []
            seen: set[str] = set()
            
            for ur in user_roles:
                # 类型守卫：确保 ur 是字典
                if not isinstance(ur, dict):
                    continue
                    
                role_data = ur.get("roles")
                if not role_data or not isinstance(role_data, dict):
                    continue
                
                # 获取角色权限
                role_perms = role_data.get("role_permissions", [])
                if not isinstance(role_perms, list):
                    continue
                
                for rp in role_perms:
                    if not isinstance(rp, dict):
                        continue
                    if not rp.get("is_active"):
                        continue
                    
                    perm = rp.get("permissions")
                    if perm and isinstance(perm, dict):
                        # 去重
                        resource = perm.get("resource")
                        action = perm.get("action")
                        if resource and action:
                            perm_key = f"{resource}:{action}"
                            if perm_key not in seen:
                                permissions.append(perm)
                                seen.add(perm_key)
            
            return permissions
        except Exception as e:
            logger.error(f"获取用户权限失败: {e}")
            return []
    
    def has_permission(self, user_id: int, resource: str, action: str) -> bool:
        """检查用户是否拥有特定权限
        
        优化：直接检查特定权限，而不是获取所有权限
        """
        try:
            # 使用更高效的查询：通过用户角色直接检查权限
            response = (
                self.client.table("user_roles")
                .select("role_id")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )
            
            user_roles = response.data or []
            if not user_roles:
                return False
            
            # 提取角色 ID 列表（类型守卫）
            role_ids: list[int] = []
            for ur in user_roles:
                if isinstance(ur, dict) and "role_id" in ur:
                    role_id = ur["role_id"]
                    if isinstance(role_id, int):
                        role_ids.append(role_id)
            
            if not role_ids:
                return False
            
            # 检查这些角色是否拥有指定权限
            perm_response = (
                self.client.table("role_permissions")
                .select("permission_id")
                .in_("role_id", role_ids)
                .eq("is_active", True)
                .execute()
            )
            
            # 获取权限 ID 列表（类型守卫）
            perm_ids: list[int] = []
            for rp in (perm_response.data or []):
                if isinstance(rp, dict) and "permission_id" in rp:
                    perm_id = rp["permission_id"]
                    if isinstance(perm_id, int):
                        perm_ids.append(perm_id)
            
            if not perm_ids:
                return False
            
            # 查询具体的权限
            check_response = (
                self.client.table("permissions")
                .select("id")
                .eq("resource", resource)
                .eq("action", action)
                .in_("id", perm_ids)
                .execute()
            )
            
            return len(check_response.data or []) > 0
        except Exception as e:
            logger.error(f"检查权限失败: user_id={user_id}, resource={resource}, action={action}, error={e}")
            return False
    
    def has_role(self, user_id: int, role_slug: str) -> bool:
        """检查用户是否拥有特定角色
        
        优化：使用关联查询直接检查，避免获取所有角色
        """
        try:
            response = (
                self.client.table("user_roles")
                .select("role_id")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )
            
            user_roles = response.data or []
            if not user_roles:
                return False
            
            # 提取角色 ID 列表（类型守卫）
            role_ids: list[int] = []
            for ur in user_roles:
                if isinstance(ur, dict) and "role_id" in ur:
                    role_id = ur["role_id"]
                    if isinstance(role_id, int):
                        role_ids.append(role_id)
            
            if not role_ids:
                return False
            
            # 检查这些角色中是否有指定的 slug
            role_response = (
                self.client.table("roles")
                .select("id")
                .in_("id", role_ids)
                .eq("slug", role_slug)
                .execute()
            )
            
            return len(role_response.data or []) > 0
        except Exception as e:
            logger.error(f"检查角色失败: user_id={user_id}, role_slug={role_slug}, error={e}")
            return False
    
    # ========================================================================
    # RBAC 约束
    # ========================================================================
    
    def get_all_constraints(self, is_active: bool = True) -> list[dict[str, Any]]:
        """获取所有约束规则"""
        try:
            query = self.client.table("rbac_constraints").select("*").order("created_at", desc=True)
            if is_active:
                query = query.eq("is_active", True)
            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error(f"获取约束列表失败: {e}")
            return []
    
    def get_constraint_by_id(self, constraint_id: int) -> dict[str, Any] | None:
        """根据 ID 获取约束"""
        try:
            response = self.client.table("rbac_constraints").select("*").eq("id", constraint_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"获取约束失败: {e}")
            return None
    
    def create_constraint(self, constraint_data: dict[str, Any]) -> dict[str, Any] | None:
        """创建约束规则"""
        try:
            response = self.client.table("rbac_constraints").insert(constraint_data).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"创建约束失败: {e}")
            return None
    
    def update_constraint(self, constraint_id: int, constraint_data: dict[str, Any]) -> dict[str, Any] | None:
        """更新约束规则"""
        try:
            response = self.client.table("rbac_constraints").update(constraint_data).eq("id", constraint_id).execute()
            data = response.data
            return data[0] if data else None
        except Exception as e:
            logger.error(f"更新约束失败: {e}")
            return None
    
    def delete_constraint(self, constraint_id: int) -> bool:
        """删除约束规则"""
        try:
            response = self.client.table("rbac_constraints").delete().eq("id", constraint_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"删除约束失败: {e}")
            return False


# 全局实例
supabase_db = SupabaseDB()
