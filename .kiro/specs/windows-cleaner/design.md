# 设计文档：Windows 垃圾文件清理工具

## 概述

Windows 垃圾文件清理工具是一个基于 Python 和 PySide6 的桌面应用程序，采用 PyQt-Fluent-Widgets 组件库实现现代化的 Fluent Design 风格界面。应用程序采用 MVC（Model-View-Controller）架构模式，将业务逻辑、数据模型和用户界面分离，确保代码的可维护性和可扩展性。

核心功能包括：
- 扫描 Windows 系统中的多种类型垃圾文件
- 提供可视化的分类展示和选择性清理
- 安全的文件删除机制，避免误删系统关键文件
- 详细的清理报告和错误处理

## 架构

### 整体架构

应用程序采用三层架构：

```
┌─────────────────────────────────────┐
│      表示层 (Presentation)          │
│   - MainWindow (主窗口)             │
│   - ScanProgressView (扫描进度)     │
│   - CleanResultView (清理结果)      │
│   - SettingsView (设置界面)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      业务逻辑层 (Business Logic)     │
│   - ScanController (扫描控制器)     │
│   - CleanController (清理控制器)    │
│   - ConfigManager (配置管理器)      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      数据层 (Data)                   │
│   - JunkScanner (垃圾扫描器)        │
│   - JunkCleaner (垃圾清理器)        │
│   - FileSystemAccess (文件系统访问) │
└─────────────────────────────────────┘
```

### 技术栈

- **UI 框架**: PySide6 (Qt for Python)
- **UI 组件库**: PyQt-Fluent-Widgets (Fluent Design 风格)
- **配置存储**: JSON 文件
- **日志**: Python logging 模块
- **异步处理**: QThread (Qt 线程)

## 组件和接口

### 1. 数据层组件

#### 1.1 JunkCategory (垃圾类别枚举)

```python
class JunkCategory(Enum):
    TEMP_FILES = "系统临时文件"
    WINDOWS_UPDATE_CACHE = "Windows 更新缓存"
    RECYCLE_BIN = "回收站"
    BROWSER_CACHE = "浏览器缓存"
    THUMBNAIL_CACHE = "缩略图缓存"
    CUSTOM = "自定义路径"
```

#### 1.2 JunkFile (垃圾文件数据类)

```python
@dataclass
class JunkFile:
    path: str
    size: int
    category: JunkCategory
    can_delete: bool
    error_message: Optional[str] = None
```

#### 1.3 ScanResult (扫描结果数据类)

```python
@dataclass
class ScanResult:
    categories: Dict[JunkCategory, List[JunkFile]]
    total_size: int
    total_count: int
    scan_duration: float
    errors: List[str]
    requires_admin: bool  # 是否有类别因权限不足而未完全扫描
    inaccessible_categories: List[JunkCategory]  # 无法访问的类别列表
```

#### 1.4 CleanResult (清理结果数据类)

```python
@dataclass
class CleanResult:
    success_count: int
    failed_count: int
    freed_space: int
    failed_files: List[Tuple[str, str]]  # (path, error_reason)
    clean_duration: float
```

#### 1.5 JunkScanner (垃圾扫描器)

负责扫描系统中的垃圾文件，处理权限问题。

```python
class JunkScanner:
    def __init__(self, config: ScanConfig):
        self.config = config
        self.category_scanners = self._init_category_scanners()
        self.has_admin = FileSystemAccess.has_admin_privileges()
    
    def scan(self, progress_callback: Callable[[str, int], None]) -> ScanResult:
        """
        扫描所有启用的垃圾类别
        
        Args:
            progress_callback: 进度回调函数 (current_path, percentage)
        
        Returns:
            ScanResult: 扫描结果，包含权限警告信息
        """
        pass
    
    def scan_category(self, category: JunkCategory) -> List[JunkFile]:
        """
        扫描特定类别的垃圾文件
        
        对于需要管理员权限的路径：
        - 如果有管理员权限：正常扫描
        - 如果没有管理员权限：跳过并记录警告
        """
        pass
    
    def get_inaccessible_categories(self) -> List[JunkCategory]:
        """
        返回由于权限不足而无法完全扫描的类别列表
        """
        pass
```

**类别扫描器映射**:
- `TempFilesScanner`: 扫描 %TEMP%, %TMP%, C:\Windows\Temp (需要管理员权限)
- `WindowsUpdateScanner`: 扫描 C:\Windows\SoftwareDistribution\Download (需要管理员权限)
- `RecycleBinScanner`: 扫描回收站
- `BrowserCacheScanner`: 扫描常见浏览器缓存目录
- `ThumbnailCacheScanner`: 扫描 %LocalAppData%\Microsoft\Windows\Explorer

#### 1.6 JunkCleaner (垃圾清理器)

负责删除选定的垃圾文件。

```python
class JunkCleaner:
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
        pass
    
    def safe_delete(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        安全删除单个文件
        
        Returns:
            (success, error_message)
        """
        pass
```

#### 1.7 FileSystemAccess (文件系统访问)

提供文件系统操作的抽象层，处理权限相关的问题。

```python
class FileSystemAccess:
    @staticmethod
    def is_file_in_use(file_path: str) -> bool:
        """检查文件是否正在被使用"""
        pass
    
    @staticmethod
    def has_admin_privileges() -> bool:
        """
        检查是否有管理员权限
        在 Windows 上使用 ctypes.windll.shell32.IsUserAnAdmin()
        """
        pass
    
    @staticmethod
    def requires_admin_access(path: str) -> bool:
        """
        检查路径是否需要管理员权限才能访问
        例如：C:\Windows\SoftwareDistribution, C:\Windows\Temp 等
        """
        pass
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小（字节）
        如果权限不足，返回 0 并记录警告
        """
        pass
    
    @staticmethod
    def is_safe_to_delete(file_path: str) -> bool:
        """检查文件是否安全删除"""
        pass
    
    @staticmethod
    def can_access_path(path: str) -> bool:
        """
        检查是否可以访问指定路径
        考虑当前权限级别
        """
        pass
```

### 2. 业务逻辑层组件

#### 2.1 ScanConfig (扫描配置)

```python
@dataclass
class ScanConfig:
    enabled_categories: Set[JunkCategory]
    excluded_paths: List[str]
    custom_patterns: List[str]
    max_file_age_days: Optional[int] = None
```

#### 2.2 AppConfig (应用配置)

```python
@dataclass
class AppConfig:
    scan_config: ScanConfig
    ui_theme: str = "light"
    language: str = "zh_CN"
    auto_check_updates: bool = True
```

#### 2.3 ConfigManager (配置管理器)

```python
class ConfigManager:
    CONFIG_FILE = "config.json"
    
    def load_config(self) -> AppConfig:
        """从文件加载配置"""
        pass
    
    def save_config(self, config: AppConfig) -> None:
        """保存配置到文件"""
        pass
    
    def get_default_config(self) -> AppConfig:
        """获取默认配置"""
        pass
```

#### 2.4 ScanController (扫描控制器)

```python
class ScanController(QObject):
    # Qt 信号
    scan_started = Signal()
    scan_progress = Signal(str, int)  # (current_path, percentage)
    scan_completed = Signal(ScanResult)
    scan_error = Signal(str)
    
    def __init__(self, scanner: JunkScanner):
        self.scanner = scanner
        self.scan_thread = None
    
    def start_scan(self) -> None:
        """在后台线程启动扫描"""
        pass
    
    def cancel_scan(self) -> None:
        """取消正在进行的扫描"""
        pass
```

#### 2.5 CleanController (清理控制器)

```python
class CleanController(QObject):
    # Qt 信号
    clean_started = Signal()
    clean_progress = Signal(str, int)  # (current_file, percentage)
    clean_completed = Signal(CleanResult)
    clean_error = Signal(str)
    
    def __init__(self, cleaner: JunkCleaner):
        self.cleaner = cleaner
        self.clean_thread = None
    
    def start_clean(self, files: List[JunkFile]) -> None:
        """在后台线程启动清理"""
        pass
    
    def cancel_clean(self) -> None:
        """取消正在进行的清理"""
        pass
```

### 3. 表示层组件

#### 3.1 MainWindow (主窗口)

使用 PyQt-Fluent-Widgets 的 FluentWindow 作为基础。

```python
class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.scan_controller = ScanController(JunkScanner(config))
        self.clean_controller = CleanController(JunkCleaner())
        self.scan_result = None
        self.has_admin = FileSystemAccess.has_admin_privileges()
        
        self._init_ui()
        self._connect_signals()
        self._check_admin_privileges()
    
    def _init_ui(self) -> None:
        """初始化 UI 组件"""
        # 使用 Fluent 组件：
        # - PrimaryPushButton (开始扫描按钮)
        # - TreeWidget (垃圾类别树)
        # - ProgressRing (进度指示器)
        # - CardWidget (统计卡片)
        # - InfoBar (权限警告提示)
        pass
    
    def _check_admin_privileges(self) -> None:
        """
        检查管理员权限并显示警告
        如果没有管理员权限，显示 InfoBar 提示用户某些文件可能无法清理
        """
        pass
    
    def show_admin_warning(self, inaccessible_categories: List[JunkCategory]) -> None:
        """
        显示权限警告，列出无法访问的类别
        提供"以管理员身份重新启动"按钮
        """
        pass
    
    def restart_as_admin(self) -> None:
        """
        以管理员权限重新启动应用程序
        使用 ctypes.windll.shell32.ShellExecuteW 和 "runas" 动词
        """
        pass
    
    def on_scan_clicked(self) -> None:
        """处理扫描按钮点击"""
        pass
    
    def on_clean_clicked(self) -> None:
        """处理清理按钮点击"""
        pass
    
    def update_scan_result(self, result: ScanResult) -> None:
        """
        更新扫描结果显示
        如果 result.requires_admin 为 True，显示权限警告
        """
        pass
```

#### 3.2 ScanProgressDialog (扫描进度对话框)

```python
class ScanProgressDialog(MessageBox):
    def __init__(self, parent=None):
        super().__init__("扫描中", "", parent)
        self.progress_bar = ProgressBar()
        self.status_label = BodyLabel()
        
    def update_progress(self, path: str, percentage: int) -> None:
        """更新进度显示"""
        pass
```

#### 3.3 CleanResultDialog (清理结果对话框)

```python
class CleanResultDialog(MessageBox):
    def __init__(self, result: CleanResult, parent=None):
        super().__init__("清理完成", "", parent)
        self._display_result(result)
    
    def _display_result(self, result: CleanResult) -> None:
        """显示清理结果"""
        pass
    
    def export_report(self) -> None:
        """导出清理报告"""
        pass
```

#### 3.4 SettingsDialog (设置对话框)

```python
class SettingsDialog(Dialog):
    def __init__(self, config: AppConfig, parent=None):
        super().__init__("设置", "", parent)
        self.config = config
        self._init_ui()
    
    def _init_ui(self) -> None:
        """初始化设置界面"""
        # - SwitchButton (类别启用开关)
        # - LineEdit (自定义路径输入)
        # - ComboBox (主题选择)
        pass
    
    def save_settings(self) -> AppConfig:
        """保存并返回更新后的配置"""
        pass
```

## 数据模型

### 配置文件格式 (config.json)

```json
{
  "scan_config": {
    "enabled_categories": [
      "TEMP_FILES",
      "WINDOWS_UPDATE_CACHE",
      "RECYCLE_BIN",
      "BROWSER_CACHE",
      "THUMBNAIL_CACHE"
    ],
    "excluded_paths": [
      "C:\\Important\\Folder"
    ],
    "custom_patterns": [
      "*.tmp",
      "*.log"
    ],
    "max_file_age_days": null
  },
  "ui_theme": "light",
  "language": "zh_CN",
  "auto_check_updates": true
}
```

### 日志文件格式

使用 Python logging 模块，日志文件保存在应用程序目录下的 `logs/` 文件夹。

```
2024-01-15 10:30:45 - INFO - 开始扫描垃圾文件
2024-01-15 10:30:46 - INFO - 扫描类别: 系统临时文件
2024-01-15 10:30:47 - WARNING - 无法访问文件: C:\Windows\Temp\locked.tmp (权限不足)
2024-01-15 10:31:00 - INFO - 扫描完成，发现 1523 个文件，共 2.3 GB
2024-01-15 10:31:15 - INFO - 开始清理
2024-01-15 10:31:20 - ERROR - 删除失败: C:\Temp\inuse.tmp (文件正在使用中)
2024-01-15 10:31:45 - INFO - 清理完成，成功删除 1520 个文件，释放 2.29 GB
```


## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1：扫描结果按类别分组

*对于任何*扫描操作，返回的扫描结果中的所有垃圾文件都应该根据其类别正确分组，且每个文件只出现在一个类别中。

**验证需求：需求 1.1**

### 属性 2：扫描进度回调被调用

*对于任何*扫描操作，进度回调函数应该在扫描过程中被调用至少一次，且进度百分比应该是单调递增的（0 到 100）。

**验证需求：需求 1.2**

### 属性 3：扫描结果统计信息完整性

*对于任何*扫描结果，total_count 应该等于所有类别中文件数量的总和，total_size 应该等于所有类别中文件大小的总和。

**验证需求：需求 1.3**

### 属性 4：错误处理不中断操作

*对于任何*包含无法访问文件的扫描或清理操作，系统应该记录错误信息并继续处理其他文件，而不是中止整个操作。

**验证需求：需求 1.4, 3.3**

### 属性 5：选择文件的总大小计算正确

*对于任何*文件选择状态，待清理文件的总大小应该精确等于所有被选中文件的大小之和。

**验证需求：需求 2.2**

### 属性 6：仅清理选中的文件

*对于任何*文件选择和清理操作，清理器应该只尝试删除被选中的文件，未选中的文件应该保持不变。

**验证需求：需求 2.4**

### 属性 7：扫描结果仅包含安全文件

*对于任何*扫描结果，所有识别的垃圾文件都应该匹配预定义的安全路径模式，且不应该包含用户文档目录、程序文件目录或系统关键目录中的文件。

**验证需求：需求 3.1, 3.5**

### 属性 8：跳过被占用的文件

*对于任何*清理操作，如果文件正在被其他进程使用，清理器应该跳过该文件并在清理结果的 failed_files 列表中记录该文件及原因。

**验证需求：需求 3.2**

### 属性 9：清理结果统计信息完整性

*对于任何*清理操作，清理结果应该包含 success_count（成功删除数量）、failed_count（失败数量）、freed_space（释放空间）和 failed_files（失败文件列表），且 success_count + failed_count 应该等于尝试清理的文件总数。

**验证需求：需求 3.4, 5.1, 5.2, 5.3**

### 属性 10：配置往返一致性

*对于任何*有效的应用配置对象，将其保存到文件后再加载，应该得到一个等价的配置对象（所有字段值相同）。

**验证需求：需求 6.4, 6.5**

### 属性 11：权限不足时记录错误

*对于任何*需要管理员权限但当前权限不足的文件清理操作，系统应该在清理结果中记录该文件及权限相关的错误信息。

**验证需求：需求 7.3**

### 属性 12：错误记录到日志文件

*对于任何*扫描或清理过程中发生的错误，系统应该将错误详情（包括时间戳、错误类型、文件路径）记录到日志文件中。

**验证需求：需求 8.1**

### 属性 13：清理报告导出完整性

*对于任何*清理结果，导出的文本报告应该包含所有关键信息：成功删除数量、失败数量、释放空间、失败文件列表及原因。

**验证需求：需求 5.5**

## 错误处理

### 错误类型

应用程序需要处理以下类型的错误：

1. **文件访问错误**
   - 权限不足（PermissionError）
   - 文件不存在（FileNotFoundError）
   - 文件被占用（OSError with errno 32）
   - 路径过长（OSError with errno 206）

2. **配置错误**
   - 配置文件损坏（JSONDecodeError）
   - 配置文件缺失（使用默认配置）
   - 无效的配置值（ValidationError）

3. **系统错误**
   - 磁盘空间不足（OSError with errno 28）
   - 磁盘 I/O 错误（IOError）
   - 内存不足（MemoryError）

### 错误处理策略

#### 1. 扫描阶段错误处理

```python
try:
    # 检查路径是否需要管理员权限
    if FileSystemAccess.requires_admin_access(file_path):
        if not self.has_admin:
            errors.append(f"需要管理员权限: {file_path}")
            logger.warning(f"跳过需要管理员权限的路径: {file_path}")
            return
    
    # 检查是否可以访问路径
    if not FileSystemAccess.can_access_path(file_path):
        errors.append(f"无法访问: {file_path}")
        logger.warning(f"无法访问路径: {file_path}")
        return
    
    file_size = os.path.getsize(file_path)
    junk_files.append(JunkFile(path=file_path, size=file_size, ...))
except PermissionError:
    errors.append(f"权限不足: {file_path}")
    logger.warning(f"无法访问文件: {file_path} (权限不足)")
except FileNotFoundError:
    # 文件可能在扫描过程中被删除，忽略
    pass
except Exception as e:
    errors.append(f"未知错误: {file_path} - {str(e)}")
    logger.error(f"扫描文件时出错: {file_path}", exc_info=True)
```

#### 2. 清理阶段错误处理

```python
try:
    os.remove(file_path)
    success_count += 1
    freed_space += file_size
except PermissionError:
    failed_files.append((file_path, "权限不足"))
    logger.warning(f"无法删除文件: {file_path} (权限不足)")
except OSError as e:
    if e.errno == 32:  # 文件被占用
        failed_files.append((file_path, "文件正在使用中"))
    else:
        failed_files.append((file_path, f"系统错误: {e}"))
    logger.error(f"删除文件失败: {file_path}", exc_info=True)
```

#### 3. 配置加载错误处理

```python
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)
    return AppConfig.from_dict(config_dict)
except FileNotFoundError:
    logger.info("配置文件不存在，使用默认配置")
    return self.get_default_config()
except json.JSONDecodeError:
    logger.error("配置文件格式错误，使用默认配置")
    return self.get_default_config()
```

#### 4. UI 错误反馈

- 非关键错误：在状态栏显示警告消息
- 关键错误：显示 MessageBox 对话框
- 所有错误：记录到日志文件

### 错误恢复机制

1. **扫描中断恢复**：扫描可以随时取消，不影响系统状态
2. **清理中断恢复**：清理过程中取消，已删除的文件不会恢复，未处理的文件保持原状
3. **配置损坏恢复**：自动回退到默认配置
4. **日志文件过大**：自动轮转，保留最近 10 个日志文件

## 测试策略

### 双重测试方法

应用程序将采用单元测试和基于属性的测试相结合的方法：

- **单元测试**：验证特定示例、边缘情况和错误条件
- **属性测试**：验证跨所有输入的通用属性

两者是互补的，对于全面覆盖都是必要的。单元测试捕获具体的错误，属性测试验证一般正确性。

### 单元测试

单元测试应该专注于：
- 特定示例，展示正确行为
- 组件之间的集成点
- 边缘情况和错误条件

避免编写过多的单元测试 - 基于属性的测试会处理大量输入的覆盖。

**测试框架**：pytest

**示例单元测试**：

```python
def test_temp_files_scanner_finds_temp_directory():
    """测试临时文件扫描器能找到 TEMP 目录中的文件"""
    scanner = TempFilesScanner()
    files = scanner.scan()
    assert len(files) > 0
    assert all(file.category == JunkCategory.TEMP_FILES for file in files)

def test_cleaner_skips_file_in_use():
    """测试清理器跳过正在使用的文件"""
    # 创建并打开一个测试文件
    with open("test_locked.tmp", "w") as f:
        f.write("test")
        cleaner = JunkCleaner()
        result = cleaner.safe_delete("test_locked.tmp")
        assert result[0] is False
        assert "使用中" in result[1]

def test_config_manager_creates_default_config():
    """测试配置管理器在文件不存在时创建默认配置"""
    manager = ConfigManager()
    config = manager.load_config()
    assert config is not None
    assert len(config.scan_config.enabled_categories) == 5
```

### 基于属性的测试

**测试库**：Hypothesis (Python 的属性测试库)

**配置**：每个属性测试最少运行 100 次迭代

**标签格式**：每个测试必须用注释引用设计文档属性
```python
# Feature: windows-cleaner, Property 1: 扫描结果按类别分组
```

**属性测试实现**：

每个正确性属性必须由一个单独的基于属性的测试实现。

```python
from hypothesis import given, strategies as st

# Feature: windows-cleaner, Property 1: 扫描结果按类别分组
@given(st.lists(st.builds(JunkFile, ...)))
def test_scan_result_groups_by_category(files):
    """属性 1：扫描结果按类别分组"""
    result = ScanResult.from_files(files)
    
    # 验证每个文件只出现在一个类别中
    all_files_in_result = []
    for category_files in result.categories.values():
        all_files_in_result.extend(category_files)
    
    assert len(all_files_in_result) == len(set(f.path for f in all_files_in_result))
    
    # 验证每个类别中的文件都属于该类别
    for category, category_files in result.categories.items():
        assert all(f.category == category for f in category_files)

# Feature: windows-cleaner, Property 3: 扫描结果统计信息完整性
@given(st.lists(st.builds(JunkFile, ...)))
def test_scan_result_statistics_integrity(files):
    """属性 3：扫描结果统计信息完整性"""
    result = ScanResult.from_files(files)
    
    total_count = sum(len(files) for files in result.categories.values())
    total_size = sum(f.size for files in result.categories.values() for f in files)
    
    assert result.total_count == total_count
    assert result.total_size == total_size

# Feature: windows-cleaner, Property 10: 配置往返一致性
@given(st.builds(AppConfig, ...))
def test_config_round_trip(config):
    """属性 10：配置往返一致性"""
    manager = ConfigManager()
    
    # 保存配置
    manager.save_config(config)
    
    # 加载配置
    loaded_config = manager.load_config()
    
    # 验证配置相同
    assert loaded_config == config
```

### 测试覆盖目标

- 代码覆盖率：> 80%
- 属性测试：所有 13 个正确性属性都必须实现
- 单元测试：至少覆盖每个组件的核心功能和错误处理
- 集成测试：测试扫描 → 选择 → 清理的完整流程

### 测试环境

- **操作系统**：Windows 10/11
- **Python 版本**：3.8+
- **依赖项**：PySide6, PyQt-Fluent-Widgets, pytest, hypothesis
- **测试数据**：使用临时目录创建测试文件，测试后清理

### 持续集成

- 每次提交前运行所有测试
- 使用 GitHub Actions 或类似 CI 工具
- 测试失败时阻止合并
