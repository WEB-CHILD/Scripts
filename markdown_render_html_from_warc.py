import os
import re
from datetime import datetime
from warcio.archiveiterator import ArchiveIterator
import html2text
import argparse

# ======== CONFIGURATION ========
parser = argparse.ArgumentParser(description='Render HTML pages from a WARC file into Markdown files')
parser.add_argument('warc_file', help='Path to the input WARC or WARC.GZ file')
parser.add_argument('--output-dir', '-o', default='markdown_pages', help='Directory to write Markdown files to (default: markdown_pages)')
args = parser.parse_args()

WARC_FILE = args.warc_file
OUTPUT_DIR = args.output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set up HTML → Markdown converter
converter = html2text.HTML2Text()
converter.ignore_links = False
converter.ignore_images = False
converter.body_width = 0  # no line wrapping

# ======== MAIN PROCESS ========
count = 0

with open(WARC_FILE, "rb") as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type == "response":
            content_type = record.http_headers.get_header("Content-Type") or ""
            if "text/html" in content_type.lower():
                # Extract metadata
                url = record.rec_headers.get_header("WARC-Target-URI") or "unknown_url"
                warc_date = record.rec_headers.get_header("WARC-Date") or ""

                # Convert date to a filesystem-friendly format
                try:
                    wayback_date = datetime.strptime(warc_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H%M%S")
                except Exception:
                    wayback_date = "unknown_date"

                # Create a safe filename from the URL
                safe_url = re.sub(r"[^a-zA-Z0-9._-]+", "_", url)
                filename = f"{wayback_date}_{safe_url}.md"

                # Limit filename length (to avoid filesystem issues)
                if len(filename) > 200:
                    filename = filename[:200] + ".md"

                filepath = os.path.join(OUTPUT_DIR, filename)

                # Extract and convert HTML
                html_content = record.content_stream().read().decode("utf-8", errors="ignore")
                markdown_content = converter.handle(html_content)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# Source URL\n{url}\n\n")
                    f.write(f"# Archived at\n{warc_date}\n\n")
                    f.write(markdown_content)

                count += 1

print(f"Extracted and converted {count} HTML pages to Markdown in '{OUTPUT_DIR}/'")
