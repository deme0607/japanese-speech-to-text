#!/usr/bin/env python3

"""
Usage:
    src_generator.py generate <csv_filename>

Options:
    -h --help    show this
"""

import csv
from datetime import datetime, timedelta
import sys

from docopt import docopt
from srt import compose, Subtitle
from typing import List

if __name__ != "__main__":
    sys.exit(__doc__)

arguments = docopt(__doc__)
csv_filename = arguments["<csv_filename>"]

subs: List[Subtitle] = list()

with open(csv_filename) as csvfile:
    reader = csv.reader(csvfile)

    for i, row in enumerate(reader):
        if i == 0:
            continue

        s = Subtitle(i + 1, timedelta(milliseconds=int(row[0])), timedelta(milliseconds=int(row[1])), row[-1])
        subs.append(s)

print(compose(subs))
