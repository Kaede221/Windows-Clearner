"""
日志配置模块

配置应用程序的日志系统，将日志输出到 logs/ 目录和控制台。
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(log_dir: str = "logs") -> None:
    """
    配置应用程序的根日志记录器
    
    Args:
        log_dir: 日志文件目录
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if root_logger.handlers:
        return
    
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
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到根日志记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别，避免过多输出
    logging.getLogger("PySide6").setLevel(logging.WARNING)
    logging.getLogger("qfluentwidgets").setLevel(logging.WARNING)

