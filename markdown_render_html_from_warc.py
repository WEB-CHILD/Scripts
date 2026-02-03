import os
import re
from datetime import datetime
from warcio.archiveiterator import ArchiveIterator
"""markdown_render_html_from_warc

Convert HTML responses inside a WARC/WARC.GZ archive into individual
Markdown files.

Behavior:
- Scans each WARC `response` record and selects those with a
    `Content-Type` containing `text/html`.
- Converts the HTML payload to Markdown using `html2text`.
- Writes one `.md` file per page under the configured output
    directory. Each file begins with a single metadata line in the
    format `waybackdate/original-url` followed by the converted
    Markdown body.

Output filename format:
- `{waybackdate}_{safe_url}.md` where `waybackdate` is derived
    from the `WARC-Date` header in `YYYYmmddHHMMSS` form or
    `unknown_date` when parsing fails. `safe_url` is a filesystem-
    safe transformation of the original URL.

Limitations and notes:
- Requires Python 3.8+ and the third-party packages `warcio`
    and `html2text`.
- HTML→Markdown conversion is best-effort; complex pages may need
    post-processing.
- Non-UTF8 bytes are decoded with errors ignored to avoid crashes.

Example usage:
```
python markdown_render_html_from_warc.py archive.warc.gz --output-dir markdown_pages
```
"""
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
                    # Write a single metadata line in the format: waybackdate/original-url
                    f.write(f"{wayback_date}/{url}\n\n")
                    f.write(markdown_content)

                count += 1

print(f"Extracted and converted {count} HTML pages to Markdown in '{OUTPUT_DIR}/'")
