"""
主窗口模块

实现应用程序的主窗口界面。
"""

import sys
import os
import ctypes
import logging
from typing import Dict, List, Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTreeWidgetItem
from PySide6.QtGui import QColor, QIcon
from qfluentwidgets import (
    FluentWindow, 
    PrimaryPushButton, 
    PushButton,
    TreeWidget,
    ProgressRing,
    CardWidget,
    BodyLabel,
    StrongBodyLabel,
    InfoBar,
    InfoBarPosition,
    FluentIcon,
    setThemeColor,
    qconfig
)

from ..models import ScanResult, CleanResult, JunkFile, JunkCategory, ScanConfig
from ..controllers import ScanController, CleanController
from ..scanner import JunkScanner
from ..cleaner import JunkCleaner
from ..file_system import FileSystemAccess
from ..config_manager import ConfigManager
from .settings_page import SettingsPage

logger = logging.getLogger(__name__)


class MainWindow(FluentWindow):
    """主窗口类，使用 PyQt-Fluent-Widgets 的 FluentWindow"""
    
    def __init__(self):
        super().__init__()
        
        # 加载配置
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # 初始化控制器
        scanner = JunkScanner(self.config.scan_config)
        cleaner = JunkCleaner()
        self.scan_controller = ScanController(scanner)
        self.clean_controller = CleanController(cleaner)
        
        # 扫描结果
        self.scan_result: Optional[ScanResult] = None
        
        # 检查管理员权限
        self.has_admin = FileSystemAccess.has_admin_privileges()
        
        # 初始化 UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 检查管理员权限并显示警告
        self._check_admin_privileges()
        
        logger.info(f"主窗口初始化完成，管理员权限: {self.has_admin}")
    
    def _init_ui(self) -> None:
        """初始化 UI 组件"""
        # 设置窗口属性
        self.setWindowTitle("Windows 垃圾文件清理工具")
        self.resize(900, 700)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            logger.info(f"已设置窗口图标: {icon_path}")
        else:
            logger.warning(f"图标文件不存在: {icon_path}")
        
        # 创建中心部件
        central_widget = QWidget()
        central_widget.setObjectName("homeInterface")
        self.addSubInterface(central_widget, FluentIcon.HOME, "主页")
        
        # 创建设置页面
        settings_widget = SettingsPage()
        settings_widget.setObjectName("settingsInterface")
        self.addSubInterface(settings_widget, FluentIcon.SETTING, "设置")
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 统计卡片区域
        self._create_stats_cards(main_layout)
        
        # 树形列表区域
        self._create_tree_widget(main_layout)
        
        # 操作按钮区域
        self._create_action_buttons(main_layout)
        
        # 进度指示器（初始隐藏）
        self.progress_ring = ProgressRing(self)
        self.progress_ring.setFixedSize(40, 40)
        self.progress_ring.hide()
        
        # 状态标签
        self.status_label = BodyLabel("就绪")
        main_layout.addWidget(self.status_label)
    
    def _create_stats_cards(self, parent_layout: QVBoxLayout) -> None:
        """创建统计卡片"""
        # 卡片容器
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # 文件数量卡片
        self.file_count_card, self.file_count_label = self._create_stat_card("文件数量", "0")
        cards_layout.addWidget(self.file_count_card)
        
        # 总大小卡片
        self.total_size_card, self.total_size_label = self._create_stat_card("总大小", "0 MB")
        cards_layout.addWidget(self.total_size_card)
        
        # 选中大小卡片
        self.selected_size_card, self.selected_size_label = self._create_stat_card("选中大小", "0 MB")
        cards_layout.addWidget(self.selected_size_card)
        
        parent_layout.addLayout(cards_layout)
    
    def _create_stat_card(self, title: str, value: str):
        """创建单个统计卡片，返回卡片和值标签"""
        card = CardWidget()
        card.setFixedHeight(100)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(5)
        
        title_label = BodyLabel(title)
        value_label = StrongBodyLabel(value)
        
        # 设置值标签的字体大小
        font = value_label.font()
        font.setPointSize(20)
        value_label.setFont(font)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()
        
        logger.info(f"创建统计卡片: {title}, 初始值: {value}")
        
        return card, value_label
    
    def _create_tree_widget(self, parent_layout: QVBoxLayout) -> None:
        """创建树形列表"""
        self.tree_widget = TreeWidget()
        self.tree_widget.setHeaderLabels(["类别/文件", "大小", "路径"])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.setColumnWidth(1, 120)
        self.tree_widget.setColumnWidth(2, 400)
        
        # 连接复选框变化信号
        self.tree_widget.itemChanged.connect(self._on_tree_item_changed)
        
        parent_layout.addWidget(self.tree_widget, 1)
    
    def _create_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 开始扫描按钮
        self.scan_button = PrimaryPushButton("开始扫描")
        self.scan_button.setFixedHeight(40)
        self.scan_button.clicked.connect(self.on_scan_clicked)
        button_layout.addWidget(self.scan_button)
        
        # 开始清理按钮（初始禁用）
        self.clean_button = PrimaryPushButton("开始清理")
        self.clean_button.setFixedHeight(40)
        self.clean_button.setEnabled(False)
        self.clean_button.clicked.connect(self.on_clean_clicked)
        button_layout.addWidget(self.clean_button)
        
        # 取消按钮（初始隐藏）
        self.cancel_button = PushButton("取消")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.hide()
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """连接控制器信号"""
        # 扫描信号
        self.scan_controller.scan_started.connect(self._on_scan_started)
        self.scan_controller.scan_progress.connect(self._on_scan_progress)
        self.scan_controller.scan_completed.connect(self._on_scan_completed)
        self.scan_controller.scan_error.connect(self._on_scan_error)
        
        # 清理信号
        self.clean_controller.clean_started.connect(self._on_clean_started)
        self.clean_controller.clean_progress.connect(self._on_clean_progress)
        self.clean_controller.clean_completed.connect(self._on_clean_completed)
        self.clean_controller.clean_error.connect(self._on_clean_error)
    
    def _check_admin_privileges(self) -> None:
        """检查管理员权限并显示警告"""
        if not self.has_admin:
            InfoBar.warning(
                title="权限提示",
                content="未以管理员身份运行，某些文件可能无法清理",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            logger.info("显示管理员权限警告")
    
    def show_admin_warning(self, inaccessible_categories: List[JunkCategory]) -> None:
        """显示权限警告，列出无法访问的类别"""
        if not inaccessible_categories:
            return
        
        category_names = "、".join([cat.value for cat in inaccessible_categories])
        
        # 创建自定义信息栏，包含重启按钮
        info_bar = InfoBar.warning(
            title="权限不足",
            content=f"以下类别需要管理员权限：{category_names}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,  # 不自动关闭
            parent=self
        )
        
        # 添加重启按钮
        restart_button = PushButton("以管理员身份重新启动")
        restart_button.clicked.connect(self.restart_as_admin)
        info_bar.addWidget(restart_button)
        
        logger.info(f"显示权限警告，无法访问的类别: {category_names}")
    
    def restart_as_admin(self) -> None:
        """以管理员权限重新启动应用程序"""
        try:
            # 获取当前脚本路径
            script_path = sys.argv[0]
            
            # 使用 ShellExecuteW 以管理员身份运行
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                script_path,
                None,
                1  # SW_SHOWNORMAL
            )
            
            # 关闭当前应用程序
            self.close()
            logger.info("请求以管理员身份重新启动")
            
        except Exception as e:
            logger.error(f"以管理员身份重新启动失败: {e}", exc_info=True)
            InfoBar.error(
                title="错误",
                content=f"无法以管理员身份重新启动: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def on_scan_clicked(self) -> None:
        """处理扫描按钮点击"""
        logger.info("用户点击扫描按钮")
        self.scan_controller.start_scan()
    
    def on_clean_clicked(self) -> None:
        """处理清理按钮点击"""
        if self.scan_result is None:
            logger.warning("没有扫描结果，无法清理")
            return
        
        # 获取选中的文件
        selected_files = self._get_selected_files()
        
        if not selected_files:
            InfoBar.warning(
                title="提示",
                content="请先选择要清理的文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            logger.info("没有选中文件，取消清理")
            return
        
        logger.info(f"用户点击清理按钮，选中 {len(selected_files)} 个文件")
        self.clean_controller.start_clean(selected_files)
    
    def _on_cancel_clicked(self) -> None:
        """处理取消按钮点击"""
        logger.info("用户点击取消按钮")
        self.scan_controller.cancel_scan()
        self.clean_controller.cancel_clean()
    
    def _on_scan_started(self) -> None:
        """处理扫描开始"""
        logger.info("扫描开始")
        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.cancel_button.show()
        self.progress_ring.show()
        self.status_label.setText("正在扫描...")
        
        # 清空树形列表
        self.tree_widget.clear()
    
    def _on_scan_progress(self, path: str, percentage: int) -> None:
        """处理扫描进度更新"""
        self.status_label.setText(f"正在扫描... {percentage}% - {path}")
    
    def _on_scan_completed(self, result: ScanResult) -> None:
        """处理扫描完成"""
        logger.info(f"收到扫描完成信号，共 {result.total_count} 个文件")
        self.scan_result = result
        
        # 更新 UI
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)
        self.cancel_button.hide()
        self.progress_ring.hide()
        self.status_label.setText(f"扫描完成，发现 {result.total_count} 个文件")
        
        logger.info("开始更新扫描结果显示")
        # 更新扫描结果显示
        self.update_scan_result(result)
        logger.info("扫描结果显示更新完成")
        
        # 显示权限警告
        if result.requires_admin:
            self.show_admin_warning(result.inaccessible_categories)
        
        # 显示完成提示
        InfoBar.success(
            title="扫描完成",
            content=f"发现 {result.total_count} 个文件，共 {self._format_size(result.total_size)}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        logger.info("扫描完成处理结束")
    
    def _on_scan_error(self, error_message: str) -> None:
        """处理扫描错误"""
        logger.error(f"扫描错误: {error_message}")
        self.scan_button.setEnabled(True)
        self.cancel_button.hide()
        self.progress_ring.hide()
        self.status_label.setText(f"扫描失败: {error_message}")
        
        InfoBar.error(
            title="扫描失败",
            content=error_message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
    
    def _on_clean_started(self) -> None:
        """处理清理开始"""
        logger.info("清理开始")
        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.cancel_button.show()
        self.progress_ring.show()
        self.status_label.setText("正在清理...")
    
    def _on_clean_progress(self, file_path: str, percentage: int) -> None:
        """处理清理进度更新"""
        self.status_label.setText(f"正在清理... {percentage}% - {file_path}")
    
    def _on_clean_completed(self, result: CleanResult) -> None:
        """处理清理完成"""
        logger.info("清理完成")
        
        # 更新 UI
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(False)
        self.cancel_button.hide()
        self.progress_ring.hide()
        self.status_label.setText(
            f"清理完成，成功删除 {result.success_count} 个文件，"
            f"释放 {self._format_size(result.freed_space)}"
        )
        
        # 清空扫描结果和树形列表
        self.scan_result = None
        self.tree_widget.clear()
        self._update_stats_cards(0, 0, 0)
        
        # 显示完成提示
        InfoBar.success(
            title="清理完成",
            content=f"成功删除 {result.success_count} 个文件，释放 {self._format_size(result.freed_space)}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
        
        # 如果有失败的文件，显示警告
        if result.failed_count > 0:
            InfoBar.warning(
                title="部分文件清理失败",
                content=f"{result.failed_count} 个文件无法删除",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
    
    def _on_clean_error(self, error_message: str) -> None:
        """处理清理错误"""
        logger.error(f"清理错误: {error_message}")
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)
        self.cancel_button.hide()
        self.progress_ring.hide()
        self.status_label.setText(f"清理失败: {error_message}")
        
        InfoBar.error(
            title="清理失败",
            content=error_message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
    
    def update_scan_result(self, result: ScanResult) -> None:
        """更新扫描结果显示"""
        logger.info(f"开始更新扫描结果，共 {result.total_count} 个文件")
        
        # 更新统计卡片
        self._update_stats_cards(result.total_count, result.total_size, result.total_size)
        
        # 清空树形列表
        self.tree_widget.clear()
        
        # 暂时阻止信号，避免频繁触发
        self.tree_widget.blockSignals(True)
        
        try:
            # 添加类别和文件
            for category, files in result.categories.items():
                if not files:
                    continue
                
                logger.debug(f"添加类别 {category.value}，共 {len(files)} 个文件")
                
                # 创建类别节点
                category_item = QTreeWidgetItem(self.tree_widget)
                category_item.setText(0, category.value)
                category_item.setText(1, self._format_size(sum(f.size for f in files)))
                category_item.setText(2, f"{len(files)} 个文件")
                category_item.setCheckState(0, Qt.Checked)
                category_item.setData(0, Qt.UserRole, category)
                
                # 限制显示的文件数量，避免界面卡顿
                max_display_files = 1000
                display_files = files[:max_display_files]
                
                # 添加文件节点
                for junk_file in display_files:
                    file_item = QTreeWidgetItem(category_item)
                    file_item.setText(0, os.path.basename(junk_file.path))
                    file_item.setText(1, self._format_size(junk_file.size))
                    file_item.setText(2, junk_file.path)
                    file_item.setCheckState(0, Qt.Checked)
                    file_item.setData(0, Qt.UserRole, junk_file)
                
                # 如果文件数超过限制，添加提示节点
                if len(files) > max_display_files:
                    hint_item = QTreeWidgetItem(category_item)
                    hint_item.setText(0, f"... 还有 {len(files) - max_display_files} 个文件未显示")
                    hint_item.setText(1, "")
                    hint_item.setText(2, "所有文件仍会被选中清理")
                    hint_item.setFlags(hint_item.flags() & ~Qt.ItemIsUserCheckable)
            
            # 展开所有节点
            self.tree_widget.expandAll()
            
        finally:
            # 恢复信号
            self.tree_widget.blockSignals(False)
        
        logger.info("扫描结果已更新到树形列表")
    
    def _on_tree_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """处理树形列表项变化"""
        if column != 0:
            return
        
        # 阻止信号递归
        self.tree_widget.blockSignals(True)
        
        # 如果是类别节点，更新所有子节点
        if item.parent() is None:
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, check_state)
        else:
            # 如果是文件节点，检查父节点状态
            parent = item.parent()
            checked_count = sum(
                1 for i in range(parent.childCount())
                if parent.child(i).checkState(0) == Qt.Checked
            )
            
            if checked_count == 0:
                parent.setCheckState(0, Qt.Unchecked)
            elif checked_count == parent.childCount():
                parent.setCheckState(0, Qt.Checked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)
        
        # 恢复信号
        self.tree_widget.blockSignals(False)
        
        # 更新选中大小
        self._update_selected_size()
    
    def _update_selected_size(self) -> None:
        """更新选中文件的总大小"""
        selected_files = self._get_selected_files()
        selected_size = sum(f.size for f in selected_files)
        
        # 更新选中大小卡片
        self.selected_size_label.setText(self._format_size(selected_size))
    
    def _get_selected_files(self) -> List[JunkFile]:
        """获取选中的文件列表"""
        selected_files = []
        
        # 遍历所有类别节点
        for i in range(self.tree_widget.topLevelItemCount()):
            category_item = self.tree_widget.topLevelItem(i)
            
            # 如果类别被选中，获取该类别的所有文件（包括未显示的）
            if category_item.checkState(0) == Qt.Checked:
                category = category_item.data(0, Qt.UserRole)
                if isinstance(category, JunkCategory) and self.scan_result:
                    # 从扫描结果中获取该类别的所有文件
                    category_files = self.scan_result.categories.get(category, [])
                    selected_files.extend(category_files)
            else:
                # 如果类别未完全选中，遍历子节点
                for j in range(category_item.childCount()):
                    file_item = category_item.child(j)
                    
                    # 如果文件被选中，添加到列表
                    if file_item.checkState(0) == Qt.Checked:
                        junk_file = file_item.data(0, Qt.UserRole)
                        if isinstance(junk_file, JunkFile):
                            selected_files.append(junk_file)
        
        return selected_files
    
    def _update_stats_cards(self, file_count: int, total_size: int, selected_size: int) -> None:
        """更新统计卡片"""
        logger.info(f"更新统计卡片: 文件数={file_count}, 总大小={total_size}, 选中大小={selected_size}")
        
        # 更新标签文本
        count_str = str(file_count)
        formatted_total = self._format_size(total_size)
        formatted_selected = self._format_size(selected_size)
        
        self.file_count_label.setText(count_str)
        self.total_size_label.setText(formatted_total)
        self.selected_size_label.setText(formatted_selected)
        
        logger.info(f"标签文本已更新: {count_str}, {formatted_total}, {formatted_selected}")
        
        # 强制重绘标签
        self.file_count_label.repaint()
        self.total_size_label.repaint()
        self.selected_size_label.repaint()
        
        # 强制重绘卡片
        self.file_count_card.repaint()
        self.total_size_card.repaint()
        self.selected_size_card.repaint()
        
        logger.info("卡片和标签已强制重绘")
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"
