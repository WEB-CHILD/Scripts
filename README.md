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

