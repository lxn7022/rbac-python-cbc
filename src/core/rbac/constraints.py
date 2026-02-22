"""
RBAC 约束规则
实现 RBAC2 约束模型
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from src.db.supabase_client import supabase_db
from src.utils.logger import get_logger
from src.utils.exceptions import ConstraintViolationError

logger = get_logger(__name__)


# ============================================================================
# 约束基类
# ============================================================================

class Constraint(ABC):
    """
    约束基类
    
    所有约束类型必须继承此类并实现 check 方法
    """
    
    def __init__(self, db: Any, config: Dict[str, Any]):
        """
        初始化约束
        
        Args:
            db: 数据库客户端
            config: 约束配置
        """
        self.db = db
        self.config = config
    
    @abstractmethod
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """
        检查约束
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            action: 操作类型（assign/revoke）
        
        Returns:
            bool: 是否通过约束检查
        
        Raises:
            ConstraintViolationError: 违反约束
        """
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """获取错误消息"""
        pass


# ============================================================================
# 互斥约束（Mutually Exclusive）
# ============================================================================

class MutuallyExclusiveConstraint(Constraint):
    """
    互斥约束（静态职责分离 - SSD）
    
    用户不能同时拥有互斥的角色
    """
    
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """检查互斥约束"""
        if action != 'assign':
            return True
        
        # 获取互斥角色列表
        mutually_exclusive_roles = self.config.get('roles', [])
        
        # 获取当前角色标识
        current_role = self.db.get_role_by_id(role_id)
        if not current_role:
            return True
        
        # 检查当前角色是否在互斥列表中
        if current_role['slug'] not in mutually_exclusive_roles:
            return True
        
        # 获取用户当前拥有的角色
        user_roles = self.db.get_user_roles(user_id)
        
        # 检查用户是否拥有互斥角色
        for user_role in user_roles:
            role = user_role.get('roles')
            if role and role['slug'] in mutually_exclusive_roles:
                # 发现互斥角色
                if role['slug'] != current_role['slug']:
                    raise ConstraintViolationError(
                        f"违反互斥约束：用户已拥有角色 '{role['name']}'，"
                        f"不能同时拥有角色 '{current_role['name']}'"
                    )
        
        return True
    
    def get_error_message(self) -> str:
        return f"违反互斥约束：不能同时拥有这些角色 {self.config.get('roles', [])}"


# ============================================================================
# 基数约束（Cardinality）
# ============================================================================

class CardinalityConstraint(Constraint):
    """
    基数约束
    
    限制角色可以分配给的最大用户数
    """
    
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """检查基数约束"""
        if action != 'assign':
            return True
        
        # 获取角色限制
        role_slug = self.config.get('role')
        max_users = self.config.get('max_users', 1)
        
        # 获取当前角色
        current_role = self.db.get_role_by_id(role_id)
        if not current_role:
            return True
        
        # 只检查指定的角色
        if current_role['slug'] != role_slug:
            return True
        
        # 统计当前拥有该角色的用户数
        # 通过查询 user_roles 表统计
        # 注意：这里需要实现统计方法，暂时简化处理
        # 实际应该查询所有拥有该角色的用户数量
        
        logger.warning(f"基数约束检查需要实现统计方法: role_id={role_id}")
        
        # 暂时返回 True，后续可以实现精确统计
        return True
    
    def get_error_message(self) -> str:
        return f"违反基数约束：角色 '{self.config.get('role')}' 最多分配给 {self.config.get('max_users')} 个用户"


# ============================================================================
# 先决条件约束（Prerequisite）
# ============================================================================

class PrerequisiteConstraint(Constraint):
    """
    先决条件约束
    
    用户必须先拥有某个角色才能分配另一个角色
    """
    
    def check(self, user_id: int, role_id: int, action: str) -> bool:
        """检查先决条件约束"""
        if action != 'assign':
            return True
        
        # 获取先决条件配置
        role_slug = self.config.get('role')
        required_roles = self.config.get('required_roles', [])
        
        # 获取当前角色
        current_role = self.db.get_role_by_id(role_id)
        if not current_role:
            return True
        
        # 只检查指定的角色
        if current_role['slug'] != role_slug:
            return True
        
        # 获取用户当前拥有的角色
        user_roles = self.db.get_user_roles(user_id)
        user_role_slugs = {ur.get('roles', {}).get('slug') for ur in user_roles if ur.get('roles')}
        
        # 检查是否满足所有先决条件
        missing_roles = []
        for required_role_slug in required_roles:
            if required_role_slug not in user_role_slugs:
                missing_roles.append(required_role_slug)
        
        if missing_roles:
            raise ConstraintViolationError(
                f"违反先决条件约束：分配角色 '{current_role['name']}' 需要先拥有角色 {missing_roles}"
            )
        
        return True
    
    def get_error_message(self) -> str:
        return f"违反先决条件约束：需要先拥有角色 {self.config.get('required_roles', [])}"


# ============================================================================
# 约束管理器
# ============================================================================

class ConstraintManager:
    """
    约束管理器
    
    负责加载和执行所有约束规则
    """
    
    # 约束类型映射
    CONSTRAINT_TYPES = {
        'mutually_exclusive': MutuallyExclusiveConstraint,
        'cardinality': CardinalityConstraint,
        'prerequisite': PrerequisiteConstraint,
    }
    
    def __init__(self, db: Any = None):
        """初始化约束管理器
        
        Args:
            db: 数据库客户端（可选，默认使用 supabase_db）
        """
        self.db = db or supabase_db
        self._constraints_cache: List[Constraint] | None = None
    
    def load_constraints(self, use_cache: bool = True) -> List[Constraint]:
        """
        加载所有活跃的约束规则
        
        Args:
            use_cache: 是否使用缓存
        
        Returns:
            List[Constraint]: 约束对象列表
        """
        if use_cache and self._constraints_cache is not None:
            return self._constraints_cache
        
        constraints = []
        
        # 从数据库加载约束
        db_constraints = self.db.get_all_constraints(is_active=True)
        
        for db_constraint in db_constraints:
            constraint_type = db_constraint.get('constraint_type')
            constraint_class = self.CONSTRAINT_TYPES.get(constraint_type)
            
            if constraint_class:
                constraint = constraint_class(self.db, db_constraint.get('config', {}))
                constraints.append(constraint)
            else:
                logger.warning(f"未知的约束类型: {constraint_type}")
        
        if use_cache:
            self._constraints_cache = constraints
        
        return constraints
    
    def check_constraints(
        self,
        user_id: int,
        role_id: int,
        action: str
    ) -> bool:
        """
        检查所有约束
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            action: 操作类型（assign/revoke）
        
        Returns:
            bool: 是否通过所有约束检查
        
        Raises:
            ConstraintViolationError: 违反约束
        """
        try:
            constraints = self.load_constraints()
            
            for constraint in constraints:
                constraint.check(user_id, role_id, action)
            
            logger.debug(f"约束检查通过: user_id={user_id}, role_id={role_id}, action={action}")
            return True
            
        except ConstraintViolationError:
            raise
        except Exception as e:
            logger.error(f"约束检查失败: user_id={user_id}, role_id={role_id}, action={action}, error={e}")
            raise
    
    def refresh_cache(self):
        """刷新约束缓存"""
        self._constraints_cache = None
        self.load_constraints(use_cache=True)
    
    def add_constraint(
        self,
        constraint_type: str,
        name: str,
        description: str,
        config: Dict[str, Any]
    ) -> dict[str, Any]:
        """
        添加新的约束规则
        
        Args:
            constraint_type: 约束类型
            name: 约束名称
            description: 约束描述
            config: 约束配置
        
        Returns:
            dict: 约束记录
        """
        try:
            constraint_data = {
                'constraint_type': constraint_type,
                'name': name,
                'description': description,
                'config': config,
                'is_active': True
            }
            
            constraint = supabase_db.create_constraint(constraint_data)
            
            # 刷新缓存
            self.refresh_cache()
            
            logger.info(f"添加约束成功: name={name}, type={constraint_type}")
            return constraint
            
        except Exception as e:
            logger.error(f"添加约束失败: name={name}, error={e}")
            raise
