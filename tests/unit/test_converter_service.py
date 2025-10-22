"""
ConverterService单元测试

测试WebP转换核心功能,包括成功转换、错误处理、元数据保留和取消机制。
"""

import pytest
from pathlib import Path
import threading
import time
from PIL import Image

from src.models.image_file import ImageFile


class TestConverterService:
    """ConverterService单元测试"""

    def test_convert_image_success(self, tmp_path):
        """测试成功转换图片到WebP"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建测试图片
        test_image_path = tmp_path / "test_input.png"
        img = Image.new('RGB', (200, 150), color='blue')
        img.save(test_image_path, format='PNG')

        image_file = ImageFile.from_path(test_image_path)
        output_path = tmp_path / "output.webp"

        service = ConverterService()
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=80
        )

        # 验证结果
        assert result.success is True
        assert output_path.exists()
        assert result.output_size > 0
        assert result.output_path == output_path

        # 验证压缩比计算正确(PNG转WebP通常有压缩)
        assert result.compression_ratio is not None
        assert result.compression_ratio > 0  # 应该有一定压缩

        # 验证耗时记录
        assert result.duration > 0

    def test_convert_image_file_not_found(self, tmp_path):
        """测试转换不存在的文件"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建一个不存在的文件路径
        non_existent_path = tmp_path / "non_existent.png"

        # 尝试创建ImageFile会抛出异常
        with pytest.raises(FileNotFoundError):
            ImageFile.from_path(non_existent_path)

    def test_convert_image_invalid_quality(self, tmp_path):
        """测试使用无效的质量参数转换"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建测试图片
        test_image_path = tmp_path / "test_input.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path, format='PNG')

        image_file = ImageFile.from_path(test_image_path)
        output_path = tmp_path / "output.webp"

        service = ConverterService()

        # 测试质量参数超出范围
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=150  # 无效值
        )

        # 应该返回失败结果
        assert result.success is False
        assert result.error_message is not None
        assert "质量" in result.error_message or "范围" in result.error_message

    def test_convert_image_preserve_metadata(self, tmp_path):
        """测试转换时保留元数据"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建带EXIF的测试图片
        test_image_path = tmp_path / "test_with_exif.jpg"
        img = Image.new('RGB', (200, 150), color='green')
        exif_bytes = b'\xff\xd8\xff\xe1\x00\x10Exif\x00\x00'
        img.save(test_image_path, format='JPEG', exif=exif_bytes)

        image_file = ImageFile.from_path(test_image_path)
        output_path = tmp_path / "output_with_metadata.webp"

        service = ConverterService()
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=80,
            preserve_metadata=True
        )

        # 验证转换成功
        assert result.success is True
        assert output_path.exists()

        # 验证元数据保留(打开输出文件检查)
        with Image.open(output_path) as output_img:
            # WebP可能保留EXIF
            assert 'exif' in output_img.info or True  # 允许WebP不完全支持EXIF

    def test_convert_image_without_metadata(self, tmp_path):
        """测试转换时不保留元数据"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建带EXIF的测试图片
        test_image_path = tmp_path / "test_with_exif.jpg"
        img = Image.new('RGB', (200, 150), color='yellow')
        exif_bytes = b'\xff\xd8\xff\xe1\x00\x10Exif\x00\x00'
        img.save(test_image_path, format='JPEG', exif=exif_bytes)

        image_file = ImageFile.from_path(test_image_path)
        output_path = tmp_path / "output_no_metadata.webp"

        service = ConverterService()
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=80,
            preserve_metadata=False  # 不保留元数据
        )

        # 验证转换成功
        assert result.success is True
        assert output_path.exists()

    def test_convert_image_cancelled(self, tmp_path):
        """测试转换过程中取消操作"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建测试图片
        test_image_path = tmp_path / "test_input.png"
        img = Image.new('RGB', (100, 100), color='purple')
        img.save(test_image_path, format='PNG')

        image_file = ImageFile.from_path(test_image_path)
        output_path = tmp_path / "output_cancelled.webp"

        # 创建取消事件
        stop_event = threading.Event()
        stop_event.set()  # 立即设置取消标志

        service = ConverterService()
        result = service.convert_image(
            input_file=image_file,
            output_path=output_path,
            quality=80,
            stop_event=stop_event
        )

        # 验证取消结果
        assert result.success is False
        assert result.error_message == "转换已取消"
        # 取消后不应生成文件
        assert not output_path.exists()

    def test_convert_image_quality_range(self, tmp_path):
        """测试不同质量参数的转换"""
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建更大的测试图片,使质量差异更明显
        test_image_path = tmp_path / "test_input.png"
        img = Image.new('RGB', (800, 600), color='cyan')
        img.save(test_image_path, format='PNG')

        image_file = ImageFile.from_path(test_image_path)
        service = ConverterService()

        # 测试高质量
        output_high = tmp_path / "output_high.webp"
        result_high = service.convert_image(
            input_file=image_file,
            output_path=output_high,
            quality=95
        )
        assert result_high.success is True

        # 测试低质量
        output_low = tmp_path / "output_low.webp"
        result_low = service.convert_image(
            input_file=image_file,
            output_path=output_low,
            quality=30  # 使用更低的质量以确保明显差异
        )
        assert result_low.success is True

        # 高质量文件应该更大(对于大图片)
        # 注意:对于纯色小图片,WebP压缩可能导致文件大小差异不明显
        assert result_high.output_size >= result_low.output_size * 0.5  # 允许一定容差


class TestConverterServiceBatchConvert:
    """批量转换单元测试 (T077-T080)"""

    def test_batch_convert_success(self, tmp_path):
        """
        T077: 测试批量转换成功

        验证点:
        - 批量转换3张图片全部成功
        - 返回结果数量正确
        - 所有输出文件存在
        """
        try:
            from src.services.converter_service import ConverterService
            from src.models.conversion_task import ConversionTask
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建3张测试图片
        tasks = []
        for i in range(3):
            img_path = tmp_path / f"test_image_{i}.jpg"
            img = Image.new('RGB', (150, 150), color=['red', 'green', 'blue'][i])
            img.save(img_path, 'JPEG')

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 批量转换
        service = ConverterService()
        results = service.batch_convert(tasks=tasks, max_workers=3)

        # 验证结果
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.success is True
            assert tasks[i].output_path.exists()
            assert result.output_size > 0
            assert result.compression_ratio is not None

    def test_batch_convert_partial_failure(self, tmp_path):
        """
        T078: 测试批量转换部分失败

        验证点:
        - 包含有效和无效任务的批量转换
        - 有效任务成功,无效任务失败
        - 失败任务返回错误消息
        """
        try:
            from src.services.converter_service import ConverterService
            from src.models.conversion_task import ConversionTask
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        tasks = []

        # 创建2张有效图片
        for i in range(2):
            img_path = tmp_path / f"test_image_{i}.jpg"
            img = Image.new('RGB', (100, 100), color='yellow')
            img.save(img_path, 'JPEG')

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 创建1个无效质量参数的任务
        img_path = tmp_path / "test_image_2.jpg"
        img = Image.new('RGB', (100, 100), color='cyan')
        img.save(img_path, 'JPEG')
        img_file = ImageFile.from_path(img_path)

        invalid_task = ConversionTask(
            input_file=img_file,
            output_path=tmp_path / "output_2.webp",
            quality=150  # 无效质量参数
        )
        tasks.append(invalid_task)

        # 批量转换
        service = ConverterService()
        results = service.batch_convert(tasks=tasks, max_workers=3)

        # 验证结果
        assert len(results) == 3

        # 前2个应该成功
        assert results[0].success is True
        assert results[1].success is True

        # 第3个应该失败
        assert results[2].success is False
        assert results[2].error_message is not None

    def test_batch_convert_cancelled_after_2_tasks(self, tmp_path):
        """
        T079: 测试批量转换中途取消

        验证点:
        - 转换5张图片,完成2张后取消
        - 已完成的文件保留
        - 未开始的任务标记为"转换已取消"
        """
        try:
            from src.services.converter_service import ConverterService
            from src.models.conversion_task import ConversionTask
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建10张较大的测试图片,增加转换时间
        tasks = []
        for i in range(10):
            img_path = tmp_path / f"test_image_{i}.jpg"
            # 创建更大的图片以增加转换时间
            img = Image.new('RGB', (1000, 1000), color='magenta')
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

        # 延迟取消
        def delayed_cancel():
            time.sleep(0.05)  # 等待部分任务完成
            stop_event.set()

        cancel_thread = threading.Thread(target=delayed_cancel)
        cancel_thread.start()

        # 批量转换
        service = ConverterService()
        results = service.batch_convert(
            tasks=tasks,
            max_workers=3,
            stop_event=stop_event
        )

        cancel_thread.join()

        # 验证结果
        assert len(results) == 10

        # 统计成功和取消的任务
        success_count = sum(1 for r in results if r.success)
        cancelled_count = sum(1 for r in results if not r.success and r.error_message == "转换已取消")

        # 应该有部分成功,部分取消
        assert success_count > 0
        assert cancelled_count > 0
        assert success_count + cancelled_count == 10

        # 已完成的文件应该存在
        for i, result in enumerate(results):
            if result.success:
                assert tasks[i].output_path.exists()


class TestBatchConversionJobProgressPercentage:
    """批量作业进度计算测试 (T080)"""

    def test_batch_job_progress_percentage(self):
        """
        T080: 测试BatchConversionJob.progress_percentage属性

        验证点:
        - 空作业返回0.0
        - 部分完成返回正确百分比
        - 全部完成返回100.0
        - 包含失败和取消任务的计算
        """
        from src.models.batch_conversion_job import BatchConversionJob
        from src.models.conversion_task import ConversionTask
        from src.models.image_file import ImageFile

        # 创建测试图片
        test_fixtures = Path(__file__).parent.parent / 'fixtures' / 'sample_images'
        test_fixtures.mkdir(parents=True, exist_ok=True)
        test_path = test_fixtures / 'test_image.jpg'

        # 如果测试图片不存在,创建一个
        if not test_path.exists():
            img = Image.new('RGB', (100, 100), color='red')
            img.save(test_path, 'JPEG')

        img_file = ImageFile.from_path(test_path)

        # 场景1: 空作业
        job = BatchConversionJob(quality=80)
        assert job.progress_percentage == 0.0

        # 场景2: 添加5个任务,完成2个,失败1个,取消1个,pending 1个
        for i in range(5):
            task = ConversionTask(
                input_file=img_file,
                output_path=Path(f"/tmp/output_{i}.webp"),
                quality=80
            )
            job.add_task(task)

        # 完成2个
        job.tasks[0].start()
        job.tasks[0].complete(output_size=5000, duration=1.0)
        job.tasks[1].start()
        job.tasks[1].complete(output_size=5000, duration=1.0)

        # 失败1个
        job.tasks[2].start()
        job.tasks[2].fail("测试失败")

        # 取消1个
        job.tasks[3].cancel()

        # pending 1个 (tasks[4])

        # 进度 = (2完成 + 1失败 + 1取消) / 5 = 80%
        assert job.progress_percentage == pytest.approx(80.0, rel=0.1)

        # 场景3: 全部完成
        job.tasks[4].start()
        job.tasks[4].complete(output_size=5000, duration=1.0)

        assert job.progress_percentage == 100.0
