"""
验证工具

提供通用验证功能。
"""


def validate_quality(quality: int) -> tuple[bool, str]:
    """
    验证质量参数是否在有效范围内。

    参数:
        quality: 质量参数(0-100)

    返回:
        (is_valid, error_message)
    """
    if not isinstance(quality, int):
        return False, "质量参数必须是整数"

    if quality < 0 or quality > 100:
        return False, "质量参数必须在0-100之间"

    return True, ""


def validate_quality_range(quality) -> tuple[int, str]:
    """
    验证并自动修正质量参数范围。

    T068: 自定义质量参数验证
    - 范围: 0-100
    - 超出范围自动修正并提示
    - 支持整数、浮点数、字符串转换

    参数:
        quality: 质量参数(可以是int, float, str或None)

    返回:
        (修正后的质量值, 提示消息)
        - 如果在范围内: (quality, "")
        - 如果超出范围: (修正值, "质量参数已修正为X")
        - 如果无效输入: (80, "质量参数无效,已设置为默认值80")

    示例:
        >>> validate_quality_range(85)
        (85, "")

        >>> validate_quality_range(150)
        (100, "质量参数超出范围,已修正为100")

        >>> validate_quality_range(-10)
        (0, "质量参数超出范围,已修正为0")

        >>> validate_quality_range("75")
        (75, "")

        >>> validate_quality_range("abc")
        (80, "质量参数无效,已设置为默认值80")
    """
    # 处理None和无效输入
    if quality is None:
        return 80, "质量参数无效,已设置为默认值80"

    # 尝试转换为整数
    try:
        # 支持字符串和浮点数
        if isinstance(quality, str):
            quality_int = int(quality)
        elif isinstance(quality, float):
            quality_int = int(quality)
        elif isinstance(quality, int):
            quality_int = quality
        else:
            return 80, "质量参数无效,已设置为默认值80"
    except (ValueError, TypeError):
        return 80, "质量参数无效,已设置为默认值80"

    # 范围检查和自动修正
    if quality_int > 100:
        return 100, "质量参数超出范围,已修正为100"
    elif quality_int < 0:
        return 0, "质量参数超出范围,已修正为0"
    else:
        return quality_int, ""
