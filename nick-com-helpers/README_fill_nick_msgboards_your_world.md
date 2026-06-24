# fill_nick_msgboards_your_world.py

Enriches a JSON dataset of archived Nickelodeon "Your World" message boards by probing each board URL and filling in two boolean flags that indicate whether archived content is actually available.

## Background

The input data is extracted from a SolrWayback instance serving archived crawls of `nick.com/blab/messageboards`. Each record represents one board as seen on a specific crawl date. Because the Wayback Machine sometimes records a URL without capturing meaningful content (returning a "Url has never been harvested" stub instead), this script checks each board and its threads to distinguish real captures from empty stubs.

## Input

A JSON file — default `nick_msgboards_your_world.json` — containing a list of objects. Each object must have at minimum:

| Field | Type | Description |
|---|---|---|
| `board_name` | string | Human-readable board name (e.g. `"Jokes"`) |
| `board_link` | string | Full URL to the archived board page |
| `board_id` | number | Numeric board ID from the original site |
| `year` / `month` / `day` | number | Crawl date |
| `source_url` | string | URL of the index page the board was found on |

The CSV file (`nick_msgboards_your_world.csv`) shows the same schema and can be used as a reference for what the JSON contains.

Entries that already have both `has_playback` and `has_msg_content` set are skipped without re-fetching.

## Output

The same list of objects with two new boolean fields added to each entry:

| Field | Description |
|---|---|
| `has_playback` | `true` if the board URL returns real archived HTML (not a "never harvested" stub) |
| `has_msg_content` | `true` if `has_playback` is true **and** at least one linked thread also has real archived content |

## Usage

```bash
python fill_nick_msgboards_your_world.py [--input FILE] [--output FILE] [--dry-run]
```

| Flag | Default | Description |
|---|---|---|
| `--input` | `nick_msgboards_your_world.json` | Path to the input JSON file |
| `--output` | `nick_msgboards_your_world.json` | Path to write the updated JSON (overwrites in place by default) |
| `--dry-run` | off | Print how many entries would be updated without writing the file |

### Examples

Update in place:
```bash
python fill_nick_msgboards_your_world.py
```

Write to a separate file:
```bash
python fill_nick_msgboards_your_world.py --input boards.json --output boards_filled.json
```

Preview without writing:
```bash
python fill_nick_msgboards_your_world.py --dry-run
```

## Notes

- Board URLs are cached within a run: if multiple entries share the same `board_link`, the URL is only fetched once.
- Network errors and timeouts for individual boards or threads are handled gracefully — the entry is marked `false` for both flags rather than aborting.
- Requires Python 3.10+ (uses `list[str]` and `tuple[bool, bool]` type hints in function signatures).
