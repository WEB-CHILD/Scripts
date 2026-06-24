"""Extract post content from JSON board files into a CSV for topic modelling."""

import csv
import glob
import json
import os
import re
import sys

INPUT_DIR = "output_your_world_threaded4_4_no_dups"
OUTPUT_CSV = "data/posts.csv"


def parse_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    # e.g. 0002_y-2003_bid-1_crawl-20030207203300_books-reading
    m = re.match(r"(\d+)_y-(\d+)_bid-(\w+)_crawl-(\d+)_(.+)$", base)
    if m:
        return {
            "file_index": m.group(1),
            "year": m.group(2),
            "board_id": m.group(3),
            "crawl_date": m.group(4),
            "board": m.group(5).replace("-", " "),
        }
    return {"file_index": base, "year": "", "board_id": "", "crawl_date": "", "board": ""}


def main():
    files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.json")))
    files = [f for f in files if not os.path.basename(f).startswith("index")]

    rows = []
    for filepath in files:
        file_meta = parse_filename(filepath)
        with open(filepath, encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as e:
                print(f"Skipping {filepath}: {e}", file=sys.stderr)
                continue

        for board in data:
            for thread_idx, thread in enumerate(board.get("threads", [])):
                for post_idx, post in enumerate(thread.get("posts", [])):
                    content = post.get("content", "").strip()
                    if not content:
                        continue
                    meta = post.get("metadata", {})
                    rows.append({
                        "id": f"{file_meta['file_index']}_t{thread_idx}_p{post_idx}",
                        "content": content,
                        "year": file_meta["year"],
                        "board": file_meta["board"],
                        "board_id": file_meta["board_id"],
                        "crawl_date": file_meta["crawl_date"],
                        "subject": meta.get("subject", ""),
                        "author": meta.get("from", ""),
                        "date": meta.get("date", ""),
                        "url": meta.get("playback_url", ""),
                    })

    os.makedirs("data", exist_ok=True)
    fieldnames = ["id", "content", "year", "board", "board_id", "crawl_date", "subject", "author", "date", "url"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} posts to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
