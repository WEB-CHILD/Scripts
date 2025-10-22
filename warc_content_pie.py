import warcio
from warcio.archiveiterator import ArchiveIterator
from collections import Counter
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Plot MIME type distribution from a WARC file')
parser.add_argument('warc_file', help='Path to the input WARC or WARC.GZ file')
parser.add_argument('--output', '-o', help='Optional path to save the pie chart image (e.g., pie.png)')
parser.add_argument('--min-percent', type=float, default=1.0, help='Minimum percent threshold; types below this are grouped into "Other" (default: 1.0)')
args = parser.parse_args()

warc_file_path = args.warc_file

# Collect MIME types
mime_types = []

with open(warc_file_path, 'rb') as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type == 'response':
            content_type = record.http_headers.get_header('Content-Type')
            if content_type:
                # Some Content-Types have parameters like charset, so split them
                mime_type = content_type.split(';')[0].strip()
                mime_types.append(mime_type)

# Count occurrences of each MIME type
mime_counter = Counter(mime_types)

# Prepare data for pie chart, grouping small categories into 'Other'
total = sum(mime_counter.values())
min_pct = max(0.0, args.min_percent) / 100.0

labels = []
sizes = []
other_count = 0

for mime, count in mime_counter.most_common():
    pct = count / total if total > 0 else 0
    if pct < min_pct:
        other_count += count
    else:
        labels.append(mime)
        sizes.append(count)

if other_count > 0:
    labels.append('Other')
    sizes.append(other_count)

# Create pie chart
plt.figure(figsize=(10, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title('MIME Type Distribution in WARC File')
plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
if args.output:
    plt.savefig(args.output, bbox_inches='tight')
    print(f"Saved pie chart to {args.output}")
else:
    plt.show()
