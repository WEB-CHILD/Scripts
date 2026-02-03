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

- `harvest_comparator.py`
  - Description: Test script which primary use is intended for testing the limiter function in our fork of python-wayback-machine-downloader during implementation.
  In general it compares two harvest directories and visualizes the distribution of captured snapshots over time. Analyzes file statistics and generates histograms comparing harvest patterns between two directories (e.g., with and without rate limiting).
  - Basic usage:

    ```bash
    python3 harvest_comparator.py <original_dir> <modified_dir>
    ```

    Example:

    ```bash
    python3 harvest_comparator.py harvest_unlimited/ harvest_limited/
    ```

  - Features:
    - Collects and analyzes file information (count, total size, file types) for both directories
    - Extracts snapshot dates from `waybackup_snapshots` folder structure
    - Generates side-by-side histograms showing harvest date distribution
    - Useful for comparing harvest results before/after applying rate limiters or other modifications
  - Notes:
    - Requires `pandas` and `matplotlib` packages. Install with `pip install pandas matplotlib`.
    - Expects directories to contain a `waybackup_snapshots` subdirectory with snapshot data organized by site and timestamp.
    - Snapshot timestamps are expected to be 14-digit strings in `YYYYMMDDHHmmss` format.

- `ia_stats_fetcher.py`
  - Description: First VERY RAW and unpolished stab at fetching Internet Archive (Wayback Machine) statistics for a list of URLs. Queries the CDX API to retrieve capture counts by MIME type and unique URL counts for each site.
  - Basic usage:

    ```bash
    python3 ia_stats_fetcher.py <input.csv> <output.csv> [--parallel] [--delay SECONDS] [--workers N]
    ```

    Example:

    ```bash
    python3 ia_stats_fetcher.py urls.csv ia_stats.csv --parallel --delay 1 --workers 5
    ```

  - Features:
    - Queries the Internet Archive CDX API for URL captures
    - Counts captures by MIME type (text/html, image/jpeg, image/png)
    - Tracks unique URLs captured for each site
    - Supports sequential or parallel processing with configurable delays and worker threads
    - Outputs results to CSV format
  - Notes:
    - Requires `pandas` and `requests` packages. Install with `pip install pandas requests`.
    - Input CSV should have URLs in the first column.
    - **⚠️ Disclaimer**: This script has known timeout issues and may be buggy. The CDX API requests can timeout intermittently, especially with large batches of URLs, when processing multiple sites in parallel, or with very large sites.
- `create_build_ia-harvester_virtual_pyenv.sh`
  - Description: Helper shell script to create a `pyenv` virtualenv, clone the local development forks of `InternetArchiveExtractor` and `python-wayback-machine-downloader`, build/install the wayback package locally, patch the `InternetArchiveExtractor` requirements to point at the local wayback package, and install dependencies.
  - Basic usage:

    ```bash
    # Make executable (if necessary) and run from repository root
    chmod +x create_build_ia-harvester_virtual_pyenv.sh
    ./create_build_ia-harvester_virtual_pyenv.sh
    ```

    The script will create a `pyenv` virtualenv named `IA-Extractor_<folder>` (where `<folder>` is the current directory name), clone the two repos into the current directory, install the local wayback package, and install requirements for `InternetArchiveExtractor`.

  - Features / notes:
    - Uses `pyenv` + `pyenv-virtualenv` to create and activate a named virtual environment.
    - Clones `InternetArchiveExtractor` and `python-wayback-machine-downloader` from the project's GitHub forks.
    - Installs `python-wayback-machine-downloader` locally (`pip install .`) and updates `InternetArchiveExtractor/requirements.txt` to reference the local `pywaybackup` package via a `file://` URL. A backup of `requirements.txt` is created as `requirements.txt.bak` before modification.
    - Installs `InternetArchiveExtractor` dependencies into the created virtualenv.
    - Exits on errors (`set -euo pipefail`) and prints progress messages.

  - Requirements / prerequisites:
    - `pyenv` and `pyenv-virtualenv` installed and configured in your shell.
    - `git` and `pip` available in PATH.
    - Ability to build/compile Python (system build tools / headers may be required for some Python versions).
    - The script uses `PYTHON_VERSION="3.13.7"` by default — change the script if a different interpreter is needed.


- `multible_catagory_matcher.sql`
  - Description: SQLite SQL script for matching and categorizing URLs across multiple category labels in the corpus database. Intended to be run interactively inside a SQLite GUI (for example `DB Browser for SQLite`) against the `corpus-120b-wayback_url.db` schema.
  - Basic usage:

    1. Open `DB Browser for SQLite`.
    2. Open the database file `corpus-120b-wayback_url.db` (see Requirements below for location).
    3. Switch to the "Execute SQL" tab and run the contents of `multible_catagory_matcher.sql`.

    Example (run inside DB Browser for SQLite):

    ```sql
    -- Paste the SQL file contents into the Execute SQL tab and run
    ```

  - Notes / Requirements for running:
    - Runs in `DB Browser for SQLite` (or any SQLite client that can execute multi-statement SQL scripts).
    - Built to work with the structure of the `corpus-120b-wayback_url.db` database. Do not run on different schemas without adapting the queries.
    - The `corpus-120b-wayback_url.db` can be retrieved from OneDrive under `/Data/Databases/` in the project's storage.
    - Always backup the database before running scripts that modify data.

## Requirements

- Python 3.7 or newer
- The `warcio` package (install with `pip install warcio`)
 - `DB Browser for SQLite` (or any SQLite client) — required to run `multible_catagory_matcher.sql`. The `corpus-120b-wayback_url.db` used by the script can be retrieved from OneDrive under `/Data/Databases/`.

It's recommended to run the scripts inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install warcio
```

## Contributing

Add new scripts at the repository root and update this README with a short description and usage example for each new file.

