<div align="center">

# 🧹 Windows 垃圾文件清理工具

<img src="icon.svg" alt="Logo" width="120" height="120">

**一款现代化、高效的 Windows 系统垃圾清理工具**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6.0+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用说明](#-使用说明) • [截图展示](#-截图展示) • [支持项目](#-支持项目)

</div>

---

## ✨ 功能特性

- 🎨 **现代化界面** - 基于 Fluent Design 设计语言，美观易用
- 🚀 **高效清理** - 快速扫描并清理系统垃圾文件
- 🔍 **智能分类** - 自动识别并分类不同类型的垃圾文件
- 🛡️ **安全可靠** - 管理员权限运行，确保清理效果
- 🌙 **深色模式** - 支持亮色/深色主题切换
- 📊 **详细报告** - 清晰展示清理前后的空间变化
- ⚙️ **自定义配置** - 支持自定义扫描路径和清理规则
- 🔄 **自动更新** - 内置更新检查功能

## 🚀 快速开始

### 环境要求

- Windows 10/11
- Python 3.8 或更高版本
- 管理员权限（用于清理系统文件）

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone https://github.com/Kaede221/Windows-Clearner.git
   cd Windows-Clearner
   ```

2. **创建虚拟环境**（推荐）

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

### 打包为可执行文件

使用 PyInstaller 打包为独立的 .exe 文件.

```bash
pyinstaller --noconsole --onefile --name="WindowsCleaner" --icon="icon.ico" --add-data="icon.svg;." --collect-all=qfluentwidgets main.py
```

打包后的文件位于 `dist` 目录中。

## 📖 使用说明

### 基本操作

1. **启动程序** - 以管理员身份运行程序（程序会自动请求权限）
2. **扫描垃圾** - 点击"开始扫描"按钮，等待扫描完成
3. **查看结果** - 查看扫描到的垃圾文件分类和大小
4. **清理文件** - 选择要清理的类别，点击"开始清理"
5. **查看报告** - 清理完成后查看详细的清理报告

### 高级功能

- **自定义扫描路径** - 在设置中添加自定义文件夹进行扫描
- **主题切换** - 支持亮色/深色主题，自动适应系统设置
- **自动更新** - 程序会自动检查并提示可用更新

### 清理类别

程序支持清理以下类型的垃圾文件：

- 🗑️ 临时文件
- 🌐 浏览器缓存
- 📦 系统缓存
- 🔄 更新残留
- 📝 日志文件
- 🎮 游戏缓存
- 💾 回收站

</div>

## 🛠️ 技术栈

- **UI 框架**: PySide6 (Qt for Python)
- **设计系统**: QFluentWidgets (Fluent Design)
- **系统交互**: psutil
- **测试框架**: pytest, hypothesis
- **打包工具**: PyInstaller

## 📁 项目结构

```
windows-cleaner/
├── src/                    # 源代码目录
│   ├── ui/                # UI 组件
│   ├── scanner.py         # 文件扫描器
│   ├── cleaner.py         # 文件清理器
│   ├── models.py          # 数据模型
│   └── ...
├── config/                # 配置文件
├── logs/                  # 日志文件
├── main.py               # 主程序入口
├── requirements.txt      # 依赖列表
└── build.bat            # 打包脚本
```

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest

# 运行带控制台的调试版本
python main.py
```

## 📝 更新日志

查看 Git Commit 了解版本更新历史。

## ⚠️ 注意事项

- 请在清理前仔细检查要删除的文件
- 建议定期备份重要数据
- 某些系统文件需要管理员权限才能清理
- 清理后可能需要重启某些应用程序

## ☕ 支持项目

如果这个项目对你有帮助，欢迎请我喝杯咖啡！你的支持是我持续开发的动力 ❤️

<div align="center">

### 通过以下方式支持

<table>
  <tr>
    <td align="center">
      <img src="docs/wechat.png" alt="WeChat Pay" width="200"><br>
      <sub><b>微信支付</b></sub>
    </td>
    <td align="center">
      <img src="docs/alipay.jpg" alt="Alipay" width="200"><br>
      <sub><b>支付宝</b></sub>
    </td>
    <td align="center">
      <img src="https://img.shields.io/badge/爱发电-946CE6?style=for-the-badge&logo=lightning&logoColor=white" alt="爱发电"><br>
      <sub><a href="https://afdian.com/a/KaedeShimizu">爱发电支持</a></sub>
    </td>
  </tr>
</table>
    </td>
  </tr>
</table>

### ⭐ Star 历史

如果觉得项目不错，请给个 Star 支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=Kaede221/Windows-Clearner&type=Date)](https://star-history.com/#Kaede221/Windows-Clearner&Date)

</div>

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [问题反馈](https://github.com/Kaede221/Windows-Clearner/issues)
- [功能建议](https://github.com/Kaede221/Windows-Clearner/discussions)
- [PySide6 文档](https://doc.qt.io/qtforpython/)
- [QFluentWidgets 文档](https://qfluentwidgets.com/)

## 👨‍💻 作者

**Kaede221**

- GitHub: [@Kaede221](https://github.com/Kaede221)
- 仓库: [Windows-Clearner](https://github.com/Kaede221/Windows-Clearner)

## 🙏 致谢

- 感谢 [PySide6](https://www.qt.io/qt-for-python) 提供强大的 UI 框架
- 感谢 [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) 提供精美的 Fluent Design 组件
- 感谢所有贡献者和支持者

---

<div align="center">

**如果这个项目帮到了你，别忘了给个 ⭐ Star！**

Made with ❤️ by [Kaede221](https://github.com/Kaede221)

</div>
