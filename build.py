#!/usr/bin/env python3
"""
WebP图片转换器 - 一键打包脚本

支持平台:
- macOS: 生成 .app 应用
- Windows: 生成 .exe 可执行文件

使用方法:
    python build.py              # 自动检测平台并打包
    python build.py --platform mac    # 指定打包Mac版本
    python build.py --platform windows # 指定打包Windows版本
    python build.py --clean      # 清理构建文件
"""

import os
import sys
import shutil
import platform
import argparse
import subprocess
from pathlib import Path

# 项目配置
PROJECT_NAME = "WebP图片转换器"
APP_NAME = "WebPConverter"
VERSION = "1.0.0"
AUTHOR = "Your Name"
MAIN_SCRIPT = "src/main.py"

# 路径配置
PROJECT_ROOT = Path(__file__).parent.absolute()
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_DIR = PROJECT_ROOT


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(message):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_info(message):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_success(message):
    """打印成功消息"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_warning(message):
    """打印警告"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_error(message):
    """打印错误"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def detect_platform():
    """检测当前平台"""
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def check_dependencies():
    """检查构建依赖"""
    print_info("检查构建依赖...")

    # 检查 PyInstaller
    try:
        import PyInstaller
        print_success(f"PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print_error("PyInstaller 未安装")
        print_info("正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print_success("PyInstaller 安装完成")

    # 检查 Pillow
    try:
        import PIL
        print_success(f"Pillow 已安装 (版本: {PIL.__version__})")
    except ImportError:
        print_error("Pillow 未安装，请先运行: pip install -r requirements.txt")
        sys.exit(1)

    # 检查主脚本
    main_script_path = PROJECT_ROOT / MAIN_SCRIPT
    if not main_script_path.exists():
        print_error(f"主脚本不存在: {main_script_path}")
        sys.exit(1)
    print_success(f"主脚本: {main_script_path}")


def clean_build():
    """清理构建文件"""
    print_info("清理构建文件...")

    dirs_to_clean = [BUILD_DIR, DIST_DIR]
    files_to_clean = list(SPEC_DIR.glob("*.spec"))

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print_info(f"删除目录: {dir_path}")
            shutil.rmtree(dir_path)
            print_success(f"已删除: {dir_path}")

    for file_path in files_to_clean:
        if file_path.exists():
            print_info(f"删除文件: {file_path}")
            file_path.unlink()
            print_success(f"已删除: {file_path}")

    print_success("清理完成")


def build_mac():
    """构建 macOS 应用"""
    print_header("构建 macOS 应用")

    # PyInstaller 参数
    pyinstaller_args = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # 不显示控制台窗口
        "--onefile",   # 打包成单个文件
        "--clean",     # 清理缓存
        # 添加数据文件
        "--add-data", "src:src",
        # 隐藏导入
        "--hidden-import", "PIL._tkinter_finder",
        # macOS 特定选项
        "--osx-bundle-identifier", f"com.{AUTHOR.lower().replace(' ', '')}.{APP_NAME.lower()}",
        # 图标(如果有)
        # "--icon", "resources/icon.icns",
        # 主脚本
        MAIN_SCRIPT,
    ]

    print_info("PyInstaller 命令:")
    print(f"  {' '.join(pyinstaller_args)}\n")

    # 执行打包
    try:
        subprocess.run(pyinstaller_args, check=True, cwd=PROJECT_ROOT)
        print_success("打包完成")
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        sys.exit(1)

    # 检查输出
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if app_path.exists():
        print_success(f"macOS 应用已生成: {app_path}")
        print_info(f"应用大小: {get_dir_size(app_path):.2f} MB")

        # 提示如何运行
        print_info("\n运行方法:")
        print(f"  1. 双击打开: {app_path}")
        print(f"  2. 命令行: open {app_path}")
    else:
        print_error("应用生成失败")
        sys.exit(1)


def build_windows():
    """构建 Windows 应用"""
    print_header("构建 Windows 应用")

    # PyInstaller 参数
    pyinstaller_args = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # 不显示控制台窗口(对于GUI应用)
        "--onefile",   # 打包成单个exe
        "--clean",     # 清理缓存
        # 添加数据文件
        "--add-data", "src;src",  # Windows 使用分号
        # 隐藏导入
        "--hidden-import", "PIL._tkinter_finder",
        # 图标(如果有)
        # "--icon", "resources/icon.ico",
        # 主脚本
        MAIN_SCRIPT,
    ]

    print_info("PyInstaller 命令:")
    print(f"  {' '.join(pyinstaller_args)}\n")

    # 执行打包
    try:
        subprocess.run(pyinstaller_args, check=True, cwd=PROJECT_ROOT)
        print_success("打包完成")
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        sys.exit(1)

    # 检查输出
    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    if exe_path.exists():
        print_success(f"Windows 应用已生成: {exe_path}")
        print_info(f"文件大小: {get_file_size(exe_path):.2f} MB")

        # 提示如何运行
        print_info("\n运行方法:")
        print(f"  双击运行: {exe_path}")
    else:
        print_error("应用生成失败")
        sys.exit(1)


def build_linux():
    """构建 Linux 应用"""
    print_header("构建 Linux 应用")

    # PyInstaller 参数
    pyinstaller_args = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",   # 打包成单个文件
        "--clean",     # 清理缓存
        # 添加数据文件
        "--add-data", "src:src",
        # 隐藏导入
        "--hidden-import", "PIL._tkinter_finder",
        # 主脚本
        MAIN_SCRIPT,
    ]

    print_info("PyInstaller 命令:")
    print(f"  {' '.join(pyinstaller_args)}\n")

    # 执行打包
    try:
        subprocess.run(pyinstaller_args, check=True, cwd=PROJECT_ROOT)
        print_success("打包完成")
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        sys.exit(1)

    # 检查输出
    bin_path = DIST_DIR / APP_NAME
    if bin_path.exists():
        print_success(f"Linux 应用已生成: {bin_path}")
        print_info(f"文件大小: {get_file_size(bin_path):.2f} MB")

        # 添加执行权限
        os.chmod(bin_path, 0o755)

        # 提示如何运行
        print_info("\n运行方法:")
        print(f"  ./{bin_path.name}")
    else:
        print_error("应用生成失败")
        sys.exit(1)


def get_file_size(file_path):
    """获取文件大小(MB)"""
    return file_path.stat().st_size / (1024 * 1024)


def get_dir_size(dir_path):
    """获取目录大小(MB)"""
    total_size = 0
    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size / (1024 * 1024)


def create_installer_info():
    """创建安装说明文件"""
    print_info("创建安装说明...")

    readme_content = f"""# {PROJECT_NAME} v{VERSION}

## 安装说明

### macOS
1. 下载 `{APP_NAME}.app`
2. 双击运行（如果提示"无法验证开发者"）:
   - 右键点击应用 -> 选择"打开"
   - 或在系统偏好设置 -> 安全性与隐私中允许

### Windows
1. 下载 `{APP_NAME}.exe`
2. 双击运行（如果Windows Defender提示）:
   - 点击"更多信息" -> "仍要运行"

### Linux
1. 下载 `{APP_NAME}`
2. 添加执行权限: `chmod +x {APP_NAME}`
3. 运行: `./{APP_NAME}`

## 使用方法

1. **单张转换**:
   - 点击"选择图片"
   - 选择压缩质量（高压缩/普通/低压缩）
   - 点击"开始转换"

2. **自定义质量**:
   - 选择"自定义"模式
   - 拖动滑块或输入数值(0-100)
   - 点击"开始转换"

3. **批量转换**:
   - 点击"批量选择"
   - 选择多张图片
   - 设置质量参数
   - 点击"批量转换"

## 支持的格式

输入: JPEG, PNG, GIF, BMP
输出: WebP

## 常见问题

**Q: 转换后文件在哪里?**
A: 默认保存在原图片同一目录，文件名为 `原文件名.webp`

**Q: 如何保证最佳质量?**
A: 选择"低压缩"(质量95)或自定义质量≥90

**Q: 批量转换有数量限制吗?**
A: 没有限制，但建议单次不超过100张以保证最佳性能

## 联系我们

问题反馈: https://github.com/your-org/webpexchange/issues

---

© {AUTHOR} - v{VERSION}
"""

    readme_path = DIST_DIR / "README.txt"
    readme_path.write_text(readme_content, encoding="utf-8")
    print_success(f"安装说明已创建: {readme_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="WebP图片转换器打包脚本")
    parser.add_argument(
        "--platform",
        choices=["mac", "windows", "linux", "auto"],
        default="auto",
        help="目标平台 (默认: auto 自动检测)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理构建文件"
    )

    args = parser.parse_args()

    # 显示欢迎信息
    print_header(f"{PROJECT_NAME} 打包脚本 v{VERSION}")

    # 清理模式
    if args.clean:
        clean_build()
        print_success("完成！")
        return

    # 检测或使用指定平台
    if args.platform == "auto":
        target_platform = detect_platform()
        print_info(f"自动检测平台: {target_platform}")
    else:
        target_platform = args.platform
        print_info(f"目标平台: {target_platform}")

    # 检查依赖
    check_dependencies()

    # 清理旧的构建文件
    clean_build()

    # 根据平台执行打包
    if target_platform == "mac":
        build_mac()
    elif target_platform == "windows":
        build_windows()
    elif target_platform == "linux":
        build_linux()
    else:
        print_error(f"不支持的平台: {target_platform}")
        sys.exit(1)

    # 创建安装说明
    create_installer_info()

    # 显示总结
    print_header("打包完成")
    print_success(f"输出目录: {DIST_DIR}")
    print_info("\n📦 分发文件:")
    for item in DIST_DIR.iterdir():
        if item.is_file():
            print(f"  - {item.name} ({get_file_size(item):.2f} MB)")
        elif item.is_dir():
            print(f"  - {item.name}/ ({get_dir_size(item):.2f} MB)")

    print_info("\n🎉 打包成功！可以将 dist/ 目录中的文件分发给用户。")


if __name__ == "__main__":
    main()
