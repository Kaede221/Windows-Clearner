"""
文件系统访问模块的单元测试
"""

import os
import tempfile
import pytest
from pathlib import Path
from src.file_system import FileSystemAccess


class TestFileSystemAccess:
    """FileSystemAccess 类的单元测试"""
    
    def test_has_admin_privileges(self):
        """测试管理员权限检测"""
        # 这个测试只验证方法能够正常调用并返回布尔值
        result = FileSystemAccess.has_admin_privileges()
        assert isinstance(result, bool)
    
    def test_requires_admin_access_for_windows_temp(self):
        """测试 Windows Temp 目录需要管理员权限"""
        result = FileSystemAccess.requires_admin_access(r"C:\Windows\Temp")
        assert result is True
    
    def test_requires_admin_access_for_windows_update(self):
        """测试 Windows Update 目录需要管理员权限"""
        result = FileSystemAccess.requires_admin_access(
            r"C:\Windows\SoftwareDistribution\Download"
        )
        assert result is True
    
    def test_requires_admin_access_for_user_temp(self):
        """测试用户临时目录不需要管理员权限"""
        user_temp = os.path.expandvars(r"%TEMP%")
        result = FileSystemAccess.requires_admin_access(user_temp)
        assert result is False
    
    def test_can_access_path_nonexistent(self):
        """测试访问不存在的路径"""
        result = FileSystemAccess.can_access_path(r"C:\NonExistentPath\test.txt")
        assert result is False
    
    def test_can_access_path_temp_directory(self):
        """测试访问临时目录"""
        temp_dir = tempfile.gettempdir()
        result = FileSystemAccess.can_access_path(temp_dir)
        assert result is True
    
    def test_is_file_in_use_nonexistent(self):
        """测试检查不存在的文件"""
        result = FileSystemAccess.is_file_in_use(r"C:\NonExistent\file.txt")
        assert result is False
    
    def test_is_file_in_use_with_temp_file(self):
        """测试检查临时文件的占用状态"""
        # 创建一个临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"test data")
        
        try:
            # 文件已关闭，应该不被占用
            result = FileSystemAccess.is_file_in_use(tmp_path)
            assert result is False
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_is_file_in_use_with_open_file(self):
        """测试检查打开的文件"""
        # 创建并打开一个临时文件
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp_path = tmp.name
            tmp.write("test data")
            tmp.flush()
            
            # 文件仍然打开，检查占用状态
            # 注意：在 Windows 上，文件可能被检测为占用
            result = FileSystemAccess.is_file_in_use(tmp_path)
            # 这个测试可能因平台而异，所以我们只验证返回布尔值
            assert isinstance(result, bool)
        
        # 清理
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    def test_get_file_size_existing_file(self):
        """测试获取存在文件的大小"""
        # 创建一个已知大小的临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
            test_data = b"test data content"
            tmp.write(test_data)
        
        try:
            size = FileSystemAccess.get_file_size(tmp_path)
            assert size == len(test_data)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_get_file_size_nonexistent_file(self):
        """测试获取不存在文件的大小"""
        size = FileSystemAccess.get_file_size(r"C:\NonExistent\file.txt")
        assert size == 0
    
    def test_is_safe_to_delete_temp_file(self):
        """测试临时目录中的文件是安全的"""
        temp_dir = os.path.expandvars(r"%TEMP%")
        test_file = os.path.join(temp_dir, "test.tmp")
        result = FileSystemAccess.is_safe_to_delete(test_file)
        assert result is True
    
    def test_is_safe_to_delete_windows_temp(self):
        """测试 Windows Temp 目录中的文件是安全的"""
        test_file = r"C:\Windows\Temp\test.tmp"
        result = FileSystemAccess.is_safe_to_delete(test_file)
        assert result is True
    
    def test_is_safe_to_delete_browser_cache(self):
        """测试浏览器缓存文件是安全的"""
        chrome_cache = os.path.expandvars(
            r"%LocalAppData%\Google\Chrome\User Data\Default\Cache\test.cache"
        )
        result = FileSystemAccess.is_safe_to_delete(chrome_cache)
        assert result is True
    
    def test_is_safe_to_delete_recycle_bin(self):
        """测试回收站文件是安全的"""
        recycle_file = r"C:\$Recycle.Bin\S-1-5-21\test.txt"
        result = FileSystemAccess.is_safe_to_delete(recycle_file)
        assert result is True
    
    def test_is_safe_to_delete_system_file(self):
        """测试系统文件不安全"""
        system_file = r"C:\Windows\System32\kernel32.dll"
        result = FileSystemAccess.is_safe_to_delete(system_file)
        assert result is False
    
    def test_is_safe_to_delete_user_documents(self):
        """测试用户文档不安全"""
        user_doc = os.path.expandvars(r"%USERPROFILE%\Documents\important.docx")
        result = FileSystemAccess.is_safe_to_delete(user_doc)
        assert result is False
    
    def test_is_safe_to_delete_program_files(self):
        """测试程序文件不安全"""
        program_file = r"C:\Program Files\SomeApp\app.exe"
        result = FileSystemAccess.is_safe_to_delete(program_file)
        assert result is False
