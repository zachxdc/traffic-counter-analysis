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
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
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


if __name__ == "__main__":
    sys.exit(main())

