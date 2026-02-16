"""
属性测试：扫描进度回调被调用

Feature: windows-cleaner, Property 2: 扫描进度回调被调用
**验证需求：需求 1.2**
"""

import pytest
from hypothesis import given, strategies as st, settings
from src.models import JunkCategory, ScanConfig
from src.scanner import JunkScanner


# 定义策略：生成启用的类别集合
@st.composite
def scan_config_strategy(draw):
    """生成随机的扫描配置"""
    # 至少启用一个类别
    enabled_categories = draw(st.sets(
        st.sampled_from([
            JunkCategory.TEMP_FILES,
            JunkCategory.WINDOWS_UPDATE_CACHE,
            JunkCategory.RECYCLE_BIN,
            JunkCategory.BROWSER_CACHE,
            JunkCategory.THUMBNAIL_CACHE
        ]),
        min_size=1,
        max_size=5
    ))
    
    return ScanConfig(
        enabled_categories=enabled_categories,
        excluded_paths=[],
        custom_patterns=[]
    )


@settings(max_examples=100, deadline=None)
@given(config=scan_config_strategy())
def test_scan_progress_callback_is_called(config):
    """
    属性 2：扫描进度回调被调用
    
    对于任何扫描操作，进度回调函数应该在扫描过程中被调用至少一次，
    且进度百分比应该是单调递增的（0 到 100）。
    
    **验证需求：需求 1.2**
    """
    # 创建扫描器
    scanner = JunkScanner(config)
    
    # 记录回调调用
    callback_calls = []
    
    def progress_callback(path: str, percentage: int):
        """记录进度回调"""
        callback_calls.append({
            'path': path,
            'percentage': percentage
        })
    
    # 执行扫描
    result = scanner.scan(progress_callback)
    
    # 属性 1：回调至少被调用一次
    assert len(callback_calls) > 0, \
        "进度回调应该至少被调用一次"
    
    # 属性 2：进度百分比应该在 0 到 100 之间
    for call in callback_calls:
        percentage = call['percentage']
        assert 0 <= percentage <= 100, \
            f"进度百分比 {percentage} 应该在 0 到 100 之间"
    
    # 属性 3：进度百分比应该是单调递增的（或相等）
    percentages = [call['percentage'] for call in callback_calls]
    for i in range(len(percentages) - 1):
        assert percentages[i] <= percentages[i + 1], \
            f"进度百分比应该单调递增，但 {percentages[i]} > {percentages[i + 1]}"
    
    # 属性 4：最后一次回调的进度应该是 100
    if callback_calls:
        last_percentage = callback_calls[-1]['percentage']
        assert last_percentage == 100, \
            f"最后一次回调的进度应该是 100，但实际是 {last_percentage}"


@settings(max_examples=100, deadline=None)
@given(config=scan_config_strategy())
def test_scan_progress_callback_receives_valid_paths(config):
    """
    属性测试：验证进度回调接收到的路径信息是有效的
    
    进度回调应该接收到非空的路径描述信息。
    
    **验证需求：需求 1.2**
    """
    # 创建扫描器
    scanner = JunkScanner(config)
    
    # 记录回调调用
    callback_calls = []
    
    def progress_callback(path: str, percentage: int):
        """记录进度回调"""
        callback_calls.append({
            'path': path,
            'percentage': percentage
        })
    
    # 执行扫描
    result = scanner.scan(progress_callback)
    
    # 验证所有回调都有非空的路径信息
    for call in callback_calls:
        path = call['path']
        assert isinstance(path, str), \
            f"路径应该是字符串类型，但实际是 {type(path)}"
        assert len(path) > 0, \
            "路径信息不应该为空"


@settings(max_examples=100, deadline=None)
@given(config=scan_config_strategy())
def test_scan_progress_callback_count_matches_categories(config):
    """
    属性测试：验证进度回调的调用次数与启用的类别数量相关
    
    进度回调应该至少为每个启用的类别调用一次，加上最终的完成回调。
    
    **验证需求：需求 1.2**
    """
    # 创建扫描器
    scanner = JunkScanner(config)
    
    # 记录回调调用
    callback_calls = []
    
    def progress_callback(path: str, percentage: int):
        """记录进度回调"""
        callback_calls.append({
            'path': path,
            'percentage': percentage
        })
    
    # 执行扫描
    result = scanner.scan(progress_callback)
    
    # 验证回调次数至少等于启用的类别数量 + 1（完成回调）
    expected_min_calls = len(config.enabled_categories) + 1
    assert len(callback_calls) >= expected_min_calls, \
        f"回调次数 {len(callback_calls)} 应该至少为 {expected_min_calls}（每个类别 + 完成回调）"
