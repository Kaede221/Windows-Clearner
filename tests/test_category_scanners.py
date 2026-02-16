"""
测试类别扫描器模块
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from src.category_scanners import (
    TempFilesScanner,
    WindowsUpdateScanner,
    RecycleBinScanner,
    BrowserCacheScanner,
    ThumbnailCacheScanner
)
from src.models import JunkCategory


class TestTempFilesScanner:
    """测试系统临时文件扫描器"""
    
    def test_temp_files_scanner_returns_list(self):
        """测试临时文件扫描器返回列表"""
        scanner = TempFilesScanner()
        files = scanner.scan()
        
        assert isinstance(files, list)
    
    def test_temp_files_scanner_category(self):
        """测试临时文件扫描器返回正确的类别"""
        scanner = TempFilesScanner()
        files = scanner.scan()
        
        # 如果有文件，验证类别
        for file in files:
            assert file.category == JunkCategory.TEMP_FILES
    
    def test_temp_files_scanner_handles_missing_directory(self):
        """测试临时文件扫描器处理不存在的目录"""
        scanner = TempFilesScanner()
        
        # 模拟所有临时目录都不存在
        with patch('os.path.exists', return_value=False):
            files = scanner.scan()
            
            # 应该返回空列表，不抛出异常
            assert files == []
    
    def test_temp_files_scanner_handles_permission_error(self):
        """测试临时文件扫描器处理权限错误"""
        scanner = TempFilesScanner()
        
        # 模拟权限错误
        with patch('os.walk', side_effect=PermissionError("Access denied")):
            with patch('os.path.exists', return_value=True):
                files = scanner.scan()
                
                # 应该返回空列表或部分结果，不抛出异常
                assert isinstance(files, list)


class TestWindowsUpdateScanner:
    """测试 Windows 更新缓存扫描器"""
    
    def test_windows_update_scanner_returns_list(self):
        """测试 Windows 更新扫描器返回列表"""
        scanner = WindowsUpdateScanner()
        files = scanner.scan()
        
        assert isinstance(files, list)
    
    def test_windows_update_scanner_category(self):
        """测试 Windows 更新扫描器返回正确的类别"""
        scanner = WindowsUpdateScanner()
        files = scanner.scan()
        
        # 如果有文件，验证类别
        for file in files:
            assert file.category == JunkCategory.WINDOWS_UPDATE_CACHE
    
    def test_windows_update_scanner_handles_missing_directory(self):
        """测试 Windows 更新扫描器处理不存在的目录"""
        scanner = WindowsUpdateScanner()
        
        # 模拟目录不存在
        with patch('os.path.exists', return_value=False):
            files = scanner.scan()
            
            # 应该返回空列表，不抛出异常
            assert files == []


class TestRecycleBinScanner:
    """测试回收站扫描器"""
    
    def test_recycle_bin_scanner_returns_list(self):
        """测试回收站扫描器返回列表"""
        scanner = RecycleBinScanner()
        files = scanner.scan()
        
        assert isinstance(files, list)
    
    def test_recycle_bin_scanner_category(self):
        """测试回收站扫描器返回正确的类别"""
        scanner = RecycleBinScanner()
        files = scanner.scan()
        
        # 如果有文件，验证类别
        for file in files:
            assert file.category == JunkCategory.RECYCLE_BIN
    
    def test_recycle_bin_scanner_get_drives(self):
        """测试回收站扫描器获取驱动器列表"""
        scanner = RecycleBinScanner()
        drives = scanner._get_drives()
        
        assert isinstance(drives, list)
        # 至少应该有 C 盘
        assert any('C' in drive.upper() for drive in drives)
    
    def test_recycle_bin_scanner_handles_no_drives(self):
        """测试回收站扫描器处理无驱动器情况"""
        scanner = RecycleBinScanner()
        
        # 模拟没有驱动器
        with patch.object(scanner, '_get_drives', return_value=[]):
            files = scanner.scan()
            
            # 应该返回空列表，不抛出异常
            assert files == []


class TestBrowserCacheScanner:
    """测试浏览器缓存扫描器"""
    
    def test_browser_cache_scanner_returns_list(self):
        """测试浏览器缓存扫描器返回列表"""
        scanner = BrowserCacheScanner()
        files = scanner.scan()
        
        assert isinstance(files, list)
    
    def test_browser_cache_scanner_category(self):
        """测试浏览器缓存扫描器返回正确的类别"""
        scanner = BrowserCacheScanner()
        files = scanner.scan()
        
        # 如果有文件，验证类别
        for file in files:
            assert file.category == JunkCategory.BROWSER_CACHE
    
    def test_browser_cache_scanner_handles_missing_directories(self):
        """测试浏览器缓存扫描器处理不存在的目录"""
        scanner = BrowserCacheScanner()
        
        # 模拟所有目录都不存在
        with patch('os.path.exists', return_value=False):
            files = scanner.scan()
            
            # 应该返回空列表，不抛出异常
            assert files == []
    
    def test_browser_cache_scanner_firefox_cache(self):
        """测试浏览器缓存扫描器处理 Firefox 缓存"""
        scanner = BrowserCacheScanner()
        
        # 创建临时目录模拟 Firefox 配置文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建配置文件目录
            profile_dir = os.path.join(temp_dir, "test.profile")
            cache_dir = os.path.join(profile_dir, "cache2")
            os.makedirs(cache_dir, exist_ok=True)
            
            # 创建测试文件
            test_file = os.path.join(cache_dir, "test.cache")
            with open(test_file, 'w') as f:
                f.write("test")
            
            # 扫描 Firefox 缓存
            files = scanner._scan_firefox_cache(temp_dir)
            
            # 验证结果
            assert isinstance(files, list)


class TestThumbnailCacheScanner:
    """测试缩略图缓存扫描器"""
    
    def test_thumbnail_cache_scanner_returns_list(self):
        """测试缩略图缓存扫描器返回列表"""
        scanner = ThumbnailCacheScanner()
        files = scanner.scan()
        
        assert isinstance(files, list)
    
    def test_thumbnail_cache_scanner_category(self):
        """测试缩略图缓存扫描器返回正确的类别"""
        scanner = ThumbnailCacheScanner()
        files = scanner.scan()
        
        # 如果有文件，验证类别
        for file in files:
            assert file.category == JunkCategory.THUMBNAIL_CACHE
    
    def test_thumbnail_cache_scanner_handles_missing_directory(self):
        """测试缩略图缓存扫描器处理不存在的目录"""
        scanner = ThumbnailCacheScanner()
        
        # 模拟目录不存在
        with patch('os.path.exists', return_value=False):
            files = scanner.scan()
            
            # 应该返回空列表，不抛出异常
            assert files == []
    
    def test_thumbnail_cache_scanner_filters_thumbcache_files(self):
        """测试缩略图缓存扫描器只扫描 thumbcache 文件"""
        scanner = ThumbnailCacheScanner()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            thumbcache_file = os.path.join(temp_dir, "thumbcache_256.db")
            other_file = os.path.join(temp_dir, "other.txt")
            
            with open(thumbcache_file, 'w') as f:
                f.write("test")
            with open(other_file, 'w') as f:
                f.write("test")
            
            # 模拟扫描该目录
            with patch('os.path.expandvars', return_value=temp_dir):
                with patch('os.path.exists', return_value=True):
                    files = scanner.scan()
                    
                    # 验证只扫描 thumbcache 文件
                    assert len(files) == 1
                    assert "thumbcache_256.db" in files[0].path


class TestCategoryScannerIntegration:
    """测试类别扫描器集成"""
    
    def test_all_scanners_handle_errors_gracefully(self):
        """测试所有扫描器都能优雅处理错误"""
        scanners = [
            TempFilesScanner(),
            WindowsUpdateScanner(),
            RecycleBinScanner(),
            BrowserCacheScanner(),
            ThumbnailCacheScanner()
        ]
        
        for scanner in scanners:
            # 模拟各种错误情况
            with patch('os.walk', side_effect=Exception("Test error")):
                with patch('os.path.exists', return_value=True):
                    try:
                        files = scanner.scan()
                        # 应该返回列表，不抛出异常
                        assert isinstance(files, list)
                    except Exception as e:
                        pytest.fail(f"Scanner {scanner.__class__.__name__} did not handle error gracefully: {e}")
    
    def test_all_scanners_return_correct_category(self):
        """测试所有扫描器返回正确的类别"""
        test_cases = [
            (TempFilesScanner(), JunkCategory.TEMP_FILES),
            (WindowsUpdateScanner(), JunkCategory.WINDOWS_UPDATE_CACHE),
            (RecycleBinScanner(), JunkCategory.RECYCLE_BIN),
            (BrowserCacheScanner(), JunkCategory.BROWSER_CACHE),
            (ThumbnailCacheScanner(), JunkCategory.THUMBNAIL_CACHE),
        ]
        
        for scanner, expected_category in test_cases:
            files = scanner.scan()
            
            # 如果有文件，验证类别
            for file in files:
                assert file.category == expected_category, \
                    f"Scanner {scanner.__class__.__name__} returned wrong category"
