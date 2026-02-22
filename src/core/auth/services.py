"""
认证服务
处理用户登录、注册、Token 管理等
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from src.db.supabase_client import supabase_db
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.exceptions import AuthenticationError, UserNotFoundError

logger = get_logger(__name__)
settings = get_settings()


class AuthService:
    """
    认证服务类
    
    提供：
    - 用户注册
    - 用户登录
    - Token 生成和验证
    - 密码加密和验证
    """
    
    # ========================================================================
    # 用户注册
    # ========================================================================
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            full_name: 全名（可选）
        
        Returns:
            Dict: 用户信息
        
        Raises:
            AuthenticationError: 用户名或邮箱已存在
        """
        try:
            # 1. 检查用户名是否已存在
            existing_user = supabase_db.get_user_by_username(username)
            if existing_user:
                raise AuthenticationError("用户名已存在")
            
            # 2. 检查邮箱是否已存在
            existing_email = supabase_db.get_user_by_email(email)
            if existing_email:
                raise AuthenticationError("邮箱已存在")
            
            # 3. 加密密码
            password_hash = self._hash_password(password)
            
            # 4. 创建用户
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "is_active": True,
                "is_verified": False
            }
            
            user = supabase_db.create_user(user_data)
            
            if not user:
                raise AuthenticationError("用户创建失败")
            
            logger.info(f"用户注册成功: username={username}, email={email}")
            
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            raise AuthenticationError(f"注册失败: {e}")
    
    # ========================================================================
    # 用户登录
    # ========================================================================
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username: 用户名或邮箱
            password: 密码
        
        Returns:
            Dict: 登录结果（包含 token 和用户信息）
        
        Raises:
            AuthenticationError: 认证失败
        """
        try:
            # 1. 查找用户（支持用户名或邮箱登录）
            user = supabase_db.get_user_by_username(username)
            if not user:
                user = supabase_db.get_user_by_email(username)
            
            if not user:
                raise AuthenticationError("用户名或密码错误")
            
            # 2. 检查用户状态
            if not user.get("is_active"):
                raise AuthenticationError("用户已被禁用")
            
            # 3. 验证密码
            if not self._verify_password(password, user.get("password_hash")):
                raise AuthenticationError("用户名或密码错误")
            
            # 4. 生成 Token
            access_token = self._create_access_token(user["id"])
            refresh_token = self._create_refresh_token(user["id"])
            
            # 5. 更新最后登录时间
            supabase_db.update_user(user["id"], {
                "last_login_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"用户登录成功: username={user['username']}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            raise AuthenticationError(f"登录失败: {e}")
    
    # ========================================================================
    # Token 管理
    # ========================================================================
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证 Token
        
        Args:
            token: JWT Token
        
        Returns:
            Dict: Token 解码后的数据
        
        Raises:
            AuthenticationError: Token 无效或过期
        """
        try:
            # 先检查 token 是否为空或格式错误
            if not token or not isinstance(token, str):
                raise AuthenticationError("无效的 Token")
            
            # 检查 token 格式（JWT 应该有 3 部分）
            parts = token.split('.')
            if len(parts) != 3:
                raise AuthenticationError("无效的 Token 格式")
            
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # 检查是否过期
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise AuthenticationError("Token 已过期")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token 已过期")
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的 Token: {e}")
            raise AuthenticationError("无效的 Token")
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Token 验证失败: {e}")
            raise AuthenticationError("Token 验证失败")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新 Token
        
        Args:
            refresh_token: 刷新 Token
        
        Returns:
            Dict: 新的访问 Token
        
        Raises:
            AuthenticationError: 刷新 Token 无效
        """
        try:
            # 验证刷新 Token
            payload = self.verify_token(refresh_token)
            
            # 检查是否为刷新 Token
            if payload.get("type") != "refresh":
                raise AuthenticationError("无效的刷新 Token")
            
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("无效的 Token 载荷")
            
            # 生成新的访问 Token
            access_token = self._create_access_token(user_id)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Token 刷新失败: {e}")
            raise AuthenticationError(f"Token 刷新失败: {e}")
    
    # ========================================================================
    # 用户信息
    # ========================================================================
    
    def get_current_user(self, user_id: int) -> Dict[str, Any]:
        """
        获取当前用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            Dict: 用户信息
        
        Raises:
            UserNotFoundError: 用户不存在
        """
        user = supabase_db.get_user_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"用户不存在: {user_id}")
        
        return user
    
    # ========================================================================
    # 密码管理
    # ========================================================================
    
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            bool: 是否成功
        
        Raises:
            AuthenticationError: 密码验证失败
        """
        try:
            # 1. 获取用户
            user = supabase_db.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"用户不存在: {user_id}")
            
            # 2. 验证旧密码
            if not self._verify_password(old_password, user.get("password_hash")):
                raise AuthenticationError("旧密码错误")
            
            # 3. 加密新密码
            password_hash = self._hash_password(new_password)
            
            # 4. 更新密码
            result = supabase_db.update_user(user_id, {
                "password_hash": password_hash
            })
            
            if result:
                logger.info(f"用户密码修改成功: user_id={user_id}")
                return True
            else:
                raise AuthenticationError("密码修改失败")
                
        except (UserNotFoundError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"密码修改失败: {e}")
            raise AuthenticationError(f"密码修改失败: {e}")
    
    # ========================================================================
    # 密码管理（公共方法）
    # ========================================================================
    
    def hash_password(self, password: str) -> str:
        """加密密码（公共方法）"""
        return self._hash_password(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码（公共方法）"""
        return self._verify_password(password, password_hash)
    
    def create_user(self, user_data: Any) -> Dict[str, Any]:
        """创建用户（兼容测试接口）"""
        # 如果是 Pydantic 模型，转换为字典
        if hasattr(user_data, 'dict'):
            data = user_data.dict()
        else:
            data = user_data
            
        return self.register(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('full_name')
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """认证用户（兼容测试接口）"""
        try:
            result = self.login(username, password)
            return result.get('user')
        except AuthenticationError:
            return None
    
    # ========================================================================
    # 辅助方法（私有）
    # ========================================================================
    
    def _hash_password(self, password: str) -> str:
        """加密密码"""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"密码验证异常: {e}")
            return False
    
    def _create_access_token(self, user_id: int) -> str:
        """创建访问 Token"""
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    def _create_refresh_token(self, user_id: int) -> str:
        """创建刷新 Token"""
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )


# 全局认证服务实例
auth_service = AuthService()
