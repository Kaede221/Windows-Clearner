"""
设置页面模块

实现应用程序的设置界面。
"""

import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    TitleLabel,
    BodyLabel
)

logger = logging.getLogger(__name__)


class SettingsPage(QWidget):
    """设置页面类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        logger.info("设置页面初始化完成")
    
    def _init_ui(self) -> None:
        """初始化 UI 组件"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = TitleLabel("设置")
        main_layout.addWidget(title_label)
        
        # Hello World 内容
        hello_label = BodyLabel("Hello World")
        hello_label.setAlignment(Qt.AlignCenter)
        
        # 设置字体大小
        font = hello_label.font()
        font.setPointSize(24)
        hello_label.setFont(font)
        
        main_layout.addWidget(hello_label)
        main_layout.addStretch()
