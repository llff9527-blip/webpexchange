"""
测试FileService文件服务

测试目标:
- resolve_output_path: 文件名冲突解决
- check_disk_space: 磁盘空间检查
- validate_file_path: 文件路径验证
- get_safe_filename: 文件名清理
"""

import pytest
from pathlib import Path
import tempfile
import os


# ============= resolve_output_path 测试 =============

def test_resolve_output_path_no_conflict():
    """测试文件不存在时,返回原路径"""
    from src.services.file_service import FileService

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.jpg"
        input_path.touch()  # 创建输入文件

        result = service.resolve_output_path(input_path)

        expected = Path(tmpdir) / "input.webp"
        assert result == expected


def test_resolve_output_path_with_conflict():
    """测试文件存在时,返回_1后缀路径"""
    from src.services.file_service import FileService

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.jpg"
        input_path.touch()

        # 创建冲突文件
        conflict_path = Path(tmpdir) / "input.webp"
        conflict_path.touch()

        result = service.resolve_output_path(input_path)

        expected = Path(tmpdir) / "input_1.webp"
        assert result == expected
        assert not result.exists()  # 返回的路径不应存在


def test_resolve_output_path_multiple_conflicts():
    """测试多个冲突文件,返回output_2.webp"""
    from src.services.file_service import FileService

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "photo.jpg"
        input_path.touch()

        # 创建photo.webp和photo_1.webp
        (Path(tmpdir) / "photo.webp").touch()
        (Path(tmpdir) / "photo_1.webp").touch()

        result = service.resolve_output_path(input_path)

        expected = Path(tmpdir) / "photo_2.webp"
        assert result == expected
        assert not result.exists()


def test_resolve_output_path_custom_output_dir():
    """测试自定义输出目录"""
    from src.services.file_service import FileService

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input" / "photo.jpg"
        input_path.parent.mkdir(exist_ok=True)
        input_path.touch()

        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir(exist_ok=True)

        result = service.resolve_output_path(input_path, output_dir=output_dir)

        expected = output_dir / "photo.webp"
        assert result == expected
        assert result.parent == output_dir


# ============= check_disk_space 测试 =============

def test_check_disk_space_sufficient():
    """测试可用空间充足"""
    from src.services.file_service import FileService

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.webp"

        # 检查小文件(1MB)应该有足够空间
        ok, msg = service.check_disk_space(output_path, estimated_size=1024 * 1024)

        assert ok is True
        assert "充足" in msg or "足够" in msg


def test_check_disk_space_edge_case():
    """测试边界情况(预留100MB缓冲)"""
    from src.services.file_service import FileService
    import shutil

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.webp"

        # 获取实际可用空间
        stat = shutil.disk_usage(tmpdir)
        available = stat.free

        # 请求几乎全部空间(应该失败,因为需要100MB缓冲)
        ok, msg = service.check_disk_space(
            output_path,
            estimated_size=available - 50 * 1024 * 1024  # 只留50MB
        )

        assert ok is False
        assert "不足" in msg


# ============= validate_file_path 测试 =============

def test_validate_file_path_valid_jpg():
    """测试有效的JPEG文件"""
    from src.services.file_service import FileService

    service = FileService()

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.jpg'

    is_valid, error = service.validate_file_path(test_path)

    assert is_valid is True
    assert error == "文件有效" or error == ""


def test_validate_file_path_valid_png():
    """测试有效的PNG文件"""
    from src.services.file_service import FileService

    service = FileService()

    test_path = Path(__file__).parent.parent / 'fixtures' / 'sample_images' / 'test_image.png'

    is_valid, error = service.validate_file_path(test_path)

    assert is_valid is True


def test_validate_file_path_not_exists():
    """测试文件不存在"""
    from src.services.file_service import FileService

    service = FileService()

    test_path = Path("/nonexistent/image.jpg")

    is_valid, error = service.validate_file_path(test_path)

    assert is_valid is False
    assert "损坏" in error or "无法访问" in error


def test_validate_file_path_is_directory():
    """测试路径是目录而非文件"""
    from src.services.file_service import FileService

    service = FileService()

    test_path = Path(__file__).parent.parent / 'fixtures'

    is_valid, error = service.validate_file_path(test_path)

    assert is_valid is False
    assert "不是有效的文件" in error or "目录" in error


def test_validate_file_path_unsupported_format():
    """测试不支持的文件格式"""
    from src.services.file_service import FileService

    service = FileService()

    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        temp_path = Path(f.name)
        f.write(b'test content')

    try:
        is_valid, error = service.validate_file_path(temp_path)

        assert is_valid is False
        assert "不支持的文件格式" in error
    finally:
        os.unlink(temp_path)


def test_validate_file_path_supported_formats():
    """测试所有支持的格式"""
    from src.services.file_service import FileService

    service = FileService()

    supported = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    for ext in supported:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            temp_path = Path(f.name)
            # 写入有效的图片头部
            if ext in ['.jpg', '.jpeg']:
                f.write(b'\xff\xd8\xff')  # JPEG magic number
            else:
                f.write(b'dummy')

        try:
            is_valid, error = service.validate_file_path(temp_path)
            # 只检查格式验证通过,不检查文件内容
            # (内容验证在ImageFile.from_path中进行)
            assert is_valid is True or "损坏" in error  # 可能因为不是真实图片而失败
        finally:
            os.unlink(temp_path)


# ============= get_safe_filename 测试 =============

def test_get_safe_filename_remove_illegal_chars():
    """测试移除非法字符"""
    from src.services.file_service import FileService

    service = FileService()

    unsafe = "photo<1>.jpg"
    safe = service.get_safe_filename(unsafe)

    assert safe == "photo_1_.jpg"
    assert '<' not in safe
    assert '>' not in safe


def test_get_safe_filename_all_illegal_chars():
    """测试所有Windows非法字符"""
    from src.services.file_service import FileService

    service = FileService()

    unsafe = 'file<>:"/\\|?*.jpg'
    safe = service.get_safe_filename(unsafe)

    # 所有非法字符应被替换
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        assert char not in safe

    # 应该保留扩展名
    assert safe.endswith('.jpg')


def test_get_safe_filename_control_chars():
    """测试移除控制字符"""
    from src.services.file_service import FileService

    service = FileService()

    unsafe = "file\x00\x01\x1f.jpg"
    safe = service.get_safe_filename(unsafe)

    # 控制字符应被移除
    assert '\x00' not in safe
    assert '\x01' not in safe
    assert '\x1f' not in safe


def test_get_safe_filename_limit_length():
    """测试限制长度≤255字符"""
    from src.services.file_service import FileService

    service = FileService()

    # 创建260字符的文件名
    long_name = "a" * 260 + ".jpg"
    safe = service.get_safe_filename(long_name)

    assert len(safe) <= 255


def test_get_safe_filename_preserve_valid_chars():
    """测试保留有效字符"""
    from src.services.file_service import FileService

    service = FileService()

    valid = "photo_2024-10-21.jpg"
    safe = service.get_safe_filename(valid)

    assert safe == valid  # 完全相同


def test_get_safe_filename_unicode():
    """测试Unicode字符处理"""
    from src.services.file_service import FileService

    service = FileService()

    unicode_name = "照片2024.jpg"
    safe = service.get_safe_filename(unicode_name)

    # Unicode字符应该保留
    assert "照片" in safe
    assert safe.endswith('.jpg')


def test_get_safe_filename_empty():
    """测试空文件名"""
    from src.services.file_service import FileService

    service = FileService()

    safe = service.get_safe_filename("")

    assert safe == ""  # 或返回默认值如"untitled"
