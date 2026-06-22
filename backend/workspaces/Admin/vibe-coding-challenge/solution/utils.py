#!/usr/bin/env python3
"""
工具函数模块 - 参考答案
"""

import os
from pathlib import Path


def progress(step, total, desc):
    """打印进度信息。"""
    print(f"\n{'#'*60}")
    print(f" 步骤 {step}/{total}: {desc}")
    print(f"{'#'*60}")


def format_duration(seconds):
    """格式化时间间隔。"""
    if seconds < 60:
        return f"{seconds:.1f} 秒"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes} 分 {secs:.1f} 秒"


def verify_csv(filepath, desc):
    """验证 CSV 文件是否存在且非空。"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"[FAIL] {desc}不存在: {filepath}")
        return False
    if filepath.stat().st_size < 100:
        print(f"[FAIL] {desc}文件过小: {filepath.stat().st_size} 字节")
        return False
    print(f"[PASS] {desc}存在，大小: {filepath.stat().st_size} 字节")
    return True


def row(*values, widths=None):
    """格式化表格行。"""
    if widths is None:
        widths = [20] * len(values)
    parts = []
    for i, val in enumerate(values):
        w = widths[i] if i < len(widths) else 20
        parts.append(str(val).ljust(w))
    return ''.join(parts)
