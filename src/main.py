"""
应用入口

WebP图片转换器主程序。
"""

import tkinter as tk
import sys
import os

# 添加项目根目录到路径（用于PyInstaller打包）
if getattr(sys, 'frozen', False):
    # 运行在PyInstaller打包后的环境
    application_path = sys._MEIPASS
else:
    # 运行在正常Python环境
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保src目录在路径中
if application_path not in sys.path:
    sys.path.insert(0, application_path)

from src.gui.main_window import MainWindow


def check_webp_support():
    """
    检查Pillow的WebP支持

    Returns:
        bool: True表示支持WebP,False表示不支持
    """
    try:
        from PIL import features
        return features.check('webp')
    except Exception as e:
        print(f"检查WebP支持时出错: {e}", file=sys.stderr)
        return False


def show_webp_not_supported_dialog():
    """显示WebP不支持的错误对话框"""
    import platform
    from tkinter import messagebox

    # 创建临时窗口用于显示对话框
    temp_root = tk.Tk()
    temp_root.withdraw()  # 隐藏主窗口

    # 根据操作系统提供不同的安装指南
    system = platform.system()

    if system == "Windows":
        instructions = (
            "Windows用户:\n"
            "1. 打开命令提示符(CMD)\n"
            "2. 运行: pip uninstall Pillow\n"
            "3. 运行: pip install --upgrade Pillow\n"
            "4. 重新启动应用"
        )
    elif system == "Darwin":  # macOS
        instructions = (
            "macOS用户:\n"
            "1. 打开终端\n"
            "2. 安装WebP库: brew install webp\n"
            "3. 重新安装Pillow: pip install --no-cache-dir --upgrade Pillow\n"
            "4. 重新启动应用"
        )
    else:  # Linux
        instructions = (
            "Linux用户:\n"
            "1. 安装WebP开发库:\n"
            "   Ubuntu/Debian: sudo apt-get install libwebp-dev\n"
            "   CentOS/RHEL: sudo yum install libwebp-devel\n"
            "2. 重新安装Pillow: pip install --no-cache-dir --upgrade Pillow\n"
            "3. 重新启动应用"
        )

    message = (
        f"系统不支持WebP格式\n\n"
        f"WebP图片转换器需要Pillow库支持WebP格式。\n"
        f"请按照以下步骤安装:\n\n"
        f"{instructions}\n\n"
        f"详细信息请参考README.md中的故障排除部分。"
    )

    messagebox.showerror("WebP支持缺失", message)
    temp_root.destroy()


def main():
    """主函数"""
    # T103: 检查WebP支持并显示友好提示
    if not check_webp_support():
        show_webp_not_supported_dialog()
        sys.exit(1)

    # 创建主窗口
    root = tk.Tk()

    # 创建应用
    app = MainWindow(root)

    # 运行应用
    app.run()


if __name__ == "__main__":
    main()
