"""
测试质量参数验证功能

对应任务: T062-T063
测试 src/utils/validator.py::validate_quality_range()
"""

import pytest
from src.utils.validator import validate_quality_range


class TestValidateQualityRange:
    """测试自定义质量范围验证"""

    def test_validate_quality_in_range(self):
        """T062: 测试有效质量范围内的值"""
        # 测试边界值
        assert validate_quality_range(0) == (0, "")
        assert validate_quality_range(100) == (100, "")

        # 测试中间值
        assert validate_quality_range(50) == (50, "")
        assert validate_quality_range(85) == (85, "")
        assert validate_quality_range(1) == (1, "")
        assert validate_quality_range(99) == (99, "")

    def test_validate_quality_out_of_range(self):
        """T063: 测试超出范围的值自动修正"""
        # 超过上限
        corrected, msg = validate_quality_range(150)
        assert corrected == 100
        assert "已修正为100" in msg

        corrected, msg = validate_quality_range(101)
        assert corrected == 100
        assert "已修正为100" in msg

        # 低于下限
        corrected, msg = validate_quality_range(-10)
        assert corrected == 0
        assert "已修正为0" in msg

        corrected, msg = validate_quality_range(-1)
        assert corrected == 0
        assert "已修正为0" in msg

    def test_validate_quality_with_non_integer(self):
        """测试非整数输入"""
        # 浮点数应转为整数
        assert validate_quality_range(85.7) == (85, "")
        assert validate_quality_range(50.2) == (50, "")

        # 字符串数字应转为整数
        assert validate_quality_range("75") == (75, "")

        # 超出范围的浮点数
        corrected, msg = validate_quality_range(105.5)
        assert corrected == 100
        assert "已修正为100" in msg

    def test_validate_quality_invalid_input(self):
        """测试无效输入"""
        # 非数字字符串应返回默认值80
        corrected, msg = validate_quality_range("abc")
        assert corrected == 80
        assert "无效" in msg

        # None应返回默认值80
        corrected, msg = validate_quality_range(None)
        assert corrected == 80
        assert "无效" in msg
