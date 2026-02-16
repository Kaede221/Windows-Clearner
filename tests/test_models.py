"""
数据模型单元测试

测试数据类的创建、字段访问和枚举值的正确性。
"""

import pytest
from src.models import (
    JunkCategory,
    JunkFile,
    ScanResult,
    CleanResult,
    ScanConfig,
    AppConfig
)


class TestJunkCategory:
    """测试 JunkCategory 枚举"""
    
    def test_enum_values_exist(self):
        """测试所有枚举值都存在"""
        assert JunkCategory.TEMP_FILES.value == "系统临时文件"
        assert JunkCategory.WINDOWS_UPDATE_CACHE.value == "Windows 更新缓存"
        assert JunkCategory.RECYCLE_BIN.value == "回收站"
        assert JunkCategory.BROWSER_CACHE.value == "浏览器缓存"
        assert JunkCategory.THUMBNAIL_CACHE.value == "缩略图缓存"
        assert JunkCategory.CUSTOM.value == "自定义路径"
    
    def test_enum_count(self):
        """测试枚举值数量正确"""
        assert len(JunkCategory) == 6
    
    def test_enum_membership(self):
        """测试枚举成员检查"""
        assert JunkCategory.TEMP_FILES in JunkCategory
        assert JunkCategory.BROWSER_CACHE in JunkCategory


class TestJunkFile:
    """测试 JunkFile 数据类"""
    
    def test_create_junk_file(self):
        """测试创建垃圾文件对象"""
        junk_file = JunkFile(
            path="C:\\Temp\\test.tmp",
            size=1024,
            category=JunkCategory.TEMP_FILES,
            can_delete=True
        )
        
        assert junk_file.path == "C:\\Temp\\test.tmp"
        assert junk_file.size == 1024
        assert junk_file.category == JunkCategory.TEMP_FILES
        assert junk_file.can_delete is True
        assert junk_file.error_message is None
    
    def test_junk_file_with_error(self):
        """测试带错误信息的垃圾文件对象"""
        junk_file = JunkFile(
            path="C:\\Temp\\locked.tmp",
            size=2048,
            category=JunkCategory.TEMP_FILES,
            can_delete=False,
            error_message="权限不足"
        )
        
        assert junk_file.error_message == "权限不足"
        assert junk_file.can_delete is False
    
    def test_junk_file_field_access(self):
        """测试字段访问"""
        junk_file = JunkFile(
            path="test.log",
            size=512,
            category=JunkCategory.CUSTOM,
            can_delete=True
        )
        
        # 测试所有字段都可以访问
        _ = junk_file.path
        _ = junk_file.size
        _ = junk_file.category
        _ = junk_file.can_delete
        _ = junk_file.error_message


class TestScanResult:
    """测试 ScanResult 数据类"""
    
    def test_create_scan_result(self):
        """测试创建扫描结果对象"""
        junk_file = JunkFile(
            path="C:\\Temp\\test.tmp",
            size=1024,
            category=JunkCategory.TEMP_FILES,
            can_delete=True
        )
        
        scan_result = ScanResult(
            categories={JunkCategory.TEMP_FILES: [junk_file]},
            total_size=1024,
            total_count=1,
            scan_duration=1.5,
            errors=[]
        )
        
        assert len(scan_result.categories) == 1
        assert scan_result.total_size == 1024
        assert scan_result.total_count == 1
        assert scan_result.scan_duration == 1.5
        assert len(scan_result.errors) == 0
        assert scan_result.requires_admin is False
        assert len(scan_result.inaccessible_categories) == 0
    
    def test_scan_result_with_admin_requirements(self):
        """测试需要管理员权限的扫描结果"""
        scan_result = ScanResult(
            categories={},
            total_size=0,
            total_count=0,
            scan_duration=0.5,
            errors=["需要管理员权限"],
            requires_admin=True,
            inaccessible_categories=[JunkCategory.WINDOWS_UPDATE_CACHE]
        )
        
        assert scan_result.requires_admin is True
        assert JunkCategory.WINDOWS_UPDATE_CACHE in scan_result.inaccessible_categories
        assert len(scan_result.errors) == 1
    
    def test_scan_result_multiple_categories(self):
        """测试多个类别的扫描结果"""
        file1 = JunkFile("C:\\Temp\\1.tmp", 100, JunkCategory.TEMP_FILES, True)
        file2 = JunkFile("C:\\Cache\\2.cache", 200, JunkCategory.BROWSER_CACHE, True)
        
        scan_result = ScanResult(
            categories={
                JunkCategory.TEMP_FILES: [file1],
                JunkCategory.BROWSER_CACHE: [file2]
            },
            total_size=300,
            total_count=2,
            scan_duration=2.0,
            errors=[]
        )
        
        assert len(scan_result.categories) == 2
        assert JunkCategory.TEMP_FILES in scan_result.categories
        assert JunkCategory.BROWSER_CACHE in scan_result.categories


class TestCleanResult:
    """测试 CleanResult 数据类"""
    
    def test_create_clean_result(self):
        """测试创建清理结果对象"""
        clean_result = CleanResult(
            success_count=10,
            failed_count=2,
            freed_space=10240,
            failed_files=[("C:\\Temp\\locked.tmp", "文件正在使用中")],
            clean_duration=3.5
        )
        
        assert clean_result.success_count == 10
        assert clean_result.failed_count == 2
        assert clean_result.freed_space == 10240
        assert len(clean_result.failed_files) == 1
        assert clean_result.clean_duration == 3.5
    
    def test_clean_result_no_failures(self):
        """测试没有失败的清理结果"""
        clean_result = CleanResult(
            success_count=5,
            failed_count=0,
            freed_space=5120,
            failed_files=[],
            clean_duration=1.0
        )
        
        assert clean_result.failed_count == 0
        assert len(clean_result.failed_files) == 0
    
    def test_clean_result_failed_files_format(self):
        """测试失败文件列表格式"""
        failed_files = [
            ("C:\\Temp\\file1.tmp", "权限不足"),
            ("C:\\Temp\\file2.tmp", "文件正在使用中")
        ]
        
        clean_result = CleanResult(
            success_count=3,
            failed_count=2,
            freed_space=3072,
            failed_files=failed_files,
            clean_duration=2.0
        )
        
        assert len(clean_result.failed_files) == 2
        assert clean_result.failed_files[0] == ("C:\\Temp\\file1.tmp", "权限不足")
        assert clean_result.failed_files[1] == ("C:\\Temp\\file2.tmp", "文件正在使用中")


class TestScanConfig:
    """测试 ScanConfig 数据类"""
    
    def test_create_scan_config(self):
        """测试创建扫描配置对象"""
        scan_config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES, JunkCategory.BROWSER_CACHE},
            excluded_paths=["C:\\Important"],
            custom_patterns=["*.tmp", "*.log"]
        )
        
        assert len(scan_config.enabled_categories) == 2
        assert JunkCategory.TEMP_FILES in scan_config.enabled_categories
        assert len(scan_config.excluded_paths) == 1
        assert len(scan_config.custom_patterns) == 2
        assert scan_config.max_file_age_days is None
    
    def test_scan_config_with_max_age(self):
        """测试带最大文件年龄的扫描配置"""
        scan_config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES},
            excluded_paths=[],
            custom_patterns=[],
            max_file_age_days=30
        )
        
        assert scan_config.max_file_age_days == 30
    
    def test_scan_config_all_categories(self):
        """测试启用所有类别的配置"""
        all_categories = {
            JunkCategory.TEMP_FILES,
            JunkCategory.WINDOWS_UPDATE_CACHE,
            JunkCategory.RECYCLE_BIN,
            JunkCategory.BROWSER_CACHE,
            JunkCategory.THUMBNAIL_CACHE,
            JunkCategory.CUSTOM
        }
        
        scan_config = ScanConfig(
            enabled_categories=all_categories,
            excluded_paths=[],
            custom_patterns=[]
        )
        
        assert len(scan_config.enabled_categories) == 6


class TestAppConfig:
    """测试 AppConfig 数据类"""
    
    def test_create_app_config(self):
        """测试创建应用配置对象"""
        scan_config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        app_config = AppConfig(scan_config=scan_config)
        
        assert app_config.scan_config == scan_config
        assert app_config.ui_theme == "light"
        assert app_config.language == "zh_CN"
        assert app_config.auto_check_updates is True
    
    def test_app_config_custom_values(self):
        """测试自定义值的应用配置"""
        scan_config = ScanConfig(
            enabled_categories={JunkCategory.BROWSER_CACHE},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        app_config = AppConfig(
            scan_config=scan_config,
            ui_theme="dark",
            language="en_US",
            auto_check_updates=False
        )
        
        assert app_config.ui_theme == "dark"
        assert app_config.language == "en_US"
        assert app_config.auto_check_updates is False
    
    def test_app_config_field_access(self):
        """测试应用配置字段访问"""
        scan_config = ScanConfig(
            enabled_categories=set(),
            excluded_paths=[],
            custom_patterns=[]
        )
        
        app_config = AppConfig(scan_config=scan_config)
        
        # 测试所有字段都可以访问
        _ = app_config.scan_config
        _ = app_config.ui_theme
        _ = app_config.language
        _ = app_config.auto_check_updates
