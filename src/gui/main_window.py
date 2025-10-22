"""
主窗口

整合所有GUI组件,实现完整的转换界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys
import traceback

from src.models.image_file import ImageFile
from src.services.converter_service import ConverterService, ConversionResult
from src.services.file_service import FileService
from src.gui.components import ImageSelector, QualityControl, ProgressDisplay
from src.gui.handlers import ConversionHandler, CancelHandler
from src.utils.error_messages import ErrorMessages, ErrorCode


class MainWindow:
    """主窗口"""

    def __init__(self, root: tk.Tk):
        """
        初始化主窗口

        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("WebP图片转换器")
        self.root.geometry("800x700")
        self.root.minsize(800, 600)  # T107: 最小尺寸800x600

        # 服务实例
        self.converter_service = ConverterService()
        self.file_service = FileService()

        # 处理器
        self.conversion_handler = ConversionHandler(
            converter_service=self.converter_service,
            on_complete=self._on_conversion_complete
        )
        self.cancel_handler = CancelHandler(
            on_cancelled=self._on_cancelled
        )

        # 当前选择的图片
        self.current_image: ImageFile | None = None

        # T098: 设置全局异常处理器
        self._setup_exception_handler()

        self._init_ui()
        self._setup_polling()

    def _init_ui(self):
        """初始化UI"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 配置网格权重
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="WebP图片转换器",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        # 图片选择组件
        self.image_selector = ImageSelector(
            main_frame,
            on_image_selected=self._on_image_selected
        )
        self.image_selector.grid(row=1, column=0, pady=5, sticky="ew")

        # 质量控制组件
        self.quality_control = QualityControl(main_frame)
        self.quality_control.grid(row=2, column=0, pady=5, sticky="ew")

        # 转换按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=10, sticky="ew")

        self.convert_btn = ttk.Button(
            button_frame,
            text="开始转换",
            command=self._start_conversion,
            state="disabled"
        )
        self.convert_btn.pack(side="left", padx=5)

        # 进度显示组件
        self.progress_display = ProgressDisplay(
            main_frame,
            on_cancel=self._on_cancel_click
        )
        self.progress_display.grid(row=4, column=0, pady=5, sticky="nsew")

    def _setup_polling(self):
        """设置结果轮询"""
        self._poll_conversion_result()

    def _poll_conversion_result(self):
        """轮询转换结果"""
        if self.conversion_handler.is_running():
            # 检查结果
            result = self.conversion_handler.get_result()
            if result:
                self._handle_conversion_result(result)

        # 继续轮询
        self.root.after(100, self._poll_conversion_result)

    def _on_image_selected(self, image_file: ImageFile):
        """图片选择回调"""
        self.current_image = image_file
        self.convert_btn.config(state="normal")

    def _start_conversion(self):
        """开始转换"""
        if not self.current_image:
            messagebox.showwarning("提示", "请先选择图片文件")
            return

        # 获取质量设置
        quality = self.quality_control.get_quality_value()

        # 确定输出路径
        output_path = self.file_service.resolve_output_path(
            input_path=self.current_image.file_path,
            output_dir=self.current_image.file_path.parent,
            output_format="webp"
        )

        # 禁用转换按钮
        self.convert_btn.config(state="disabled")

        # 显示进度
        self.progress_display.start_conversion()

        # 重置取消处理器
        self.cancel_handler.reset()

        # 启动转换
        self.conversion_handler.start_conversion(
            image_file=self.current_image,
            output_path=output_path,
            quality=quality,
            preserve_metadata=True
        )

    def _on_cancel_click(self):
        """取消按钮点击"""
        if self.conversion_handler.is_running():
            # 请求取消
            self.cancel_handler.request_cancel()
            self.conversion_handler.cancel()
            self.progress_display.cancel_conversion()

    def _on_cancelled(self):
        """取消回调"""
        # 恢复转换按钮
        if self.current_image:
            self.convert_btn.config(state="normal")

    def _on_conversion_complete(self, result: ConversionResult):
        """转换完成回调"""
        # 这个回调在工作线程中,不做任何事
        # 实际处理在_handle_conversion_result中进行
        pass

    def _handle_conversion_result(self, result: ConversionResult):
        """处理转换结果(主线程)"""
        # 更新进度显示
        if result.success:
            self.progress_display.finish_conversion(
                success=True,
                output_path=str(result.output_path),
                compression_ratio=result.compression_ratio,
                duration=result.duration
            )
            messagebox.showinfo("成功", f"转换完成!\n\n输出文件: {result.output_path}")
        else:
            self.progress_display.finish_conversion(
                success=False,
                error_message=result.error_message
            )
            messagebox.showerror("失败", f"转换失败\n\n{result.error_message}")

        # 恢复转换按钮
        if self.current_image:
            self.convert_btn.config(state="normal")

    def _setup_exception_handler(self):
        """设置全局异常处理器"""
        # 设置tk异常处理器
        self.root.report_callback_exception = self._handle_uncaught_exception

        # 设置Python异常钩子(处理非tk异常)
        sys.excepthook = self._handle_uncaught_exception

    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """
        处理未捕获的异常

        Args:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常追踪
        """
        # 忽略键盘中断
        if issubclass(exc_type, KeyboardInterrupt):
            sys.exit(0)
            return

        # 记录详细错误信息到控制台(用于调试)
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"\n=== 未捕获的异常 ===\n{error_msg}", file=sys.stderr)

        # 显示用户友好的错误对话框
        user_message = (
            f"程序遇到意外错误\n\n"
            f"错误类型: {exc_type.__name__}\n"
            f"错误信息: {str(exc_value)}\n\n"
            f"建议:\n"
            f"- 请重新启动应用\n"
            f"- 如果问题持续,请联系技术支持\n"
        )

        try:
            messagebox.showerror("程序错误", user_message)
        except Exception:
            # 如果无法显示对话框,至少打印到控制台
            print(f"无法显示错误对话框: {user_message}", file=sys.stderr)

    def run(self):
        """运行主窗口"""
        self.root.mainloop()
