from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union


@dataclass
class TrafficRecord:
    timestamp: datetime
    count: int


def parse_record_line(line: str) -> Optional[TrafficRecord]:
    stripped = line.strip()
    if not stripped:
        return None
    
    parts = stripped.split(maxsplit=1)
    if len(parts) != 2:
        return None

    timestamp_text, count_text = parts
    timestamp = datetime.fromisoformat(timestamp_text)
    count = int(count_text)
    
    return TrafficRecord(timestamp, count)


def load_records(path: Union[str, Path]) -> list[TrafficRecord]:
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
    return sum(record.count for record in records)


def daily_totals(records: list[TrafficRecord]) -> list[tuple[date, int]]:
    totals: dict[date, int] = {}
    for record in records:
        record_date = record.timestamp.date()
        totals[record_date] = totals.get(record_date, 0) + record.count
    return sorted(totals.items(), key=lambda item: item[0])


def top_n_half_hours(records: list[TrafficRecord], n: int = 3) -> list[TrafficRecord]:
    # Ignore requests for zero or negative results to avoid surprising slices
    if n <= 0 or not records:
        return []
    sorted_records = sorted(records, key=lambda record: (-record.count, record.timestamp))
    return sorted_records[:n]


def lowest_traffic_window(records: list[TrafficRecord], window_size: int = 3) -> tuple[TrafficRecord, ...]:
    # Uses sliding window algorithm for O(n) time complexity
    # Reject nonsensical window sizes early
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    ordered_records = sorted(records, key=lambda record: record.timestamp)
    
    if len(ordered_records) < window_size:
        raise ValueError(f"Not enough records: need {window_size}, got {len(ordered_records)}")
    
    current_sum = sum(record.count for record in ordered_records[:window_size])
    min_total = current_sum
    best_start = 0
    
    for start_index in range(1, len(ordered_records) - window_size + 1):
        current_sum -= ordered_records[start_index - 1].count
        current_sum += ordered_records[start_index + window_size - 1].count
        
        if current_sum < min_total:
            min_total = current_sum
            best_start = start_index
    
    return tuple(ordered_records[best_start : best_start + window_size])

