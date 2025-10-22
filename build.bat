@echo off
REM WebP图片转换器 - Windows 一键打包脚本

echo 🚀 开始打包 WebP图片转换器...
echo.

REM 激活虚拟环境(如果存在)
if exist venv\Scripts\activate.bat (
    echo 📦 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 安装依赖
echo 📥 检查依赖...
pip install -q pyinstaller pillow

REM 执行打包
echo 🔨 开始打包...
python build.py

echo.
echo ✅ 打包完成！
echo 📁 输出目录: dist\
pause
