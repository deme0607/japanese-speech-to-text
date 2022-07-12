#!/usr/bin/env python3

"""
Usage:
    csv_validator.py validate <csv_filename>

Options:
    -h --help    show this
"""

import sys
import csv
from typing import List, Optional
from docopt import docopt


class CsvRow:
    """
    CSV header
    start_ms, end_ms, start_tc, end_tc, is_estimated_start, is_estimated_end, original_text, translated_text
    """
    i_start_ms = 0
    i_end_ms = 1
    i_start_tc = 2
    i_end_tc = 3

    def __init__(self, row_num: int, original: List[str], prev: Optional["CsvRow"]) -> None:
        self.row_num = row_num
        self.start_ms = int(original[self.i_start_ms]) if original[self.i_start_ms] else None
        self.end_ms = int(original[self.i_end_ms]) if original[self.i_end_ms] else None
        self.start_tc = original[self.i_start_tc]
        self.end_tc = original[self.i_end_tc]
        self.original = original
        self.prev = prev

    def validate_timestamp(self) -> bool:
        if self.start_ms and self.end_ms:
            assert self.start_ms < self.end_ms, f"Invalid row {self.row_num}: start_ms: {self.start_ms}, end_ms: {self.end_ms}"

        if self.start_tc and self.end_tc:
            assert self.start_tc < self.end_tc, f"Invalid row {self.row_num}: start_tc: {self.start_tc}, end_tc: {self.end_tc}"

        if not self.prev:
            return True

        if self.start_ms and self.prev.end_ms:
            assert self.prev.end_ms < self.start_ms, f"Invalid row {i + 1}: start_ms: {self.start_ms}, p_end_ms: {self.prev.end_ms}"

        if self.start_tc and self.end_tc:
            assert self.prev.end_tc < self.start_tc, f"Invalid row {i + 1}: start_tc: {self.start_tc}, p_end_tc: {self.prev.end_tc}"

        return True


if __name__ != "__main__":
    sys.exit(__doc__)

arguments = docopt(__doc__)
csv_filename = arguments["<csv_filename>"]


with open(csv_filename) as csvfile:
    reader = csv.reader(csvfile)

    prev_r = None
    count = 0
    for i, row in enumerate(reader):
        count += 1
        if i == 0:
            continue

        r = CsvRow(i + 1, row, prev_r)
        r.validate_timestamp()
        prev_r = r

print(f"{count} rows validated.")
