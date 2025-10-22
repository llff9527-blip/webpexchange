#!/bin/bash
# 使用Docker打包Windows应用（在Mac/Linux上）

echo "🐳 使用 Docker 打包 Windows 应用..."
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

# 构建Docker镜像
echo "📦 构建 Docker 镜像..."
docker build -f Dockerfile.windows -t webp-builder-windows .

# 运行容器并打包
echo "🔨 开始打包..."
docker run --rm -v "$(pwd)/dist:/app/dist" webp-builder-windows

echo ""
echo "✅ 打包完成！"
echo "📁 输出目录: dist/"
