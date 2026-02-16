"""
数据模型模块

定义应用程序使用的数据类和枚举。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class JunkCategory(Enum):
    """垃圾文件类别枚举"""
    TEMP_FILES = "系统临时文件"
    WINDOWS_UPDATE_CACHE = "Windows 更新缓存"
    RECYCLE_BIN = "回收站"
    BROWSER_CACHE = "浏览器缓存"
    THUMBNAIL_CACHE = "缩略图缓存"
    CUSTOM = "自定义路径"


@dataclass
class JunkFile:
    """垃圾文件数据类"""
    path: str
    size: int
    category: JunkCategory
    can_delete: bool
    error_message: Optional[str] = None


@dataclass
class ScanResult:
    """扫描结果数据类"""
    categories: Dict[JunkCategory, List[JunkFile]]
    total_size: int
    total_count: int
    scan_duration: float
    errors: List[str]
    requires_admin: bool = False
    inaccessible_categories: List[JunkCategory] = field(default_factory=list)


@dataclass
class CleanResult:
    """清理结果数据类"""
    success_count: int
    failed_count: int
    freed_space: int
    failed_files: List[Tuple[str, str]]  # (path, error_reason)
    clean_duration: float


@dataclass
class ScanConfig:
    """扫描配置数据类"""
    enabled_categories: Set[JunkCategory]
    excluded_paths: List[str]
    custom_patterns: List[str]
    max_file_age_days: Optional[int] = None


@dataclass
class AppConfig:
    """应用配置数据类"""
    scan_config: ScanConfig
    ui_theme: str = "light"
    language: str = "zh_CN"
    auto_check_updates: bool = True
