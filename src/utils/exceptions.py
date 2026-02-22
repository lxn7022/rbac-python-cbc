"""
自定义异常模块
定义系统中使用的自定义异常类
"""


class RBACError(Exception):
    """RBAC 基础异常"""
    
    def __init__(self, message: str = "RBAC 错误"):
        self.message = message
        super().__init__(self.message)


class PermissionDeniedError(RBACError):
    """权限拒绝异常"""
    
    def __init__(self, resource: str = None, action: str = None):
        if resource and action:
            message = f"权限拒绝：没有权限执行 '{resource}:{action}' 操作"
        else:
            message = "权限拒绝：没有足够的权限"
        super().__init__(message)


class RoleNotFoundError(RBACError):
    """角色未找到异常"""
    
    def __init__(self, role_id: int = None, role_slug: str = None):
        if role_id:
            message = f"角色未找到：ID={role_id}"
        elif role_slug:
            message = f"角色未找到：slug={role_slug}"
        else:
            message = "角色未找到"
        super().__init__(message)


class UserNotFoundError(RBACError):
    """用户未找到异常"""
    
    def __init__(self, user_id: int = None, username: str = None):
        if user_id:
            message = f"用户未找到：ID={user_id}"
        elif username:
            message = f"用户未找到：username={username}"
        else:
            message = "用户未找到"
        super().__init__(message)


class ConstraintViolationError(RBACError):
    """约束违反异常"""
    
    def __init__(self, message: str = "违反约束规则"):
        super().__init__(message)


class AuthenticationError(Exception):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        self.message = message
        super().__init__(self.message)


class TokenExpiredError(AuthenticationError):
    """Token 过期异常"""
    
    def __init__(self):
        super().__init__("Token 已过期")


class InvalidTokenError(AuthenticationError):
    """无效 Token 异常"""
    
    def __init__(self):
        super().__init__("无效的 Token")


class UserAlreadyExistsError(RBACError):
    """用户已存在异常"""
    
    def __init__(self, username: str = None, email: str = None):
        if username:
            message = f"用户已存在：username={username}"
        elif email:
            message = f"邮箱已被注册：email={email}"
        else:
            message = "用户已存在"
        super().__init__(message)


class RoleAlreadyAssignedError(RBACError):
    """角色已分配异常"""
    
    def __init__(self, user_id: int, role_id: int):
        message = f"用户 {user_id} 已拥有角色 {role_id}"
        super().__init__(message)


class PermissionAlreadyGrantedError(RBACError):
    """权限已授予异常"""
    
    def __init__(self, role_id: int, permission_id: int):
        message = f"角色 {role_id} 已拥有权限 {permission_id}"
        super().__init__(message)


__all__ = [
    "RBACError",
    "PermissionDeniedError",
    "RoleNotFoundError",
    "UserNotFoundError",
    "ConstraintViolationError",
    "AuthenticationError",
    "TokenExpiredError",
    "InvalidTokenError",
    "UserAlreadyExistsError",
    "RoleAlreadyAssignedError",
    "PermissionAlreadyGrantedError",
]
