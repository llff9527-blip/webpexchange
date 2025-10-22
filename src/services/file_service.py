"""
文件服务

提供跨平台文件路径处理、文件名冲突解决、磁盘空间检查。
"""

from pathlib import Path
import shutil
import os
import re


class FileService:
    """文件路径处理服务"""

    def resolve_output_path(
        self,
        input_path: Path,
        output_dir: Path = None,
        output_format: str = "webp"
    ) -> Path:
        """
        解决文件名冲突,自动重命名以避免覆盖已有文件。

        参数:
            input_path: 输入文件路径
            output_dir: 输出目录(None表示与输入相同目录)
            output_format: 输出格式(默认webp)

        返回:
            唯一的输出路径

        示例:
            output.webp -> output_1.webp -> output_2.webp
        """
        # 确定输出目录
        if output_dir is None:
            output_dir = input_path.parent

        # 构建基础输出路径
        stem = input_path.stem
        base_path = output_dir / f"{stem}.{output_format}"

        # 检查冲突
        if not base_path.exists():
            return base_path

        # 自动重命名
        counter = 1
        while True:
            new_path = output_dir / f"{stem}_{counter}.{output_format}"
            if not new_path.exists():
                return new_path
            counter += 1

    def check_disk_space(
        self,
        output_path: Path,
        estimated_size: int
    ) -> tuple[bool, str]:
        """
        检查目标路径的可用磁盘空间是否足够保存转换后的文件。

        参数:
            output_path: 输出文件路径
            estimated_size: 预估文件大小(字节)

        返回:
            (是否有足够空间, 描述信息)
        """
        try:
            # 获取磁盘使用情况
            stat = shutil.disk_usage(output_path.parent)
            available = stat.free

            # 需要预留100MB缓冲
            buffer = 100 * 1024 * 1024  # 100MB
            required = estimated_size + buffer

            if available >= required:
                return True, "磁盘空间充足"
            else:
                return False, "磁盘空间不足,无法保存转换后的文件"

        except Exception as e:
            return False, f"检查磁盘空间失败: {e}"

    def validate_file_path(self, file_path: Path) -> tuple[bool, str]:
        """
        验证文件路径的有效性(存在性、可读性、格式支持)。

        参数:
            file_path: 要验证的文件路径

        返回:
            (是否有效, 错误消息)
        """
        # 检查文件存在
        if not file_path.exists():
            return False, "图片文件损坏或无法访问,请检查文件"

        # 检查是文件(非目录)
        if not file_path.is_file():
            return False, "路径不是有效的文件"

        # 检查文件可读
        if not os.access(file_path, os.R_OK):
            return False, "无权限读取文件"

        # 检查扩展名支持
        supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if file_path.suffix.lower() not in supported_extensions:
            return False, "不支持的文件格式,请选择图片文件(JPEG, PNG, GIF等)"

        return True, "文件有效"

    def get_safe_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符,确保跨平台兼容性。

        参数:
            filename: 原始文件名

        返回:
            清理后的文件名
        """
        if not filename:
            return filename

        # Windows非法字符: < > : " / \ | ? *
        illegal_chars = r'[<>:"/\\|?*]'
        safe = re.sub(illegal_chars, '_', filename)

        # 移除控制字符(ASCII < 32)
        safe = ''.join(char for char in safe if ord(char) >= 32)

        # 限制长度 ≤ 255字符(文件系统限制)
        if len(safe) > 255:
            # 保留扩展名,截断主文件名
            path = Path(safe)
            stem = path.stem
            suffix = path.suffix

            # 计算可用于stem的长度
            max_stem_len = 255 - len(suffix)
            if max_stem_len > 0:
                safe = stem[:max_stem_len] + suffix
            else:
                # 扩展名本身超过255,只取前255字符
                safe = safe[:255]

        return safe
