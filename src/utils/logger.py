"""
日志工具模块
使用 loguru 提供统一的日志记录
"""

import sys
from loguru import logger
from src.config.settings import settings


def get_logger(name: str = __name__):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logger 实例
    """
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # 添加文件处理器（可选）
    if not settings.DEBUG:
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            encoding="utf-8",
        )
    
    return logger.bind(name=name)


# 导出默认 logger
__all__ = ["get_logger"]
