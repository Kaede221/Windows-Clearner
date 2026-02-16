"""
Windows 垃圾文件清理工具 - 主入口（无控制台窗口版本）

应用程序的启动入口，使用 .pyw 扩展名避免显示控制台窗口。
"""

import sys
import os
import logging
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.logger import setup_logger


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin():
    """请求管理员权限并重新启动程序"""
    try:
        # 获取当前脚本路径
        script_path = os.path.abspath(sys.argv[0])
        
        # .pyw 文件始终使用 pythonw.exe（无窗口）
        executable = sys.executable
        if 'python.exe' in executable.lower():
            executable = executable.replace('python.exe', 'pythonw.exe')
        
        # 使用 ShellExecuteW 以管理员身份运行
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            f'"{script_path}"',
            None,
            1  # SW_SHOWNORMAL
        )
        
        # 如果成功请求管理员权限（返回值 > 32），退出当前进程
        if ret > 32:
            sys.exit(0)
        else:
            # 用户拒绝或失败，继续以普通权限运行
            return False
    except Exception as e:
        # .pyw 文件中不能用 print，写入日志
        import logging
        logging.error(f"请求管理员权限失败: {e}")
        return False


def main():
    """主函数"""
    # 设置日志
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # 检查并请求管理员权限
    if not is_admin():
        logger.info("未以管理员身份运行，尝试请求管理员权限")
        request_admin()
        # 如果到这里说明用户拒绝或失败，继续以普通权限运行
        logger.info("继续以普通权限运行")
    else:
        logger.info("以管理员身份运行")
    
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
