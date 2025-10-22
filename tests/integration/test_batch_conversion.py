"""
批量转换集成测试

测试完整的批量转换工作流程,包括性能验证。
"""

import pytest
from pathlib import Path
import time
from PIL import Image

from src.models.image_file import ImageFile
from src.models.conversion_task import ConversionTask


class TestBatchConversionIntegration:
    """批量转换集成测试 (T081)"""

    def test_batch_convert_10_images(self, tmp_path):
        """
        T081: 测试批量转换10张图片的性能

        验证点:
        - 批量转换10张5MB图片
        - 总耗时 < 60秒 (性能要求)
        - 所有图片转换成功
        - 输出文件正确生成
        """
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建10张约5MB的测试图片
        tasks = []
        for i in range(10):
            # 创建约5MB的图片 (约2000x2000像素,JPEG质量95)
            img_path = tmp_path / f"large_image_{i}.jpg"
            img = Image.new('RGB', (2000, 2000), color='blue')

            # 填充一些渐变以确保文件大小
            pixels = img.load()
            for x in range(2000):
                for y in range(2000):
                    pixels[x, y] = (
                        (x * 255 // 2000),
                        (y * 255 // 2000),
                        ((x + y) * 255 // 4000)
                    )

            img.save(img_path, 'JPEG', quality=95)

            # 验证文件大小接近5MB
            file_size_mb = img_path.stat().st_size / (1024 * 1024)
            print(f"Image {i} size: {file_size_mb:.2f} MB")

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 记录开始时间
        start_time = time.time()

        # 批量转换
        service = ConverterService()
        results = service.batch_convert(tasks=tasks, max_workers=3)

        # 计算耗时
        duration = time.time() - start_time

        # 验证结果
        assert len(results) == 10

        # 所有转换应该成功
        success_count = sum(1 for r in results if r.success)
        assert success_count == 10, f"只有{success_count}个任务成功,应该全部成功"

        # 所有输出文件应该存在
        for i, result in enumerate(results):
            assert tasks[i].output_path.exists(), f"输出文件{i}不存在"
            assert result.output_size > 0, f"输出文件{i}大小为0"

        # 性能验证: 总耗时 < 60秒
        print(f"\n批量转换10张图片耗时: {duration:.2f}秒")
        assert duration < 60, f"批量转换耗时{duration:.2f}秒,超过60秒限制"

    def test_batch_convert_with_progress_tracking(self, tmp_path):
        """
        测试批量转换进度跟踪

        验证点:
        - 进度回调正确调用
        - 进度从0到100%
        - 每个步骤的进度正确
        """
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建5张测试图片
        tasks = []
        for i in range(5):
            img_path = tmp_path / f"test_image_{i}.jpg"
            img = Image.new('RGB', (300, 300), color='green')
            img.save(img_path, 'JPEG')

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 跟踪进度
        progress_history = []

        def on_progress(completed, total):
            progress_pct = (completed / total) * 100
            progress_history.append((completed, total, progress_pct))
            print(f"进度: {completed}/{total} ({progress_pct:.1f}%)")

        # 批量转换
        service = ConverterService()
        results = service.batch_convert(
            tasks=tasks,
            max_workers=3,
            progress_callback=on_progress
        )

        # 验证进度跟踪
        assert len(progress_history) == 5

        # 验证进度递增
        for i, (completed, total, pct) in enumerate(progress_history):
            assert total == 5
            assert completed == i + 1
            assert pct == (i + 1) * 20  # 0%, 20%, 40%, 60%, 80%, 100%

        # 验证所有任务成功
        assert all(r.success for r in results)

    def test_batch_convert_mixed_formats(self, tmp_path):
        """
        测试批量转换混合格式图片

        验证点:
        - 支持JPEG, PNG, GIF等多种格式
        - 所有格式都能成功转换为WebP
        """
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建不同格式的测试图片
        formats = [
            ('JPEG', 'test_image.jpg'),
            ('PNG', 'test_image.png'),
            ('GIF', 'test_image.gif'),
        ]

        tasks = []
        for i, (fmt, filename) in enumerate(formats):
            img_path = tmp_path / filename
            img = Image.new('RGB', (200, 200), color=['red', 'green', 'blue'][i])
            img.save(img_path, format=fmt)

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

        # 验证所有格式都转换成功
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.success is True, f"格式{formats[i][0]}转换失败"
            assert tasks[i].output_path.exists()

    def test_batch_convert_concurrency(self, tmp_path):
        """
        测试批量转换并发控制

        验证点:
        - max_workers参数生效
        - 并发转换正确执行
        - 结果顺序与任务顺序对应
        """
        try:
            from src.services.converter_service import ConverterService
        except ImportError:
            pytest.skip("ConverterService尚未实现")

        # 创建6张测试图片
        tasks = []
        for i in range(6):
            img_path = tmp_path / f"test_image_{i}.jpg"
            img = Image.new('RGB', (400, 400), color='purple')
            img.save(img_path, 'JPEG')

            img_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                input_file=img_file,
                output_path=output_path,
                quality=80
            )
            tasks.append(task)

        # 使用max_workers=2限制并发
        service = ConverterService()
        results = service.batch_convert(tasks=tasks, max_workers=2)

        # 验证结果
        assert len(results) == 6

        # 验证结果顺序与任务顺序对应
        for i, (task, result) in enumerate(zip(tasks, results)):
            assert result.output_path == task.output_path
            assert result.success is True
