# Windows 垃圾文件清理工具

一个基于 PySide6 和 PyQt-Fluent-Widgets 的 Windows 垃圾文件清理工具。

## 功能特性

- 扫描多种类型的垃圾文件：
  - 系统临时文件
  - Windows 更新缓存
  - 回收站
  - 浏览器缓存（Chrome、Edge、Firefox）
  - 缩略图缓存
- 自动请求管理员权限
- 多线程扫描和清理，不阻塞界面
- 现代化的 Fluent Design 界面
- 详细的日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

### 方式一：双击运行（无控制台窗口）

直接双击 `main.pyw` 文件即可启动程序，不会显示黑色控制台窗口。

### 方式二：命令行运行（查看日志）

在命令行中运行可以看到实时日志输出：

```bash
python main.py
```

## 日志文件

程序运行日志保存在 `logs/app.log` 文件中，可以查看详细的运行信息。

## 注意事项

1. 首次运行会弹出 UAC 提示，请求管理员权限
2. 如果拒绝管理员权限，程序会以普通权限运行，但某些系统目录无法清理
3. 扫描大目录时可能需要一些时间，请耐心等待
4. 清理前请仔细检查要删除的文件，避免误删重要数据

## 项目结构

```
.
├── main.py              # 主入口（用于命令行调试）
├── main.pyw             # 主入口（双击运行，无控制台）
├── requirements.txt     # 依赖列表
├── src/
│   ├── ui/             # 界面模块
│   ├── scanner.py      # 扫描器
│   ├── cleaner.py      # 清理器
│   ├── controllers.py  # 控制器（多线程）
│   ├── models.py       # 数据模型
│   ├── file_system.py  # 文件系统访问
│   ├── logger.py       # 日志配置
│   └── ...
├── logs/               # 日志目录
└── tests/              # 测试文件
```

## 开发说明

- 使用 PySide6 作为 GUI 框架
- 使用 PyQt-Fluent-Widgets 实现 Fluent Design 风格
- 使用 QThread 实现多线程扫描和清理
- 遵循 MVC 架构模式

## 许可证

MIT License
