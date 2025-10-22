"""
转换处理器

处理单张图片的转换逻辑,使用线程异步执行。
"""

import threading
import queue
from pathlib import Path
from typing import Optional, Callable

from src.models.image_file import ImageFile
from src.services.converter_service import ConverterService, ConversionResult


class ConversionHandler:
    """转换处理器"""

    def __init__(
        self,
        converter_service: ConverterService,
        on_complete: Optional[Callable[[ConversionResult], None]] = None
    ):
        """
        初始化转换处理器

        Args:
            converter_service: 转换服务实例
            on_complete: 转换完成回调函数
        """
        self.converter_service = converter_service
        self.on_complete = on_complete

        self.stop_event = threading.Event()
        self.worker_thread: Optional[threading.Thread] = None
        self.result_queue = queue.Queue()

    def start_conversion(
        self,
        image_file: ImageFile,
        output_path: Path,
        quality: int,
        preserve_metadata: bool = True
    ):
        """
        开始转换

        Args:
            image_file: 输入图片文件
            output_path: 输出文件路径
            quality: 质量参数
            preserve_metadata: 是否保留元数据
        """
        # 重置停止标志
        self.stop_event.clear()

        # 创建工作线程
        self.worker_thread = threading.Thread(
            target=self._conversion_worker,
            args=(image_file, output_path, quality, preserve_metadata),
            daemon=True
        )
        self.worker_thread.start()

    def _conversion_worker(
        self,
        image_file: ImageFile,
        output_path: Path,
        quality: int,
        preserve_metadata: bool
    ):
        """转换工作线程"""
        try:
            # 执行转换
            result = self.converter_service.convert_image(
                input_file=image_file,
                output_path=output_path,
                quality=quality,
                preserve_metadata=preserve_metadata,
                stop_event=self.stop_event
            )

            # 将结果放入队列
            self.result_queue.put(result)

            # 触发回调(在主线程中调用)
            if self.on_complete:
                # 注意: GUI更新必须在主线程中进行
                # 这里将结果放入队列,由主线程轮询处理
                pass

        except Exception as e:
            # 错误处理
            error_result = ConversionResult(
                success=False,
                error_message=f"转换异常: {str(e)}"
            )
            self.result_queue.put(error_result)

    def cancel(self):
        """取消转换"""
        self.stop_event.set()

    def is_running(self) -> bool:
        """是否正在运行"""
        return self.worker_thread is not None and self.worker_thread.is_alive()

    def get_result(self) -> Optional[ConversionResult]:
        """获取转换结果(非阻塞)"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

    def wait_for_completion(self, timeout: Optional[float] = None):
        """等待转换完成"""
        if self.worker_thread:
            self.worker_thread.join(timeout=timeout)
