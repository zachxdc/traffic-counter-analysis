# Traffic Counter Analysis

A Python program to analyse traffic counter data. The program reads files containing timestamped vehicle counts (recorded every half-hour) and provides statistical analysis.

## Features

The program analyses traffic counter output files and provides:

- **Total cars**: The total number of cars seen across all records
- **Daily totals**: Number of cars seen per day (in `yyyy-mm-dd` format)
- **Top busiest periods**: The top N half-hour periods with the most traffic
- **Lowest traffic window**: The 1.5-hour period (3 contiguous half-hour records) with the least traffic

## Input Format

Each line in the input file contains:
- A timestamp in ISO 8601 format (`yyyy-mm-ddThh:mm:ss`)
- The number of cars seen in that half-hour period

Example:
```
2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
```

## Usage

```bash
python3 -m traffic_counter.cli data/traffic_data_sample.txt
```

### Options

- `--top N`: Number of busiest half hours to show (default: 3)
- `--window N`: Number of half-hour records per low-traffic window (default: 3)

### Example

```bash
python3 -m traffic_counter.cli data/traffic_data_sample.txt --top 5 --window 3
```

## Running Tests

```bash
python3 -m pytest tests/
```
