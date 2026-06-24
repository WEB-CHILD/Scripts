#!/usr/bin/env python3

import argparse
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


NEVER_HARVESTED_MARKER = 'Url has never been harvested:'


def fetch_text(url: str, timeout: int = 20) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read().decode('utf-8', 'ignore')


def is_never_harvested(text: str) -> bool:
    return text.lstrip().startswith(NEVER_HARVESTED_MARKER)


def extract_thread_links(board_url: str, text: str) -> list[str]:
    hrefs = re.findall(r'href="([^"]+)"', text, flags=re.I)
    seen = set()
    thread_links = []

    for raw_href in hrefs:
        href = html.unescape(raw_href)
        if 'viewthread.jhtml' not in href:
            continue
        if '/blab/messageboards/' not in href and 'messageboards/viewthread.jhtml' not in href:
            continue
        absolute_href = urllib.parse.urljoin(board_url, href)
        if absolute_href in seen:
            continue
        seen.add(absolute_href)
        thread_links.append(absolute_href)

    return thread_links


def has_msg_content(board_url: str, board_text: str) -> bool:
    for thread_url in extract_thread_links(board_url, board_text):
        try:
            thread_text = fetch_text(thread_url)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            continue
        if not is_never_harvested(thread_text):
            return True
    return False


def fill_entries(entries: list[dict]) -> int:
    updated = 0
    board_cache: dict[str, tuple[bool, bool]] = {}

    for entry in entries:
        if 'has_playback' in entry and 'has_msg_content' in entry:
            continue

        board_url = entry['board_link']
        if board_url in board_cache:
            playback, msg_content = board_cache[board_url]
        else:
            try:
                board_text = fetch_text(board_url)
                playback = not is_never_harvested(board_text)
                msg_content = playback and has_msg_content(board_url, board_text)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
                playback = False
                msg_content = False
            board_cache[board_url] = (playback, msg_content)

        entry['has_playback'] = playback
        entry['has_msg_content'] = msg_content
        updated += 1

    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description='Fill missing playback flags for Nick message boards JSON.')
    parser.add_argument('--input', default='nick_msgboards_your_world.json')
    parser.add_argument('--output', default='nick_msgboards_your_world.json')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    entries = json.loads(input_path.read_text())
    updated = fill_entries(entries)

    print(f'updated {updated} entries')
    if not args.dry_run:
        output_path.write_text(json.dumps(entries, indent=2) + '\n')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())