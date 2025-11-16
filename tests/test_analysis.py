from datetime import datetime
from pathlib import Path

import pytest

from traffic_counter.analysis import (
    TrafficRecord,
    daily_totals,
    load_records,
    lowest_traffic_window,
    top_n_half_hours,
    total_cars,
)


# 使用 Path(__file__).parent.parent 获取项目根目录
# 如果不用 Path，需要手动拼接路径，代码不跨平台且容易出错
PROJECT_ROOT = Path(__file__).parent.parent
SAMPLE_DATA_FILE = PROJECT_ROOT / "data" / "traffic_data_sample.txt"


@pytest.fixture()
def sample_file(tmp_path):
    """
    测试 fixture：为每个测试提供样本数据文件
    
    实现要点：
    - 使用 pytest fixture 自动管理测试数据。
      如果不用 fixture，每个测试都需要重复创建和清理文件，代码冗余
    - 使用 tmp_path 创建临时文件，测试结束后自动清理。
      如果不用 tmp_path，需要手动清理文件，可能留下测试垃圾
    - 从项目数据文件复制内容到临时文件。
      如果直接使用项目文件，测试可能修改原始数据，影响其他测试
    """
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_DATA_FILE.read_text(encoding="utf-8"))
    return file_path


def test_load_records_orders_by_timestamp(sample_file):
    """
    测试 load_records 按时间戳排序
    
    验证要点：
    - 确保记录按时间戳升序排列。
      如果记录无序，滑动窗口等算法会得到错误结果
    - 使用 sorted() 与原始列表比较，验证排序正确性。
      如果不用 sorted() 比较，需要手动检查每个相邻元素，代码复杂
    """
    records = load_records(sample_file)
    timestamps = [record.timestamp for record in records]
    assert timestamps == sorted(timestamps)


def test_total_cars(sample_file):
    """
    测试总车辆数计算
    
    验证要点：
    - 验证总车辆数计算正确。
      如果计算错误，所有基于总数的分析都会出错
    - 使用固定预期值验证结果。
      如果不用固定值，无法确保计算逻辑正确
    """
    records = load_records(sample_file)
    assert total_cars(records) == 398


def test_daily_totals(sample_file):
    """
    测试每日车辆数汇总
    
    验证要点：
    - 验证按日期分组和累加正确。
      如果分组或累加错误，每日统计结果会不准确
    - 验证结果按日期排序。
      如果结果无序，用户难以查看时间趋势
    - 使用 datetime.date() 确保日期格式一致。
      如果不用 date()，datetime 对象比较可能因时间部分不同而失败
    """
    records = load_records(sample_file)
    totals = daily_totals(records)
    assert totals == [
        (datetime(2021, 12, 1).date(), 179),
        (datetime(2021, 12, 5).date(), 81),
        (datetime(2021, 12, 8).date(), 134),
        (datetime(2021, 12, 9).date(), 4),
    ]


def test_top_n_half_hours(sample_file):
    """
    测试最繁忙时段查找
    
    验证要点：
    - 验证返回的是车辆数最多的 N 个时段。
      如果排序或选择错误，用户会看到错误的繁忙时段
    - 验证结果按车辆数降序排列。
      如果顺序错误，用户无法快速识别最繁忙的时段
    - 使用 isoformat() 确保时间格式一致。
      如果不用 isoformat()，时间格式可能不一致，导致比较失败
    """
    records = load_records(sample_file)
    top = top_n_half_hours(records)
    assert [(record.timestamp.isoformat(), record.count) for record in top] == [
        ("2021-12-01T07:30:00", 46),
        ("2021-12-01T08:00:00", 42),
        ("2021-12-08T18:00:00", 33),
    ]


def test_lowest_traffic_window(sample_file):
    """
    测试最低流量窗口查找
    
    验证要点：
    - 验证返回的是流量最低的连续时间段。
      如果算法错误，用户会看到错误的低流量时段
    - 验证窗口起始时间正确。
      如果起始时间错误，用户无法准确定位低流量时段
    - 验证窗口内车辆总数正确。
      如果总和计算错误，无法确定真正的低流量窗口
    - 验证窗口内各时段车辆数正确。
      如果窗口内容错误，可能返回了错误的连续时间段
    """
    records = load_records(sample_file)
    window = lowest_traffic_window(records)
    assert window[0].timestamp == datetime.fromisoformat("2021-12-01T15:00:00")
    assert sum(record.count for record in window) == 20
    assert [record.count for record in window] == [9, 11, 0]


def test_lowest_traffic_window_requires_enough_records():
    """
    测试边界情况：记录数不足时抛出异常
    
    验证要点：
    - 验证记录数不足时抛出 ValueError。
      如果不抛出异常，函数可能返回错误结果或崩溃
    - 使用 pytest.raises() 验证异常类型和触发条件。
      如果不用 pytest.raises()，需要手动捕获异常并验证，代码冗长
    - 测试边界情况确保程序健壮性。
      如果不测试边界情况，生产环境可能遇到未处理的错误
    """
    records = [
        TrafficRecord(datetime.fromisoformat("2021-12-01T05:00:00"), 10),
        TrafficRecord(datetime.fromisoformat("2021-12-01T05:30:00"), 5),
    ]
    with pytest.raises(ValueError):
        lowest_traffic_window(records, window_size=3)