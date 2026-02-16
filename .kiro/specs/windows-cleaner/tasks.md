# 实现计划：Windows 垃圾文件清理工具

## 概述

本实现计划将 Windows 垃圾文件清理工具分解为一系列增量开发任务。应用程序使用 Python 和 PySide6 构建，采用 PyQt-Fluent-Widgets 组件库实现现代化界面，遵循 MVC 架构模式。

实现顺序：数据层 → 业务逻辑层 → 表示层，确保每个阶段都有可测试的功能。

## 任务

- [x] 1. 搭建项目结构和核心基础设施
  - 创建项目目录结构：`src/`, `tests/`, `logs/`, `config/`
  - 创建 `requirements.txt`，包含依赖：PySide6, PyQt-Fluent-Widgets, pytest, hypothesis
  - 配置 Python logging 模块，日志输出到 `logs/` 目录
  - 创建 `src/__init__.py` 和主要模块文件
  - _需求：8.1_

- [x] 2. 实现数据模型和枚举
  - 实现 `JunkCategory` 枚举（5 个类别）
  - 实现 `JunkFile` 数据类
  - 实现 `ScanResult` 数据类（包含 `requires_admin` 和 `inaccessible_categories` 字段）
  - 实现 `CleanResult` 数据类
  - 实现 `ScanConfig` 和 `AppConfig` 数据类
  - _需求：1.5, 3.4, 6.4_

- [x] 3. 实现文件系统访问层
  - 实现 `has_admin_privileges()` 方法（使用 ctypes.windll.shell32.IsUserAnAdmin()）
  - 实现 `requires_admin_access()` 方法（检查路径是否需要管理员权限）
  - 实现 `can_access_path()` 方法（检查路径访问权限）
  - 实现 `is_file_in_use()` 方法（检测文件占用状态）
  - 实现 `get_file_size()` 方法（安全获取文件大小）
  - 实现 `is_safe_to_delete()` 方法（验证文件是否在安全删除列表中）
  - _需求：3.1, 3.5, 7.1, 7.3_

- [x] 4. 实现垃圾文件扫描器
  - 创建 `JunkScanner` 基类，包含权限检查逻辑
  - 实现 `scan()` 方法框架，支持进度回调
  - 实现 `get_inaccessible_categories()` 方法
  - 实现 `TempFilesScanner`（扫描 %TEMP%, %TMP%, C:\Windows\Temp）
  - 实现 `WindowsUpdateScanner`（扫描 C:\Windows\SoftwareDistribution\Download）
  - 实现 `RecycleBinScanner`（扫描回收站）
  - 实现 `BrowserCacheScanner`（扫描浏览器缓存）
  - 实现 `ThumbnailCacheScanner`（扫描缩略图缓存）
  - 每个扫描器都要处理权限不足的情况
  - _需求：1.1, 1.2, 1.5, 7.1, 7.3_

- [x] 5. 实现垃圾文件清理器
  - 实现 `clean()` 方法，支持进度回调
  - 实现 `safe_delete()` 方法，处理文件占用和权限问题
  - 实现错误记录和统计逻辑
  - _需求：2.4, 3.2, 3.3, 3.4_

- [x] 6. 实现配置管理
  - 实现 `load_config()` 方法（从 JSON 文件加载）
  - 实现 `save_config()` 方法（保存到 JSON 文件）
  - 实现 `get_default_config()` 方法
  - 处理配置文件损坏的情况（回退到默认配置）
  - _需求：6.4, 6.5_

- [x] 7. 实现业务逻辑控制器
  - 实现 ScanController 类
    - 继承 QObject，定义 Qt 信号（scan_started, scan_progress, scan_completed, scan_error）
    - 实现 `start_scan()` 方法（在 QThread 中运行扫描）
    - 实现 `cancel_scan()` 方法
    - 连接扫描器的进度回调到 Qt 信号
  - 实现 CleanController 类
    - 继承 QObject，定义 Qt 信号（clean_started, clean_progress, clean_completed, clean_error）
    - 实现 `start_clean()` 方法（在 QThread 中运行清理）
    - 实现 `cancel_clean()` 方法
    - 连接清理器的进度回调到 Qt 信号
  - _需求：1.1, 1.2, 2.4, 3.2_

- [x] 8. 实现主窗口 UI
  - 创建 MainWindow 基础结构（继承 FluentWindow）
  - 初始化扫描和清理控制器
  - 检查管理员权限并存储状态
  - 实现主界面布局（统计卡片、树形列表、操作按钮）
  - 实现扫描功能集成（启动扫描、更新结果、显示进度）
  - 实现清理功能集成（启动清理、文件选择、显示进度）
  - 实现管理员权限处理（权限检查、警告显示、重启功能）
  - _需求：1.1, 1.2, 1.3, 2.1, 2.2, 2.4, 4.1, 4.2, 4.4, 7.1, 7.2, 7.4_

- [ ] 9. 实现扫描进度对话框
  - 创建 ScanProgressDialog 类（继承 MessageBox）
  - 添加 ProgressBar 和状态标签
  - 实现 `update_progress()` 方法
  - 添加"取消"按钮，连接到 ScanController.cancel_scan()
  - _需求：4.3_

- [ ] 10. 实现清理结果对话框
  - 创建 CleanResultDialog 类（继承 MessageBox）
  - 实现 `_display_result()` 方法（显示统计信息）
  - 显示成功数量、失败数量、释放空间
  - 提供"查看失败文件"按钮（如果有失败项）
  - 实现 `export_report()` 方法（导出为文本文件）
  - _需求：4.6, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 11. 实现设置对话框
  - 创建 SettingsDialog 类（继承 Dialog）
  - 添加类别启用/禁用开关（使用 SwitchButton）
  - 添加排除路径列表编辑器
  - 添加自定义路径模式输入（使用 LineEdit）
  - 添加主题选择（使用 ComboBox）
  - 实现 `save_settings()` 方法，返回更新后的配置
  - _需求：6.1, 6.2, 6.3_

- [ ] 12. 集成和应用程序入口
  - 连接主窗口和设置对话框
  - 在主窗口添加"设置"菜单项
  - 实现设置对话框的打开和配置更新
  - 创建 `main.py`，初始化 QApplication
  - 加载配置，创建并显示 MainWindow
  - 设置应用程序图标和样式
  - _需求：4.1, 4.2, 6.1, 6.4_

## 注意事项

- 每个任务都引用了具体的需求，确保可追溯性
- 所有测试由用户手动进行，无需编写自动化测试
- 实现顺序：数据层 → 业务逻辑层 → 表示层
- 重点关注核心功能的实现和用户体验
