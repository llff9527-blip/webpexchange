"""
测试核心数据模型

测试目标:
- ImageMetadata: 元数据提取和保存参数
- QualityPreset: 质量预设枚举
- ImageFile: 图片文件实体及验证逻辑
- ConversionTask: 转换任务状态转换
- BatchConversionJob: 批量作业进度计算
"""

import pytest
from pathlib import Path
from datetime import datetime
from PIL import Image
import tempfile
import os


# ============= ImageMetadata 测试 =============

def test_image_metadata_from_pil_image_with_exif():
    """测试从带EXIF的PIL Image提取元数据"""
    from src.models.image_metadata import ImageMetadata

    # 创建带EXIF的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    exif_data = b'\xff\xd8\xff\xe1'  # 简单的EXIF头部

    # 手动设置info
    img.info['exif'] = exif_data

    metadata = ImageMetadata.from_pil_image(img)

    assert metadata is not None
    assert metadata.exif == exif_data
    assert metadata.has_metadata is True


def test_image_metadata_from_pil_image_without_metadata():
    """测试从无元数据的PIL Image提取"""
    from src.models.image_metadata import ImageMetadata

    img = Image.new('RGB', (100, 100), color='blue')
    metadata = ImageMetadata.from_pil_image(img)

    assert metadata is not None
    assert metadata.exif is None
    assert metadata.xmp is None
    assert metadata.icc_profile is None
    assert metadata.has_metadata is False


def test_image_metadata_to_save_params():
    """测试转换为Pillow保存参数"""
    from src.models.image_metadata import ImageMetadata

    exif_data = b'exif_test'
    xmp_data = b'xmp_test'
    icc_data = b'icc_test'

    metadata = ImageMetadata(
        exif=exif_data,
        xmp=xmp_data,
        icc_profile=icc_data
    )

    params = metadata.to_save_params()

    assert params['exif'] == exif_data
    assert params['xmp'] == xmp_data
    assert params['icc_profile'] == icc_data


# ============= QualityPreset 测试 =============

def test_quality_preset_values():
    """测试质量预设的值正确性"""
    from src.models.quality_preset import QualityPreset

    # 测试三个预设
    high_comp = QualityPreset.HIGH_COMPRESSION
    assert high_comp.display_name == "高压缩"
    assert high_comp.quality_value == 60
    assert "敏感" in high_comp.desc or "文件大小" in high_comp.desc

    normal = QualityPreset.NORMAL
    assert normal.display_name == "普通"
    assert normal.quality_value == 80
    assert "平衡" in normal.desc

    low_comp = QualityPreset.LOW_COMPRESSION
    assert low_comp.display_name == "低压缩"
    assert low_comp.quality_value == 95
    assert "质量" in low_comp.desc


def test_quality_preset_ordering():
    """测试质量预设值的大小关系"""
    from src.models.quality_preset import QualityPreset

    high = QualityPreset.HIGH_COMPRESSION.quality_value
    normal = QualityPreset.NORMAL.quality_value
    low = QualityPreset.LOW_COMPRESSION.quality_value

    assert high < normal < low


# ============= ImageFile 测试 =============

def test_image_file_from_path_valid():
    """测试从有效路径创建ImageFile"""
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'

    img_file = ImageFile.from_path(test_path)

    assert img_file.file_path == test_path
    assert img_file.file_name == 'test_image.jpg'
    assert img_file.format == 'JPEG'
    assert img_file.width > 0
    assert img_file.height > 0
    assert img_file.file_size > 0
    assert img_file.file_size_mb > 0
    assert img_file.is_valid is True


def test_image_file_validate_success():
    """测试有效文件验证通过"""
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.png'
    img_file = ImageFile.from_path(test_path)

    is_valid, error_msg = img_file.validate()

    assert is_valid is True
    assert error_msg == ""


def test_image_file_validate_file_not_exists():
    """测试文件不存在时验证失败"""
    from src.models.image_file import ImageFile

    test_path = Path("/nonexistent/path/image.jpg")

    with pytest.raises(Exception):  # 应该在from_path时就抛出异常
        ImageFile.from_path(test_path)


def test_image_file_exceeds_soft_limit():
    """测试软性限制标记"""
    from src.models.image_file import ImageFile

    # 创建一个大文件用于测试
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        temp_path = Path(f.name)
        # 创建大于200MB的虚拟文件(实际测试中使用小文件,但手动设置属性)
        large_img = Image.new('RGB', (9000, 9000), color='white')
        large_img.save(f.name, 'JPEG')

    try:
        img_file = ImageFile.from_path(temp_path)

        # 9000x9000应该触发软性限制
        assert img_file.exceeds_soft_limit is True
    finally:
        os.unlink(temp_path)


def test_image_file_get_display_info():
    """测试获取显示信息"""
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    display_info = img_file.get_display_info()

    assert 'file_name' in display_info
    assert 'format' in display_info
    assert 'dimensions' in display_info or 'width' in display_info
    assert 'file_size' in display_info or 'file_size_mb' in display_info


# ============= ConversionTask 测试 =============

def test_conversion_task_creation():
    """测试创建转换任务"""
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)
    output_path = Path("/tmp/output.webp")

    task = ConversionTask(
        input_file=img_file,
        output_path=output_path,
        quality=80
    )

    assert task.task_id is not None
    assert len(task.task_id) > 0  # UUID应该非空
    assert task.input_file == img_file
    assert task.output_path == output_path
    assert task.quality == 80
    assert task.preserve_metadata is True
    assert task.status == TaskStatus.PENDING
    assert task.created_at is not None


def test_conversion_task_state_transition_pending_to_in_progress():
    """测试任务状态: PENDING -> IN_PROGRESS"""
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output.webp"),
        quality=80
    )

    task.start()

    assert task.status == TaskStatus.IN_PROGRESS
    assert task.started_at is not None


def test_conversion_task_state_transition_to_completed():
    """测试任务状态: IN_PROGRESS -> COMPLETED"""
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output.webp"),
        quality=80
    )

    task.start()
    task.complete(output_size=5000, duration=1.5)

    assert task.status == TaskStatus.COMPLETED
    assert task.finished_at is not None
    assert task.output_file_size == 5000
    assert task.duration_seconds == 1.5
    assert task.compression_ratio is not None  # 应该计算了压缩比


def test_conversion_task_state_transition_to_failed():
    """测试任务状态: IN_PROGRESS -> FAILED"""
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output.webp"),
        quality=80
    )

    task.start()
    task.fail("内存不足,无法处理此图片")

    assert task.status == TaskStatus.FAILED
    assert task.finished_at is not None
    assert task.error_message == "内存不足,无法处理此图片"


def test_conversion_task_state_transition_to_cancelled():
    """测试任务状态: PENDING/IN_PROGRESS -> CANCELLED"""
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output.webp"),
        quality=80
    )

    task.cancel()

    assert task.status == TaskStatus.CANCELLED
    assert task.finished_at is not None


def test_conversion_task_get_result_summary():
    """测试获取任务结果摘要"""
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output.webp"),
        quality=80
    )

    task.start()
    task.complete(output_size=5000, duration=1.5)

    summary = task.get_result_summary()

    assert 'status' in summary or 'task_id' in summary
    assert summary is not None


# ============= BatchConversionJob 测试 =============

def test_batch_conversion_job_creation():
    """测试创建批量作业"""
    from src.models.batch_conversion_job import BatchConversionJob

    job = BatchConversionJob(quality=80)

    assert job.job_id is not None
    assert job.quality == 80
    assert job.total_count == 0
    assert job.created_at is not None


def test_batch_conversion_job_add_task():
    """测试添加子任务"""
    from src.models.batch_conversion_job import BatchConversionJob
    from src.models.conversion_task import ConversionTask
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    job = BatchConversionJob(quality=80)
    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output1.webp"),
        quality=80
    )

    job.add_task(task)

    assert job.total_count == 1
    assert len(job.tasks) == 1


def test_batch_conversion_job_progress_calculation():
    """测试进度计算"""
    from src.models.batch_conversion_job import BatchConversionJob
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    job = BatchConversionJob(quality=80)

    # 添加3个任务
    for i in range(3):
        task = ConversionTask(
            input_file=img_file,
            output_path=Path(f"/tmp/output{i}.webp"),
            quality=80
        )
        job.add_task(task)

    # 完成1个
    job.tasks[0].start()
    job.tasks[0].complete(output_size=5000, duration=1.0)

    # 失败1个
    job.tasks[1].start()
    job.tasks[1].fail("测试失败")

    # 1个仍然pending

    assert job.total_count == 3
    assert job.completed_count == 1
    assert job.failed_count == 1
    assert job.progress_percentage == pytest.approx(66.67, rel=0.1)  # (1+1)/3 * 100
    assert job.is_complete is False


def test_batch_conversion_job_get_pending_tasks():
    """测试获取待处理任务"""
    from src.models.batch_conversion_job import BatchConversionJob
    from src.models.conversion_task import ConversionTask
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    job = BatchConversionJob(quality=80)

    # 添加3个任务
    for i in range(3):
        task = ConversionTask(
            input_file=img_file,
            output_path=Path(f"/tmp/output{i}.webp"),
            quality=80
        )
        job.add_task(task)

    # 完成1个
    job.tasks[0].start()
    job.tasks[0].complete(output_size=5000, duration=1.0)

    pending = job.get_pending_tasks()

    assert len(pending) == 2


def test_batch_conversion_job_cancel_pending_tasks():
    """测试取消所有待处理任务"""
    from src.models.batch_conversion_job import BatchConversionJob
    from src.models.conversion_task import ConversionTask, TaskStatus
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    job = BatchConversionJob(quality=80)

    # 添加3个任务
    for i in range(3):
        task = ConversionTask(
            input_file=img_file,
            output_path=Path(f"/tmp/output{i}.webp"),
            quality=80
        )
        job.add_task(task)

    # 完成1个
    job.tasks[0].start()
    job.tasks[0].complete(output_size=5000, duration=1.0)

    # 取消剩余任务
    cancelled_count = job.cancel_pending_tasks()

    assert cancelled_count == 2
    assert job.cancelled_count == 2


def test_batch_conversion_job_get_summary():
    """测试获取作业摘要"""
    from src.models.batch_conversion_job import BatchConversionJob
    from src.models.conversion_task import ConversionTask
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    job = BatchConversionJob(quality=80)

    # 添加任务
    task = ConversionTask(
        input_file=img_file,
        output_path=Path("/tmp/output.webp"),
        quality=80
    )
    job.add_task(task)

    summary = job.get_summary()

    assert 'total_count' in summary
    assert 'completed_count' in summary
    assert 'failed_count' in summary
    assert 'progress_percentage' in summary


def test_batch_conversion_job_is_complete():
    """测试作业完成判断"""
    from src.models.batch_conversion_job import BatchConversionJob
    from src.models.conversion_task import ConversionTask
    from src.models.image_file import ImageFile

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'
    img_file = ImageFile.from_path(test_path)

    job = BatchConversionJob(quality=80)

    # 添加2个任务
    for i in range(2):
        task = ConversionTask(
            input_file=img_file,
            output_path=Path(f"/tmp/output{i}.webp"),
            quality=80
        )
        job.add_task(task)

    assert job.is_complete is False

    # 全部完成
    for task in job.tasks:
        task.start()
        task.complete(output_size=5000, duration=1.0)

    assert job.is_complete is True
