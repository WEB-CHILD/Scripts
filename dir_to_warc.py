# -----------------------------------------------------------------------------
# dir_to_warc.py
#
# This script archives all files in a given directory into a WARC (Web ARChive)
# file. Each file is stored as a WARC "response" record with a synthetic URL
# based on a provided base URL. The crawl date can be set manually or defaults
# to the current UTC time. Useful for preserving static sites or file trees in
# a format compatible with web archiving tools.
# -

import os
import argparse
import mimetypes
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from io import BytesIO
from datetime import datetime


parser = argparse.ArgumentParser(description="Archive a directory to WARC format.")
parser.add_argument("input_dir", help="Directory to archive")
parser.add_argument("output_file", help="Output WARC file (e.g., archive.warc.gz)")
parser.add_argument("url", help="Base URL for the archived files")
parser.add_argument("--date", help="Crawl date in ISO format (e.g., 2020-01-01T12:00:00Z)")

args = parser.parse_args()

input_dir = args.input_dir
output_file = args.output_file


# Use provided date or default to now in ISO format
warc_date = args.date or datetime.utcnow().isoformat(timespec='seconds') + 'Z'


# Create WARC file
with open(output_file, 'wb') as output:
    writer = WARCWriter(output, gzip=True)

    for root, _, files in os.walk(input_dir):
        for fname in files:
            path = os.path.join(root, fname)
            rel_path = os.path.relpath(path, input_dir)
            base_url = args.url.rstrip('/') + '/'
            url = base_url + rel_path.replace(os.sep, '/')

            with open(path, 'rb') as f:
                content = f.read()

            content_type = mimetypes.guess_type(fname)[0] or 'application/octet-stream'

            http_headers = StatusAndHeaders('200 OK', [('Content-Type', content_type)], protocol='HTTP/1.1')

            record = writer.create_warc_record(
                url,
                'response',
                payload=BytesIO(content),
                http_headers=http_headers,
                warc_headers_dict={'WARC-Date': warc_date}
            )
            writer.write_record(record)

print(f"WARC file created: {output_file}")
