"""
跨平台路径处理测试

验证path_utils模块的跨平台兼容性。
"""

import pytest
from pathlib import Path
import tempfile
import platform


def test_windows_path_compatibility():
    """
    测试Windows路径兼容性

    验证:
    - pathlib.Path正确处理Windows路径格式
    - 路径分隔符正确处理
    """
    from pathlib import Path

    # 测试Windows风格路径(即使在非Windows系统上也应能处理)
    if platform.system() == "Windows":
        # 在Windows上测试实际路径
        path = Path("C:\\Users\\test\\photo.jpg")
        assert path.parts[0] == "C:\\"
        assert path.stem == "photo"
        assert path.suffix == ".jpg"
    else:
        # 在非Windows系统上,测试PurePosixPath的行为
        from pathlib import PureWindowsPath
        path = PureWindowsPath("C:\\Users\\test\\photo.jpg")
        assert path.stem == "photo"
        assert path.suffix == ".jpg"


def test_unix_path_compatibility():
    """
    测试Unix/Linux路径兼容性

    验证:
    - pathlib.Path正确处理Unix路径格式
    - 路径分隔符正确处理
    """
    from pathlib import Path

    # 测试Unix风格路径
    if platform.system() != "Windows":
        # 在Unix系统上测试实际路径
        path = Path("/home/user/photos/sunset.jpg")
        assert path.parts[0] == "/"
        assert path.stem == "sunset"
        assert path.suffix == ".jpg"
    else:
        # 在Windows上,测试PurePosixPath的行为
        from pathlib import PurePosixPath
        path = PurePosixPath("/home/user/photos/sunset.jpg")
        assert path.stem == "sunset"
        assert path.suffix == ".jpg"


def test_path_join_cross_platform():
    """
    测试跨平台路径拼接

    验证:
    - pathlib.Path正确拼接路径
    - 使用正确的路径分隔符
    """
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        subdir = base / "photos" / "2025"
        filename = subdir / "photo.jpg"

        # 验证路径拼接正确
        assert base in filename.parents
        assert filename.name == "photo.jpg"
        assert filename.parent.name == "2025"


def test_path_resolution_cross_platform():
    """
    测试跨平台路径解析

    验证:
    - Path.resolve()正确解析相对路径
    - 路径规范化处理
    """
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # 创建测试文件
        test_file = base / "test.txt"
        test_file.touch()

        # 测试相对路径解析
        relative = Path(tmpdir) / ".." / base.name / "test.txt"
        resolved = relative.resolve()

        assert resolved.exists()
        assert resolved.name == "test.txt"


def test_special_characters_in_filename():
    """
    测试文件名中的特殊字符处理

    验证:
    - 文件名中的空格、中文等特殊字符
    - 跨平台兼容性
    """
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # 测试包含空格的文件名
        filename_with_space = base / "photo with space.jpg"
        filename_with_space.touch()
        assert filename_with_space.exists()
        assert filename_with_space.name == "photo with space.jpg"

        # 测试包含中文的文件名
        filename_with_chinese = base / "测试图片.jpg"
        filename_with_chinese.touch()
        assert filename_with_chinese.exists()
        assert filename_with_chinese.name == "测试图片.jpg"


def test_path_exists_check():
    """
    测试路径存在性检查

    验证:
    - Path.exists()跨平台一致性
    - 文件和目录区分
    """
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # 测试文件存在性
        test_file = base / "file.txt"
        assert not test_file.exists()

        test_file.touch()
        assert test_file.exists()
        assert test_file.is_file()
        assert not test_file.is_dir()

        # 测试目录存在性
        test_dir = base / "subdir"
        assert not test_dir.exists()

        test_dir.mkdir()
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert not test_dir.is_file()


def test_path_parent_navigation():
    """
    测试路径父目录导航

    验证:
    - Path.parent正确返回父目录
    - Path.parents正确返回所有父目录
    """
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        deep_path = Path(tmpdir) / "a" / "b" / "c" / "file.txt"

        # 测试parent
        assert deep_path.parent.name == "c"
        assert deep_path.parent.parent.name == "b"

        # 测试parents
        parents = list(deep_path.parents)
        assert len(parents) >= 3
        assert parents[0].name == "c"
        assert parents[1].name == "b"
        assert parents[2].name == "a"


def test_file_service_cross_platform_safe_filename():
    """
    测试FileService.get_safe_filename()跨平台兼容性

    验证:
    - 非法字符被清理
    - 跨平台文件名安全
    """
    from src.services.file_service import FileService

    service = FileService()

    # 测试Windows非法字符
    unsafe_filename = 'photo<>:"|?*.jpg'
    safe = service.get_safe_filename(unsafe_filename)

    # 验证非法字符被替换
    for char in '<>:"|?*':
        assert char not in safe

    # 文件名应保留基本结构
    assert ".jpg" in safe or "jpg" in safe


def test_file_service_long_filename_handling():
    """
    测试FileService处理超长文件名

    验证:
    - 超过255字符的文件名被截断
    - 保留扩展名
    """
    from src.services.file_service import FileService

    service = FileService()

    # 创建超长文件名(>255字符)
    long_filename = "a" * 300 + ".jpg"
    safe = service.get_safe_filename(long_filename)

    # 验证长度被限制
    assert len(safe) <= 255

    # 验证扩展名被保留
    assert safe.endswith(".jpg") or "jpg" in safe


def test_resolve_output_path_cross_platform():
    """
    测试FileService.resolve_output_path()跨平台兼容性

    验证:
    - 在不同操作系统上正确解析路径
    - 文件名冲突解决跨平台一致
    """
    from src.services.file_service import FileService
    from pathlib import Path

    service = FileService()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "photo.jpg"
        input_path.touch()

        # 测试基本解析
        output_path = service.resolve_output_path(input_path)
        assert output_path.suffix == ".webp"
        assert output_path.parent == Path(tmpdir)

        # 创建冲突文件
        conflict = Path(tmpdir) / "photo.webp"
        conflict.touch()

        # 测试冲突解决
        output_path = service.resolve_output_path(input_path)
        assert output_path.name == "photo_1.webp"
        assert not output_path.exists()


def test_pathlib_pure_paths():
    """
    测试Pathlib Pure路径(用于跨平台路径操作)

    验证:
    - PureWindowsPath和PurePosixPath的行为
    - 路径操作不依赖文件系统
    """
    from pathlib import PureWindowsPath, PurePosixPath

    # 测试Windows Pure路径
    win_path = PureWindowsPath("C:/Users/test/photo.jpg")
    assert win_path.stem == "photo"
    assert win_path.suffix == ".jpg"

    # 测试Unix Pure路径
    unix_path = PurePosixPath("/home/user/photo.jpg")
    assert unix_path.stem == "photo"
    assert unix_path.suffix == ".jpg"

    # 验证Pure路径可以拼接
    win_joined = win_path.parent / "output.webp"
    assert "output.webp" in str(win_joined)

    unix_joined = unix_path.parent / "output.webp"
    assert "output.webp" in str(unix_joined)
