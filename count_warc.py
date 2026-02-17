#!/usr/bin/env python3
from warcio.archiveiterator import ArchiveIterator
import sys

filename = sys.argv[1]
count = 0

with open(filename, 'rb') as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type == 'response':
            count += 1

print(f"Response records: {count}")