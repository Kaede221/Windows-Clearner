"""
Windows 垃圾文件清理工具 - 主入口（带控制台版本）

应用程序的启动入口，用于调试时查看日志。
正常使用请运行 main.pyw 以避免显示控制台窗口。
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
        
        # 检查是否有 --console 参数
        args = ' '.join(sys.argv[1:])
        if '--console' not in args:
            args = '--console ' + args
        
        # 始终使用 python.exe（保持控制台）
        executable = sys.executable
        
        logger = logging.getLogger(__name__)
        logger.info(f"请求管理员权限，使用 {executable} 重启")
        
        # 使用 ShellExecuteW 以管理员身份运行
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            f'"{script_path}" {args}',
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
        print(f"请求管理员权限失败: {e}")
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
    
    # 设置应用程序图标
    from PySide6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logger.info(f"已设置应用程序图标: {icon_path}")
    else:
        logger.warning(f"图标文件不存在: {icon_path}")
    
    # 初始化 qconfig - 必须在创建 QApplication 之后
    from qfluentwidgets import qconfig, setThemeColor
    
    # 确保配置目录存在
    config_dir = "config"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # 加载 qconfig 配置文件
    qconfig.load("config/qconfig.json")
    
    # 设置默认主题色（如果配置文件中没有）
    try:
        setThemeColor("#2d7eff")
        logger.info("已设置默认主题色: #2d7eff")
    except Exception as e:
        logger.warning(f"设置主题色失败: {e}")
    
    logger.info("qconfig 配置已加载")
    
    # 延迟导入 MainWindow（必须在创建 QApplication 之后）
    from src.ui import MainWindow
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    logger.info("主窗口已显示，进入事件循环")
    
    # 运行应用程序
    exit_code = app.exec()
    logger.info(f"应用程序退出，退出码: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
