"""
辅助函数模块
提供通用的工具函数
"""

from datetime import datetime
from typing import Optional


def datetime_to_str(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """
    将 datetime 转换为字符串
    
    Args:
        dt: datetime 对象
        fmt: 格式字符串
    
    Returns:
        格式化后的字符串或 None
    """
    if dt is None:
        return None
    return dt.strftime(fmt)


def str_to_datetime(dt_str: Optional[str], fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    将字符串转换为 datetime
    
    Args:
        dt_str: 日期时间字符串
        fmt: 格式字符串
    
    Returns:
        datetime 对象或 None
    """
    if dt_str is None or dt_str == "":
        return None
    return datetime.strptime(dt_str, fmt)


def is_expired(expires_at: Optional[datetime]) -> bool:
    """
    检查是否已过期
    
    Args:
        expires_at: 过期时间
    
    Returns:
        是否已过期
    """
    if expires_at is None:
        return False
    return datetime.utcnow() > expires_at


__all__ = [
    "datetime_to_str",
    "str_to_datetime",
    "is_expired",
]
