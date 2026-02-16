"""
类别扫描器模块

实现各种垃圾文件类别的扫描器。
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from src.models import JunkCategory, JunkFile
from src.file_system import FileSystemAccess

logger = logging.getLogger(__name__)


class CategoryScanner(ABC):
    """类别扫描器基类"""
    
    @abstractmethod
    def scan(self) -> List[JunkFile]:
        """
        扫描并返回该类别的垃圾文件列表
        
        Returns:
            垃圾文件列表
        """
        pass
    
    def _scan_directory(self, directory: str, category: JunkCategory) -> List[JunkFile]:
        """
        扫描目录并返回文件列表
        
        Args:
            directory: 要扫描的目录路径
            category: 文件类别
            
        Returns:
            垃圾文件列表
        """
        files = []
        
        # 检查目录是否可访问
        if not FileSystemAccess.can_access_path(directory):
            logger.warning(f"无法访问目录: {directory}")
            return files
        
        try:
            # 遍历目录
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    try:
                        file_path = os.path.join(root, filename)
                        
                        # 获取文件大小
                        file_size = FileSystemAccess.get_file_size(file_path)
                        
                        # 检查文件是否安全删除
                        can_delete = FileSystemAccess.is_safe_to_delete(file_path)
                        
                        # 创建 JunkFile 对象
                        junk_file = JunkFile(
                            path=file_path,
                            size=file_size,
                            category=category,
                            can_delete=can_delete
                        )
                        
                        files.append(junk_file)
                        
                    except PermissionError:
                        logger.debug(f"权限不足，跳过文件: {file_path}")
                    except Exception as e:
                        logger.debug(f"处理文件时出错 {file_path}: {e}")
                        
        except PermissionError:
            logger.warning(f"权限不足，无法扫描目录: {directory}")
        except Exception as e:
            logger.error(f"扫描目录时出错 {directory}: {e}", exc_info=True)
        
        return files


class TempFilesScanner(CategoryScanner):
    r"""系统临时文件扫描器"""
    
    def scan(self) -> List[JunkFile]:
        r"""
        扫描系统临时文件
        扫描 %TEMP%, %TMP%, C:\Windows\Temp
        
        Returns:
            临时文件列表
        """
        logger.info("开始扫描系统临时文件")
        files = []
        
        # 定义要扫描的临时目录
        temp_dirs = [
            os.path.expandvars(r"%TEMP%"),
            os.path.expandvars(r"%TMP%"),
            r"C:\Windows\Temp",
        ]
        
        # 扫描每个临时目录
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                logger.debug(f"扫描临时目录: {temp_dir}")
                dir_files = self._scan_directory(temp_dir, JunkCategory.TEMP_FILES)
                files.extend(dir_files)
            else:
                logger.debug(f"临时目录不存在: {temp_dir}")
        
        logger.info(f"系统临时文件扫描完成，发现 {len(files)} 个文件")
        return files


class WindowsUpdateScanner(CategoryScanner):
    r"""Windows 更新缓存扫描器"""
    
    def scan(self) -> List[JunkFile]:
        r"""
        扫描 Windows 更新缓存
        扫描 C:\Windows\SoftwareDistribution\Download
        
        Returns:
            更新缓存文件列表
        """
        logger.info("开始扫描 Windows 更新缓存")
        files = []
        
        # Windows 更新下载目录
        update_dir = r"C:\Windows\SoftwareDistribution\Download"
        
        if os.path.exists(update_dir):
            logger.debug(f"扫描更新缓存目录: {update_dir}")
            files = self._scan_directory(update_dir, JunkCategory.WINDOWS_UPDATE_CACHE)
        else:
            logger.debug(f"更新缓存目录不存在: {update_dir}")
        
        logger.info(f"Windows 更新缓存扫描完成，发现 {len(files)} 个文件")
        return files



class RecycleBinScanner(CategoryScanner):
    r"""回收站扫描器"""
    
    def scan(self) -> List[JunkFile]:
        r"""
        扫描回收站
        扫描所有驱动器的 $Recycle.Bin 目录
        
        Returns:
            回收站文件列表
        """
        logger.info("开始扫描回收站")
        files = []
        
        # 获取所有驱动器
        drives = self._get_drives()
        
        # 扫描每个驱动器的回收站
        for drive in drives:
            recycle_bin_path = os.path.join(drive, "$Recycle.Bin")
            if os.path.exists(recycle_bin_path):
                logger.debug(f"扫描回收站: {recycle_bin_path}")
                dir_files = self._scan_directory(recycle_bin_path, JunkCategory.RECYCLE_BIN)
                files.extend(dir_files)
        
        logger.info(f"回收站扫描完成，发现 {len(files)} 个文件")
        return files
    
    def _get_drives(self) -> List[str]:
        r"""
        获取所有可用的驱动器
        
        Returns:
            驱动器列表（如 ['C:\\', 'D:\\']）
        """
        drives = []
        
        try:
            # 在 Windows 上，检查 A-Z 驱动器
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        except Exception as e:
            logger.error(f"获取驱动器列表时出错: {e}", exc_info=True)
        
        return drives


class BrowserCacheScanner(CategoryScanner):
    """浏览器缓存扫描器"""
    
    def scan(self) -> List[JunkFile]:
        """
        扫描浏览器缓存
        扫描常见浏览器的缓存目录（Chrome, Edge, Firefox）
        
        Returns:
            浏览器缓存文件列表
        """
        logger.info("开始扫描浏览器缓存")
        files = []
        
        # 定义浏览器缓存目录
        cache_dirs = [
            # Chrome
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Code Cache"),
            # Edge
            os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"),
            os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Code Cache"),
            # Firefox (扫描所有配置文件)
            os.path.expandvars(r"%LocalAppData%\Mozilla\Firefox\Profiles"),
        ]
        
        # 扫描每个缓存目录
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                logger.debug(f"扫描浏览器缓存目录: {cache_dir}")
                
                # Firefox 需要特殊处理，扫描所有配置文件的 cache2 目录
                if "Firefox\\Profiles" in cache_dir:
                    files.extend(self._scan_firefox_cache(cache_dir))
                else:
                    dir_files = self._scan_directory(cache_dir, JunkCategory.BROWSER_CACHE)
                    files.extend(dir_files)
            else:
                logger.debug(f"浏览器缓存目录不存在: {cache_dir}")
        
        logger.info(f"浏览器缓存扫描完成，发现 {len(files)} 个文件")
        return files
    
    def _scan_firefox_cache(self, profiles_dir: str) -> List[JunkFile]:
        """
        扫描 Firefox 配置文件的缓存
        
        Args:
            profiles_dir: Firefox 配置文件目录
            
        Returns:
            Firefox 缓存文件列表
        """
        files = []
        
        try:
            # 遍历所有配置文件
            for profile in os.listdir(profiles_dir):
                profile_path = os.path.join(profiles_dir, profile)
                if os.path.isdir(profile_path):
                    # 扫描 cache2 目录
                    cache_path = os.path.join(profile_path, "cache2")
                    if os.path.exists(cache_path):
                        logger.debug(f"扫描 Firefox 缓存: {cache_path}")
                        dir_files = self._scan_directory(cache_path, JunkCategory.BROWSER_CACHE)
                        files.extend(dir_files)
        except PermissionError:
            logger.warning(f"权限不足，无法扫描 Firefox 配置文件: {profiles_dir}")
        except Exception as e:
            logger.error(f"扫描 Firefox 缓存时出错: {e}", exc_info=True)
        
        return files


class ThumbnailCacheScanner(CategoryScanner):
    r"""缩略图缓存扫描器"""
    
    def scan(self) -> List[JunkFile]:
        r"""
        扫描缩略图缓存
        扫描 %LocalAppData%\Microsoft\Windows\Explorer
        
        Returns:
            缩略图缓存文件列表
        """
        logger.info("开始扫描缩略图缓存")
        files = []
        
        # 缩略图缓存目录
        thumbnail_dir = os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer")
        
        if os.path.exists(thumbnail_dir):
            logger.debug(f"扫描缩略图缓存目录: {thumbnail_dir}")
            
            # 只扫描 thumbcache_*.db 文件
            try:
                for filename in os.listdir(thumbnail_dir):
                    if filename.startswith("thumbcache_") and filename.endswith(".db"):
                        file_path = os.path.join(thumbnail_dir, filename)
                        
                        try:
                            # 获取文件大小
                            file_size = FileSystemAccess.get_file_size(file_path)
                            
                            # 检查文件是否安全删除
                            can_delete = FileSystemAccess.is_safe_to_delete(file_path)
                            
                            # 创建 JunkFile 对象
                            junk_file = JunkFile(
                                path=file_path,
                                size=file_size,
                                category=JunkCategory.THUMBNAIL_CACHE,
                                can_delete=can_delete
                            )
                            
                            files.append(junk_file)
                            
                        except Exception as e:
                            logger.debug(f"处理缩略图文件时出错 {file_path}: {e}")
                            
            except PermissionError:
                logger.warning(f"权限不足，无法扫描缩略图缓存目录: {thumbnail_dir}")
            except Exception as e:
                logger.error(f"扫描缩略图缓存时出错: {e}", exc_info=True)
        else:
            logger.debug(f"缩略图缓存目录不存在: {thumbnail_dir}")
        
        logger.info(f"缩略图缓存扫描完成，发现 {len(files)} 个文件")
        return files
