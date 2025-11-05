"""
Buffer Utility Functions
Buffer 计算工具函数
"""


def apply_buffer(value: float, use_buffer: bool, buffer_size: float) -> float:
    """
    应用 buffer 安全余量到给定值

    参数:
        value: 原始值
        use_buffer: 是否启用 buffer
        buffer_size: buffer 大小

    返回:
        应用 buffer 后的值（保证非负）
    """
    if use_buffer:
        return max(0, value - buffer_size)
    else:
        return max(0, value)
