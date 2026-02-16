"""
日志配置模块

配置应用程序的日志系统，将日志输出到 logs/ 目录。
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "windows_cleaner", log_dir: str = "logs") -> logging.Logger:
    """
    配置并返回应用程序日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
    
    Returns:
        配置好的 Logger 实例
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 文件处理器 - 轮转日志，保留最近 10 个文件
    log_file = log_path / "app.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 创建默认日志记录器
logger = setup_logger()
