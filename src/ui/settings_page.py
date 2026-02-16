"""
设置页面模块

实现应用程序的设置界面。
"""

import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QColor
from qfluentwidgets import (
    ScrollArea,
    ExpandLayout,
    SettingCardGroup,
    CustomColorSettingCard,
    SwitchSettingCard,
    OptionsSettingCard,
    PrimaryPushSettingCard,
    setThemeColor,
    setTheme,
    qconfig,
    Theme,
    FluentIcon as FIF,
    InfoBar,
    isDarkTheme
)

logger = logging.getLogger(__name__)


class SettingsPage(ScrollArea):
    """设置页面类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        # 设置标签
        self.settingLabel = QLabel("设置", self)
        
        # 个性化设置组
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        
        # 主题模式卡片
        self.themeCard = OptionsSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            "应用主题",
            "更改应用程序的外观",
            texts=["浅色", "深色", "跟随系统"],
            parent=self.personalGroup
        )
        
        # 主题色卡片 - 绑定到 qconfig.themeColor
        self.themeColorCard = CustomColorSettingCard(
            qconfig.themeColor,
            FIF.PALETTE,
            "主题色",
            "更改应用程序的主题色",
            self.personalGroup
        )
        
        # 应用设置组
        self.appGroup = SettingCardGroup("应用", self.scrollWidget)
        
        # 自动检查更新卡片
        self.autoUpdateCard = SwitchSettingCard(
            FIF.UPDATE,
            "启动时检查更新",
            "新版本将更加稳定并拥有更多功能",
            configItem=None,  # 暂时不绑定配置项
            parent=self.appGroup
        )
        
        # 关于设置组
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        
        # 关于卡片
        self.aboutCard = PrimaryPushSettingCard(
            "查看详情",
            FIF.INFO,
            "关于",
            "© 2024 Windows 垃圾文件清理工具 v1.0.0",
            self.aboutGroup
        )
        
        self._init_ui()
        self._connect_signals()
        logger.info("设置页面初始化完成")
    
    def _init_ui(self) -> None:
        """初始化 UI 组件"""
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingsPage')
        
        # 设置样式
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        
        # 应用样式表
        self._apply_style_sheet()
        
        self._init_layout()
    
    def _apply_style_sheet(self) -> None:
        """应用样式表"""
        # 设置透明背景
        self.setStyleSheet("""
            SettingsPage, #scrollWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        # 根据主题设置标签样式
        if isDarkTheme():
            label_style = """
                QLabel#settingLabel {
                    font-size: 33px;
                    font-weight: bold;
                    background-color: transparent;
                    color: white;
                }
            """
        else:
            label_style = """
                QLabel#settingLabel {
                    font-size: 33px;
                    font-weight: bold;
                    background-color: transparent;
                    color: black;
                }
            """
        
        self.settingLabel.setStyleSheet(label_style)
    
    def _init_layout(self) -> None:
        """初始化布局"""
        self.settingLabel.move(36, 30)
        
        # 添加卡片到个性化组
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        
        # 添加卡片到应用组
        self.appGroup.addSettingCard(self.autoUpdateCard)
        
        # 添加卡片到关于组
        self.aboutGroup.addSettingCard(self.aboutCard)
        
        # 添加设置卡片组到布局
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.appGroup)
        self.expandLayout.addWidget(self.aboutGroup)
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        # 主题变化
        qconfig.themeChanged.connect(self._on_theme_changed)
        
        # 主题色变化 - 使用 lambda 来调用 setThemeColor
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))
        
        # 关于按钮点击
        self.aboutCard.clicked.connect(self._on_about_clicked)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变化"""
        setTheme(theme)
        # 重新应用样式表
        self._apply_style_sheet()
        logger.info(f"主题已更改为: {theme}")
    
    def _on_about_clicked(self) -> None:
        """处理关于按钮点击"""
        InfoBar.info(
            title="关于",
            content="Windows 垃圾文件清理工具 v1.0.0\n基于 PySide6 和 PyQt-Fluent-Widgets 开发",
            orient=Qt.Orientation.Vertical,
            isClosable=True,
            duration=3000,
            parent=self
        )
