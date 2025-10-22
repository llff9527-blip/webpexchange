"""
警告对话框组件

显示软性限制警告(大文件、大尺寸)并获取用户确认。
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional


class WarningDialog:
    """警告对话框"""

    @staticmethod
    def show_large_file_warning(size_mb: float, on_continue: Optional[Callable] = None) -> bool:
        """
        显示大文件警告

        参数:
            size_mb: 文件大小(MB)
            on_continue: 用户选择继续时的回调函数

        返回:
            True表示用户选择继续,False表示取消
        """
        message = (
            f"⚠️ 警告\n\n"
            f"图片文件较大({size_mb:.1f} MB),\n"
            f"转换可能需要较长时间且消耗较多内存。\n\n"
            f"是否继续转换?"
        )

        result = messagebox.askyesno("大文件警告", message, icon='warning')

        if result and on_continue:
            on_continue()

        return result

    @staticmethod
    def show_large_dimension_warning(
        width: int,
        height: int,
        on_continue: Optional[Callable] = None
    ) -> bool:
        """
        显示大尺寸警告

        参数:
            width: 图片宽度(像素)
            height: 图片高度(像素)
            on_continue: 用户选择继续时的回调函数

        返回:
            True表示用户选择继续,False表示取消
        """
        message = (
            f"⚠️ 警告\n\n"
            f"图片尺寸较大({width}x{height}像素),\n"
            f"转换可能需要较长时间且消耗较多内存。\n\n"
            f"是否继续转换?"
        )

        result = messagebox.askyesno("大尺寸警告", message, icon='warning')

        if result and on_continue:
            on_continue()

        return result

    @staticmethod
    def show_combined_warning(
        size_mb: float,
        width: int,
        height: int,
        on_continue: Optional[Callable] = None
    ) -> bool:
        """
        显示组合警告(大文件且大尺寸)

        参数:
            size_mb: 文件大小(MB)
            width: 图片宽度(像素)
            height: 图片高度(像素)
            on_continue: 用户选择继续时的回调函数

        返回:
            True表示用户选择继续,False表示取消
        """
        message = (
            f"⚠️ 警告\n\n"
            f"图片文件较大({size_mb:.1f} MB)\n"
            f"且尺寸较大({width}x{height}像素),\n"
            f"转换可能需要较长时间且消耗较多内存。\n\n"
            f"建议:\n"
            f"- 确保系统内存充足(建议>4GB可用内存)\n"
            f"- 关闭其他占用内存的程序\n"
            f"- 转换过程中可随时取消\n\n"
            f"是否继续转换?"
        )

        result = messagebox.askyesno("性能警告", message, icon='warning')

        if result and on_continue:
            on_continue()

        return result

    @staticmethod
    def show_quality_warning(quality: int, warning_type: str = "low") -> bool:
        """
        显示质量参数警告

        参数:
            quality: 质量值
            warning_type: 警告类型("low"或"high")

        返回:
            True表示用户选择继续,False表示取消
        """
        if warning_type == "low":
            message = (
                f"⚠️ 质量警告\n\n"
                f"当前质量参数较低(质量: {quality}),\n"
                f"转换后的图片可能出现明显的压缩痕迹。\n\n"
                f"建议质量参数≥60以保证基本质量。\n\n"
                f"是否继续?"
            )
        else:  # high
            message = (
                f"⚠️ 质量警告\n\n"
                f"当前质量参数较高(质量: {quality}),\n"
                f"转换后的文件大小可能接近原图,\n"
                f"压缩效果有限。\n\n"
                f"建议:\n"
                f"- 如需高质量,可使用质量85-90\n"
                f"- 如需平衡质量和大小,可使用质量70-80\n\n"
                f"是否继续?"
            )

        return messagebox.askyesno("质量警告", message, icon='warning')

    @staticmethod
    def show_disk_space_warning(required_mb: float, available_mb: float) -> bool:
        """
        显示磁盘空间不足警告

        参数:
            required_mb: 需要的空间(MB)
            available_mb: 可用空间(MB)

        返回:
            True表示用户选择继续(不建议),False表示取消
        """
        message = (
            f"⚠️ 磁盘空间不足\n\n"
            f"预估需要空间: {required_mb:.1f} MB\n"
            f"当前可用空间: {available_mb:.1f} MB\n\n"
            f"磁盘空间可能不足以保存转换后的文件。\n\n"
            f"建议:\n"
            f"- 清理磁盘空间\n"
            f"- 选择其他磁盘分区\n"
            f"- 减小输出质量参数\n\n"
            f"是否强制继续?(不建议)"
        )

        return messagebox.askyesno("磁盘空间警告", message, icon='warning')

    @staticmethod
    def show_batch_size_warning(count: int) -> bool:
        """
        显示批量转换数量警告

        参数:
            count: 图片数量

        返回:
            True表示用户选择继续,False表示取消
        """
        if count > 100:
            message = (
                f"⚠️ 批量转换警告\n\n"
                f"您选择了 {count} 张图片进行批量转换。\n\n"
                f"提示:\n"
                f"- 转换可能需要较长时间\n"
                f"- 建议分批转换(每批50-100张)\n"
                f"- 转换过程中可随时取消\n\n"
                f"是否继续?"
            )
            return messagebox.askyesno("批量转换警告", message, icon='warning')

        return True


class SoftLimitChecker:
    """软性限制检查器"""

    # 软性限制阈值
    MAX_FILE_SIZE_MB = 200  # 200MB
    MAX_DIMENSION = 8000    # 8000像素

    @classmethod
    def check_file_size(cls, size_bytes: int) -> tuple[bool, float]:
        """
        检查文件大小是否超出软性限制

        参数:
            size_bytes: 文件大小(字节)

        返回:
            (是否超出限制, 文件大小MB)
        """
        size_mb = size_bytes / (1024 * 1024)
        exceeds = size_mb > cls.MAX_FILE_SIZE_MB
        return exceeds, size_mb

    @classmethod
    def check_dimension(cls, width: int, height: int) -> tuple[bool, int, int]:
        """
        检查图片尺寸是否超出软性限制

        参数:
            width: 图片宽度
            height: 图片高度

        返回:
            (是否超出限制, 宽度, 高度)
        """
        exceeds = width > cls.MAX_DIMENSION or height > cls.MAX_DIMENSION
        return exceeds, width, height

    @classmethod
    def check_and_warn(
        cls,
        size_bytes: int,
        width: int,
        height: int,
        on_continue: Optional[Callable] = None
    ) -> bool:
        """
        检查并显示警告

        参数:
            size_bytes: 文件大小(字节)
            width: 图片宽度
            height: 图片高度
            on_continue: 用户选择继续时的回调函数

        返回:
            True表示允许继续,False表示取消
        """
        size_exceeds, size_mb = cls.check_file_size(size_bytes)
        dimension_exceeds, w, h = cls.check_dimension(width, height)

        if size_exceeds and dimension_exceeds:
            # 同时超出大小和尺寸限制
            return WarningDialog.show_combined_warning(size_mb, w, h, on_continue)
        elif size_exceeds:
            # 仅超出大小限制
            return WarningDialog.show_large_file_warning(size_mb, on_continue)
        elif dimension_exceeds:
            # 仅超出尺寸限制
            return WarningDialog.show_large_dimension_warning(w, h, on_continue)
        else:
            # 未超出限制
            return True
