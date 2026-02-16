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
   git clone https://github.com/yourusername/windows-cleaner.git
   cd windows-cleaner
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

使用 PyInstaller 打包为独立的 .exe 文件：

```bash
build.bat
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

