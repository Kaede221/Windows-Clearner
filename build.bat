@echo off
chcp 65001 >nul
echo ========================================
echo Windows 垃圾文件清理工具 - 打包脚本
echo ========================================
echo.

REM 检查是否安装了 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller
    echo 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
)

echo [1/4] 转换图标文件...
if not exist icon.ico (
    echo 正在将 SVG 转换为 ICO 格式...
    python convert_icon.py
    if errorlevel 1 (
        echo [警告] 图标转换失败，将使用默认图标
    )
) else (
    echo icon.ico 已存在，跳过转换
)
echo 完成

echo.
echo [2/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo 完成

echo.
echo [3/4] 开始打包程序...
pyinstaller --clean build_exe.spec
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)
echo 完成

echo.
echo [4/4] 打包完成！
echo 生成的 exe 文件位于: dist\WindowsCleaner.exe
echo.
echo ========================================
echo 打包成功！
echo ========================================
pause
