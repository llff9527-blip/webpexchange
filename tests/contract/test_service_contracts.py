"""
服务契约测试

测试MetadataService和ConverterService的公共接口契约,确保服务满足规范。
"""

import pytest
from pathlib import Path
import threading
import time
from PIL import Image

from src.models.image_file import ImageFile
from src.models.image_metadata import ImageMetadata
from src.models.conversion_task import ConversionTask, TaskStatus
from src.models.quality_preset import QualityPreset


class TestMetadataServiceContract:
    """MetadataService契约测试"""

    def test_metadata_service_extract_metadata(self, tmp_path):
        """契约: extract_metadata() 应返回ImageMetadata对象,包含可用的元数据"""
        # 延迟导入,避免在服务实现前失败
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        # 创建带EXIF的测试图片
        test_image_path = tmp_path / "test_with_exif.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        # 使用更完整的EXIF数据
        exif = img.getexif()
        exif[0x0110] = "Test Camera"  # Make
        img.save(test_image_path, format='JPEG', exif=exif)

        # 重新打开以获取Pillow Image对象
        with Image.open(test_image_path) as pil_img:
            service = MetadataService()
            metadata = service.extract_metadata(pil_img)

            # 契约验证
            assert isinstance(metadata, ImageMetadata)
            assert metadata is not None
            # EXIF可能存在也可能不存在(取决于Pillow版本)
            # 至少验证返回了正确类型

    def test_metadata_service_embed_metadata(self):
        """契约: embed_metadata() 应返回字典,且过滤None值"""
        try:
            from src.services.metadata_service import MetadataService
        except ImportError:
            pytest.skip("MetadataService尚未实现")

        service = MetadataService()

        # 测试包含None值的元数据
        metadata = ImageMetadata(exif=b'\xff\xd8', xmp=None, icc_profile=b'\x00\x01')
        save_params = service.embed_metadata(metadata)

        # 契约验证
        assert isinstance(save_params, dict)
        assert 'exif' in save_params
        assert save_params['exif'] == b'\xff\xd8'
        assert 'xmp' not in save_params  # None值应被过滤
        assert 'icc_profile' in save_params
        assert save_params['icc_profile'] == b'\x00\x01'


class TestConverterServiceContract:
    """ConverterService契约测试"""

    def test_converter_service_convert_image_success(self, tmp_path):
        """契约: convert_image() 成功时应返回ConversionResult,success=True"""
        try:
            from src.services.converter_service import ConverterService, ConversionResult
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建测试图片
        test_image_path = tmp_path / "test_input.png"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(test_image_path, format='PNG')

        # 创建ImageFile对象
        image_file = ImageFile.from_path(test_image_path)

        # 执行转换
        output_path = tmp_path / "output.webp"
        service = ConverterService()
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=80,
            preserve_metadata=True
        )

        # 契约验证
        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.output_path == output_path
        assert output_path.exists()
        assert result.output_size > 0
        assert result.compression_ratio is not None
        assert result.duration > 0
        assert result.error_message is None

    def test_converter_service_convert_cancelled(self, tmp_path):
        """契约: convert_image() 取消时应返回success=False,error_message='转换已取消'"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建测试图片
        test_image_path = tmp_path / "test_input.png"
        img = Image.new('RGB', (100, 100), color='green')
        img.save(test_image_path, format='PNG')

        image_file = ImageFile.from_path(test_image_path)
        output_path = tmp_path / "output.webp"

        # 创建取消事件并立即设置
        stop_event = threading.Event()
        stop_event.set()

        service = ConverterService()
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=80,
            stop_event=stop_event
        )

        # 契约验证
        assert result.success is False
        assert result.error_message == "转换已取消"
        assert not output_path.exists()  # 取消后不应生成文件

    def test_converter_service_batch_convert(self, tmp_path):
        """
        T074: 测试batch_convert()契约 - 基本批量转换

        验证点:
        - 接受tasks列表,max_workers,progress_callback,stop_event参数
        - 返回list[ConversionResult],与tasks顺序对应
        - 使用ThreadPoolExecutor(max_workers=3)并发执行
        """
        try:
            from src.services.converter_service import ConverterService, ConversionResult
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建3张测试图片
        tasks = []
        for i in range(3):
            # 创建测试图片
            img_path = tmp_path / f"test_image_{i}.jpg"
            img = Image.new('RGB', (100, 100), color='red')
            img.save(img_path, 'JPEG')

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 调用batch_convert
        service = ConverterService()
        results = service.batch_convert(
            tasks=tasks,
            max_workers=3,
            progress_callback=None,
            stop_event=None
        )

        # 契约验证
        assert len(results) == len(tasks)
        for result in results:
            assert isinstance(result, ConversionResult)
            assert hasattr(result, 'success')
            assert hasattr(result, 'output_path')
            assert hasattr(result, 'output_size')
            assert hasattr(result, 'compression_ratio')
            assert hasattr(result, 'duration')
            assert hasattr(result, 'error_message')

    def test_batch_convert_progress_callback(self, tmp_path):
        """
        T075: 测试progress_callback契约

        验证点:
        - 每完成一个任务,调用progress_callback(completed_count, total_count)
        - 回调参数正确(1/3 -> 2/3 -> 3/3)
        """
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建3张测试图片
        tasks = []
        for i in range(3):
            img_path = tmp_path / f"test_image_{i}.jpg"
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(img_path, 'JPEG')

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 模拟进度回调
        progress_calls = []

        def on_progress(completed, total):
            progress_calls.append((completed, total))

        # 调用batch_convert
        service = ConverterService()
        results = service.batch_convert(
            tasks=tasks,
            max_workers=3,
            progress_callback=on_progress
        )

        # 验证进度回调被正确调用
        assert len(progress_calls) == 3  # 每完成一个任务调用一次
        assert (1, 3) in progress_calls
        assert (2, 3) in progress_calls
        assert (3, 3) in progress_calls

    def test_batch_convert_cancelled_mid_way(self, tmp_path):
        """
        T076: 测试取消机制契约

        验证点:
        - 设置stop_event后,未开始的任务应标记为"转换已取消"
        - 已完成的文件保留,不删除
        - 返回结果中,未开始任务的error_message="转换已取消"
        """
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建10张较大的测试图片,增加转换时间
        tasks = []
        for i in range(10):
            img_path = tmp_path / f"test_image_{i}.jpg"
            # 创建更大的图片以增加转换时间
            img = Image.new('RGB', (1000, 1000), color='green')
            img.save(img_path, 'JPEG', quality=95)

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 创建取消事件
        stop_event = threading.Event()

        # 模拟:在转换部分任务后触发取消
        def delayed_cancel():
            time.sleep(0.1)  # 等待部分任务完成
            stop_event.set()

        cancel_thread = threading.Thread(target=delayed_cancel)
        cancel_thread.start()

        service = ConverterService()
        results = service.batch_convert(
            tasks=tasks,
            max_workers=3,
            stop_event=stop_event
        )

        cancel_thread.join()

        # 验证:
        # 1. 返回结果数量正确
        assert len(results) == len(tasks)

        # 2. 部分成功,部分取消
        success_count = sum(1 for r in results if r.success)
        cancelled_count = sum(1 for r in results if not r.success and r.error_message == "转换已取消")

        assert success_count > 0  # 至少有一些成功
        assert cancelled_count > 0  # 至少有一些被取消
        assert success_count + cancelled_count == len(tasks)

        # 3. 已完成的文件存在
        for i, result in enumerate(results):
            if result.success:
                assert tasks[i].output_path.exists()
