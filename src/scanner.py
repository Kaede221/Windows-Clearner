"""
垃圾文件扫描器模块

负责扫描系统中的垃圾文件。
"""

import logging
import time
from typing import Callable, Dict, List
from src.models import JunkCategory, JunkFile, ScanResult, ScanConfig
from src.file_system import FileSystemAccess
from src.category_scanners import (
    TempFilesScanner,
    WindowsUpdateScanner,
    RecycleBinScanner,
    BrowserCacheScanner,
    ThumbnailCacheScanner
)

logger = logging.getLogger(__name__)


class JunkScanner:
    """垃圾扫描器基类，负责扫描系统中的垃圾文件"""
    
    def __init__(self, config: ScanConfig):
        """
        初始化扫描器
        
        Args:
            config: 扫描配置
        """
        self.config = config
        self.has_admin = FileSystemAccess.has_admin_privileges()
        self.category_scanners = self._init_category_scanners()
        
        logger.info(f"初始化扫描器，管理员权限: {self.has_admin}")
    
    def _init_category_scanners(self) -> Dict[JunkCategory, 'CategoryScanner']:
        """
        初始化各类别扫描器
        
        Returns:
            类别扫描器映射字典
        """
        return {
            JunkCategory.TEMP_FILES: TempFilesScanner(),
            JunkCategory.WINDOWS_UPDATE_CACHE: WindowsUpdateScanner(),
            JunkCategory.RECYCLE_BIN: RecycleBinScanner(),
            JunkCategory.BROWSER_CACHE: BrowserCacheScanner(),
            JunkCategory.THUMBNAIL_CACHE: ThumbnailCacheScanner(),
        }
    
    def scan(self, progress_callback: Callable[[str, int], None]) -> ScanResult:
        """
        扫描所有启用的垃圾类别
        
        Args:
            progress_callback: 进度回调函数 (current_path, percentage)
        
        Returns:
            ScanResult: 扫描结果，包含权限警告信息
        """
        logger.info("开始扫描垃圾文件")
        start_time = time.time()
        
        categories: Dict[JunkCategory, List[JunkFile]] = {}
        errors: List[str] = []
        inaccessible_categories: List[JunkCategory] = []
        
        # 获取启用的类别列表
        enabled_categories = list(self.config.enabled_categories)
        total_categories = len(enabled_categories)
        
        # 扫描每个启用的类别
        for index, category in enumerate(enabled_categories):
            try:
                # 计算进度百分比
                percentage = int((index / total_categories) * 100)
                progress_callback(f"正在扫描: {category.value}", percentage)
                
                # 扫描类别
                category_files = self.scan_category(category)
                
                # 如果类别为空且需要管理员权限，标记为无法访问
                if not category_files and self._category_requires_admin(category) and not self.has_admin:
                    inaccessible_categories.append(category)
                    errors.append(f"类别 {category.value} 需要管理员权限")
                    logger.warning(f"类别 {category.value} 因权限不足而无法完全扫描")
                
                categories[category] = category_files
                
            except Exception as e:
                error_msg = f"扫描类别 {category.value} 时出错: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)
                categories[category] = []
        
        # 完成扫描
        progress_callback("扫描完成", 100)
        
        # 计算统计信息
        total_count = sum(len(files) for files in categories.values())
        total_size = sum(f.size for files in categories.values() for f in files)
        scan_duration = time.time() - start_time
        
        # 判断是否需要管理员权限
        requires_admin = len(inaccessible_categories) > 0
        
        result = ScanResult(
            categories=categories,
            total_size=total_size,
            total_count=total_count,
            scan_duration=scan_duration,
            errors=errors,
            requires_admin=requires_admin,
            inaccessible_categories=inaccessible_categories
        )
        
        logger.info(f"扫描完成，发现 {total_count} 个文件，共 {total_size / (1024**3):.2f} GB，耗时 {scan_duration:.2f} 秒")
        if requires_admin:
            logger.warning(f"有 {len(inaccessible_categories)} 个类别因权限不足而无法完全扫描")
        
        return result
    
    def scan_category(self, category: JunkCategory) -> List[JunkFile]:
        """
        扫描特定类别的垃圾文件
        
        对于需要管理员权限的路径：
        - 如果有管理员权限：正常扫描
        - 如果没有管理员权限：跳过并记录警告
        
        Args:
            category: 要扫描的类别
            
        Returns:
            该类别下的垃圾文件列表
        """
        # 检查类别是否需要管理员权限
        if self._category_requires_admin(category) and not self.has_admin:
            logger.warning(f"跳过类别 {category.value}，需要管理员权限")
            return []
        
        # 获取类别扫描器
        scanner = self.category_scanners.get(category)
        if scanner is None:
            logger.warning(f"未找到类别 {category.value} 的扫描器")
            return []
        
        # 执行扫描
        try:
            return scanner.scan()
        except Exception as e:
            logger.error(f"扫描类别 {category.value} 时出错: {e}", exc_info=True)
            return []
    
    def get_inaccessible_categories(self) -> List[JunkCategory]:
        """
        返回由于权限不足而无法完全扫描的类别列表
        
        Returns:
            无法访问的类别列表
        """
        if self.has_admin:
            # 如果有管理员权限，所有类别都可以访问
            return []
        
        # 返回需要管理员权限的类别
        inaccessible = []
        for category in self.config.enabled_categories:
            if self._category_requires_admin(category):
                inaccessible.append(category)
        
        return inaccessible
    
    def _category_requires_admin(self, category: JunkCategory) -> bool:
        """
        检查类别是否需要管理员权限
        
        Args:
            category: 要检查的类别
            
        Returns:
            如果需要管理员权限返回 True，否则返回 False
        """
        # 根据设计文档，以下类别需要管理员权限
        admin_required_categories = {
            JunkCategory.TEMP_FILES,  # C:\Windows\Temp 需要管理员权限
            JunkCategory.WINDOWS_UPDATE_CACHE,  # C:\Windows\SoftwareDistribution 需要管理员权限
        }
        
        return category in admin_required_categories
