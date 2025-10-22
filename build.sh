#!/bin/bash
# WebP图片转换器 - macOS/Linux 一键打包脚本

echo "🚀 开始打包 WebP图片转换器..."
echo ""

# 激活虚拟环境(如果存在)
if [ -d "venv" ]; then
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
fi

# 安装依赖
echo "📥 检查依赖..."
pip install -q pyinstaller pillow

# 执行打包
echo "🔨 开始打包..."
python3 build.py

echo ""
echo "✅ 打包完成！"
echo "📁 输出目录: dist/"
