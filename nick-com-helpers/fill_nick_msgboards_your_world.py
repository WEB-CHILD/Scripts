#!/usr/bin/env python3

import argparse
import html
import json
import re
import sys
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


def _log(msg: str) -> None:
    print(msg, flush=True)


def has_msg_content(board_url: str, board_text: str) -> bool:
    thread_urls = extract_thread_links(board_url, board_text)
    for i, thread_url in enumerate(thread_urls, 1):
        _log(f"    thread {i}/{len(thread_urls)}: {thread_url}")
        try:
            thread_text = fetch_text(thread_url)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            _log(f"      -> fetch error: {e}")
            continue
        if not is_never_harvested(thread_text):
            _log(f"      -> has content")
            return True
        _log(f"      -> never harvested")
    return False


def fill_entries(entries: list[dict]) -> int:
    updated = 0
    board_cache: dict[str, tuple[bool, bool]] = {}

    needs_update = [e for e in entries if 'has_playback' not in e or 'has_msg_content' not in e]
    total = len(needs_update)
    _log(f"{len(entries)} total entries, {total} need updating, {len(entries) - total} already filled")

    for idx, entry in enumerate(needs_update, 1):
        board_url = entry['board_link']
        _log(f"\n[{idx}/{total}] {board_url}")

        if board_url in board_cache:
            playback, msg_content = board_cache[board_url]
            _log(f"  -> cached: has_playback={playback}, has_msg_content={msg_content}")
        else:
            try:
                board_text = fetch_text(board_url)
                playback = not is_never_harvested(board_text)
                if playback:
                    _log(f"  board reachable, checking threads for content...")
                    msg_content = has_msg_content(board_url, board_text)
                else:
                    msg_content = False
                    _log(f"  board never harvested")
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                _log(f"  fetch error: {e}")
                playback = False
                msg_content = False
            _log(f"  -> has_playback={playback}, has_msg_content={msg_content}")
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