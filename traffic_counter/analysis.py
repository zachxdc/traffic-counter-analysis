from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union


# @dataclass 装饰器自动生成 __init__, __repr__ 等方法
# 这样就不用手动写构造函数了
@dataclass
class TrafficRecord:
    timestamp: datetime  # 时间戳：记录的时间
    count: int  # 车辆数量：该时间段内的车辆数


def parse_record_line(line: str) -> Optional[TrafficRecord]:
    # 去除行首行尾的空白字符（空格、换行符等）
    stripped = line.strip()
    # 如果行是空的，返回 None（表示解析失败）
    if not stripped:
        return None
    
    # maxsplit=1 表示最多分割成2部分：时间戳和数量
    # 例如 "2021-12-01T05:00:00 10" -> ["2021-12-01T05:00:00", "10"]
    parts = stripped.split(maxsplit=1)
    if len(parts) != 2:
        return None

    # 解包：将列表的两个元素分别赋给两个变量
    timestamp_text, count_text = parts
    # fromisoformat 将 ISO 格式的字符串转换为 datetime 对象
    timestamp = datetime.fromisoformat(timestamp_text)
    # int() 将字符串转换为整数
    count = int(count_text)
    
    return TrafficRecord(timestamp, count)


def load_records(path: Union[str, Path]) -> list[TrafficRecord]:
    # Path 对象可以统一处理文件路径，无论输入是字符串还是 Path 对象
    file_path = Path(path)
    # 类型注解：records 是一个 TrafficRecord 列表
    records: list[TrafficRecord] = []
    
    # with 语句确保文件在使用后自动关闭（即使出错也会关闭）
    # encoding="utf-8" 指定文件编码，避免中文乱码
    with file_path.open("r", encoding="utf-8") as handle:
        # 逐行读取文件
        for line in handle:
            record = parse_record_line(line)
            # 只添加成功解析的记录（跳过空行和格式错误的行）
            if record:
                records.append(record)
    
    # lambda 是匿名函数：key=lambda record: record.timestamp
    # 意思是"按 timestamp 字段排序"
    records.sort(key=lambda record: record.timestamp)
    return records


def total_cars(records: list[TrafficRecord]) -> int:
    # 生成器表达式：遍历所有记录，取出每个记录的 count 字段，然后求和
    # 这是 Python 中常见的简洁写法
    return sum(record.count for record in records)


def daily_totals(records: list[TrafficRecord]) -> list[tuple[date, int]]:
    # 字典：键是日期，值是当天的总车辆数
    totals: dict[date, int] = {}
    for record in records:
        # .date() 从 datetime 中提取日期部分（去掉时间）
        record_date = record.timestamp.date()
        # dict.get(key, default) 如果键存在返回值，不存在返回默认值 0
        # 这样第一次遇到某个日期时，从 0 开始累加
        totals[record_date] = totals.get(record_date, 0) + record.count
    # totals.items() 返回 (日期, 总数) 的元组列表
    # 按日期（item[0]）排序后返回
    return sorted(totals.items(), key=lambda item: item[0])


def top_n_half_hours(records: list[TrafficRecord], n: int = 3) -> list[TrafficRecord]:
    # 处理边界情况：如果 n <= 0 或记录为空，返回空列表
    if n <= 0 or not records:
        return []
    # 排序：先按 count 降序（负数实现降序），count 相同时按时间戳升序
    # (-record.count, record.timestamp) 是元组，Python 会先比较第一个元素
    sorted_records = sorted(records, key=lambda record: (-record.count, record.timestamp))
    # 切片 [:n] 取前 n 个元素
    return sorted_records[:n]


def lowest_traffic_window(records: list[TrafficRecord], window_size: int = 3) -> tuple[TrafficRecord, ...]:
    # 滑动窗口算法：时间复杂度 O(n)，比暴力方法 O(n²) 更高效
    # 先检查参数是否合理
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    # 按时间顺序排序，确保窗口是连续的时间段
    ordered_records = sorted(records, key=lambda record: record.timestamp)
    
    # 如果记录数不够，无法形成窗口
    if len(ordered_records) < window_size:
        raise ValueError(f"Not enough records: need {window_size}, got {len(ordered_records)}")
    
    # 计算第一个窗口的总和（前 window_size 个记录）
    current_sum = sum(record.count for record in ordered_records[:window_size])
    min_total = current_sum  # 当前找到的最小总和
    best_start = 0  # 最佳窗口的起始位置
    
    # 滑动窗口：每次向右移动一位
    # range(1, len - window_size + 1) 确保窗口不会越界
    for start_index in range(1, len(ordered_records) - window_size + 1):
        # 滑动窗口技巧：减去离开窗口的元素，加上新进入窗口的元素
        # 这样不需要每次都重新计算整个窗口的和
        current_sum -= ordered_records[start_index - 1].count  # 移除左边界元素
        current_sum += ordered_records[start_index + window_size - 1].count  # 添加右边界新元素
        
        # 如果当前窗口的总和更小，更新最佳窗口
        if current_sum < min_total:
            min_total = current_sum
            best_start = start_index
    
    # 返回最佳窗口的所有记录（使用切片）
    return tuple(ordered_records[best_start : best_start + window_size])

