"""
核心数据模型模块
"""

from .image_metadata import ImageMetadata
from .quality_preset import QualityPreset
from .image_file import ImageFile
from .conversion_task import ConversionTask, TaskStatus
from .batch_conversion_job import BatchConversionJob

__all__ = [
    'ImageMetadata',
    'QualityPreset',
    'ImageFile',
    'ConversionTask',
    'TaskStatus',
    'BatchConversionJob',
]
