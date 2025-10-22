"""
取消处理器

处理转换过程的取消操作。
"""

import threading
from typing import Optional, Callable


class CancelHandler:
    """取消处理器"""

    def __init__(self, on_cancelled: Optional[Callable[[], None]] = None):
        """
        初始化取消处理器

        Args:
            on_cancelled: 取消后的回调函数
        """
        self.on_cancelled = on_cancelled
        self.stop_event = threading.Event()

    def request_cancel(self):
        """请求取消"""
        self.stop_event.set()

        if self.on_cancelled:
            self.on_cancelled()

    def is_cancelled(self) -> bool:
        """是否已取消"""
        return self.stop_event.is_set()

    def reset(self):
        """重置取消状态"""
        self.stop_event.clear()

    def get_stop_event(self) -> threading.Event:
        """获取停止事件对象"""
        return self.stop_event
