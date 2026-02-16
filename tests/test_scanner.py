"""
测试垃圾文件扫描器模块
"""

import pytest
from unittest.mock import Mock, patch
from src.scanner import JunkScanner
from src.models import JunkCategory, JunkFile, ScanConfig


class TestJunkScanner:
    """测试 JunkScanner 基类"""
    
    def test_scanner_initialization(self):
        """测试扫描器初始化"""
        config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES, JunkCategory.RECYCLE_BIN},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        
        assert scanner.config == config
        assert isinstance(scanner.has_admin, bool)
        assert isinstance(scanner.category_scanners, dict)
    
    def test_scan_calls_progress_callback(self):
        """测试扫描过程调用进度回调"""
        config = ScanConfig(
            enabled_categories={JunkCategory.RECYCLE_BIN},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        progress_callback = Mock()
        
        result = scanner.scan(progress_callback)
        
        # 验证进度回调被调用
        assert progress_callback.call_count >= 2  # 至少调用开始和结束
        
        # 验证最后一次调用是 100%
        last_call = progress_callback.call_args_list[-1]
        assert last_call[0][1] == 100  # 第二个参数是百分比
    
    def test_scan_returns_valid_result(self):
        """测试扫描返回有效的结果"""
        config = ScanConfig(
            enabled_categories={JunkCategory.RECYCLE_BIN},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        progress_callback = Mock()
        
        result = scanner.scan(progress_callback)
        
        # 验证结果结构
        assert isinstance(result.categories, dict)
        assert isinstance(result.total_size, int)
        assert isinstance(result.total_count, int)
        assert isinstance(result.scan_duration, float)
        assert isinstance(result.errors, list)
        assert isinstance(result.requires_admin, bool)
        assert isinstance(result.inaccessible_categories, list)
        
        # 验证统计信息
        assert result.total_count >= 0
        assert result.total_size >= 0
        assert result.scan_duration >= 0
    
    def test_get_inaccessible_categories_with_admin(self):
        """测试有管理员权限时无无法访问的类别"""
        config = ScanConfig(
            enabled_categories={
                JunkCategory.TEMP_FILES,
                JunkCategory.WINDOWS_UPDATE_CACHE,
                JunkCategory.RECYCLE_BIN
            },
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        
        # 模拟有管理员权限
        with patch.object(scanner, 'has_admin', True):
            inaccessible = scanner.get_inaccessible_categories()
            assert inaccessible == []
    
    def test_get_inaccessible_categories_without_admin(self):
        """测试无管理员权限时返回需要权限的类别"""
        config = ScanConfig(
            enabled_categories={
                JunkCategory.TEMP_FILES,
                JunkCategory.WINDOWS_UPDATE_CACHE,
                JunkCategory.RECYCLE_BIN
            },
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        
        # 模拟无管理员权限
        with patch.object(scanner, 'has_admin', False):
            inaccessible = scanner.get_inaccessible_categories()
            
            # 验证返回需要管理员权限的类别
            assert JunkCategory.TEMP_FILES in inaccessible
            assert JunkCategory.WINDOWS_UPDATE_CACHE in inaccessible
            assert JunkCategory.RECYCLE_BIN not in inaccessible
    
    def test_category_requires_admin(self):
        """测试类别权限需求检查"""
        config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        
        # 需要管理员权限的类别
        assert scanner._category_requires_admin(JunkCategory.TEMP_FILES) is True
        assert scanner._category_requires_admin(JunkCategory.WINDOWS_UPDATE_CACHE) is True
        
        # 不需要管理员权限的类别
        assert scanner._category_requires_admin(JunkCategory.RECYCLE_BIN) is False
        assert scanner._category_requires_admin(JunkCategory.BROWSER_CACHE) is False
        assert scanner._category_requires_admin(JunkCategory.THUMBNAIL_CACHE) is False
    
    def test_scan_category_without_admin_skips_admin_required(self):
        """测试无管理员权限时跳过需要权限的类别"""
        config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        
        # 模拟无管理员权限
        with patch.object(scanner, 'has_admin', False):
            files = scanner.scan_category(JunkCategory.TEMP_FILES)
            
            # 应该返回空列表
            assert files == []
    
    def test_scan_handles_errors_gracefully(self):
        """测试扫描过程优雅处理错误"""
        config = ScanConfig(
            enabled_categories={JunkCategory.TEMP_FILES, JunkCategory.RECYCLE_BIN},
            excluded_paths=[],
            custom_patterns=[]
        )
        
        scanner = JunkScanner(config)
        progress_callback = Mock()
        
        # 模拟扫描器抛出异常
        def mock_scan_category(category):
            if category == JunkCategory.TEMP_FILES:
                raise Exception("测试错误")
            return []
        
        with patch.object(scanner, 'scan_category', side_effect=mock_scan_category):
            result = scanner.scan(progress_callback)
            
            # 验证扫描继续进行，不会中断
            assert len(result.errors) > 0
            assert any("测试错误" in error for error in result.errors)
            
            # 验证其他类别仍然被扫描
            assert JunkCategory.RECYCLE_BIN in result.categories
