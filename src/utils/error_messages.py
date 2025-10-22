"""
错误消息管理

集中管理所有中文错误提示,确保用户友好的错误信息。
"""

from enum import Enum


class ErrorCode(Enum):
    """错误代码枚举"""

    # 文件相关错误
    FILE_NOT_FOUND = "file_not_found"
    FILE_NOT_READABLE = "file_not_readable"
    FILE_INVALID_FORMAT = "file_invalid_format"
    FILE_TOO_LARGE = "file_too_large"
    FILE_CORRUPTED = "file_corrupted"

    # 磁盘空间错误
    DISK_SPACE_INSUFFICIENT = "disk_space_insufficient"
    DISK_SPACE_CHECK_FAILED = "disk_space_check_failed"

    # 转换错误
    CONVERSION_FAILED = "conversion_failed"
    CONVERSION_CANCELLED = "conversion_cancelled"
    CONVERSION_TIMEOUT = "conversion_timeout"

    # 元数据错误
    METADATA_EXTRACTION_FAILED = "metadata_extraction_failed"
    METADATA_EMBEDDING_FAILED = "metadata_embedding_failed"

    # 质量参数错误
    QUALITY_OUT_OF_RANGE = "quality_out_of_range"
    QUALITY_INVALID_TYPE = "quality_invalid_type"

    # 输出错误
    OUTPUT_WRITE_FAILED = "output_write_failed"
    OUTPUT_PATH_INVALID = "output_path_invalid"
    OUTPUT_PERMISSION_DENIED = "output_permission_denied"

    # 系统错误
    WEBP_NOT_SUPPORTED = "webp_not_supported"
    MEMORY_INSUFFICIENT = "memory_insufficient"
    UNKNOWN_ERROR = "unknown_error"


class ErrorMessages:
    """错误消息管理器"""

    # 错误消息映射表
    _MESSAGES = {
        ErrorCode.FILE_NOT_FOUND: "图片文件不存在,请检查文件路径",
        ErrorCode.FILE_NOT_READABLE: "无权限读取图片文件,请检查文件权限",
        ErrorCode.FILE_INVALID_FORMAT: "不支持的文件格式,请选择图片文件(JPEG, PNG, GIF等)",
        ErrorCode.FILE_TOO_LARGE: "图片文件过大,可能导致转换失败或内存不足",
        ErrorCode.FILE_CORRUPTED: "图片文件损坏或无法访问,请检查文件",

        ErrorCode.DISK_SPACE_INSUFFICIENT: "磁盘空间不足,无法保存转换后的文件",
        ErrorCode.DISK_SPACE_CHECK_FAILED: "检查磁盘空间失败,请稍后重试",

        ErrorCode.CONVERSION_FAILED: "转换失败,请检查图片文件或稍后重试",
        ErrorCode.CONVERSION_CANCELLED: "转换已取消",
        ErrorCode.CONVERSION_TIMEOUT: "转换超时,图片可能过大或系统资源不足",

        ErrorCode.METADATA_EXTRACTION_FAILED: "提取元数据失败,转换将继续但元数据可能丢失",
        ErrorCode.METADATA_EMBEDDING_FAILED: "嵌入元数据失败,转换将继续但元数据可能丢失",

        ErrorCode.QUALITY_OUT_OF_RANGE: "质量参数必须在0-100之间",
        ErrorCode.QUALITY_INVALID_TYPE: "质量参数必须是整数",

        ErrorCode.OUTPUT_WRITE_FAILED: "写入输出文件失败,请检查磁盘空间和权限",
        ErrorCode.OUTPUT_PATH_INVALID: "输出路径无效,请选择有效的保存位置",
        ErrorCode.OUTPUT_PERMISSION_DENIED: "无权限写入输出文件,请选择其他保存位置",

        ErrorCode.WEBP_NOT_SUPPORTED: "系统不支持WebP格式,请重新安装Pillow库",
        ErrorCode.MEMORY_INSUFFICIENT: "内存不足,无法处理此图片",
        ErrorCode.UNKNOWN_ERROR: "发生未知错误,请稍后重试",
    }

    @classmethod
    def get(cls, code: ErrorCode, **kwargs) -> str:
        """
        获取错误消息

        参数:
            code: 错误代码
            **kwargs: 可选的格式化参数

        返回:
            格式化后的错误消息
        """
        message = cls._MESSAGES.get(code, cls._MESSAGES[ErrorCode.UNKNOWN_ERROR])

        # 如果有格式化参数,进行格式化
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                # 格式化失败,返回原始消息
                pass

        return message

    @classmethod
    def get_detailed(cls, code: ErrorCode, details: str = "") -> str:
        """
        获取详细错误消息

        参数:
            code: 错误代码
            details: 详细错误信息

        返回:
            包含详细信息的错误消息
        """
        message = cls.get(code)

        if details:
            return f"{message}\n\n详细信息: {details}"

        return message

    @classmethod
    def format_file_error(cls, file_path: str, error: str) -> str:
        """
        格式化文件错误消息

        参数:
            file_path: 文件路径
            error: 错误描述

        返回:
            格式化的错误消息
        """
        return f"文件 {file_path} 处理失败\n\n{error}"

    @classmethod
    def format_conversion_error(cls, input_file: str, error: str) -> str:
        """
        格式化转换错误消息

        参数:
            input_file: 输入文件名
            error: 错误描述

        返回:
            格式化的错误消息
        """
        return f"转换 {input_file} 失败\n\n{error}"

    @classmethod
    def format_batch_error(cls, total: int, failed: int, errors: list[str]) -> str:
        """
        格式化批量转换错误消息

        参数:
            total: 总数
            failed: 失败数
            errors: 错误列表

        返回:
            格式化的批量错误消息
        """
        message = f"批量转换完成,共 {total} 张图片,失败 {failed} 张\n\n"

        if errors:
            message += "失败详情:\n"
            for i, error in enumerate(errors[:5], 1):  # 最多显示5个错误
                message += f"{i}. {error}\n"

            if len(errors) > 5:
                message += f"... 还有 {len(errors) - 5} 个错误未显示"

        return message


# 常用错误消息快捷访问
class CommonErrors:
    """常用错误消息"""

    FILE_NOT_FOUND = ErrorMessages.get(ErrorCode.FILE_NOT_FOUND)
    FILE_CORRUPTED = ErrorMessages.get(ErrorCode.FILE_CORRUPTED)
    FILE_INVALID_FORMAT = ErrorMessages.get(ErrorCode.FILE_INVALID_FORMAT)

    DISK_SPACE_INSUFFICIENT = ErrorMessages.get(ErrorCode.DISK_SPACE_INSUFFICIENT)

    CONVERSION_FAILED = ErrorMessages.get(ErrorCode.CONVERSION_FAILED)
    CONVERSION_CANCELLED = ErrorMessages.get(ErrorCode.CONVERSION_CANCELLED)

    QUALITY_OUT_OF_RANGE = ErrorMessages.get(ErrorCode.QUALITY_OUT_OF_RANGE)

    WEBP_NOT_SUPPORTED = ErrorMessages.get(ErrorCode.WEBP_NOT_SUPPORTED)
    MEMORY_INSUFFICIENT = ErrorMessages.get(ErrorCode.MEMORY_INSUFFICIENT)
    UNKNOWN_ERROR = ErrorMessages.get(ErrorCode.UNKNOWN_ERROR)


# 警告消息
class WarningMessages:
    """警告消息"""

    LARGE_FILE_WARNING = "图片文件较大({size_mb:.1f} MB),转换可能需要较长时间且消耗较多内存,是否继续?"
    LARGE_DIMENSION_WARNING = "图片尺寸较大({width}x{height}像素),转换可能需要较长时间且消耗较多内存,是否继续?"
    QUALITY_TOO_LOW_WARNING = "质量参数较低(当前: {quality}),转换后的图片质量可能不佳,是否继续?"
    QUALITY_TOO_HIGH_WARNING = "质量参数较高(当前: {quality}),转换后的文件大小可能接近原图,压缩效果有限,是否继续?"

    @classmethod
    def format_large_file(cls, size_mb: float) -> str:
        """格式化大文件警告"""
        return cls.LARGE_FILE_WARNING.format(size_mb=size_mb)

    @classmethod
    def format_large_dimension(cls, width: int, height: int) -> str:
        """格式化大尺寸警告"""
        return cls.LARGE_DIMENSION_WARNING.format(width=width, height=height)

    @classmethod
    def format_quality_low(cls, quality: int) -> str:
        """格式化低质量警告"""
        return cls.QUALITY_TOO_LOW_WARNING.format(quality=quality)

    @classmethod
    def format_quality_high(cls, quality: int) -> str:
        """格式化高质量警告"""
        return cls.QUALITY_TOO_HIGH_WARNING.format(quality=quality)


# 成功消息
class SuccessMessages:
    """成功消息"""

    CONVERSION_SUCCESS = "转换完成!"
    BATCH_CONVERSION_SUCCESS = "批量转换完成!共 {total} 张图片,成功 {success} 张,失败 {failed} 张"

    @classmethod
    def format_batch_success(cls, total: int, success: int, failed: int) -> str:
        """格式化批量转换成功消息"""
        return cls.BATCH_CONVERSION_SUCCESS.format(total=total, success=success, failed=failed)
