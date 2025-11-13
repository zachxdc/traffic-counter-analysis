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
    # argparse 是 Python 标准库，用于解析命令行参数
    parser = argparse.ArgumentParser(description="Analyse traffic counter output files")
    # "file" 是位置参数（必须提供），不需要加 -- 前缀
    parser.add_argument("file", help="Path to the traffic counter data file")
    # "--top" 是可选参数（有默认值），需要加 -- 前缀
    parser.add_argument(
        "--top",
        type=int,  # 自动将输入转换为整数
        default=3,  # 如果用户不提供，使用默认值 3
        help="Number of busiest half hours to show (default: 3)",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=3,
        help="Half-hour records per low-traffic window (default: 3)",
    )
    # parse_args 解析命令行参数，返回一个包含所有参数的对象
    args = parser.parse_args(argv)

    # try-except 用于捕获和处理错误
    # 如果文件不存在或其他错误发生，程序不会崩溃，而是显示错误信息
    try:
        records = load_records(args.file)
    except FileNotFoundError:
        # file=sys.stderr 将错误信息输出到标准错误流（而不是标准输出）
        # 这样用户可以区分正常输出和错误信息
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1  # 返回非零值表示程序执行失败
    except Exception as e:
        # 捕获所有其他类型的异常
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
# 这是 Python 脚本的标准写法
if __name__ == "__main__":
    # sys.exit() 设置程序的退出码（0 表示成功，非零表示失败）
    sys.exit(main())

