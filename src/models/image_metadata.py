"""
图片元数据实体

封装EXIF/IPTC/XMP元数据,用于转换时保留原始信息。
"""

from dataclasses import dataclass
from typing import Optional
from PIL import Image


@dataclass
class ImageMetadata:
    """图片元数据实体"""

    exif: Optional[bytes] = None
    xmp: Optional[bytes] = None
    icc_profile: Optional[bytes] = None

    @property
    def has_metadata(self) -> bool:
        """是否包含任何元数据"""
        return any([self.exif, self.xmp, self.icc_profile])

    @classmethod
    def from_pil_image(cls, pil_image: Image.Image) -> "ImageMetadata":
        """从Pillow Image对象提取元数据"""
        exif = None
        xmp = None
        icc_profile = None

        # 提取EXIF
        if 'exif' in pil_image.info:
            exif = pil_image.info['exif']

        # 提取XMP
        if 'xmp' in pil_image.info:
            xmp = pil_image.info['xmp']

        # 提取ICC色彩配置文件
        if 'icc_profile' in pil_image.info:
            icc_profile = pil_image.info['icc_profile']

        return cls(exif=exif, xmp=xmp, icc_profile=icc_profile)

    def to_save_params(self) -> dict:
        """返回用于Pillow保存时的参数字典"""
        params = {}

        if self.exif is not None:
            params['exif'] = self.exif

        if self.xmp is not None:
            params['xmp'] = self.xmp

        if self.icc_profile is not None:
            params['icc_profile'] = self.icc_profile

        return params
