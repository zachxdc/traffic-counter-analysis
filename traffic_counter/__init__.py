# 包初始化文件：导出主要功能供外部使用
# 如果不用 __init__.py 导出，外部使用时需要写 traffic_counter.analysis.function_name，
# 使用后可以简写为 traffic_counter.function_name，更简洁
from .analysis import (
    TrafficRecord,
    daily_totals,
    load_records,
    lowest_traffic_window,
    top_n_half_hours,
    total_cars,
)

