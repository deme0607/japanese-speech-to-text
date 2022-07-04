#!/usr/bin/env python3

"""
Usage:
    csv_validator.py validate <csv_filename>

Options:
    -h --help    show this
"""

import csv
from docopt import docopt


if __name__ == "__main__":
    arguments = docopt(__doc__)
    csv_filename = arguments["<csv_filename>"]

    with open(csv_filename) as csvfile:
        reader = csv.reader(csvfile)

        prev_row = None
        count = 0
        for i, row in enumerate(reader):
            count += 1
            if i == 0:
                continue

            start_ms = int(row[0]) if row[0] else None
            end_ms = int(row[1]) if row[1] else None
            start_tc, end_tc = row[2:4]

            if start_ms and end_ms and start_ms >= end_ms:
                print(f"Invalid row {i + 1}: start_ms: {start_ms}, end_ms: {end_ms}")
                prev_row = row
                continue

            if start_tc and end_tc and start_tc >= end_tc:
                print(f"Invalid row {i + 1}: start_tc: {start_tc}, end_tc: {end_tc}")
                prev_row = row
                continue

            if not prev_row:
                prev_row = row
                continue

            p_start_ms = int(prev_row[0]) if prev_row[0] else None
            p_end_ms = int(prev_row[1]) if prev_row[1] else None
            p_start_tc, p_end_tc = prev_row[2:4]

            if start_ms and p_end_ms and start_ms <= p_end_ms:
                print(f"Invalid row {i + 1}: start_ms: {start_ms}, p_end_ms: {p_end_ms}")
                prev_row = row
                continue

            if start_tc and p_end_tc and start_tc <= p_end_tc:
                print(f"Invalid row {i + 1}: start_tc: {start_tc}, p_end_tc: {p_end_tc}")
                prev_row = row
                continue

            prev_row = row

    print(f"{count} rows validated.")

