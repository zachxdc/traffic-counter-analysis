from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union


# 数据模型：使用 dataclass 自动生成 __init__、__repr__、__eq__ 等方法
# 如果不用 dataclass，需要手动写这些方法，代码冗长且容易出错
# 包含时间戳和车辆数量两个字段，用于表示每半小时的交通流量记录
@dataclass
class TrafficRecord:
    timestamp: datetime  # 时间戳：记录的时间
    count: int  # 车辆数量：该时间段内的车辆数


def parse_record_line(line: str) -> Optional[TrafficRecord]:
    """
    解析单行数据，将文本转换为 TrafficRecord 对象
    
    设计要点：
    - 容错处理：遇到空行或格式错误返回 None，不中断程序运行。
      如果不用容错处理，遇到错误行会抛出异常，整个程序崩溃
    - 使用 maxsplit=1 确保只分割一次，得到时间戳和数量两部分.
      即使时间戳和数量之间可能有多个空格，也只分割一次
    - 使用 datetime.fromisoformat() 解析 ISO 8601 格式时间。
      如果不用这个方法，需要手动解析年月日时分秒，代码复杂且容易出错
    """
    stripped = line.strip()
    if not stripped:
        return None
    
    # maxsplit=1 确保只分割一次，得到时间戳和数量两部分
    # 例如 "2021-12-01T05:00:00 10" -> ["2021-12-01T05:00:00", "10"]
    # 如果时间戳是 "2021-12-01T05:00:00"，不用 maxsplit=1 可能会被错误分割
    parts = stripped.split(maxsplit=1)
    if len(parts) != 2:
        return None

    timestamp_text, count_text = parts
    # fromisoformat 自动解析 ISO 8601 格式，如果不用需要手动解析每个部分
    timestamp = datetime.fromisoformat(timestamp_text)
    count = int(count_text)
    
    return TrafficRecord(timestamp, count)


def load_records(path: Union[str, Path]) -> list[TrafficRecord]:
    """
    从文件加载交通流量记录
    
    实现要点：
    - 使用 Path 对象统一处理文件路径，支持跨平台。
      如果不用 Path，需要手动拼接路径，Windows 用 "\\"，Linux/Mac 用 "/"，
      代码无法跨平台运行
    - 明确指定 UTF-8 编码，避免中文乱码。
      如果不用 encoding="utf-8"，系统默认编码可能不是 UTF-8（如 Windows 可能是 GBK），
      读取中文(garbled text)等字符时会出现乱码
    - 使用 with 上下文管理器自动关闭文件：如果不用就需要手动写 handle.close()，
      而且如果代码中间出错，可能不会执行到 close()，导致文件一直打开占用资源
    - 过滤无效记录，保证数据质量。
      如果不过滤，空行和格式错误的行会导致后续分析出错
    - 按时间戳排序，为后续分析做准备。
      如果数据本身无序，滑动窗口等算法会得到错误结果
    """
    file_path = Path(path)
    records: list[TrafficRecord] = []
    
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = parse_record_line(line)
            if record:
                records.append(record)
    
    records.sort(key=lambda record: record.timestamp)
    return records


def total_cars(records: list[TrafficRecord]) -> int:
    """
    计算总车辆数
    
    使用生成器表达式遍历所有记录并求和。
    时间复杂度 O(n)，空间复杂度 O(1)。
    如果不用生成器表达式，用列表推导式 [record.count for record in records]，
    时间复杂度仍然是 O(n) 但需要两次遍历（先创建列表再求和），
    空间复杂度 O(n)（需要存储整个列表），对于大量数据会占用更多内存
    """
    return sum(record.count for record in records)


def daily_totals(records: list[TrafficRecord]) -> list[tuple[date, int]]:
    """
    计算每日车辆数汇总
    
    实现思路：
    - 使用字典按日期分组累加。
      如果不用字典，需要遍历多次或使用复杂的数据结构，效率低
    - 使用 datetime.date() 提取日期部分（去掉时分秒）。
      如果不用 date()，需要手动提取年月日，代码复杂且容易出错
    - 使用 dict.get(key, 0) 处理首次出现的日期。
      如果不用 get()，需要先判断 key 是否存在，代码冗长：
      if record_date in totals: totals[record_date] += count
      else: totals[record_date] = count
    - 返回按日期排序的结果，方便查看时间顺序
    """
    totals: dict[date, int] = {}
    for record in records:
        record_date = record.timestamp.date()
        totals[record_date] = totals.get(record_date, 0) + record.count
    return sorted(totals.items(), key=lambda item: item[0])


def top_n_half_hours(records: list[TrafficRecord], n: int = 3) -> list[TrafficRecord]:
    """
    找出最繁忙的 N 个半小时时段
    
    排序策略：
    - 先按车辆数降序（使用负数实现降序）。
      如果不用负数，需要设置 reverse=True，但这样无法同时实现多键排序
    - 数量相同时按时间戳升序。
      确保相同数量的记录有稳定的排序顺序
    - 使用元组比较实现多键排序。
      如果不用元组，需要多次排序或写复杂的比较函数，代码复杂且效率低
    """
    if n <= 0 or not records:
        return []
    sorted_records = sorted(records, key=lambda record: (-record.count, record.timestamp))
    return sorted_records[:n]


def lowest_traffic_window(records: list[TrafficRecord], window_size: int = 3) -> tuple[TrafficRecord, ...]:
    """
    使用滑动窗口算法找出流量最低的连续时间段
    
    算法优势：
    - 时间复杂度 O(n)，比暴力方法 O(n²) 更高效。
      如果不用滑动窗口，暴力法需要计算每个窗口的总和，窗口大小 k、记录数 n 时，
      需要计算 (n-k+1) 个窗口，每个窗口需要 k 次加法，总操作数约 (n-k+1)*k
    - 核心思想：维护运行总和，窗口滑动时只需更新边界元素。
      如果不用这个技巧，每次滑动都要重新计算整个窗口的和，效率低
    - 例如窗口大小 3、记录数 100：暴力法约 294 次操作，滑动窗口约 197 次
    
    实现步骤：
    1. 参数校验和记录排序：确保窗口是连续的时间段
    2. 计算第一个窗口的总和：初始化运行总和
    3. 滑动窗口：减去离开的元素，加上新进入的元素（每次只需 2 次操作）
    4. 跟踪最小总和和最佳窗口位置：记录最优解
    """
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    ordered_records = sorted(records, key=lambda record: record.timestamp)
    
    if len(ordered_records) < window_size:
        raise ValueError(f"Not enough records: need {window_size}, got {len(ordered_records)}")
    
    # 初始化第一个窗口：计算前 window_size 个记录的总和
    # 如果不用滑动窗口，这里就是暴力法的开始，后续每个窗口都要重新计算
    current_sum = sum(record.count for record in ordered_records[:window_size])
    min_total = current_sum
    best_start = 0
    
    # 滑动窗口：每次向右移动一位，更新运行总和
    # 关键优化：只需减去离开窗口的元素，加上新进入窗口的元素（2 次操作）
    # 如果不用这个优化，每次都要重新计算整个窗口（window_size 次操作）
    for start_index in range(1, len(ordered_records) - window_size + 1):
        current_sum -= ordered_records[start_index - 1].count  # 移除左边界元素
        current_sum += ordered_records[start_index + window_size - 1].count  # 添加右边界新元素
        
        if current_sum < min_total:
            min_total = current_sum
            best_start = start_index
    
    return tuple(ordered_records[best_start : best_start + window_size])

