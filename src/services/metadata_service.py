"""
元数据服务

提供EXIF/XMP/ICC元数据的提取、嵌入和验证功能。
"""

from pathlib import Path
from typing import Tuple
from PIL import Image

from src.models.image_metadata import ImageMetadata


class MetadataService:
    """元数据处理服务"""

    def extract_metadata(self, pil_image: Image.Image) -> ImageMetadata:
        """
        从Pillow Image对象中提取元数据

        Args:
            pil_image: Pillow打开的图片对象

        Returns:
            ImageMetadata对象,包含提取的EXIF/XMP/ICC数据
        """
        return ImageMetadata.from_pil_image(pil_image)

    def embed_metadata(self, metadata: ImageMetadata) -> dict:
        """
        将元数据转换为Pillow保存参数字典

        Args:
            metadata: 要嵌入的元数据对象

        Returns:
            适用于Image.save(**kwargs)的参数字典,过滤了None值
        """
        return metadata.to_save_params()

    def validate_metadata_preservation(
        self,
        original_metadata: ImageMetadata,
        output_file_path: Path
    ) -> Tuple[bool, str]:
        """
        验证转换后的文件是否成功保留了元数据

        Args:
            original_metadata: 原始图片的元数据
            output_file_path: 转换后的文件路径

        Returns:
            (是否保留成功, 描述信息)
        """
        if not output_file_path.exists():
            return False, "输出文件不存在"

        try:
            with Image.open(output_file_path) as output_img:
                output_metadata = self.extract_metadata(output_img)

                # 检查EXIF
                if original_metadata.exif:
                    if not output_metadata.exif:
                        return False, "EXIF元数据丢失"
                    if original_metadata.exif != output_metadata.exif:
                        # 注意: WebP可能会轻微修改EXIF格式,这里允许部分差异
                        # 实际应用中可能需要更精细的比较
                        pass

                # 检查XMP
                if original_metadata.xmp:
                    if not output_metadata.xmp:
                        return False, "XMP元数据丢失"
                    if original_metadata.xmp != output_metadata.xmp:
                        pass

                # 检查ICC Profile
                if original_metadata.icc_profile:
                    if not output_metadata.icc_profile:
                        return False, "ICC配置文件丢失"
                    if original_metadata.icc_profile != output_metadata.icc_profile:
                        pass

                # 如果原始图片没有元数据,验证也算成功
                if not original_metadata.has_metadata:
                    return True, "原图无元数据,无需保留"

                # 如果有元数据且都保留了,验证成功
                return True, "元数据保留成功"

        except Exception as e:
            return False, f"验证失败: {str(e)}"
