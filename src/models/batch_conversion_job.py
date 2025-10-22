"""
批量转换作业实体

管理多张图片的批量转换,跟踪整体进度和每个子任务状态。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

from .conversion_task import ConversionTask, TaskStatus


@dataclass
class BatchConversionJob:
    """批量转换作业实体"""

    quality: int
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: List[ConversionTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total_count(self) -> int:
        """总任务数"""
        return len(self.tasks)

    @property
    def completed_count(self) -> int:
        """已完成数"""
        return sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        """失败数"""
        return sum(1 for task in self.tasks if task.status == TaskStatus.FAILED)

    @property
    def cancelled_count(self) -> int:
        """已取消数"""
        return sum(1 for task in self.tasks if task.status == TaskStatus.CANCELLED)

    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total_count == 0:
            return 0.0

        finished = self.completed_count + self.failed_count + self.cancelled_count
        return round((finished / self.total_count) * 100, 2)

    @property
    def is_complete(self) -> bool:
        """作业是否完成(所有任务均处于终态)"""
        if self.total_count == 0:
            return True

        terminal_states = [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        return all(task.status in terminal_states for task in self.tasks)

    def add_task(self, task: ConversionTask) -> None:
        """添加子任务到作业"""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[ConversionTask]:
        """获取所有待处理的任务"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_summary(self) -> dict:
        """返回作业摘要(总数/完成数/失败数/进度百分比)"""
        return {
            'job_id': self.job_id,
            'quality': self.quality,
            'total_count': self.total_count,
            'completed_count': self.completed_count,
            'failed_count': self.failed_count,
            'cancelled_count': self.cancelled_count,
            'progress_percentage': self.progress_percentage,
            'is_complete': self.is_complete,
            'created_at': self.created_at.isoformat(),
        }

    def cancel_pending_tasks(self) -> int:
        """取消所有未开始的任务,返回取消数量"""
        pending = self.get_pending_tasks()
        for task in pending:
            task.cancel()
        return len(pending)
