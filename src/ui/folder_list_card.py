"""
文件夹列表设置卡片模块

实现用户自定义文件夹选择功能。
"""

import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QFileDialog, QSizePolicy
)
from qfluentwidgets import (
    ExpandSettingCard,
    PushButton,
    ToolButton,
    FluentIcon as FIF,
    isDarkTheme
)

logger = logging.getLogger(__name__)


class FolderItem(QWidget):
    """文件夹项组件"""
    
    removed = Signal(QWidget)
    
    def __init__(self, folder: str, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.hBoxLayout = QHBoxLayout(self)
        self.folderLabel = QLabel(folder, self)
        self.removeButton = ToolButton(FIF.CLOSE, self)
        
        self.removeButton.setFixedSize(39, 29)
        self.removeButton.setIconSize(QSize(12, 12))
        
        self.setFixedHeight(53)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.hBoxLayout.setContentsMargins(48, 0, 60, 0)
        self.hBoxLayout.addWidget(self.folderLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.removeButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # 设置对象名称以应用主题样式
        self.folderLabel.setObjectName('folderLabel')
        
        # 应用样式
        self._apply_style()
        
        self.removeButton.clicked.connect(lambda: self.removed.emit(self))
    
    def _apply_style(self):
        """应用样式"""
        if isDarkTheme():
            self.folderLabel.setStyleSheet("""
                QLabel#folderLabel {
                    color: white;
                    font-size: 14px;
                }
            """)
        else:
            self.folderLabel.setStyleSheet("""
                QLabel#folderLabel {
                    color: black;
                    font-size: 14px;
                }
            """)


class FolderListSettingCard(ExpandSettingCard):
    """文件夹列表设置卡片"""
    
    folderChanged = Signal(list)
    
    def __init__(self, title: str, content: str = None, directory="./", parent=None):
        """
        初始化文件夹列表设置卡片
        
        Args:
            title: 卡片标题
            content: 卡片内容描述
            directory: 文件对话框的工作目录
            parent: 父组件
        """
        super().__init__(FIF.FOLDER, title, content, parent)
        self._dialogDirectory = directory
        self.addFolderButton = PushButton('添加文件夹', self, FIF.FOLDER_ADD)
        
        self.folders = []
        self._init_widget()
    
    def _init_widget(self):
        """初始化组件"""
        self.addWidget(self.addFolderButton)
        
        # 初始化布局
        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        
        self.addFolderButton.clicked.connect(self._show_folder_dialog)
    
    def _show_folder_dialog(self):
        """显示文件夹选择对话框"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择文件夹", self._dialogDirectory
        )
        
        if not folder or folder in self.folders:
            if folder in self.folders:
                logger.info(f"文件夹已存在: {folder}")
            return
        
        self._add_folder_item(folder)
        self.folders.append(folder)
        self.folderChanged.emit(self.folders)
        logger.info(f"添加文件夹: {folder}")
    
    def _add_folder_item(self, folder: str):
        """添加文件夹项"""
        item = FolderItem(folder, self.view)
        item.removed.connect(self._remove_folder)
        self.viewLayout.addWidget(item)
        item.show()
        self._adjustViewSize()
    
    def _remove_folder(self, item: FolderItem):
        """移除文件夹"""
        if item.folder not in self.folders:
            return
        
        self.folders.remove(item.folder)
        self.viewLayout.removeWidget(item)
        item.deleteLater()
        self._adjustViewSize()
        
        self.folderChanged.emit(self.folders)
        logger.info(f"移除文件夹: {item.folder}")
    
    def set_folders(self, folders: list):
        """
        设置文件夹列表
        
        Args:
            folders: 文件夹路径列表
        """
        # 清除现有项
        for i in reversed(range(self.viewLayout.count())):
            widget = self.viewLayout.itemAt(i).widget()
            if isinstance(widget, FolderItem):
                self.viewLayout.removeWidget(widget)
                widget.deleteLater()
        
        # 添加新项
        self.folders = folders.copy()
        for folder in self.folders:
            self._add_folder_item(folder)
        
        logger.info(f"设置文件夹列表: {folders}")
    
    def get_folders(self) -> list:
        """
        获取文件夹列表
        
        Returns:
            文件夹路径列表
        """
        return self.folders.copy()
