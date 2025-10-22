"""
进度显示组件

显示转换进度、状态和结果信息。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class ProgressDisplay(ttk.Frame):
    """进度显示组件"""

    def __init__(self, parent, on_cancel: Optional[callable] = None):
        """
        初始化进度显示组件

        Args:
            parent: 父窗口
            on_cancel: 取消按钮回调函数
        """
        super().__init__(parent)
        self.on_cancel = on_cancel

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 状态标签
        self.status_label = ttk.Label(
            self,
            text="就绪",
            font=("Arial", 12)
        )
        self.status_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # 进度条
        self.progress_bar = ttk.Progressbar(
            self,
            mode="indeterminate",
            length=400
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # 取消按钮
        self.cancel_btn = ttk.Button(
            self,
            text="取消",
            command=self._on_cancel_click,
            state="disabled"
        )
        self.cancel_btn.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # 结果信息框
        result_frame = ttk.LabelFrame(self, text="转换结果", padding=10)
        result_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.result_text = tk.Text(
            result_frame,
            height=8,
            width=50,
            state="disabled"
        )
        self.result_text.pack(fill="both", expand=True)

        self.columnconfigure(0, weight=1)

    def _on_cancel_click(self):
        """取消按钮点击"""
        if self.on_cancel:
            self.on_cancel()

    def start_conversion(self):
        """开始转换"""
        self.status_label.config(text="转换中...")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)
        self.cancel_btn.config(state="normal")
        self._clear_result()

    def update_progress(self, current: int, total: int):
        """
        更新进度

        Args:
            current: 当前完成数
            total: 总数
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar.config(mode="determinate", maximum=total, value=current)
            self.status_label.config(text=f"转换中... ({current}/{total} - {percentage:.1f}%)")

    def finish_conversion(
        self,
        success: bool,
        output_path: Optional[str] = None,
        compression_ratio: Optional[float] = None,
        duration: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """
        完成转换

        Args:
            success: 是否成功
            output_path: 输出文件路径
            compression_ratio: 压缩比
            duration: 耗时
            error_message: 错误信息
        """
        self.progress_bar.stop()
        self.cancel_btn.config(state="disabled")

        if success:
            self.status_label.config(text="转换完成!")
            result = f"✅ 转换成功\n\n"
            if output_path:
                result += f"输出文件: {output_path}\n"
            if compression_ratio is not None:
                result += f"压缩比: {compression_ratio:.1f}%\n"
            if duration is not None:
                result += f"耗时: {duration:.2f}秒\n"

            self._show_result(result, "success")
        else:
            self.status_label.config(text="转换失败")
            result = f"❌ 转换失败\n\n错误: {error_message or '未知错误'}"
            self._show_result(result, "error")

    def cancel_conversion(self):
        """取消转换"""
        self.progress_bar.stop()
        self.cancel_btn.config(state="disabled")
        self.status_label.config(text="已取消")
        self._show_result("⚠️ 转换已取消", "warning")

    def _show_result(self, text: str, result_type: str = "info"):
        """显示结果信息"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.config(state="disabled")

    def _clear_result(self):
        """清空结果信息"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")

    def reset(self):
        """重置状态"""
        self.status_label.config(text="就绪")
        self.progress_bar.stop()
        self.progress_bar.config(mode="indeterminate", value=0)
        self.cancel_btn.config(state="disabled")
        self._clear_result()
