import csv
import os
import argparse

INPUT_FILE = "20260625_nick_message_board_posts_for_topic_modelling_input.csv"
OUTPUT_FILE = "20260625_nick_message_board_posts_for_topic_modelling_deduped.csv"

parser = argparse.ArgumentParser(description="Deduplicate message board posts by exact content match.")
parser.add_argument("--input-dir", default=os.path.dirname(os.path.abspath(__file__)))
parser.add_argument("--output-dir", default=os.path.dirname(os.path.abspath(__file__)))
args = parser.parse_args()

input_path = os.path.join(args.input_dir, INPUT_FILE)
output_path = os.path.join(args.output_dir, OUTPUT_FILE)

seen_content = set()
rows_kept = 0
rows_dropped = 0

with open(input_path, newline="", encoding="utf-8") as infile, \
     open(output_path, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        content = row["content"]
        if content not in seen_content:
            seen_content.add(content)
            writer.writerow(row)
            rows_kept += 1
        else:
            rows_dropped += 1

print(f"Input rows:  {rows_kept + rows_dropped:,}")
print(f"Kept:        {rows_kept:,}")
print(f"Duplicates:  {rows_dropped:,}")
print(f"Output:      {output_path}")
