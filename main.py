"""
Windows 垃圾文件清理工具 - 主入口

应用程序的启动入口。
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("应用程序启动")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("Windows 垃圾文件清理工具")
    app.setOrganizationName("WindowsCleaner")
    
    # 延迟导入 MainWindow（必须在创建 QApplication 之后）
    from src.ui import MainWindow
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    exit_code = app.exec()
    logger.info(f"应用程序退出，退出码: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
