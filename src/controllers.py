"""
业务逻辑控制器模块

提供扫描和清理操作的控制器，使用 Qt 线程进行后台处理。
"""

import logging
from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QThread

from .models import ScanResult, CleanResult, JunkFile
from .scanner import JunkScanner
from .cleaner import JunkCleaner

logger = logging.getLogger(__name__)


class ScanWorker(QObject):
    """扫描工作线程"""
    
    # 信号定义
    progress = Signal(str, int)  # (current_path, percentage)
    finished = Signal(ScanResult)
    error = Signal(str)
    
    def __init__(self, scanner: JunkScanner):
        super().__init__()
        self.scanner = scanner
        self._is_cancelled = False
    
    def run(self):
        """执行扫描任务"""
        try:
            logger.info("扫描工作线程开始")
            
            # 定义进度回调函数
            def progress_callback(path: str, percentage: int):
                if self._is_cancelled:
                    raise InterruptedError("扫描已取消")
                self.progress.emit(path, percentage)
            
            # 执行扫描
            result = self.scanner.scan(progress_callback)
            
            if not self._is_cancelled:
                logger.info("扫描完成，准备发送结果信号")
                self.finished.emit(result)
                logger.info("扫描结果信号已发送")
            
        except InterruptedError as e:
            logger.info(f"扫描被取消: {e}")
            self.error.emit("扫描已取消")
        except Exception as e:
            logger.error(f"扫描过程中出错: {e}", exc_info=True)
            self.error.emit(f"扫描失败: {str(e)}")
    
    def cancel(self):
        """取消扫描"""
        self._is_cancelled = True
        logger.info("请求取消扫描")


class ScanController(QObject):
    """扫描控制器，管理扫描操作的生命周期"""
    
    # Qt 信号
    scan_started = Signal()
    scan_progress = Signal(str, int)  # (current_path, percentage)
    scan_completed = Signal(ScanResult)
    scan_error = Signal(str)
    
    def __init__(self, scanner: JunkScanner):
        """
        初始化扫描控制器
        
        Args:
            scanner: 垃圾扫描器实例
        """
        super().__init__()
        self.scanner = scanner
        self.scan_thread: Optional[QThread] = None
        self.scan_worker: Optional[ScanWorker] = None
        
        logger.info("初始化扫描控制器")
    
    def start_scan(self) -> None:
        """在后台线程启动扫描"""
        # 如果已有扫描在运行，先取消
        if self.scan_thread is not None and self.scan_thread.isRunning():
            logger.warning("已有扫描正在运行，先取消")
            self.cancel_scan()
        
        # 创建工作线程和工作对象
        self.scan_thread = QThread()
        self.scan_worker = ScanWorker(self.scanner)
        
        # 将工作对象移动到线程
        self.scan_worker.moveToThread(self.scan_thread)
        
        # 连接信号
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self._on_progress)
        self.scan_worker.finished.connect(self._on_finished)
        self.scan_worker.error.connect(self._on_error)
        
        # 线程清理
        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.error.connect(self.scan_thread.quit)
        self.scan_thread.finished.connect(self._cleanup)
        
        # 发送开始信号
        self.scan_started.emit()
        logger.info("启动扫描线程")
        
        # 启动线程
        self.scan_thread.start()
    
    def cancel_scan(self) -> None:
        """取消正在进行的扫描"""
        if self.scan_worker is not None:
            self.scan_worker.cancel()
            logger.info("取消扫描")
        
        if self.scan_thread is not None and self.scan_thread.isRunning():
            # 等待线程结束（最多 3 秒）
            self.scan_thread.quit()
            self.scan_thread.wait(3000)
    
    def _on_progress(self, path: str, percentage: int):
        """处理进度更新"""
        self.scan_progress.emit(path, percentage)
    
    def _on_finished(self, result: ScanResult):
        """处理扫描完成"""
        self.scan_completed.emit(result)
        logger.info("扫描完成信号已发送")
    
    def _on_error(self, error_message: str):
        """处理扫描错误"""
        self.scan_error.emit(error_message)
        logger.error(f"扫描错误: {error_message}")
    
    def _cleanup(self):
        """清理线程资源"""
        if self.scan_thread is not None:
            self.scan_thread.deleteLater()
            self.scan_thread = None
        if self.scan_worker is not None:
            self.scan_worker.deleteLater()
            self.scan_worker = None
        logger.debug("扫描线程资源已清理")


class CleanWorker(QObject):
    """清理工作线程"""
    
    # 信号定义
    progress = Signal(str, int)  # (current_file, percentage)
    finished = Signal(CleanResult)
    error = Signal(str)
    
    def __init__(self, cleaner: JunkCleaner, files: List[JunkFile]):
        super().__init__()
        self.cleaner = cleaner
        self.files = files
        self._is_cancelled = False
    
    def run(self):
        """执行清理任务"""
        try:
            logger.info(f"清理工作线程开始，共 {len(self.files)} 个文件")
            
            # 定义进度回调函数
            def progress_callback(file_path: str, percentage: int):
                if self._is_cancelled:
                    raise InterruptedError("清理已取消")
                self.progress.emit(file_path, percentage)
            
            # 执行清理
            result = self.cleaner.clean(self.files, progress_callback)
            
            if not self._is_cancelled:
                self.finished.emit(result)
                logger.info("清理工作线程完成")
            
        except InterruptedError as e:
            logger.info(f"清理被取消: {e}")
            self.error.emit("清理已取消")
        except Exception as e:
            logger.error(f"清理过程中出错: {e}", exc_info=True)
            self.error.emit(f"清理失败: {str(e)}")
    
    def cancel(self):
        """取消清理"""
        self._is_cancelled = True
        logger.info("请求取消清理")


class CleanController(QObject):
    """清理控制器，管理清理操作的生命周期"""
    
    # Qt 信号
    clean_started = Signal()
    clean_progress = Signal(str, int)  # (current_file, percentage)
    clean_completed = Signal(CleanResult)
    clean_error = Signal(str)
    
    def __init__(self, cleaner: JunkCleaner):
        """
        初始化清理控制器
        
        Args:
            cleaner: 垃圾清理器实例
        """
        super().__init__()
        self.cleaner = cleaner
        self.clean_thread: Optional[QThread] = None
        self.clean_worker: Optional[CleanWorker] = None
        
        logger.info("初始化清理控制器")
    
    def start_clean(self, files: List[JunkFile]) -> None:
        """
        在后台线程启动清理
        
        Args:
            files: 要清理的文件列表
        """
        # 如果已有清理在运行，先取消
        if self.clean_thread is not None and self.clean_thread.isRunning():
            logger.warning("已有清理正在运行，先取消")
            self.cancel_clean()
        
        # 创建工作线程和工作对象
        self.clean_thread = QThread()
        self.clean_worker = CleanWorker(self.cleaner, files)
        
        # 将工作对象移动到线程
        self.clean_worker.moveToThread(self.clean_thread)
        
        # 连接信号
        self.clean_thread.started.connect(self.clean_worker.run)
        self.clean_worker.progress.connect(self._on_progress)
        self.clean_worker.finished.connect(self._on_finished)
        self.clean_worker.error.connect(self._on_error)
        
        # 线程清理
        self.clean_worker.finished.connect(self.clean_thread.quit)
        self.clean_worker.error.connect(self.clean_thread.quit)
        self.clean_thread.finished.connect(self._cleanup)
        
        # 发送开始信号
        self.clean_started.emit()
        logger.info(f"启动清理线程，共 {len(files)} 个文件")
        
        # 启动线程
        self.clean_thread.start()
    
    def cancel_clean(self) -> None:
        """取消正在进行的清理"""
        if self.clean_worker is not None:
            self.clean_worker.cancel()
            logger.info("取消清理")
        
        if self.clean_thread is not None and self.clean_thread.isRunning():
            # 等待线程结束（最多 3 秒）
            self.clean_thread.quit()
            self.clean_thread.wait(3000)
    
    def _on_progress(self, file_path: str, percentage: int):
        """处理进度更新"""
        self.clean_progress.emit(file_path, percentage)
    
    def _on_finished(self, result: CleanResult):
        """处理清理完成"""
        self.clean_completed.emit(result)
        logger.info("清理完成信号已发送")
    
    def _on_error(self, error_message: str):
        """处理清理错误"""
        self.clean_error.emit(error_message)
        logger.error(f"清理错误: {error_message}")
    
    def _cleanup(self):
        """清理线程资源"""
        if self.clean_thread is not None:
            self.clean_thread.deleteLater()
            self.clean_thread = None
        if self.clean_worker is not None:
            self.clean_worker.deleteLater()
            self.clean_worker = None
        logger.debug("清理线程资源已清理")
