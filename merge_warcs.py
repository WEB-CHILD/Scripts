#!/usr/bin/env python3
"""merge_warcs.py

Merge all .warc and .warc.gz files from a directory (recursively) into a
single gzip-compressed WARC file.

This script reads each input WARC using warcio.archiveiterator.ArchiveIterator
and writes records into an output WARC using warcio.warcwriter.WARCWriter.

Usage:
    python merge_warcs.py /path/to/warcs output.warc.gz

Notes:
- Input files ending with .gz are opened with gzip so compressed WARCs are
  supported.
- The script preserves original records, including WARC headers. If you need
  to re-assign WARC-Record-IDs or normalize headers, modify the copying logic.
"""

from __future__ import annotations
import os
import argparse
import gzip
import sys
from typing import List

try:
    from warcio.archiveiterator import ArchiveIterator
    from warcio.warcwriter import WARCWriter
except Exception as e:
    print("Required package 'warcio' is not installed. Install with: pip install warcio", file=sys.stderr)
    raise


def find_warc_files(input_dir: str) -> List[str]:
    """Recursively find files that look like WARC files in input_dir.

    Matches case-insensitively on .warc and .warc.gz.
    """
    matches: List[str] = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            lname = name.lower()
            if lname.endswith('.warc') or lname.endswith('.warc.gz'):
                matches.append(os.path.join(root, name))
    matches.sort()
    return matches


def merge_warcs(input_dir: str, output_path: str) -> None:
    files = find_warc_files(input_dir)
    if not files:
        print(f"No .warc or .warc.gz files found in {input_dir}")
        return

    total_records = 0
    print(f"Merging {len(files)} files into: {output_path}")

    with open(output_path, 'wb') as out_f:
        writer = WARCWriter(out_f, gzip=True)

        for idx, fpath in enumerate(files, start=1):
            print(f"[{idx}/{len(files)}] Reading: {fpath}")
            opener = gzip.open if fpath.lower().endswith('.gz') else open
            with opener(fpath, 'rb') as in_f:
                try:
                    for record in ArchiveIterator(in_f):
                        # write_record accepts the record yielded by ArchiveIterator
                        writer.write_record(record)
                        total_records += 1
                except Exception as exc:
                    print(f"Warning: failed to read records from {fpath}: {exc}", file=sys.stderr)

    print(f"Done. Wrote {total_records} records into {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge .warc and .warc.gz files into one warc.gz')
    parser.add_argument('input_dir', help='Directory containing .warc or .warc.gz files')
    parser.add_argument('output_file', help='Output WARC file (e.g., merged.warc.gz)')
    args = parser.parse_args()

    merge_warcs(args.input_dir, args.output_file)
