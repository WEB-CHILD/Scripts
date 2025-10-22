# Webchild Scripts

This repository stores small utility scripts used by the WEBCHILD project. Each script is a standalone tool for common tasks related to the project.
## Available scripts

- `dir_to_warc.py`
  - Description: Walks a directory and archives every file into a WARC (Web ARChive) file. Each file is written as a WARC "response" record with a synthetic URL based on a provided base URL. Useful for preserving old sites, static sites or file trees in a format compatible with web archiving tools.
  - Basic usage:

    ```bash
    python3 dir_to_warc.py <input_dir> <output_file.warc.gz> <base_url> [--date ISO_DATE]
    ```

    Example:

    ```bash
    python3 dir_to_warc.py site/ site.warc.gz https://example.com --date 2025-10-17T12:00:00Z
    ```

  - Notes:
    - If `--date` is not provided the script uses the current UTC time as the WARC date.
    - The script attempts to guess MIME types using Python's `mimetypes` module; unknown types default to `application/octet-stream`.
- `merge_warcs.py`
  - Description: Recursively finds `.warc` and `.warc.gz` files in a directory and merges their records into a single gzipped WARC file. Useful for consolidating many small WARC archives into one file for easier storage or processing.
  - Basic usage:

    ```bash
    python3 merge_warcs.py <input_dir> <output_file.warc.gz>
    ```

    Example:

    ```bash
    python3 merge_warcs.py warcs/ merged.warc.gz
    ```

  - Notes:
    - The script preserves original records and headers. It writes records exactly as read using `warcio`'s ArchiveIterator and WARCWriter.
    - Input files are detected case-insensitively by the extensions `.warc` and `.warc.gz`.
    - If you need regenerated WARC-Record-IDs, normalized timestamps, or header changes, the script can be extended to transform records before writing.
    - Ensure the `warcio` package is installed (`pip install warcio`). If `warcio` isn't available the script will raise an error and print installation advice.

- `warc_content_pie.py`
  - Description: Analyze a WARC file and create a pie chart of MIME type distribution.
  - Basic usage:

    ```bash
    python3 warc_content_pie.py <input.warc.gz> [--min-percent 1.0] [--output pie.png]
    ```

    Example (save chart):

    ```bash
    python3 warc_content_pie.py example.warc.gz --min-percent 0.5 --output mimetypes.png
    ```

  - Notes:
    - MIME types that individually account for less than `--min-percent` percent of the total are grouped into a single "Other" slice.

- `markdown_render_html_from_warc.py`
  - Description: Convert HTML pages in a WARC to Markdown files.
  - Basic usage:

    ```bash
    python3 markdown_render_html_from_warc.py <input.warc.gz> [--output-dir markdown_pages]
    ```

    Example:

    ```bash
    python3 markdown_render_html_from_warc.py example.warc.gz --output-dir md_out/
    ```

  - Notes:
    - The script uses `html2text` to convert HTML to Markdown. Install it with `pip install html2text`.

## Requirements

- Python 3.7 or newer
- The `warcio` package (install with `pip install warcio`)

It's recommended to run the scripts inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install warcio
```

## Contributing

Add new scripts at the repository root and update this README with a short description and usage example for each new file.

