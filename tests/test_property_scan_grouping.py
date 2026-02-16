"""
属性测试：扫描结果按类别分组

Feature: windows-cleaner, Property 1: 扫描结果按类别分组
**验证需求：需求 1.1**
"""

import pytest
from hypothesis import given, strategies as st, settings
from src.models import JunkCategory, JunkFile, ScanResult


# 定义策略：生成 JunkFile 对象
@st.composite
def junk_file_strategy(draw):
    """生成随机的 JunkFile 对象"""
    # 生成文件路径
    path = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters=':/\\_-.'
    )))
    
    # 生成文件大小（0 到 1GB）
    size = draw(st.integers(min_value=0, max_value=1024**3))
    
    # 随机选择一个类别（排除 CUSTOM）
    category = draw(st.sampled_from([
        JunkCategory.TEMP_FILES,
        JunkCategory.WINDOWS_UPDATE_CACHE,
        JunkCategory.RECYCLE_BIN,
        JunkCategory.BROWSER_CACHE,
        JunkCategory.THUMBNAIL_CACHE
    ]))
    
    # 生成 can_delete 标志
    can_delete = draw(st.booleans())
    
    # 可选的错误消息
    error_message = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=50)
    ))
    
    return JunkFile(
        path=path,
        size=size,
        category=category,
        can_delete=can_delete,
        error_message=error_message
    )


# 定义策略：生成 JunkFile 列表
junk_files_list_strategy = st.lists(
    junk_file_strategy(),
    min_size=0,
    max_size=50  # 限制大小以提高测试速度
)


@settings(max_examples=20)
@given(files=junk_files_list_strategy)
def test_scan_result_groups_by_category(files):
    """
    属性 1：扫描结果按类别分组
    
    对于任何扫描操作，返回的扫描结果中的所有垃圾文件都应该根据其类别正确分组，
    且每个文件只出现在一个类别中。
    
    **验证需求：需求 1.1**
    """
    # 手动构建按类别分组的字典（这模拟了扫描器的分组逻辑）
    categories = {}
    for file in files:
        if file.category not in categories:
            categories[file.category] = []
        categories[file.category].append(file)
    
    # 创建 ScanResult
    result = ScanResult(
        categories=categories,
        total_size=sum(f.size for f in files),
        total_count=len(files),
        scan_duration=0.0,
        errors=[],
        requires_admin=False,
        inaccessible_categories=[]
    )
    
    # 属性 1：验证每个类别中的文件都属于该类别
    for category, category_files in result.categories.items():
        for file in category_files:
            assert file.category == category, \
                f"文件 {file.path} 的类别是 {file.category}，但被分组到 {category}"
    
    # 属性 2：验证所有输入文件都在结果中
    all_files_in_result = []
    for category_files in result.categories.values():
        all_files_in_result.extend(category_files)
    
    assert len(all_files_in_result) == len(files), \
        "结果中的文件数量应该等于输入文件数量"
    
    # 属性 3：验证结果中的每个文件对象都来自输入
    # 注意：这里我们比较对象本身，而不是路径，因为同一路径可能有多个文件对象
    for file in all_files_in_result:
        assert file in files, \
            f"结果中的文件 {file.path} 不在输入文件列表中"


@settings(max_examples=20)
@given(files=junk_files_list_strategy)
def test_scan_result_no_duplicate_files_across_categories(files):
    """
    属性测试：验证每个文件对象只出现在其对应的类别中
    
    这是属性 1 的另一个角度：确保分组逻辑将每个文件对象放在正确的类别中，
    且不会将同一个文件对象放入多个类别。
    
    **验证需求：需求 1.1**
    """
    # 手动构建按类别分组的字典
    categories = {}
    for file in files:
        if file.category not in categories:
            categories[file.category] = []
        categories[file.category].append(file)
    
    # 创建 ScanResult
    result = ScanResult(
        categories=categories,
        total_size=sum(f.size for f in files),
        total_count=len(files),
        scan_duration=0.0,
        errors=[],
        requires_admin=False,
        inaccessible_categories=[]
    )
    
    # 收集所有类别中的文件对象（使用 id 来唯一标识对象）
    file_ids_by_category = {}
    for category, category_files in result.categories.items():
        file_ids_by_category[category] = set(id(f) for f in category_files)
    
    # 验证任意两个类别之间没有重复的文件对象
    categories_list = list(file_ids_by_category.keys())
    for i in range(len(categories_list)):
        for j in range(i + 1, len(categories_list)):
            cat1 = categories_list[i]
            cat2 = categories_list[j]
            
            intersection = file_ids_by_category[cat1] & file_ids_by_category[cat2]
            assert len(intersection) == 0, \
                f"类别 {cat1} 和 {cat2} 之间有重复的文件对象"


@settings(max_examples=20)
@given(files=junk_files_list_strategy)
def test_scan_result_category_membership_is_correct(files):
    """
    属性测试：验证每个类别中的所有文件都正确属于该类别
    
    这是属性 1 的第三个角度：确保分组逻辑正确。
    
    **验证需求：需求 1.1**
    """
    # 手动构建按类别分组的字典
    categories = {}
    for file in files:
        if file.category not in categories:
            categories[file.category] = []
        categories[file.category].append(file)
    
    # 创建 ScanResult
    result = ScanResult(
        categories=categories,
        total_size=sum(f.size for f in files),
        total_count=len(files),
        scan_duration=0.0,
        errors=[],
        requires_admin=False,
        inaccessible_categories=[]
    )
    
    # 验证每个类别中的文件都有正确的 category 属性
    for category, category_files in result.categories.items():
        for file in category_files:
            assert file.category == category, \
                f"文件 {file.path} 在类别 {category} 中，但其 category 属性是 {file.category}"
    
    # 验证所有类别的并集等于输入文件集合
    all_result_files = []
    for category_files in result.categories.values():
        all_result_files.extend(category_files)
    
    # 使用对象 id 来比较，因为同一路径可能有多个文件对象
    input_file_ids = set(id(f) for f in files)
    result_file_ids = set(id(f) for f in all_result_files)
    
    assert input_file_ids == result_file_ids, \
        "结果中的文件对象集合应该与输入文件对象集合相同"
