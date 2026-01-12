import requests
import pandas as pd
import time
import sys
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

CDX_API = "https://web.archive.org/cdx/search/cdx"
DEFAULT_REQUEST_DELAY = 2 # please note that this is in seconds
DEFAULT_WORKERS = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IAStatsFetcher/2.0)"
}

MIME_TYPES = ["text/html", "image/jpeg", "image/png"]


def normalize_url(url):
    parsed = urlparse(url)
    return parsed.scheme + "://" + parsed.netloc + parsed.path if parsed.netloc else url

def query_cdx(url):
    """Query the Internet Archive CDX API for all captures of a URL"""
    params = {
        "url": url + "/*",
        "output": "json",
        "collapse": "digest"
    }
    try:
        r = requests.get(CDX_API, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"Warning: CDX API returned {r.status_code} for {url}")
            return []
        data = r.json()
        return data[1:]  
    except Exception as e:
        print(f"Error querying {url}: {e}")
        return []

def scrape_ia_stats(site_url, index=None, total=None):
    """Scrape IA stats for a single site with optional progress display"""
    if index is not None and total is not None:
        print(f"Processing {index}/{total}: {site_url}")
    else:
        print(f"Processing: {site_url}")

    normalized = normalize_url(site_url)
    all_caps = query_cdx(normalized)

    if not all_caps:
        return {
            "Site": site_url,
            "Presence in internet archive": "N/A",
            "Captures (text/html)": "N/A",
            "Captures (image/jpeg)": "N/A",
            "Captures (image/png)": "N/A",
            "Unique URLs": "N/A"
        }

    counts = {m: 0 for m in MIME_TYPES}
    unique_urls = set()

    for row in all_caps:
        if len(row) < 4:
            continue
        mime = row[3]
        if mime in counts:
            counts[mime] += 1
        unique_urls.add(row[2])

    return {
        "Site": site_url,
        "Presence in internet archive": "Yes",
        "Captures (text/html)": counts["text/html"],
        "Captures (image/jpeg)": counts["image/jpeg"],
        "Captures (image/png)": counts["image/png"],
        "Unique URLs": len(unique_urls)
    }


def process_urls(urls, delay: int = DEFAULT_REQUEST_DELAY, parallel: bool = False, max_workers: int = DEFAULT_WORKERS):
    results = []
    total = len(urls)

    if parallel:
        per_worker_delay = delay / max_workers if max_workers > 0 else 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(scrape_ia_stats, url, i + 1, total): url
                for i, url in enumerate(urls)
            }
            for future in as_completed(future_to_url):
                res = future.result()
                results.append(res)
                if per_worker_delay > 0:
                    time.sleep(per_worker_delay)
    else:
        for i, url in enumerate(urls):
            res = scrape_ia_stats(url, i + 1, total)
            results.append(res)
            if delay > 0:
                time.sleep(delay)

    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python ia_stats_fetcher.py <input_csv> <output_csv> [--parallel] [--delay SECONDS] [--workers N]")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    # Parse optional arguments
    parallel = "--parallel" in sys.argv

    delay_index = sys.argv.index("--delay") + 1 if "--delay" in sys.argv else None
    delay = int(sys.argv[delay_index]) if delay_index else DEFAULT_REQUEST_DELAY

    workers_index = sys.argv.index("--workers") + 1 if "--workers" in sys.argv else None
    workers = int(sys.argv[workers_index]) if workers_index else DEFAULT_WORKERS

    # Read URLs from CSV (assumes first column contains URLs)
    df = pd.read_csv(input_csv)
    url_column = df.columns[0]
    urls = [str(u).strip() for u in df[url_column] if str(u).strip()]

    print(f"Processing {len(urls)} URLs {'in parallel' if parallel else 'sequentially'} with {workers} worker(s)...")

    results = process_urls(urls, delay=delay, parallel=parallel, max_workers=workers)

    # Save results
    out_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    out_df.to_csv(output_csv, index=False, encoding="utf-8")

    print(f"\nCSV generated: {output_csv}")


if __name__ == "__main__":
    main()
