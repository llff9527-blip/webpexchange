#!/usr/bin/env python
"""
打包脚本

使用PyInstaller将WebP图片转换器打包为可执行文件。
"""

import sys
import platform
import subprocess
from pathlib import Path


def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller已安装(版本: {PyInstaller.__version__})")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        print("  请运行: pip install pyinstaller")
        return False


def get_build_options():
    """
    获取构建选项

    Returns:
        dict: 构建选项
    """
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    main_script = src_dir / "main.py"

    # 应用名称
    app_name = "WebP图片转换器"

    # 操作系统特定选项
    system = platform.system()

    options = {
        "name": app_name,
        "main_script": str(main_script),
        "icon": None,  # TODO: 添加应用图标
        "onefile": True,  # 打包为单个可执行文件
        "windowed": True,  # GUI应用(无控制台窗口)
        "add_data": [],   # 需要包含的数据文件
        "hidden_imports": [
            "PIL._tkinter_finder",  # tkinter支持
        ],
        "excludes": [
            "matplotlib",
            "numpy",
            "pandas",
            "scipy",
        ],  # 排除不需要的库
    }

    # 平台特定配置
    if system == "Windows":
        options["icon"] = None  # TODO: 添加Windows图标(.ico)
    elif system == "Darwin":  # macOS
        options["icon"] = None  # TODO: 添加macOS图标(.icns)
        options["osx_bundle_identifier"] = "com.webpexchange.app"

    return options


def build_executable():
    """构建可执行文件"""
    print("\n" + "=" * 60)
    print("WebP图片转换器 - 打包脚本")
    print("=" * 60)

    # 检查PyInstaller
    if not check_pyinstaller():
        return False

    # 获取构建选项
    options = get_build_options()

    print(f"\n构建配置:")
    print(f"  应用名称: {options['name']}")
    print(f"  主脚本: {options['main_script']}")
    print(f"  单文件打包: {options['onefile']}")
    print(f"  GUI模式: {options['windowed']}")
    print(f"  操作系统: {platform.system()} {platform.release()}")

    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--name", options["name"],
        "--onefile" if options["onefile"] else "--onedir",
    ]

    if options["windowed"]:
        cmd.append("--windowed")

    if options["icon"]:
        cmd.extend(["--icon", options["icon"]])

    # 添加隐藏导入
    for hidden_import in options["hidden_imports"]:
        cmd.extend(["--hidden-import", hidden_import])

    # 添加数据文件
    for data in options["add_data"]:
        cmd.extend(["--add-data", data])

    # 排除模块
    for exclude in options["excludes"]:
        cmd.extend(["--exclude-module", exclude])

    # 添加主脚本
    cmd.append(options["main_script"])

    # 添加额外选项
    cmd.extend([
        "--noconfirm",  # 覆盖已有构建
        "--clean",       # 清理临时文件
        "--log-level", "INFO",
    ])

    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}\n")

    # 执行打包
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✓ 打包成功!")
        print("=" * 60)

        # 显示输出位置
        dist_dir = Path("dist")
        if options["onefile"]:
            output_file = dist_dir / options["name"]
            if platform.system() == "Windows":
                output_file = output_file.with_suffix(".exe")

            print(f"\n可执行文件位置:")
            print(f"  {output_file.absolute()}")
        else:
            print(f"\n应用程序位置:")
            print(f"  {(dist_dir / options['name']).absolute()}")

        print(f"\n使用方法:")
        print(f"  1. 进入 dist/ 目录")
        print(f"  2. 双击运行 {options['name']}")

        return True

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ 打包失败!")
        print("=" * 60)
        print(f"\n错误信息:")
        print(f"  {e}")
        return False


def clean_build_files():
    """清理构建临时文件"""
    import shutil

    dirs_to_clean = ["build", "__pycache__"]

    print("\n清理临时文件...")
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  删除: {dir_path}")
            shutil.rmtree(dir_path)

    # 删除.spec文件
    for spec_file in Path(".").glob("*.spec"):
        print(f"  删除: {spec_file}")
        spec_file.unlink()

    print("✓ 清理完成")


def main():
    """主函数"""
    try:
        success = build_executable()

        if success:
            clean_build_files()
            print("\n🎉 打包流程完成!")
            return 0
        else:
            print("\n❌ 打包失败,请检查错误信息")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  打包已取消")
        return 130

    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
