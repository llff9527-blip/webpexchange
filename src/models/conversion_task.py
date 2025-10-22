"""
转换任务实体

表示单张图片的转换任务,跟踪转换状态和结果。
"""

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime
from typing import Optional
import uuid

from .image_file import ImageFile


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "待转换"
    IN_PROGRESS = "转换中"
    COMPLETED = "已完成"
    FAILED = "失败"
    CANCELLED = "已取消"


@dataclass
class ConversionTask:
    """转换任务实体"""

    input_file: ImageFile
    output_path: Path
    quality: int
    preserve_metadata: bool = True
    status: TaskStatus = TaskStatus.PENDING
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    output_file_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def start(self) -> None:
        """标记任务开始,设置started_at时间"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, output_size: int, duration: float) -> None:
        """标记任务完成,计算压缩比和耗时"""
        self.status = TaskStatus.COMPLETED
        self.finished_at = datetime.now()
        self.output_file_size = output_size
        self.duration_seconds = duration

        # 计算压缩比(百分比)
        if self.input_file.file_size > 0:
            ratio = (1 - output_size / self.input_file.file_size) * 100
            self.compression_ratio = round(ratio, 2)
        else:
            self.compression_ratio = 0.0

    def fail(self, error: str) -> None:
        """标记任务失败,记录错误信息"""
        self.status = TaskStatus.FAILED
        self.finished_at = datetime.now()
        self.error_message = error

    def cancel(self) -> None:
        """标记任务取消"""
        self.status = TaskStatus.CANCELLED
        self.finished_at = datetime.now()

    def get_result_summary(self) -> dict:
        """返回任务结果摘要(用于UI显示)"""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'input_file': self.input_file.file_name,
            'output_path': str(self.output_path),
            'quality': self.quality,
            'output_file_size': self.output_file_size,
            'compression_ratio': self.compression_ratio,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
        }
