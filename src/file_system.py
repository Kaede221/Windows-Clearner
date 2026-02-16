"""
文件系统访问模块

提供文件系统操作的抽象层，处理权限相关的问题。
"""

import os
import ctypes
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class FileSystemAccess:
    """文件系统访问类，提供权限检查和文件操作的抽象层"""
    
    # 需要管理员权限的路径列表
    ADMIN_REQUIRED_PATHS = [
        r"C:\Windows\Temp",
        r"C:\Windows\SoftwareDistribution",
        r"C:\Windows\System32",
        r"C:\ProgramData",
    ]
    
    # 安全删除的路径模式（允许删除的路径前缀）
    SAFE_DELETE_PATHS = [
        os.path.expandvars(r"%TEMP%"),
        os.path.expandvars(r"%TMP%"),
        r"C:\Windows\Temp",
        r"C:\Windows\SoftwareDistribution\Download",
        os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer"),
        os.path.expandvars(r"%LocalAppData%\Temp"),
    ]
    
    # 浏览器缓存路径
    BROWSER_CACHE_PATHS = [
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"),
        os.path.expandvars(r"%AppData%\Mozilla\Firefox\Profiles"),
    ]
    
    # 回收站路径
    RECYCLE_BIN_PATHS = [
        r"$Recycle.Bin",
    ]
    
    @staticmethod
    def has_admin_privileges() -> bool:
        """
        检查是否有管理员权限
        
        Returns:
            bool: 如果有管理员权限返回 True，否则返回 False
        """
        try:
            # 在 Windows 上使用 ctypes 检查管理员权限
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.warning(f"无法检查管理员权限: {e}")
            return False
    
    @staticmethod
    def requires_admin_access(path: str) -> bool:
        """
        检查路径是否需要管理员权限才能访问
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 如果需要管理员权限返回 True，否则返回 False
        """
        try:
            # 规范化路径
            normalized_path = os.path.normpath(path).upper()
            
            # 检查是否匹配需要管理员权限的路径
            for admin_path in FileSystemAccess.ADMIN_REQUIRED_PATHS:
                normalized_admin_path = os.path.normpath(admin_path).upper()
                if normalized_path.startswith(normalized_admin_path):
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"检查路径权限需求时出错 {path}: {e}")
            return False
    
    @staticmethod
    def can_access_path(path: str) -> bool:
        """
        检查是否可以访问指定路径
        考虑当前权限级别
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 如果可以访问返回 True，否则返回 False
        """
        try:
            # 检查路径是否存在
            if not os.path.exists(path):
                return False
            
            # 如果路径需要管理员权限，检查当前是否有管理员权限
            if FileSystemAccess.requires_admin_access(path):
                if not FileSystemAccess.has_admin_privileges():
                    return False
            
            # 尝试访问路径（读取权限测试）
            if os.path.isdir(path):
                # 对于目录，尝试列出内容
                os.listdir(path)
            else:
                # 对于文件，尝试获取状态
                os.stat(path)
            
            return True
        except PermissionError:
            logger.debug(f"权限不足，无法访问: {path}")
            return False
        except Exception as e:
            logger.debug(f"无法访问路径 {path}: {e}")
            return False
    
    @staticmethod
    def is_file_in_use(file_path: str) -> bool:
        """
        检查文件是否正在被使用
        
        Args:
            file_path: 要检查的文件路径
            
        Returns:
            bool: 如果文件正在被使用返回 True，否则返回 False
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 尝试以独占模式打开文件
            # 如果文件被占用，会抛出 PermissionError 或 OSError
            with open(file_path, 'a'):
                pass
            
            return False
        except PermissionError:
            # 文件被占用或权限不足
            logger.debug(f"文件可能正在使用或权限不足: {file_path}")
            return True
        except OSError as e:
            # errno 32 表示文件被占用
            if e.errno == 32:
                logger.debug(f"文件正在使用中: {file_path}")
                return True
            return False
        except Exception as e:
            logger.debug(f"检查文件占用状态时出错 {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        安全获取文件大小（字节）
        如果权限不足，返回 0 并记录警告
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节），如果无法获取返回 0
        """
        try:
            return os.path.getsize(file_path)
        except PermissionError:
            logger.warning(f"权限不足，无法获取文件大小: {file_path}")
            return 0
        except FileNotFoundError:
            logger.debug(f"文件不存在: {file_path}")
            return 0
        except Exception as e:
            logger.warning(f"获取文件大小时出错 {file_path}: {e}")
            return 0
    
    @staticmethod
    def is_safe_to_delete(file_path: str) -> bool:
        """
        检查文件是否安全删除
        验证文件是否在安全删除列表中
        
        Args:
            file_path: 要检查的文件路径
            
        Returns:
            bool: 如果文件安全删除返回 True，否则返回 False
        """
        try:
            # 规范化路径
            normalized_path = os.path.normpath(file_path).upper()
            
            # 构建完整的安全路径列表
            all_safe_paths = (
                FileSystemAccess.SAFE_DELETE_PATHS +
                FileSystemAccess.BROWSER_CACHE_PATHS +
                FileSystemAccess.RECYCLE_BIN_PATHS
            )
            
            # 检查文件是否在安全删除路径下
            for safe_path in all_safe_paths:
                normalized_safe_path = os.path.normpath(safe_path).upper()
                if normalized_path.startswith(normalized_safe_path):
                    return True
            
            # 检查是否在回收站中（特殊处理）
            if "$RECYCLE.BIN" in normalized_path:
                return True
            
            logger.debug(f"文件不在安全删除列表中: {file_path}")
            return False
        except Exception as e:
            logger.warning(f"检查文件安全性时出错 {file_path}: {e}")
            return False
