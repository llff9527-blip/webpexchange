"""
质量控制组件

T051 (US1): 提供预设质量选项(高压缩/普通/低压缩)
T066 (US2): 扩展支持自定义质量(滑块+输入框)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.models.quality_preset import QualityPreset
from src.utils.validator import validate_quality_range


class QualityControl(ttk.Frame):
    """质量控制组件"""

    def __init__(self, parent):
        """
        初始化质量控制组件

        参数:
            parent: 父窗口
        """
        super().__init__(parent)

        # 质量模式变量
        self.quality_mode = tk.StringVar(value="preset")  # "preset" 或 "custom"

        # 预设质量变量
        self.preset_quality = tk.StringVar(value="NORMAL")

        # 自定义质量变量
        self.custom_quality = tk.IntVar(value=80)

        # 创建UI
        self._create_widgets()

        # 初始状态:禁用自定义控件
        self._update_controls_state()

    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(self, text="压缩质量设置", font=('', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))

        # --- 预设模式 ---
        preset_frame = ttk.LabelFrame(self, text="预设模式", padding=10)
        preset_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        # 预设单选按钮
        for i, preset in enumerate([
            QualityPreset.HIGH_COMPRESSION,
            QualityPreset.NORMAL,
            QualityPreset.LOW_COMPRESSION
        ]):
            rb = ttk.Radiobutton(
                preset_frame,
                text=f"{preset.display_name} (质量{preset.quality_value}) - {preset.desc}",
                variable=self.preset_quality,
                value=preset.name,
                command=self._on_preset_selected
            )
            rb.grid(row=i, column=0, sticky='w', pady=2)

        # --- 自定义模式 ---
        custom_frame = ttk.LabelFrame(self, text="自定义模式", padding=10)
        custom_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        # 自定义模式单选按钮
        custom_radio = ttk.Radiobutton(
            custom_frame,
            text="使用自定义质量",
            variable=self.quality_mode,
            value="custom",
            command=self._on_custom_selected
        )
        custom_radio.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))

        # 质量滑块
        slider_label = ttk.Label(custom_frame, text="质量参数 (0-100):")
        slider_label.grid(row=1, column=0, sticky='w', pady=2)

        self.quality_slider = ttk.Scale(
            custom_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.custom_quality,
            command=self._on_slider_change,
            length=300
        )
        self.quality_slider.grid(row=2, column=0, columnspan=2, sticky='ew', pady=2)

        # 质量输入框
        input_frame = ttk.Frame(custom_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5, 0))

        input_label = ttk.Label(input_frame, text="精确值:")
        input_label.pack(side=tk.LEFT, padx=(0, 5))

        self.quality_input = tk.Spinbox(
            input_frame,
            from_=0,
            to=100,
            textvariable=self.custom_quality,
            width=10,
            command=self._on_input_change
        )
        self.quality_input.pack(side=tk.LEFT)

        # 绑定输入框的键盘事件
        self.quality_input.bind('<FocusOut>', lambda e: self._on_input_change())
        self.quality_input.bind('<Return>', lambda e: self._on_input_change())

        # 提示标签
        hint_label = ttk.Label(
            custom_frame,
            text="提示: 值越大质量越高,文件也越大",
            font=('', 9),
            foreground='gray'
        )
        hint_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=(5, 0))

        # 配置网格权重
        self.columnconfigure(0, weight=1)
        preset_frame.columnconfigure(0, weight=1)
        custom_frame.columnconfigure(0, weight=1)

    def _update_controls_state(self):
        """更新控件启用/禁用状态"""
        if self.quality_mode.get() == "custom":
            # 启用自定义控件
            self.quality_slider.configure(state='normal')
            self.quality_input.configure(state='normal')
        else:
            # 禁用自定义控件
            self.quality_slider.configure(state='disabled')
            self.quality_input.configure(state='disabled')

    def _on_preset_selected(self):
        """预设模式被选择"""
        self.quality_mode.set("preset")
        self._update_controls_state()

    def _on_custom_selected(self):
        """自定义模式被选择"""
        self.quality_mode.set("custom")
        self._update_controls_state()

    def _on_slider_change(self, value):
        """
        滑块值改变时的回调

        T064: 滑块改变时同步到输入框
        """
        # 滑块返回的是字符串,需要转换为整数
        try:
            int_value = int(float(value))
            # 更新custom_quality会自动同步到输入框(因为它们绑定到同一个变量)
            self.custom_quality.set(int_value)
        except ValueError:
            pass

    def _on_input_change(self):
        """
        输入框值改变时的回调

        T064: 输入框改变时同步到滑块,并验证范围
        """
        try:
            # 获取输入值
            input_value = self.quality_input.get()

            # 验证和修正范围
            corrected_value, message = validate_quality_range(input_value)

            # 更新变量(会自动同步到滑块)
            self.custom_quality.set(corrected_value)

            # 如果有修正消息,显示提示
            if message:
                messagebox.showinfo("质量参数", message)

        except Exception as e:
            # 出错时恢复为默认值
            self.custom_quality.set(80)
            messagebox.showwarning("输入错误", "质量参数无效,已恢复为默认值80")

    def get_quality_value(self) -> int:
        """
        获取当前选择的质量值

        返回:
            质量参数(0-100)
        """
        if self.quality_mode.get() == "custom":
            # 自定义模式:返回滑块/输入框的值
            return self.custom_quality.get()
        else:
            # 预设模式:返回对应预设的质量值
            preset_name = self.preset_quality.get()
            preset = QualityPreset[preset_name]
            return preset.quality_value

    def set_quality_value(self, quality: int):
        """
        设置质量值

        参数:
            quality: 质量参数(0-100)
        """
        # 验证范围
        corrected_value, _ = validate_quality_range(quality)

        # 设置为自定义模式
        self.quality_mode.set("custom")
        self.custom_quality.set(corrected_value)
        self._update_controls_state()

    def reset_to_default(self):
        """重置为默认设置(普通预设)"""
        self.quality_mode.set("preset")
        self.preset_quality.set("NORMAL")
        self.custom_quality.set(80)
        self._update_controls_state()
