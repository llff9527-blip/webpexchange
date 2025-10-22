"""
路径处理工具

提供跨平台路径处理功能。
"""

from pathlib import Path


def resolve_output_path(base_path: Path) -> Path:
    """
    解决文件名冲突,自动重命名以避免覆盖已有文件。

    参数:
        base_path: 期望的输出路径

    返回:
        唯一的输出路径

    示例:
        output.webp -> output_1.webp -> output_2.webp
    """
    if not base_path.exists():
        return base_path

    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    counter = 1

    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
