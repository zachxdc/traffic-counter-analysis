from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Union


@dataclass
class TrafficRecord:
    timestamp: datetime
    count: int


@dataclass
class TrafficWindow:
    records: tuple[TrafficRecord, ...]

    @property
    def start(self):
        return self.records[0].timestamp

    @property
    def end(self):
        return self.records[-1].timestamp + timedelta(minutes=30)

    @property
    def total(self):
        return sum(record.count for record in self.records)


def parse_record_line(line: str) -> TrafficRecord:
    if not isinstance(line, str):
        raise TypeError(f"Expected str, got {type(line).__name__}")
    
    stripped = line.strip()
    if not stripped:
        raise ValueError("Line is empty")
    
    parts = stripped.split()
    if len(parts) != 2:
        raise ValueError(f"Expected exactly 2 fields (timestamp and count), got {len(parts)}: {stripped[:50]}")
    
    timestamp_text, count_text = parts
    
    try:
        timestamp = datetime.fromisoformat(timestamp_text)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_text}") from e
    
    try:
        count = int(count_text)
    except ValueError as e:
        raise ValueError(f"Count must be an integer, got: {count_text}") from e
    
    if count < 0:
        raise ValueError(f"Count must be non-negative, got: {count}")
    
    return TrafficRecord(timestamp, count)


def load_records(path: Union[str, Path]) -> list[TrafficRecord]:
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    records: list[TrafficRecord] = []
    line_number = 0
    
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(parse_record_line(line))
                except ValueError as e:
                    raise ValueError(f"Parse error at line {line_number}: {e}") from e
    except (OSError, IOError) as e:
        raise IOError(f"Failed to read file {file_path}: {e}") from e
    except UnicodeDecodeError as e:
        raise ValueError(f"File encoding error in {file_path}: {e}") from e
    
    if not records:
        raise ValueError(f"No valid records found in {file_path}")
    
    records.sort(key=lambda record: record.timestamp)
    return records


def total_cars(records: Iterable[TrafficRecord]) -> int:
    return sum(record.count for record in records)


def daily_totals(records: Iterable[TrafficRecord]) -> list[tuple[date, int]]:
    if records is None:
        raise ValueError("records cannot be None")
    totals: dict[date, int] = {}
    for record in records:
        if not isinstance(record, TrafficRecord):
            raise TypeError(f"Expected TrafficRecord, got {type(record).__name__}")
        record_date = record.timestamp.date()
        totals[record_date] = totals.get(record_date, 0) + record.count
    return sorted(totals.items(), key=lambda item: item[0])


def top_n_half_hours(records: Sequence[TrafficRecord], n: int = 3) -> list[TrafficRecord]:
    if records is None:
        raise ValueError("records cannot be None")
    if not isinstance(n, int):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 1:
        raise ValueError("n must be positive")
    if not records:
        return []
    sorted_records = sorted(records, key=lambda record: (-record.count, record.timestamp))
    return sorted_records[:n]


def lowest_traffic_window(records: Sequence[TrafficRecord], window_size: int = 3) -> TrafficWindow:
    if records is None:
        raise ValueError("records cannot be None")
    if not isinstance(window_size, int):
        raise TypeError(f"window_size must be an integer, got {type(window_size).__name__}")
    if window_size < 1:
        raise ValueError("window_size must be positive")
    if len(records) < window_size:
        raise ValueError(f"Not enough records to form a window: need {window_size}, got {len(records)}")
    
    ordered_records = sorted(records, key=lambda record: record.timestamp)
    
    if len(ordered_records) < window_size:
        raise ValueError(f"Not enough records after sorting: need {window_size}, got {len(ordered_records)}")
    
    current_sum = sum(record.count for record in ordered_records[:window_size])
    min_total = current_sum
    best_start = 0
    
    for start_index in range(1, len(ordered_records) - window_size + 1):
        current_sum -= ordered_records[start_index - 1].count
        current_sum += ordered_records[start_index + window_size - 1].count
        
        if current_sum < min_total:
            min_total = current_sum
            best_start = start_index
    
    best_slice = tuple(ordered_records[best_start : best_start + window_size])
    return TrafficWindow(best_slice)

