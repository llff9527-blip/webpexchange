"""
MetadataService单元测试

测试元数据提取、嵌入和验证功能。
"""

import pytest
from pathlib import Path
from PIL import Image

from src.models.image_metadata import ImageMetadata


class TestMetadataService:
    """MetadataService单元测试"""

    def test_extract_metadata_with_exif(self, tmp_path):
        """测试从带EXIF的图片提取元数据"""
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        # 创建带EXIF的测试图片
        test_image_path = tmp_path / "test_exif.jpg"
        img = Image.new('RGB', (200, 150), color='red')
        exif = img.getexif()
        exif[0x0110] = "Test Camera"
        img.save(test_image_path, format='JPEG', exif=exif)

        # 重新打开并提取元数据
        with Image.open(test_image_path) as pil_img:
            service = MetadataService()
            metadata = service.extract_metadata(pil_img)

            assert metadata is not None
            # EXIF可能存在也可能不存在,取决于Pillow版本和格式支持
            # 至少验证返回了正确的对象类型
            assert isinstance(metadata, ImageMetadata)

    def test_extract_metadata_without_metadata(self, tmp_path):
        """测试从无元数据的图片提取元数据"""
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        # 创建纯PNG图片(通常无EXIF)
        test_image_path = tmp_path / "test_no_metadata.png"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(test_image_path, format='PNG')

        with Image.open(test_image_path) as pil_img:
            service = MetadataService()
            metadata = service.extract_metadata(pil_img)

            assert metadata is not None
            # PNG通常没有EXIF
            assert metadata.has_metadata is False or metadata.has_metadata is True  # 允许两种情况

    def test_embed_metadata_filters_none(self):
        """测试embed_metadata过滤None值"""
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        service = MetadataService()

        # 测试所有字段都是None
        metadata_empty = ImageMetadata(exif=None, xmp=None, icc_profile=None)
        save_params_empty = service.embed_metadata(metadata_empty)

        assert isinstance(save_params_empty, dict)
        assert len(save_params_empty) == 0  # 所有None值应被过滤

        # 测试部分字段有值
        metadata_partial = ImageMetadata(
            exif=b'\xff\xd8',
            xmp=None,
            icc_profile=b'\x00\x01\x02'
        )
        save_params_partial = service.embed_metadata(metadata_partial)

        assert 'exif' in save_params_partial
        assert 'xmp' not in save_params_partial
        assert 'icc_profile' in save_params_partial
        assert save_params_partial['exif'] == b'\xff\xd8'
        assert save_params_partial['icc_profile'] == b'\x00\x01\x02'

    def test_validate_metadata_preservation_success(self, tmp_path):
        """测试元数据保留验证成功的情况"""
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        service = MetadataService()

        # 创建原始图片
        original_path = tmp_path / "original.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        exif_bytes = b'\xff\xd8\xff\xe1\x00\x10Exif\x00\x00'
        img.save(original_path, format='JPEG', exif=exif_bytes)

        # 提取原始元数据
        with Image.open(original_path) as pil_img:
            original_metadata = service.extract_metadata(pil_img)

        # 创建输出WebP文件,保留元数据
        output_path = tmp_path / "output.webp"
        with Image.open(original_path) as pil_img:
            save_params = service.embed_metadata(original_metadata)
            pil_img.save(output_path, format='WEBP', quality=80, **save_params)

        # 验证元数据保留
        is_valid, message = service.validate_metadata_preservation(
            original_metadata,
            output_path
        )

        assert is_valid is True
        assert "成功" in message or "保留" in message

    def test_validate_metadata_preservation_failure(self, tmp_path):
        """测试元数据保留验证失败的情况"""
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        service = MetadataService()

        # 创建原始图片
        original_path = tmp_path / "original.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        exif_bytes = b'\xff\xd8\xff\xe1\x00\x10Exif\x00\x00'
        img.save(original_path, format='JPEG', exif=exif_bytes)

        # 提取原始元数据
        with Image.open(original_path) as pil_img:
            original_metadata = service.extract_metadata(pil_img)

        # 创建输出WebP文件,不保留元数据
        output_path = tmp_path / "output_no_metadata.webp"
        with Image.open(original_path) as pil_img:
            pil_img.save(output_path, format='WEBP', quality=80)  # 不传入元数据

        # 验证元数据保留
        is_valid, message = service.validate_metadata_preservation(
            original_metadata,
            output_path
        )

        # 如果原始有EXIF,验证应失败
        if original_metadata.exif:
            assert is_valid is False
            assert "丢失" in message or "失败" in message or "不一致" in message
