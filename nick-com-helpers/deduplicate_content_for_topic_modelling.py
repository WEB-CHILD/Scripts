import csv
import os
import glob
import argparse

INPUT_GLOB = "*_nick_message_board_posts_for_topic_modelling_input.csv"

parser = argparse.ArgumentParser(description="Deduplicate message board posts by exact content match.")
parser.add_argument("--input-dir", default=os.path.dirname(os.path.abspath(__file__)))
parser.add_argument("--output-dir", default=os.path.dirname(os.path.abspath(__file__)))
parser.add_argument(
    "--input-file",
    help="Specific posts CSV to dedupe (overrides auto-discovery of the latest "
         "*_input.csv in --input-dir)",
)
args = parser.parse_args()

if args.input_file:
    input_path = (
        args.input_file if os.path.isabs(args.input_file)
        else os.path.join(args.input_dir, args.input_file)
    )
else:
    # Date-prefixed filenames sort chronologically, so the last match is newest.
    candidates = sorted(glob.glob(os.path.join(args.input_dir, INPUT_GLOB)))
    if not candidates:
        parser.error(f"No file matching {INPUT_GLOB!r} found in {args.input_dir}")
    input_path = candidates[-1]

# Mirror the input's date prefix in the deduped output name.
output_name = os.path.basename(input_path).replace("_input.csv", "_deduped.csv")
output_path = os.path.join(args.output_dir, output_name)

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

print(f"Input file:  {input_path}")
print(f"Input rows:  {rows_kept + rows_dropped:,}")
print(f"Kept:        {rows_kept:,}")
print(f"Duplicates:  {rows_dropped:,}")
print(f"Output:      {output_path}")
