"""
质量预设枚举

定义三种预设的压缩质量选项,对应spec.md的FR-004需求。
"""

from enum import Enum


class QualityPreset(Enum):
    """质量预设枚举"""

    HIGH_COMPRESSION = ("高压缩", 60, "适用于对文件大小敏感的场景")
    NORMAL = ("普通", 80, "平衡质量和大小")
    LOW_COMPRESSION = ("低压缩", 95, "优先保证质量")

    def __init__(self, name: str, quality: int, description: str):
        self.display_name = name
        self.quality_value = quality
        self.desc = description
