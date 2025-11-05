import argparse
import sys

from .analysis import (
    daily_totals,
    load_records,
    lowest_traffic_window,
    top_n_half_hours,
    total_cars,
)


def main(argv=None):
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

    records = load_records(args.file)

    print(f"Total {total_cars(records)}")
    for record_date, count in daily_totals(records):
        print(f"{record_date.isoformat()} {count}")

    busiest = top_n_half_hours(records, args.top)
    print("Top half hours:")
    for record in busiest:
        print(f"{record.timestamp.isoformat()} {record.count}")

    try:
        lowest_window = lowest_traffic_window(records, args.window)
    except ValueError:
        print("No low-traffic window available")
    else:
        print("Lowest traffic window:")
        print(f"Start {lowest_window.start.isoformat()} Total {lowest_window.total}")
        for record in lowest_window.records:
            print(f"  {record.timestamp.isoformat()} {record.count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

