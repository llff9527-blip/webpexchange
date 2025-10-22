"""
图片文件实体

表示待转换或已转换的图片文件,封装文件元信息和验证逻辑。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

from .image_metadata import ImageMetadata


@dataclass
class ImageFile:
    """图片文件实体"""

    file_path: Path
    file_name: str
    format: str
    width: int
    height: int
    file_size: int
    metadata: Optional[ImageMetadata] = None

    @property
    def file_size_mb(self) -> float:
        """文件大小(MB)"""
        return self.file_size / (1024 * 1024)

    @property
    def exceeds_soft_limit(self) -> bool:
        """是否超出软性限制(文件大小>200MB或尺寸>8000)"""
        return self.file_size_mb > 200 or self.width > 8000 or self.height > 8000

    @property
    def is_valid(self) -> bool:
        """文件是否有效"""
        is_valid, _ = self.validate()
        return is_valid

    @classmethod
    def from_path(cls, file_path: str | Path) -> "ImageFile":
        """从文件路径创建ImageFile实例,自动提取元信息"""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # 验证文件存在
        if not file_path.exists():
            raise FileNotFoundError(f"图片文件损坏或无法访问,请检查文件: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"路径不是有效的文件: {file_path}")

        # 使用Pillow打开图片并提取信息
        try:
            with Image.open(file_path) as img:
                format_str = img.format if img.format else "UNKNOWN"
                width = img.width
                height = img.height

                # 提取元数据
                metadata = ImageMetadata.from_pil_image(img)

        except Exception as e:
            raise ValueError(f"无法读取图片文件: {e}")

        # 获取文件大小
        file_size = file_path.stat().st_size

        return cls(
            file_path=file_path,
            file_name=file_path.name,
            format=format_str,
            width=width,
            height=height,
            file_size=file_size,
            metadata=metadata
        )

    def validate(self) -> Tuple[bool, str]:
        """验证文件有效性,返回(is_valid, error_message)"""
        # 检查文件存在性
        if not self.file_path.exists():
            return False, "图片文件损坏或无法访问,请检查文件"

        # 检查是否为文件
        if not self.file_path.is_file():
            return False, "路径不是有效的文件"

        # 检查格式支持
        supported_formats = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
        if self.format not in supported_formats:
            return False, "不支持的文件格式,请选择图片文件(JPEG, PNG, GIF等)"

        # 检查尺寸有效性
        if self.width <= 0 or self.height <= 0:
            return False, "图片尺寸无效"

        return True, ""

    def get_display_info(self) -> dict:
        """返回适合在UI显示的信息字典"""
        return {
            'file_name': self.file_name,
            'format': self.format,
            'width': self.width,
            'height': self.height,
            'dimensions': f"{self.width}x{self.height}",
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size_mb, 2),
            'exceeds_soft_limit': self.exceeds_soft_limit,
            'has_metadata': self.metadata.has_metadata if self.metadata else False
        }
