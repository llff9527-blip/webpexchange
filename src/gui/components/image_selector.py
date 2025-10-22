"""
图片选择组件

提供文件选择对话框和图片预览功能。
"""

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from typing import Optional, Callable
from PIL import Image, ImageTk

from src.models.image_file import ImageFile


class ImageSelector(ttk.Frame):
    """图片选择组件"""

    def __init__(self, parent, on_image_selected: Optional[Callable[[ImageFile], None]] = None):
        """
        初始化图片选择组件

        Args:
            parent: 父窗口
            on_image_selected: 选择图片后的回调函数
        """
        super().__init__(parent)
        self.on_image_selected = on_image_selected
        self.current_image_file: Optional[ImageFile] = None

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 选择按钮
        self.select_btn = ttk.Button(
            self,
            text="选择图片",
            command=self._select_image
        )
        self.select_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # 文件信息标签
        self.info_label = ttk.Label(
            self,
            text="未选择图片",
            relief="sunken",
            anchor="w"
        )
        self.info_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # 详细信息框
        info_frame = ttk.LabelFrame(self, text="图片信息", padding=10)
        info_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.detail_text = tk.Text(
            info_frame,
            height=6,
            width=50,
            state="disabled"
        )
        self.detail_text.pack(fill="both", expand=True)

        self.columnconfigure(0, weight=1)

    def _select_image(self):
        """打开文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self._load_image(Path(file_path))

    def _load_image(self, file_path: Path):
        """加载图片文件"""
        try:
            # 创建ImageFile对象
            image_file = ImageFile.from_path(file_path)

            # 验证文件
            if not image_file.is_valid:
                is_valid, error_msg = image_file.validate()
                self._show_error(error_msg)
                return

            # 保存当前图片
            self.current_image_file = image_file

            # 更新UI
            self._update_ui(image_file)

            # 触发回调
            if self.on_image_selected:
                self.on_image_selected(image_file)

        except Exception as e:
            self._show_error(f"无法加载图片: {str(e)}")

    def _update_ui(self, image_file: ImageFile):
        """更新UI显示图片信息"""
        # 更新文件名标签
        self.info_label.config(text=f"已选择: {image_file.file_name}")

        # 更新详细信息
        info = image_file.get_display_info()
        details = f"""文件名: {info['file_name']}
格式: {info['format']}
尺寸: {info['dimensions']}
文件大小: {info['file_size_mb']} MB
元数据: {'有' if info['has_metadata'] else '无'}"""

        if info['exceeds_soft_limit']:
            details += "\n\n⚠️ 警告: 文件较大,转换可能需要较长时间"

        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", details)
        self.detail_text.config(state="disabled")

    def _show_error(self, error_msg: str):
        """显示错误信息"""
        self.info_label.config(text="选择失败")
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", f"错误: {error_msg}")
        self.detail_text.config(state="disabled")

    def get_selected_image(self) -> Optional[ImageFile]:
        """获取当前选择的图片"""
        return self.current_image_file

    def clear(self):
        """清空选择"""
        self.current_image_file = None
        self.info_label.config(text="未选择图片")
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.config(state="disabled")
