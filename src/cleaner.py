"""
垃圾文件清理器模块

负责删除选定的垃圾文件。
"""

import os
import time
import logging
from typing import List, Callable, Tuple, Optional

from .models import JunkFile, CleanResult
from .file_system import FileSystemAccess

logger = logging.getLogger(__name__)


class JunkCleaner:
    """垃圾文件清理器，负责删除选定的垃圾文件"""
    
    def clean(
        self, 
        files: List[JunkFile],
        progress_callback: Callable[[str, int], None]
    ) -> CleanResult:
        """
        清理指定的垃圾文件
        
        Args:
            files: 要清理的文件列表
            progress_callback: 进度回调函数 (current_file, percentage)
        
        Returns:
            CleanResult: 清理结果
        """
        logger.info(f"开始清理，共 {len(files)} 个文件")
        start_time = time.time()
        
        success_count = 0
        failed_count = 0
        freed_space = 0
        failed_files = []
        
        total_files = len(files)
        
        for index, junk_file in enumerate(files):
            # 计算进度百分比
            percentage = int((index / total_files) * 100) if total_files > 0 else 0
            
            # 调用进度回调
            try:
                progress_callback(junk_file.path, percentage)
            except Exception as e:
                logger.warning(f"进度回调出错: {e}")
            
            # 尝试删除文件
            success, error_message = self.safe_delete(junk_file.path)
            
            if success:
                success_count += 1
                freed_space += junk_file.size
                logger.debug(f"成功删除: {junk_file.path}")
            else:
                failed_count += 1
                failed_files.append((junk_file.path, error_message or "未知错误"))
                logger.warning(f"删除失败: {junk_file.path} - {error_message}")
        
        # 最后一次进度回调（100%）
        try:
            progress_callback("", 100)
        except Exception as e:
            logger.warning(f"进度回调出错: {e}")
        
        clean_duration = time.time() - start_time
        
        logger.info(
            f"清理完成，成功删除 {success_count} 个文件，"
            f"失败 {failed_count} 个，释放 {freed_space / (1024 * 1024):.2f} MB，"
            f"耗时 {clean_duration:.2f} 秒"
        )
        
        return CleanResult(
            success_count=success_count,
            failed_count=failed_count,
            freed_space=freed_space,
            failed_files=failed_files,
            clean_duration=clean_duration
        )
    
    def safe_delete(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        安全删除单个文件
        
        处理以下情况：
        - 文件不存在
        - 文件正在被使用
        - 权限不足
        - 文件不在安全删除列表中
        
        Args:
            file_path: 要删除的文件路径
        
        Returns:
            (success, error_message): 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.debug(f"文件不存在，跳过: {file_path}")
                return False, "文件不存在"
            
            # 检查文件是否在安全删除列表中
            if not FileSystemAccess.is_safe_to_delete(file_path):
                logger.warning(f"文件不在安全删除列表中，跳过: {file_path}")
                return False, "文件不在安全删除列表中"
            
            # 检查文件是否正在被使用
            if FileSystemAccess.is_file_in_use(file_path):
                logger.debug(f"文件正在使用中，跳过: {file_path}")
                return False, "文件正在使用中"
            
            # 尝试删除文件
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # 如果是目录，尝试删除（仅当目录为空时）
                os.rmdir(file_path)
            else:
                return False, "不是有效的文件或目录"
            
            return True, None
            
        except PermissionError:
            error_msg = "权限不足"
            logger.warning(f"无法删除文件: {file_path} ({error_msg})")
            return False, error_msg
            
        except OSError as e:
            # errno 32 表示文件被占用
            if e.errno == 32:
                error_msg = "文件正在使用中"
            else:
                error_msg = f"系统错误: {e}"
            logger.error(f"删除文件失败: {file_path} ({error_msg})")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"未知错误: {e}"
            logger.error(f"删除文件时出错: {file_path}", exc_info=True)
            return False, error_msg
