import argparse
import sys

from .analysis import (
    daily_totals,
    load_records,
    lowest_traffic_window,
    top_n_half_hours,
    total_cars,
)


def main(argv=None) -> int:
    """
    命令行接口主函数，解析参数并执行交通流量分析
    
    实现要点：
    - 使用 argparse 解析命令行参数。
      如果不用 argparse，需要手动解析 sys.argv，代码复杂且容易出错
    - 位置参数 "file" 必须提供，可选参数 "--top" 和 "--window" 有默认值。
      如果不用 argparse，需要手动判断参数是否存在，处理默认值等
    - 使用 try-except 捕获和处理错误。
      如果不用异常处理，文件不存在或其他错误会导致程序崩溃，用户体验差
    - 使用 sys.stderr 输出错误信息，sys.stdout 输出正常结果。
      如果不用 stderr，错误信息和正常输出混在一起，无法区分
    - 返回退出码：0 表示成功，非零表示失败。
      如果不用退出码，调用者无法判断程序是否成功执行
    """
    parser = argparse.ArgumentParser(description="Analyse traffic counter output files")
    parser.add_argument("file", help="Path to the traffic counter data file")
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of busiest half hours to show (default: 3)",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=3,
        help="Half-hour records per low-traffic window (default: 3)",
    )
    args = parser.parse_args(argv)

    try:
        records = load_records(args.file)
    except FileNotFoundError:
        # 文件不存在时输出到标准错误流，返回非零退出码
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        # 捕获所有其他异常，避免程序崩溃
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    print(f"Total {total_cars(records)}")
    for record_date, count in daily_totals(records):
        print(f"{record_date.isoformat()} {count}")

    busiest = top_n_half_hours(records, args.top)
    print("Top half hours:")
    for record in busiest:
        print(f"{record.timestamp.isoformat()} {record.count}")

    try:
        lowest_window = lowest_traffic_window(records, args.window)
        start_time = lowest_window[0].timestamp
        total = sum(record.count for record in lowest_window)
        print("Lowest traffic window:")
        print(f"Start {start_time.isoformat()} Total {total}")
    except ValueError:
        print("No low-traffic window available")

    return 0


# 这个判断确保：直接运行此文件时执行 main()，但作为模块导入时不会执行
# 如果不用这个判断，导入模块时就会执行 main()，导致意外行为
# 这是 Python 脚本的标准写法
if __name__ == "__main__":
    # sys.exit() 设置程序的退出码（0 表示成功，非零表示失败）
    # 如果不用 sys.exit()，退出码可能不正确，调用者无法判断程序执行结果
    sys.exit(main())

