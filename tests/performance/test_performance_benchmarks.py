"""
性能基准测试

验证系统满足性能要求:
- SC-003: 10MB图片转换<5秒
- SC-007: 10张5MB图片批量转换<60秒
"""

import pytest
import time
from pathlib import Path
from PIL import Image
import tempfile

from src.services.converter_service import ConverterService
from src.models.image_file import ImageFile
from src.models.conversion_task import ConversionTask


@pytest.fixture
def converter_service():
    """转换服务fixture"""
    return ConverterService()


@pytest.fixture
def create_test_image():
    """创建测试图片的工厂函数"""
    def _create_image(size_mb: float, width: int = 2000, height: int = 1500):
        """
        创建指定大小的测试图片

        Args:
            size_mb: 目标大小(MB)
            width: 图片宽度
            height: 图片高度

        Returns:
            Path: 测试图片路径
        """
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img_path = Path(tmp.name)

        # 创建图片
        img = Image.new('RGB', (width, height))

        # 填充随机像素以达到目标大小
        import random
        pixels = img.load()
        for x in range(width):
            for y in range(height):
                pixels[x, y] = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )

        # 保存并调整质量直到达到目标大小
        target_bytes = size_mb * 1024 * 1024
        quality = 95

        while quality > 10:
            img.save(img_path, quality=quality)
            current_size = img_path.stat().st_size

            if current_size >= target_bytes * 0.9:  # 允许10%误差
                break

            quality -= 5

        return img_path

    return _create_image


def test_10mb_image_conversion_performance(converter_service, create_test_image, tmp_path):
    """
    测试10MB图片转换性能

    性能要求: SC-003 - 10MB图片转换<5秒

    验证:
    - 转换成功
    - 耗时<5秒
    """
    # 创建10MB测试图片
    print("\n创建10MB测试图片...")
    test_image = create_test_image(size_mb=10.0, width=4000, height=3000)

    try:
        # 验证图片大小
        size_mb = test_image.stat().st_size / (1024 * 1024)
        print(f"测试图片大小: {size_mb:.2f} MB")

        assert size_mb >= 9.0, "测试图片大小不足10MB"

        # 创建ImageFile
        image_file = ImageFile.from_path(test_image)

        # 输出路径
        output_path = tmp_path / "output_10mb.webp"

        # 记录开始时间
        start_time = time.time()

        # 执行转换
        print("开始转换...")
        result = converter_service.convert_image(
            image_file=image_file,
            output_path=output_path,
            quality=80,
            preserve_metadata=True
        )

        # 计算耗时
        duration = time.time() - start_time

        # 验证转换成功
        assert result.success is True, f"转换失败: {result.error_message}"
        assert output_path.exists(), "输出文件不存在"

        # 验证性能要求
        print(f"转换耗时: {duration:.2f} 秒")
        print(f"性能要求: < 5.00 秒")

        assert duration < 5.0, f"转换耗时{duration:.2f}秒,超过5秒性能要求"

        # 显示压缩比
        output_size_mb = output_path.stat().st_size / (1024 * 1024)
        compression_ratio = (1 - output_size_mb / size_mb) * 100
        print(f"压缩比: {compression_ratio:.1f}%")
        print(f"输出大小: {output_size_mb:.2f} MB")

        print("✓ 性能测试通过 (SC-003)")

    finally:
        # 清理测试文件
        if test_image.exists():
            test_image.unlink()


def test_batch_conversion_performance(converter_service, create_test_image, tmp_path):
    """
    测试批量转换性能

    性能要求: SC-007 - 10张5MB图片批量转换<60秒

    验证:
    - 所有图片转换成功
    - 总耗时<60秒
    """
    # 创建10张5MB测试图片
    num_images = 10
    target_size_mb = 5.0

    print(f"\n创建{num_images}张{target_size_mb}MB测试图片...")

    test_images = []
    for i in range(num_images):
        img_path = create_test_image(
            size_mb=target_size_mb,
            width=3000,
            height=2000
        )
        test_images.append(img_path)
        size_mb = img_path.stat().st_size / (1024 * 1024)
        print(f"  图片 {i+1}/{num_images}: {size_mb:.2f} MB")

    try:
        # 创建转换任务
        tasks = []
        for i, img_path in enumerate(test_images):
            image_file = ImageFile.from_path(img_path)
            output_path = tmp_path / f"output_{i}.webp"

            task = ConversionTask(
                image_file=image_file,
                output_path=output_path,
                quality=80,
                preserve_metadata=True
            )
            tasks.append(task)

        # 记录开始时间
        start_time = time.time()

        # 执行批量转换
        print(f"\n开始批量转换{num_images}张图片...")
        results = converter_service.batch_convert(
            tasks=tasks,
            max_workers=3
        )

        # 计算耗时
        duration = time.time() - start_time

        # 验证所有转换成功
        success_count = sum(1 for r in results if r.success)
        print(f"\n转换完成: {success_count}/{num_images} 成功")
        print(f"总耗时: {duration:.2f} 秒")
        print(f"性能要求: < 60.00 秒")

        assert success_count == num_images, f"部分转换失败({success_count}/{num_images})"

        # 验证性能要求
        assert duration < 60.0, f"批量转换耗时{duration:.2f}秒,超过60秒性能要求"

        # 计算平均耗时
        avg_duration = duration / num_images
        print(f"平均单张耗时: {avg_duration:.2f} 秒")

        # 计算总压缩比
        total_input_size = sum(img.stat().st_size for img in test_images)
        total_output_size = sum(
            task.output_path.stat().st_size
            for task in tasks
            if task.output_path.exists()
        )

        total_compression = (1 - total_output_size / total_input_size) * 100
        print(f"总压缩比: {total_compression:.1f}%")

        print("✓ 性能测试通过 (SC-007)")

    finally:
        # 清理测试文件
        for img_path in test_images:
            if img_path.exists():
                img_path.unlink()


def test_small_image_conversion_speed(converter_service, tmp_path):
    """
    测试小图片转换速度

    验证:
    - 1MB图片转换<2秒
    """
    # 创建1MB测试图片
    test_image = tmp_path / "small_test.jpg"
    img = Image.new('RGB', (800, 600), color='blue')
    img.save(test_image, quality=90)

    size_mb = test_image.stat().st_size / (1024 * 1024)
    print(f"\n小图片大小: {size_mb:.2f} MB")

    # 创建ImageFile
    image_file = ImageFile.from_path(test_image)

    # 输出路径
    output_path = tmp_path / "output_small.webp"

    # 记录开始时间
    start_time = time.time()

    # 执行转换
    result = converter_service.convert_image(
        image_file=image_file,
        output_path=output_path,
        quality=80,
        preserve_metadata=True
    )

    # 计算耗时
    duration = time.time() - start_time

    # 验证转换成功
    assert result.success is True
    assert output_path.exists()

    # 验证性能
    print(f"小图片转换耗时: {duration:.2f} 秒")
    assert duration < 2.0, f"小图片转换耗时{duration:.2f}秒,超过2秒"

    print("✓ 小图片转换性能测试通过")


def test_memory_usage_large_image(converter_service, create_test_image, tmp_path):
    """
    测试大图片转换的内存占用

    验证:
    - 50MB图片转换不崩溃
    - 内存增长在合理范围内
    """
    import psutil
    import os

    # 创建50MB测试图片
    print("\n创建50MB测试图片(用于内存测试)...")
    test_image = create_test_image(size_mb=50.0, width=6000, height=4000)

    try:
        size_mb = test_image.stat().st_size / (1024 * 1024)
        print(f"测试图片大小: {size_mb:.2f} MB")

        # 获取当前进程
        process = psutil.Process(os.getpid())

        # 记录转换前内存
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB
        print(f"转换前内存: {mem_before:.2f} MB")

        # 创建ImageFile
        image_file = ImageFile.from_path(test_image)

        # 输出路径
        output_path = tmp_path / "output_50mb.webp"

        # 执行转换
        result = converter_service.convert_image(
            image_file=image_file,
            output_path=output_path,
            quality=80,
            preserve_metadata=True
        )

        # 记录转换后内存
        mem_after = process.memory_info().rss / (1024 * 1024)  # MB
        print(f"转换后内存: {mem_after:.2f} MB")

        # 计算内存增长
        mem_increase = mem_after - mem_before
        print(f"内存增长: {mem_increase:.2f} MB")

        # 验证转换成功
        assert result.success is True, "大图片转换失败"
        assert output_path.exists(), "输出文件不存在"

        # 验证内存增长在合理范围(不超过图片大小的2倍)
        assert mem_increase < size_mb * 2, f"内存增长过大: {mem_increase:.2f}MB"

        print("✓ 内存占用测试通过")

    finally:
        # 清理测试文件
        if test_image.exists():
            test_image.unlink()


if __name__ == "__main__":
    """允许直接运行性能测试"""
    pytest.main([__file__, "-v", "-s"])
