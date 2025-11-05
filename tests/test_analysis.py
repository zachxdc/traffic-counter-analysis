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


SAMPLE_TEXT = """
2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-01T06:30:00 15
2021-12-01T07:00:00 25
2021-12-01T07:30:00 46
2021-12-01T08:00:00 42
2021-12-01T15:00:00 9
2021-12-01T15:30:00 11
2021-12-01T23:30:00 0
2021-12-05T09:30:00 18
2021-12-05T10:30:00 15
2021-12-05T11:30:00 7
2021-12-05T12:30:00 6
2021-12-05T13:30:00 9
2021-12-05T14:30:00 11
2021-12-05T15:30:00 15
2021-12-08T18:00:00 33
2021-12-08T19:00:00 28
2021-12-08T20:00:00 25
2021-12-08T21:00:00 21
2021-12-08T22:00:00 16
2021-12-08T23:00:00 11
2021-12-09T00:00:00 4
""".strip()


@pytest.fixture()
def sample_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT, encoding="utf-8")
    return file_path


def test_load_records_orders_by_timestamp(sample_file):
    records = load_records(sample_file)
    timestamps = [record.timestamp for record in records]
    assert timestamps == sorted(timestamps)


def test_total_cars(sample_file):
    records = load_records(sample_file)
    assert total_cars(records) == 398


def test_daily_totals(sample_file):
    records = load_records(sample_file)
    totals = daily_totals(records)
    assert totals == [
        (datetime(2021, 12, 1).date(), 179),
        (datetime(2021, 12, 5).date(), 81),
        (datetime(2021, 12, 8).date(), 134),
        (datetime(2021, 12, 9).date(), 4),
    ]


def test_top_n_half_hours(sample_file):
    records = load_records(sample_file)
    top = top_n_half_hours(records)
    assert [(record.timestamp.isoformat(), record.count) for record in top] == [
        ("2021-12-01T07:30:00", 46),
        ("2021-12-01T08:00:00", 42),
        ("2021-12-08T18:00:00", 33),
    ]


def test_lowest_traffic_window(sample_file):
    records = load_records(sample_file)
    window = lowest_traffic_window(records)
    assert window.start == datetime.fromisoformat("2021-12-01T15:00:00")
    assert window.total == 20
    assert [record.count for record in window.records] == [9, 11, 0]


def test_lowest_traffic_window_requires_enough_records():
    records = [
        TrafficRecord(datetime.fromisoformat("2021-12-01T05:00:00"), 10),
        TrafficRecord(datetime.fromisoformat("2021-12-01T05:30:00"), 5),
    ]
    with pytest.raises(ValueError):
        lowest_traffic_window(records, window_size=3)

